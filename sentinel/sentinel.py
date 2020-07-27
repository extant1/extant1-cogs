from datetime import datetime, timedelta

import discord
from redbot.core import Config, commands, checks
from discord.enums import ChannelType, MessageType

from redbot.core.utils.chat_formatting import bold


class Sentinel(commands.Cog):
    """The sentinel watches who comes and goes and makes a note in a specified channel."""

    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=91928524318855168)
        default_guild = {
            "channel": None,
            "enabled": False,
            "toggle_join": True,
            "toggle_leave": True,
            "toggle_edit": False,
            "toggle_ban": True,
            "toggle_unban": True,
            "toggle_role_change": True,
            "toggle_name_change": True,
            "ignored_roles": []
        }
        self.config.register_guild(**default_guild)

    async def on_member_join(self, member):
        toggle_join = await self.config.guild(member.guild).toggle_join()
        if toggle_join:
            # logger.info("{} joined the server.".format(member.display_name))
            channel = self.bot.get_channel(await self.config.guild(member.guild).channel())
            if (datetime.utcnow() - member.created_at) < timedelta(1):
                message = "\nWARNING!!!  ACCOUNT IS LESS THAN ONE DAY OLD."
            elif (datetime.utcnow() - member.created_at) < timedelta(7):
                message = "\nWARNING!!!  ACCOUNT IS LESS THAN SEVEN DAYS OLD."
            elif (datetime.utcnow() - member.created_at) > timedelta(7):
                message = ""
            embed = discord.Embed(title="Member Joined", description="\n{}{}".format(member.mention, message),
                                  color=0x00ff00)
            embed.set_thumbnail(url=member.avatar_url)
            embed.add_field(name=member.display_name, value="{}#{}".format(member.name, member.discriminator),
                            inline=True)
            embed.add_field(name="Account Created:", value="{}".format(member.created_at))
            embed.set_footer(text="ID: {}".format(member.id))
            await channel.send(embed=embed)
        else:
            return

    async def on_member_remove(self, member):
        toggle_leave = await self.config.guild(member.guild).toggle_leave()
        if toggle_leave:
            # logger.info("{} left the server.".format(member.display_name))
            channel = self.bot.get_channel(await self.config.guild(member.guild).channel())
            embed = discord.Embed(title="Member Left", color=0xff8000)
            embed.set_thumbnail(url=member.avatar_url)
            embed.add_field(name=member.display_name, value="{}#{}".format(member.name, member.discriminator),
                            inline=True)
            embed.set_footer(text="ID: {}".format(member.id))
            await channel.send(embed=embed)
        else:
            return

    async def on_member_ban(self, guild, member):
        toggle_ban = await self.config.guild(member.guild).toggle_ban()
        if toggle_ban:
            # logger.info("{} was banned from the server.".format(member.display_name))
            channel = self.bot.get_channel(await self.config.guild(member.guild).channel())
            embed = discord.Embed(title="Member Banned", color=0xffff00)
            embed.set_thumbnail(url=member.avatar_url)
            embed.add_field(name=member.display_name, value="{}#{}".format(member.name, member.discriminator),
                            inline=True)
            embed.set_footer(text="ID: {}".format(member.id))
            await channel.send(embed=embed)
        else:
            return

    async def on_member_unban(self, guild, member):
        toggle_unban = await self.config.guild(member.guild).toggle_unban()
        if toggle_unban:
            # logger.info("{} was unbanned from the server.".format(user.display_name))
            channel = self.bot.get_channel(await self.config.guild(member.guild).channel())
            embed = discord.Embed(title="Member Unbanned", color=0x8080ff)
            embed.set_thumbnail(url=member.avatar_url)
            embed.add_field(name=member.display_name, value="{}#{}".format(member.name, member.discriminator),
                            inline=True)
            embed.set_footer(text="ID: {}".format(member.id))
            await channel.send(embed=embed)
        else:
            return

    async def on_member_update(self, before, after):
        toggle_name_change = await self.config.guild(before.guild).toggle_unban()
        toggle_role_change = await self.config.guild(before.guild).toggle_unban()
        ignored_roles = await self.config.guild(before.guild).ignored_roles()
        if before.display_name != after.display_name or before.name != after.name and toggle_name_change:
            # logger.info("{} changed their name to {}.".format(before.display_name, after.display_name))
            channel = self.bot.get_channel(await self.config.guild(before.guild).channel())
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
            await channel.send(embed=embed)

        if before.roles != after.roles and toggle_role_change:
            old_roles = [r.name for r in before.roles if r.name != "@everyone"]
            new_roles = [r.name for r in after.roles if r.name != "@everyone"]
            old_roles_length = len(old_roles)
            new_roles_length = len(new_roles)
            verb = None
            role = []

            if old_roles_length < new_roles_length:
                verb = 'added'
                role = list(set(new_roles).difference(old_roles))
            elif old_roles_length > new_roles_length:
                verb = 'removed'
                role = list(set(old_roles).difference(new_roles))

            if role[0] in ignored_roles:
                return
            else:
                # logger.info("{} roles changed from {} to {}.".format(after.display_name, old_roles, new_roles))

                channel = self.bot.get_channel(await self.config.guild(before.guild).channel())
                embed = discord.Embed(title="Role changed",
                                      description="{} was {}.".format(role[0], verb),
                                      color=0xffff00)
                embed.set_thumbnail(url=after.avatar_url)
                embed.add_field(name="{}".format(after.display_name),
                                value="{}#{}".format(after.name, after.discriminator))
                embed.set_footer(text="ID: {}".format(before.id))
                await channel.send(embed=embed)


