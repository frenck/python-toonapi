"""Asynchronous Python client for Quby ToonAPI."""
from __future__ import annotations

import asyncio
import json
import socket
from typing import Any, Awaitable, Callable, Dict, List, Optional

import aiohttp
import async_timeout
import backoff
from yarl import URL

from .__version__ import __version__
from .const import (
    ACTIVE_STATE_OFF,
    PROGRAM_STATE_OVERRIDE,
    TOON_API_BASE_PATH,
    TOON_API_HOST,
    TOON_API_PORT,
    TOON_API_SCHEME,
    TOON_API_VERSION,
)
from .exceptions import (
    ToonConnectionError,
    ToonConnectionTimeoutError,
    ToonError,
    ToonRateLimitError,
)
from .models import Agreement, Status


class Toon:
    """Main class for handling connections with the Quby ToonAPI."""

    agreement_id: Optional[str] = None
    _agreements: Optional[List[Agreement]] = None
    _status: Optional[Status] = None
    _close_session: bool = False

    _webhook_refresh_timer_task: Optional[asyncio.TimerHandle] = None
    _webhook_url: Optional[str] = None

    def __init__(
        self,
        *,
        request_timeout: int = 8,
        session: Optional[aiohttp.client.ClientSession] = None,
        token_refresh_method: Optional[Callable[[], Awaitable[str]]] = None,
        token: str,
        user_agent: Optional[str] = None,
    ) -> None:
        """Initialize connection with the Quby ToonAPI."""
        self._session = session

        self.request_timeout = request_timeout
        self.user_agent = user_agent
        self.token = token

        self.token_refresh_method = token_refresh_method

        if user_agent is None:
            self.user_agent = f"PythonToonAPI/{__version__}"

    @backoff.on_exception(backoff.expo, ToonConnectionError, max_tries=3, logger=None)
    @backoff.on_exception(
        backoff.expo, ToonRateLimitError, base=60, max_tries=6, logger=None
    )
    async def _request(
        self,
        uri: str = "",
        *,
        data: Optional[Any] = None,
        method: str = "GET",
        no_agreement: bool = False,
    ) -> Any:
        """Handle a request to the Quby ToonAPI."""
        if self.token_refresh_method is not None:
            self.token = await self.token_refresh_method()

        if self._status is None and self.agreement_id and not no_agreement:
            self.activate_agreement(agreement_id=self.agreement_id,)

        url = URL.build(
            scheme=TOON_API_SCHEME,
            host=TOON_API_HOST,
            port=TOON_API_PORT,
            path=TOON_API_BASE_PATH,
        ).join(URL(uri))

        headers = {
            "Authorization": f"Bearer {self.token}",
            "User-Agent": self.user_agent,
            "Accept": "application/json",
        }

        if not no_agreement and self._status is not None:
            headers.update(
                {
                    "X-Common-Name": self._status.agreement.display_common_name,
                    "X-Agreement-ID": self._status.agreement.agreement_id,
                }
            )

        if self._session is None:
            self._session = aiohttp.ClientSession()
            self._close_session = True

        try:
            with async_timeout.timeout(self.request_timeout):
                response = await self._session.request(
                    method, url, json=data, headers=headers, ssl=True,
                )
        except asyncio.TimeoutError as exception:
            raise ToonConnectionTimeoutError(
                "Timeout occurred while connecting to the Quby ToonAPI"
            ) from exception
        except (aiohttp.ClientError, socket.gaierror) as exception:
            raise ToonConnectionError(
                "Error occurred while communicating with the Quby ToonAPI"
            ) from exception

        content_type = response.headers.get("Content-Type", "")
        # Error handling
        if (response.status // 100) in [4, 5]:
            contents = await response.read()
            response.close()

            if response.status == 429:
                raise ToonRateLimitError(
                    "Rate limit error has occurred with the Quby ToonAPI"
                )

            if content_type == "application/json":
                raise ToonError(response.status, json.loads(contents.decode("utf8")))
            raise ToonError(response.status, {"message": contents.decode("utf8")})

        # Handle empty response
        if response.status == 204:
            return

        if "application/json" in content_type:
            return await response.json()
        return await response.text()

    async def activate_agreement(
        self,
        *,
        agreement_id: Optional[str] = None,
        display_common_name: Optional[str] = None,
        agreement: Optional[Agreement] = None,
    ) -> Agreement:
        """Set the active agreement for this Toon instance."""
        if self._agreements is None:
            await self.agreements()

        if not self._agreements:
            raise ToonError("No agreements found on linked account")

        for known_agreement in self._agreements:
            if (
                known_agreement == agreement
                or known_agreement.agreement_id == agreement_id
                or known_agreement.display_common_name == display_common_name
            ):
                self._status = Status(agreement=known_agreement)
                self.agreement_id = known_agreement.agreement_id
                self.display_common_name = known_agreement.display_common_name
                return known_agreement

        raise ToonError("Agreement could not be found on the linked account")

    async def agreements(self, force_update: bool = False) -> List[Agreement]:
        """Return the agreement(s) that are associated with the utility customer."""
        if self._agreements is None or force_update:
            agreements = await self._request(
                f"/toon/{TOON_API_VERSION}/agreements", no_agreement=True
            )
            self._agreements = [
                Agreement.from_dict(agreement) for agreement in agreements
            ]
        return self._agreements

    async def update(self, data: Dict[str, Any] = None) -> Optional[Status]:
        """Get all information in a single call."""
        assert self._status
        if data is None:
            data = await self._request(
                f"/toon/{TOON_API_VERSION}/{self.agreement_id}/status"
            )
        return self._status.update_from_dict(data)

    async def set_current_setpoint(self, temperature: float) -> None:
        """Set the target temperature for the thermostat."""
        assert self._status
        data = {
            "currentSetpoint": round(temperature * 100),
            "programState": PROGRAM_STATE_OVERRIDE,
            "activeState": ACTIVE_STATE_OFF,
        }
        await self._request(
            f"/toon/{TOON_API_VERSION}/{self.agreement_id}/thermostat",
            method="PUT",
            data=data,
        )
        self._status.thermostat.update_from_dict(data)

    async def set_active_state(
        self, active_state: int, program_state: int = PROGRAM_STATE_OVERRIDE
    ) -> None:
        """.."""
        assert self._status
        data = {"programState": program_state, "activeState": active_state}
        await self._request(
            f"/toon/{TOON_API_VERSION}/{self.agreement_id}/thermostat",
            method="PUT",
            data=data,
        )
        self._status.thermostat.update_from_dict(data)

    async def subscribe_webhook(self, application_id: str, url: str) -> None:
        """Register a webhook with Toon for live updates."""
        # Unregister old webhooks from this application ID
        await self.unsubscribe_webhook(application_id)

        # Register webhook
        await self._request(
            f"/toon/{TOON_API_VERSION}/{self.agreement_id}/webhooks",
            method="POST",
            data={
                "applicationId": application_id,
                "callbackUrl": url,
                "subscribedActions": [
                    "BoilerErrorInfo",
                    "GasUsage",
                    "PowerUsage",
                    "Thermostat",
                ],
            },
        )

    async def unsubscribe_webhook(self, application_id: str) -> None:
        """Delete all webhooks for this application ID."""
        await self._request(
            f"/toon/{TOON_API_VERSION}/{self.agreement_id}/webhooks/{application_id}",
            method="DELETE",
        )

    async def close(self) -> None:
        """Close open client session."""
        if self._session and self._close_session:
            await self._session.close()

    async def __aenter__(self) -> Toon:
        """Async enter."""
        return self

    async def __aexit__(self, *exc_info) -> None:
        """Async exit."""
        await self.close()
