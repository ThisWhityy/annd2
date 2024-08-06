from redbot.core.bot import Red

from .announcedaily4 import announcedaily4


async def setup(bot: Red):
    daily = announcedaily4(bot)
    r = bot.add_cog(daily)
    if r is not None:
        await r
        bot.loop.create_task(daily.check_day())
