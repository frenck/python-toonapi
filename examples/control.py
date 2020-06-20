# pylint: disable=W0621
"""Asynchronous Python client for Quby ToonAPI."""

import asyncio

from toonapi import Toon


async def main():
    """Show example on using the ToonAPI."""
    async with Toon(token="put-in-token-here") as toon:
        agreements = await toon.agreements()
        print(agreements)

        await toon.activate_agreement(agreement=agreements[0])

        status = await toon.update()
        print(status.gas_usage)
        print(status.thermostat)
        print(status.power_usage)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
