from redbot.core.bot import Red

from .announcedaily3 import announcedaily3


async def setup(bot: Red):
    daily = announcedaily3(bot)
    r = bot.add_cog(daily)
    if r is not None:
        await r
        bot.loop.create_task(daily.check_day())
