import datetime
import logging
import os

from .utils.dataIO import dataIO
from .utils import checks
from .utils import chat_formatting

import discord
from discord.ext import commands

DATA_PATH = "data/bouncer/"
JSON_PATH = DATA_PATH + "config.json"


class Bouncer:
    """The bouncer watches who comes and goes and makes a note in a specified channel."""

    def __init__(self, bot):
        self.bot = bot
        self.config = dataIO.load_json(JSON_PATH)

    def _set_setting(self, ctx, setting, value):
        settings = self._get_settings(ctx)
        if not settings:
            settings = {"channel": None}
        settings[setting] = value
        return self._create_settings(ctx, settings)

    def _create_settings(self, ctx, settings):
        serverid = ctx.message.server.id
        if serverid not in self.config:
            self.config[serverid] = {}
        self.config[serverid] = settings
        dataIO.save_json(JSON_PATH, self.config)

    def _get_settings(self, ctx):
        serverid = ctx.server.id
        if serverid not in self.config:
            return None
        else:
            return self.config[serverid]

    async def on_member_join(self, member):
        logger.info("{} joined the server.".format(member.display_name))
        channel_name = self._get_settings(member)
        logger.info("server settings: {}".format(channel_name['channel']))
        if channel_name is not None:
            logger.info("Config channel name: " + channel_name['channel'])
            channel = discord.utils.get(member.server.channels, name=channel_name['channel'])
            logger.info("channel: " + channel)
            logger.info("member: " + member.display_name)
            await self.bot.send_message(channel, '{} joined the server.'.format(member.display_name))
        else:
            logger.info("None?")
            return

    async def on_member_remove(self, member):
        logger.info("{} left the server.".format(member.display_name))
        channel_name = self._get_settings(member)
        logger.info("server settings: {}".format(channel_name['channel']))
        if channel_name is not None:
            logger.info("LConfig channel name: " + channel_name['channel'])
            channel = discord.utils.get(member.server.channels, name=channel_name['channel'])
            logger.info("Lchannel: " + channel)
            logger.info("Lmember: " + member.display_name)
            await self.bot.send_message(channel, '{} joined the server.'.format(member.display_name))
        else:
            logger.info("LNone?")
            return

    @checks.admin()
    @commands.group(name="bouncer", invoke_without_command=False, pass_context=True, no_pm=True)
    async def _bouncer(self, ctx):
        """Change the bouncer settings"""
        if ctx.invoked_subcommand is None:
            await self.bot.send_cmd_help(ctx)

    @checks.admin()
    @_bouncer.command(name="channel", pass_context=True, no_pm=True)
    async def _ip(self, ctx, channel: str = None):
        """Set the channel the bouncer reports to."""
        if channel is not None:
            self._set_setting(ctx, "channel", channel)
            logger.info("Someone joined the server.")
            await self.bot.say("Setting bouncer channel to: " + chat_formatting.bold(channel))
        else:
            await self.bot.send_cmd_help(ctx)


def check_folders():
    if os.path.exists("data/bouncer/"):
        os.rename("data/bouncer/", DATA_PATH)
    if not os.path.exists(DATA_PATH):
        print("Creating data/bouncer folder...")
        os.mkdir(DATA_PATH)


def check_files():
    if not dataIO.is_valid_json(JSON_PATH):
        print("Creating config.json...")
        dataIO.save_json(JSON_PATH, {})


def setup(bot):
    global logger
    check_folders()
    check_files()
    logger = logging.getLogger("bouncer")
    if logger.level == 0:
        # Prevents the logger from being loaded again in case of module reload
        logger.setLevel(logging.INFO)
        handler = logging.FileHandler(
            filename='data/bouncer/bouncer.log', encoding='utf-8', mode='a')
        handler.setFormatter(logging.Formatter(
            '%(asctime)s %(message)s', datefmt="[%d/%m/%Y %H:%M]"))
        logger.addHandler(handler)
    bot.add_cog(Bouncer(bot))