async def on_message_edit(self, before, after):
    toggle_edit = await self.config.guild(before.guild).toggle_edit()
    if toggle_edit:
        if len(after.embeds) is not 0:
            return
        if after.call is MessageType.pins_add:
            # logger.info("messaged was pinned:  {}".format(after.content))
            return
        if not after.author.bot:
            # logger.info("{} changed the message {} to {}.".format(after.author.display_name, before.content,
            #                                                       after.content))
            channel = self.bot.get_channel(await self.config.guild(before.guild).channel())
            embed = discord.Embed(title="Message edited",
                                  description="{}\n{}\nto\n{}".format(after.author.display_name, before.content,
                                                                      after.content),
                                  color=0x8080ff)
            embed.set_thumbnail(url=after.author.avatar_url)
            embed.set_footer(text="ID: {}".format(after.author.id))
            await channel.send(embed=embed)
    else:
        return


@checks.admin()
@commands.guild_only()
@commands.group(name="sentinel", invoke_without_command=False)
async def _sentinel(self, ctx):
    """Change sentinel settings"""
    if ctx.invoked_subcommand is None:
        await ctx.send_help()


@checks.admin()
@commands.guild_only()
@_sentinel.command(name="channel")
async def _channel(self, ctx, channel: str = None):
    """Set the channel the sentinel logs messages to."""
    if channel is not None:
        self._set_setting(ctx.message.server, "CHANNEL", channel)
        await self.bot.say("Setting sentinel channel to: " + bold(channel))
    else:
        await ctx.send_help()


@checks.admin()
@commands.guild_only()
@_sentinel.command(name="togglejoin")
async def _togglejoin(self, ctx, option: bool):
    """Toggle ."""
    if option is not None:
        self._set_setting(ctx.message.server, "ENABLED", option)
        await self.bot.say("The sentinel is enabled: " + bold(option))
    else:
        await ctx.send_help()


@checks.admin()
@commands.guild_only()
@_sentinel.command(name="ignored")
async def _ignored(self, ctx, *ignored):
    """Set a list of roles to ignore. Use space as a separator and quotes (") around roles with spaces.\n
    Example: [p]sentinel ignored First \"A Second\" \"The Third\" Fourth"""
    if len(ignored) is not 0:
        await self.config.guild(ctx.guild).ignored_roles.set(ignored)
        await ctx.send("Sentinel ignored roles are " + bold(ignored) + ".")
    else:
        await ctx.send_help()
