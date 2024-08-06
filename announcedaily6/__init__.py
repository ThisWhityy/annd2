from redbot.core.bot import Red

from .announcedaily6 import announcedaily6


async def setup(bot: Red):
    daily = announcedaily6(bot)
    r = bot.add_cog(daily)
    if r is not None:
        await r
        bot.loop.create_task(daily.check_day())
