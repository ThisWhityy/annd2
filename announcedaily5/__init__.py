from redbot.core.bot import Red

from .announcedaily5 import announcedaily5


async def setup(bot: Red):
    daily = announcedaily5(bot)
    r = bot.add_cog(daily)
    if r is not None:
        await r
        bot.loop.create_task(daily.check_day())
