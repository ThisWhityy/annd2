import asyncio
from datetime import datetime, timedelta, time
import discord
from redbot.core import commands, Config
from redbot.core.utils.chat_formatting import pagify, warning
from redbot.core.i18n import Translator

from .helpers import (
    parse_time,
    allowed_to_create,
    get_event_embed,
    allowed_to_edit,
    check_event_start,
)
from .menus import event_menu

_ = Translator("EventMaker", __file__)

class EventMaker(commands.Cog):
    """
    A tool for creating events inside of Discord. Anyone can
    create an event by default. If a specific role has been
    specified, users must have that role or any role above it in
    the hierarchy or be the server owner to create events.
    """

    default_guild = {"events": [], "min_role": 0, "next_available_id": 1, "channel": 0}
    default_member = {"dms": False}

    def __init__(self, bot: Red):
        self.bot = bot
        self.settings = Config.get_conf(self, identifier=59595922, force_registration=True)
        self.settings.register_guild(**self.default_guild)
        self.settings.register_member(**self.default_member)
        loop = self.bot.loop
        self.event_check_task = loop.create_task(self.check_events())
        self.daily_event_task = loop.create_task(self.schedule_daily_events())

    def cog_unload(self):
        self.event_check_task.cancel()
        self.daily_event_task.cancel()

    @commands.group()
    @commands.guild_only()
    async def event(self, ctx: commands.Context):
        """Base command for events"""
        pass

    @event.command(name="create")
    @allowed_to_create()
    async def event_create(self, ctx: commands.Context, *, event_data: str):
        """Create a new event"""
        # Implementation for creating an event based on user input
        pass

    async def schedule_daily_events(self):
        while True:
            now = datetime.utcnow()
            # Calculate the next 1 PM, 2 PM, and 3 PM UTC
            next_1pm = datetime.combine(now.date(), time(13, 0)) + timedelta(days=1 if now.time() >= time(13, 0) else 0)
            next_2pm = datetime.combine(now.date(), time(14, 0)) + timedelta(days=1 if now.time() >= time(14, 0) else 0)
            next_3pm = datetime.combine(now.date(), time(15, 0)) + timedelta(days=1 if now.time() >= time(15, 0) else 0)

            # Calculate the sleep time until the next event
            sleep_time_1pm = (next_1pm - now).total_seconds()
            sleep_time_2pm = (next_2pm - now).total_seconds()
            sleep_time_3pm = (next_3pm - now).total_seconds()

            # Sleep until the next event time
            await asyncio.sleep(min(sleep_time_1pm, sleep_time_2pm, sleep_time_3pm))

            # Create events at 1 PM, 2 PM, and 3 PM UTC
            if sleep_time_1pm <= 0:
                await self.create_event("Training Center Session", 13)
            if sleep_time_2pm <= 0:
                await self.create_event("Training Center Session", 14)
            if sleep_time_3pm <= 0:
                await self.create_event("Training Center Session", 15)

    async def create_event(self, name, hour):
        now = datetime.utcnow()
        event_time = datetime.combine(now.date(), time(hour, 0))
        event = {
            "id": await self.settings.guild(ctx.guild).next_available_id(),
            "name": name,
            "start_time": event_time.timestamp(),
            "participants": [],
            "has_started": False,
            "create_time": now.timestamp()
        }
        async with self.settings.guild(ctx.guild).events() as event_list:
            event_list.append(event)
            event_list.sort(key=lambda x: x["id"])
        await self.settings.guild(ctx.guild).next_available_id.set(event["id"] + 1)

    async def check_events(self):
        CHECK_DELAY = 300
        while self == self.bot.get_cog("EventMaker"):
            for guild in self.bot.guilds:
                async with self.settings.guild(guild).events() as event_list:
                    channel = guild.get_channel(await self.settings.guild(guild).channel())
                    if channel is None:
                        channel = guild.system_channel
                    for event in event_list:
                        changed, data = await check_event_start(channel, event, self.settings)
                        if not changed:
                            continue
                        event_list.remove(event)
                        event_list.append(data)
                    event_list.sort(key=lambda x: x["create_time"])
            await asyncio.sleep(CHECK_DELAY)

    @commands.command(name="join")
    async def event_join(self, ctx: commands.Context, event_id: int):
        """Join an event"""
        guild = ctx.guild
        to_join = None
        async with self.settings.guild(guild).events() as event_list:
            for event in event_list:
                if event["id"] == event_id:
                    to_join = event
                    event_list.remove(event)
                    break

            if not to_join:
                return await ctx.send("I could not find an event with that id!")

            if not to_join["has_started"]:
                if ctx.author.id not in to_join["participants"]:
                    to_join["participants"].append(ctx.author.id)
                    await ctx.tick()
                    event_list.append(to_join)
                    event_list.sort(key=lambda x: x["id"])
                else:
                    await ctx.send("You have already joined that event!")
            else:
                await ctx.send("That event has already started!")

    @commands.command(name="leave")
    async def event_leave(self, ctx: commands.Context, event_id: int):
        """Leave the specified event"""
        guild = ctx.guild
        to_leave = None
        async with self.settings.guild(guild).events() as event_list:
            for event in event_list:
                if event["id"] == event_id:
                    to_leave = event
                    event_list.remove(event)
                    break

            if not to_leave:
                return await ctx.send("I could not find an event with that id!")

            if not to_leave["has_started"]:
                if ctx.author.id in to_leave["participants"]:
                    to_leave["participants"].remove(ctx.author.id)
                    await ctx.send("Left the event!")
                    event_list.append(to_leave)
                    event_list.sort(key=lambda x: x["id"])
                else:
                    await ctx.send("You are not part of that event!")

    @eventset.command(name="channel")
    @checks.admin_or_permissions(manage_guild=True)

    async def check_events(self):
        CHECK_DELAY = 300
        while self == self.bot.get_cog("EventMaker"):
            for guild in self.bot.guilds:
                async with self.settings.guild(guild).events() as event_list:
                    channel = guild.get_channel(await self.settings.guild(guild).channel())
                    if channel is None:
                        channel = guild.system_channel
                    for event in event_list:
                        changed, data = await check_event_start(channel, event, self.settings)
                        if not changed:
                            continue
                        event_list.remove(event)
                        event_list.append(data)
                    event_list.sort(key=lambda x: x["create_time"])
            await asyncio.sleep(CHECK_DELAY)
