import logging
import os
from datetime import datetime, timedelta

import discord
from discord.enums import ChannelType, MessageType
from discord.ext import commands

from .utils import chat_formatting
from .utils import checks
from .utils.dataIO import dataIO

DATA_PATH = "data/sentinel/"
JSON_PATH = DATA_PATH + "settings.json"


class Sentinel:
    """The sentinel watches who comes and goes and makes a note in a specified channel."""

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
        serverid = ctx.id
        if serverid not in self.config:
            self.config[serverid] = {}
        self.config[serverid] = settings
        dataIO.save_json(JSON_PATH, self.config)

    def _get_settings(self, ctx):
        if ctx.id is None:
            serverid = None
        else:
            serverid = ctx.id
        if serverid not in self.config:
            return None
            # self.config[serverid] = {}
            # settings = {"CHANNEL": None, "ENABLED": False, "CreatedBy": 'GetSettings'}
            # self._create_settings(ctx, settings)
            # dataIO.save_json(JSON_PATH, self.config)
        return self.config[serverid]

    async def on_member_join(self, member):
        settings = self._get_settings(member.server)
        if settings is not None and settings['ENABLED'] is not False:
            logger.info("{} joined the server.".format(member.display_name))
            channel = discord.utils.get(member.server.channels, name=str(settings['CHANNEL']),
                                        type=ChannelType.text)
            if (datetime.utcnow() - member.created_at) < timedelta(1):
                message = "\nWARNING!!!  ACCOUNT IS LESS THAN ONE DAY OLD."
            elif (datetime.utcnow() - member.created_at) < timedelta(3):
                message = "\nWARNING!!!  ACCOUNT IS LESS THAN THREE DAYS OLD."
            elif (datetime.utcnow() - member.created_at) > timedelta(3):
                message = ""
            embed = discord.Embed(title="Member Joined", description="\n{}{}".format(member.mention, message), color=0x00ff00)
            embed.set_thumbnail(url=member.avatar_url)
            embed.add_field(name=member.display_name, value="{}#{}".format(member.name, member.discriminator),
                            inline=True)
            embed.add_field(name="Account Created:", value="{}".format(member.created_at))
            embed.set_footer(text="ID: {}".format(member.id))
            await self.bot.send_message(channel, embed=embed)
        else:
            logger.info("None?")
            return

    async def on_member_remove(self, member):
        settings = self._get_settings(member.server)
        if settings is not None and settings['ENABLED'] is not False:
            logger.info("{} left the server.".format(member.display_name))
            channel = discord.utils.get(member.server.channels, name=str(settings['CHANNEL']),
                                        type=ChannelType.text)
            embed = discord.Embed(title="Member Left", color=0xff8000)
            embed.set_thumbnail(url=member.avatar_url)
            embed.add_field(name=member.display_name, value="{}#{}".format(member.name, member.discriminator),
                            inline=True)
            embed.set_footer(text="ID: {}".format(member.id))
            await self.bot.send_message(channel, embed=embed)
        else:
            return

    async def on_member_ban(self, member):
        settings = self._get_settings(member.server)
        if settings is not None and settings['ENABLED'] is not False:
            logger.info("{} was banned from the server.".format(member.display_name))
            channel = discord.utils.get(member.server.channels, name=str(settings['CHANNEL']),
                                        type=ChannelType.text)
            embed = discord.Embed(title="Member Banned", color=0xffff00)
            embed.set_thumbnail(url=member.avatar_url)
            embed.add_field(name=member.display_name, value="{}#{}".format(member.name, member.discriminator),
                            inline=True)
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
            embed.set_thumbnail(url=user.avatar_url)
            embed.add_field(name=user.display_name, value="{}#{}".format(user.name, user.discriminator), inline=True)
            embed.set_footer(text="ID: {}".format(user.id))
            await self.bot.send_message(channel, embed=embed)
        else:
            return

    async def on_member_update(self, before, after):
        settings = self._get_settings(before.server)
        if settings is not None:
            if settings['ENABLED']:
                if before.display_name != after.display_name or before.name != after.name:
                    logger.info("{} changed their name to {}.".format(before.display_name, after.display_name))
                    channel = discord.utils.get(after.server.channels, name=str(settings['CHANNEL']),
                                                type=ChannelType.text)
                    embed = discord.Embed(title="User changed their name",
                                          description="{}".format(after.mention),
                                          color=0xffff00)
                    embed.set_thumbnail(url=after.avatar_url)
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
                    old_roles_length = len(old_roles)
                    new_roles_length = len(new_roles)
                    verb = None
                    role = []

                    if old_roles_length < new_roles_length:
                        verb = 'added'
                    elif old_roles_length > new_roles_length:
                        verb = 'removed'

                    def Diff(li1, li2):
                        li_dif = [i for i in li1 + li2 if i not in li1 or i not in li2]
                        return li_dif

                    role = Diff(old_roles, new_roles)

                    if role[0] in settings['IGNORED']:
                        return
                    else:
                        logger.info("{} roles changed from {} to {}.".format(after.display_name, old_roles, new_roles))

                        channel = discord.utils.get(after.server.channels, name=str(settings['CHANNEL']),
                                                    type=ChannelType.text)
                        embed = discord.Embed(title="Role changed",
                                              description="{} was {}.".format(role[0], verb),
                                              color=0xffff00)
                        embed.set_thumbnail(url=after.avatar_url)
                        embed.add_field(name="{}".format(after.display_name),
                                        value="{}#{}".format(after.name, after.discriminator))
                        embed.set_footer(text="ID: {}".format(before.id))
                        await self.bot.send_message(channel, embed=embed)
            else:
                return
        else:
            return

    async def on_message_edit(self, before, after):
        settings = self._get_settings(before.server)
        if settings is not None and settings['ENABLED']:
            if len(after.embeds) is not 0:
                return
            if after.call is MessageType.pins_add:
                logger.info("messaged was pinned:  {}".format(after.content))
                return
            if not after.author.bot:
                logger.info("{} changed the message {} to {}.".format(after.author.display_name, before.content,
                                                                      after.content))
                channel = discord.utils.get(before.server.channels, name=str(settings['CHANNEL']),
                                            type=ChannelType.text)
                embed = discord.Embed(title="Message edited",
                                      description="{}\n{}\nto\n{}".format(after.author.display_name, before.content,
                                                                          after.content),
                                      color=0x8080ff)
                embed.set_thumbnail(url=after.author.avatar_url)
                embed.set_footer(text="ID: {}".format(after.author.id))
                await self.bot.send_message(channel, embed=embed)
        else:
            return

    @checks.admin()
    @commands.group(name="sentinel", invoke_without_command=False, pass_context=True, no_pm=True)
    async def _bouncer(self, ctx):
        """Change the sentinel settings"""
        if ctx.invoked_subcommand is None:
            await self.bot.send_cmd_help(ctx)

    @checks.admin()
    @_bouncer.command(name="channel", pass_context=True, no_pm=True)
    async def _channel(self, ctx, channel: str = None):
        """Set the channel the sentinel reports to."""
        if channel is not None:
            self._set_setting(ctx.message.server, "CHANNEL", channel)
            await self.bot.say("Setting sentinel channel to: " + chat_formatting.bold(channel))
        else:
            await self.bot.send_cmd_help(ctx)

    @checks.admin()
    @_bouncer.command(name="enabled", pass_context=True, no_pm=True)
    async def _enabled(self, ctx, option: bool):
        """Enable or disable the Bouncer."""
        if option is not None:
            self._set_setting(ctx.message.server, "ENABLED", option)
            await self.bot.say("The sentinel is enabled: " + chat_formatting.bold(option))
        else:
            await self.bot.send_cmd_help(ctx)

    @checks.admin()
    @_bouncer.command(name="ignored", pass_context=True, no_pm=True)
    async def _ignored(self, ctx, *ignored):
        """Set a list of roles to ignore. Use space as a separator and quotes (") around roles with spaces.\n
        Example:  First, \"A Second\", \"The Third\", Fourth"""
        if len(ignored) is not 0:
            self._set_setting(ctx.message.server, "IGNORED", ignored)
            await self.bot.say("Ignored roles are: " + chat_formatting.bold(ignored))
        else:
            await self.bot.send_cmd_help(ctx)


def check_folders():
    if os.path.exists("data/sentinel/"):
        os.rename("data/sentinel/", DATA_PATH)
    if not os.path.exists(DATA_PATH):
        print("Creating data/sentinel folder...")
        os.mkdir(DATA_PATH)


def check_files():
    if not dataIO.is_valid_json(JSON_PATH):
        print("Creating config.json...")
        dataIO.save_json(JSON_PATH, {})


def setup(bot):
    global logger
    check_folders()
    check_files()
    logger = logging.getLogger("sentinel")
    if logger.level == 0:
        # Prevents the logger from being loaded again in case of module reload
        logger.setLevel(logging.INFO)
        handler = logging.FileHandler(
            filename='data/sentinel/sentinel.log', encoding='utf-8', mode='a')
        handler.setFormatter(logging.Formatter(
            '%(asctime)s %(message)s', datefmt="[%d/%m/%Y %H:%M]"))
        logger.addHandler(handler)
    bot.add_cog(Sentinel(bot))
