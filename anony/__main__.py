# Copyright (c) 2025 AnonymousX1025
# Licensed under the MIT License.
# This file is part of AnonXMusic


import asyncio
import signal
import importlib

from anony import (anon, app, config, db,
                   logger, stop, userbot, yt)
from anony.plugins import all_modules


async def idle():
    loop = asyncio.get_running_loop()
    stop_event = asyncio.Event()

    try:
        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(sig, stop_event.set)
    except NotImplementedError:
        def handler(sig, frame):
            loop.call_soon_threadsafe(stop_event.set)

        signal.signal(signal.SIGINT, handler)
        signal.signal(signal.SIGTERM, handler)

    await stop_event.wait()

async def main():
    await db.connect()
    await app.boot()
    await userbot.boot()
    await anon.boot()

    for module in all_modules:
        importlib.import_module(f"anony.plugins.{module}")
    logger.info(f"Loaded {len(all_modules)} modules.")

    if config.COOKIES_URL:
        await yt.save_cookies(config.COOKIES_URL)

    sudoers = await db.get_sudoers()
    app.sudoers.update(sudoers)
    app.bl_users.update(await db.get_blacklisted())
    logger.info(f"Loaded {len(app.sudoers)} sudo users.")

    from anony.helpers import thumb
    await yt.fallen.get_session()
    #await thumb.get_session()

    await idle()
    await stop()
    await yt.fallen.session.close()
    if thumb.session:
      await thumb.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
