from redbot.core.bot import Red

from .announcedaily2 import announcedaily2


async def setup(bot: Red):
    daily = announcedaily2(bot)
    r = bot.add_cog(daily)
    if r is not None:
        await r
        bot.loop.create_task(daily.check_day())
