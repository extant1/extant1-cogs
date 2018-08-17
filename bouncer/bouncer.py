import datetime
import logging
import os

from .utils.dataIO import dataIO
from .utils import checks
from .utils import chat_formatting

import discord
from discord.ext import commands
from discord.enums import ChannelType

DATA_PATH = "data/bouncer/"
JSON_PATH = DATA_PATH + "settings.json"


class Bouncer:
    """The bouncer watches who comes and goes and makes a note in a specified channel."""

    def __init__(self, bot):
        self.bot = bot
        self.config = dataIO.load_json(JSON_PATH)

    def _set_setting(self, ctx, setting, value):
        settings = self._get_settings(ctx)
        if not settings:
            settings = {"CHANNEL": None, "ENABLED": False}
        settings[setting] = value
        return self._create_settings(ctx, settings)

    def _create_settings(self, ctx, settings):
        serverid = ctx.server.id
        if serverid not in self.config:
            self.config[serverid] = {}
        self.config[serverid] = settings
        dataIO.save_json(JSON_PATH, self.config)

    def _get_settings(self, ctx):
        serverid = ctx.server.id
        if serverid not in self.config:
            self.config[serverid] = {}
            settings = {"CHANNEL": None, "ENABLED": False}
            self._create_settings(ctx, settings)
            dataIO.save_json(JSON_PATH, self.config)
        return self.config[serverid]

    async def on_member_join(self, member):
        settings = self._get_settings(member)
        if settings is not None and settings['ENABLED'] is not False:
            logger.info("{} joined the server.".format(member.display_name))
            channel = discord.utils.get(member.server.channels, name=str(settings['CHANNEL']),
                                        type=ChannelType.text)
            embed = discord.Embed(title="Member Joined", description="\n{}".format(member.mention), color=0x00ff00)
            embed.add_field(name=member.display_name, value="{}#{}".format(member.name, member.discriminator),
                            inline=True)
            embed.set_footer(text="ID: {}".format(member.id))
            await self.bot.send_message(channel, embed=embed)
        else:
            logger.info("None?")
            return

    async def on_member_remove(self, member):
        settings = self._get_settings(member)
        if settings is not None and settings['ENABLED'] is not False:
            logger.info("{} left the server.".format(member.display_name))
            channel = discord.utils.get(member.server.channels, name=str(settings['CHANNEL']),
                                        type=ChannelType.text)
            embed = discord.Embed(title="Member Left", color=0xff8000)
            embed.add_field(name=member.display_name, value="{}#{}".format(member.name, member.discriminator),
                            inline=True)
            embed.set_footer(text="ID: {}".format(member.id))
            await self.bot.send_message(channel, embed=embed)
        else:
            return

    async def on_member_ban(self, member):
        settings = self._get_settings(member)
        if settings is not None and settings['ENABLED'] is not False:
            logger.info("{} was banned from the server.".format(member.display_name))
            channel = discord.utils.get(member.server.channels, name=str(settings['CHANNEL']),
                                        type=ChannelType.text)
            embed = discord.Embed(title="Member Banned", color=0xffff00)
            embed.add_field(name=member.mention, value="{}#{}".format(member.name, member.discriminator), inline=True)
            embed.set_footer(text="ID: {}".format(member.id))
            await self.bot.send_message(channel, embed=embed)
        else:
            return

    async def on_member_unban(self, server, user):
        settings = self._get_settings(server)
        if settings is not None and settings['ENABLED'] is not False:
            logger.info("{} was unbanned from the server.".format(user.display_name))
            channel = discord.utils.get(server.channels, name=str(settings['CHANNEL']),
                                        type=ChannelType.text)
            embed = discord.Embed(title="Member Unbanned", color=0x8080ff)
            embed.add_field(name=user.mention, value="{}#{}".format(user.name, user.discriminator), inline=True)
            embed.set_footer(text="ID: {}".format(user.id))
            await self.bot.send_message(channel, embed=embed)
        else:
            return

    async def on_member_update(self, before, after):
        settings = self._get_settings(after)
        if settings is not None:
            if settings['ENABLED']:
                if before.display_name != after.display_name or before.name != after.name:
                    logger.info("{} changed their name to {}.".format(before.display_name, after.display_name))
                    channel = discord.utils.get(after.server.channels, name=str(settings['CHANNEL']),
                                                type=ChannelType.text)
                    embed = discord.Embed(title="User changed their name",
                                          description="{}".format(after.mention),
                                          color=0xffff00)
                    embed.add_field(name="Before",
                                    value="{}\n{}#{}".format(before.display_name, before.name, before.discriminator),
                                    inline=True)
                    embed.add_field(name="After",
                                    value="{}\n{}#{}".format(after.display_name, after.name, after.discriminator),
                                    inline=True)
                    embed.set_footer(text="ID: {}".format(before.id))
                    await self.bot.send_message(channel, embed=embed)
                if before.roles != after.roles:
                    old_roles = [r.name for r in before.roles if r.name != "@everyone"]
                    new_roles = [r.name for r in after.roles if r.name != "@everyone"]
                    if len(old_roles) == 0:
                        old_roles.append("None")
                    if len(new_roles) == 0:
                        new_roles.append("None")
                    logger.info("{} roles changed from {} to {}.".format(after.display_name, old_roles, new_roles))
                    channel = discord.utils.get(after.server.channels, name=str(settings['CHANNEL']),
                                                type=ChannelType.text)
                    embed = discord.Embed(title="Role changed",
                                          description="Before:\n{}\n\nAfter:\n{}".format(
                                              ', '.join(str(e) for e in old_roles),
                                              ', '.join(str(e) for e in new_roles)),
                                          color=0xffff00)
                    embed.add_field(name="{}".format(after.display_name),
                                    value="{}#{}".format(after.name, after.discriminator))
                    embed.set_footer(text="ID: {}".format(before.id))
                    await self.bot.send_message(channel, embed=embed)
            else:
                return
        else:
            return

    @checks.admin()
    @commands.group(name="bouncer", invoke_without_command=False, pass_context=True, no_pm=True)
    async def _bouncer(self, ctx):
        """Change the bouncer settings"""
        if ctx.invoked_subcommand is None:
            await self.bot.send_cmd_help(ctx)

    @checks.admin()
    @_bouncer.command(name="channel", pass_context=True, no_pm=True)
    async def _channel(self, ctx, channel: str = None):
        """Set the channel the bouncer reports to."""
        if channel is not None:
            self._set_setting(ctx.message, "CHANNEL", channel)
            await self.bot.say("Setting bouncer channel to: " + chat_formatting.bold(channel))
        else:
            await self.bot.send_cmd_help(ctx)

    @checks.admin()
    @_bouncer.command(name="enabled", pass_context=True, no_pm=True)
    async def _enabled(self, ctx, option: bool):
        """Enable or disable the Bouncer."""
        if option is not None:
            self._set_setting(ctx.message, "ENABLED", option)
            await self.bot.say("The bouncer is enabled: " + chat_formatting.bold(option))
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
