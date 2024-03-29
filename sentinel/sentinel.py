
from datetime import datetime, timedelta, timezone

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

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        guild = member.guild
        enabled = await self.config.guild(member.guild).enabled()
        toggle_join = await self.config.guild(member.guild).toggle_join()
        if enabled and toggle_join:
            channel_name = await self.config.guild(guild).channel()
            channel = guild.get_channel(channel_name)
            if (datetime.now(timezone.utc) - member.created_at) < timedelta(1):
                message = "\nWARNING!!!  ACCOUNT IS LESS THAN ONE DAY OLD."
            elif (datetime.now(timezone.utc) - member.created_at) < timedelta(7):
                message = "\nWARNING!!!  ACCOUNT IS LESS THAN SEVEN DAYS OLD."
            elif (datetime.now(timezone.utc) - member.created_at) > timedelta(7):
                message = ""
            embed = discord.Embed(title="Member Joined", description=f"\n{member.mention}{message}", color=0x00FF00)

            embed.set_thumbnail(url=member.avatar_url)
            embed.add_field(name=member.display_name, value=f"{member.name}#{member.discriminator}", inline=True)

            embed.add_field(name="Account Created:", value=f"{member.created_at}")
            embed.set_footer(text=f"ID: {member.id}")
            await channel.send(embed=embed)
        else:
            return

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        guild = member.guild
        enabled = await self.config.guild(member.guild).enabled()
        toggle_leave = await self.config.guild(member.guild).toggle_leave()
        if enabled and toggle_leave:
            channel_name = await self.config.guild(guild).channel()
            channel = guild.get_channel(channel_name)
            embed = discord.Embed(title="Member Left", color=0xff8000)
            embed.set_thumbnail(url=member.avatar_url)
            embed.add_field(name=member.display_name, value=f"{member.name}#{member.discriminator}", inline=True)

            embed.set_footer(text=f"ID: {member.id}")
            await channel.send(embed=embed)
        else:
            return

    @commands.Cog.listener()
    async def on_member_ban(self, guild: discord.Guild, member: discord.Member):
        enabled = await self.config.guild(member.guild).enabled()
        toggle_ban = await self.config.guild(member.guild).toggle_ban()
        if enabled and toggle_ban:
            channel_name = await self.config.guild(guild).channel()
            channel = guild.get_channel(channel_name)
            embed = discord.Embed(title="Member Banned", color=0xffff00)
            embed.set_thumbnail(url=member.avatar_url)
            embed.add_field(name=member.display_name, value=f"{member.name}#{member.discriminator}", inline=True)

            embed.set_footer(text=f"ID: {member.id}")
            await channel.send(embed=embed)
        else:
            return

    @commands.Cog.listener()
    async def on_member_unban(self, guild: discord.Guild, member: discord.Member):
        enabled = await self.config.guild(member.guild).enabled()
        toggle_unban = await self.config.guild(member.guild).toggle_unban()
        if enabled and toggle_unban:
            channel_name = await self.config.guild(guild).channel()
            channel = guild.get_channel(channel_name)
            embed = discord.Embed(title="Member Unbanned", color=0x8080ff)
            embed.set_thumbnail(url=member.avatar_url)
            embed.add_field(name=member.display_name, value=f"{member.name}#{member.discriminator}", inline=True)

            embed.set_footer(text=f"ID: {member.id}")
            await channel.send(embed=embed)
        else:
            return

    @commands.Cog.listener()
    async def on_member_update(self, before: discord.Member, after: discord.Member):
        guild = after.guild
        channel_name = await self.config.guild(after.guild).channel()
        channel = guild.get_channel(channel_name)
        enabled = await self.config.guild(before.guild).enabled()
        toggle_name_change = await self.config.guild(before.guild).toggle_unban()
        toggle_role_change = await self.config.guild(before.guild).toggle_unban()
        ignored_roles = await self.config.guild(before.guild).ignored_roles()
        if enabled and toggle_name_change and before.display_name != after.display_name or before.name != after.name:
            embed = discord.Embed(title="User changed their name", description=f"{after.mention}", color=0xffff00)

            embed.set_thumbnail(url=after.avatar_url)
            embed.add_field(name="Before", value=f"{before.display_name}\n{before.name}#{before.discriminator}", inline=True)

            embed.add_field(name="After", value=f"{after.display_name}\n{after.name}#{after.discriminator}", inline=True)

            embed.set_footer(text=f"ID: {before.id}")
            await channel.send(embed=embed)
        if enabled and toggle_role_change and before.roles != after.roles:
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
            embed = discord.Embed(title="Role changed", description=f"{role[0]} was {verb}.", color=0xffff00)


            embed.set_thumbnail(url=after.avatar_url)
            embed.add_field(name=f"{after.display_name}", value=f"{after.name}#{after.discriminator}")

            embed.set_footer(text=f"ID: {before.id}")
            await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_message_edit(self, before: discord.Member, after: discord.Member):
        guild = after.guild
        enabled = await self.config.guild(guild).enabled()
        toggle_edit = await self.config.guild(before.guild).toggle_edit()
        if enabled and toggle_edit:
            if len(after.embeds) != 0:
                return
            if after.call is MessageType.pins_add:
                return
            if not after.author.bot:
                channel_name = await self.config.guild(after.guild).channel()
                channel = guild.get_channel(channel_name)
                embed = discord.Embed(title="Message edited", description=f"{after.author.display_name}\n{before.content}\nto\n{after.content}", color=0x8080ff)

                embed.set_thumbnail(url=after.author.avatar_url)
                embed.set_footer(text=f"ID: {after.author.id}")
                await channel.send(embed=embed)
        else:
            return

    @checks.admin()
    @commands.guild_only()
    @commands.group(name="sentinel", invoke_without_command=False)
    async def _sentinel(self, ctx):
        """Change sentinel settings"""
        if ctx.invoked_subcommand is None:
            enabled = await self.config.guild(ctx.guild).enabled()
            channel = await self.config.guild(ctx.guild).channel()
            toggle_join = await self.config.guild(ctx.guild).toggle_join()
            toggle_leave = await self.config.guild(ctx.guild).toggle_leave()
            toggle_edit = await self.config.guild(ctx.guild).toggle_edit()
            toggle_ban = await self.config.guild(ctx.guild).toggle_ban()
            toggle_unban = await self.config.guild(ctx.guild).toggle_unban()
            toggle_role_change = await self.config.guild(ctx.guild).toggle_role_change()
            toggle_name_change = await self.config.guild(ctx.guild).toggle_name_change()
            ignored_roles = await self.config.guild(ctx.guild).ignored_roles()
            embed = discord.Embed(title="GameServerQuery settings",
                                  description="Current settings for the GameServerQuery.", color=0x1675a3)
            embed.add_field(name="Enabled", value=enabled, inline=True)
            embed.add_field(name="Channel", value=channel, inline=True)
            embed.add_field(name="Toggle Join", value=toggle_join, inline=True)
            embed.add_field(name="Toggle Leave", value=toggle_leave, inline=True)
            embed.add_field(name="Toggle Edit", value=toggle_edit, inline=True)
            embed.add_field(name="Toggle Ban", value=toggle_ban, inline=True)
            embed.add_field(name="Toggle Unban", value=toggle_unban, inline=True)
            embed.add_field(name="Toggle Role Change", value=toggle_role_change, inline=True)
            embed.add_field(name="Toggle Name Change", value=toggle_name_change, inline=True)
            embed.add_field(name="Ignored Roles", value=ignored_roles)
            await ctx.send(embed=embed)

    @checks.admin()
    @commands.guild_only()
    @_sentinel.command(name="channel")
    async def _channel(self, ctx, channel: str = None):
        """Set the channel the sentinel logs messages to."""
        if channel is not None:
            channel_object = discord.utils.get(ctx.guild.channels, name=channel, type=ChannelType.text)

            await self.config.guild(ctx.guild).channel.set(channel_object.id)
            await ctx.send(f"Sentinel is using channel {bold(channel)} for logging.")
        else:
            await ctx.send_help()

    @checks.admin()
    @commands.guild_only()
    @_sentinel.command(name="toggleenable")
    async def _toggleenable(self, ctx):
        """Toggle sentinel on or off."""
        enabled = await self.config.guild(ctx.guild).enabled()
        enabled = not enabled
        await self.config.guild(ctx.guild).enabled.set(enabled)
        if enabled:
            await ctx.send("Sentinel is **enabled**.")
        else:
            await ctx.send("Sentinel is **disabled**.")

    @checks.admin()
    @commands.guild_only()
    @_sentinel.command(name="togglejoin")
    async def _togglejoin(self, ctx):
        """Toggle logging join messages."""
        toggle_join = await self.config.guild(ctx.guild).toggle_join()
        toggle_join = not toggle_join
        await self.config.guild(ctx.guild).toggle_join.set(toggle_join)
        if toggle_join:
            await ctx.send("Sentinel logging join is **enabled**.")
        else:
            await ctx.send("Sentinel logging join is **disabled**.")

    @checks.admin()
    @commands.guild_only()
    @_sentinel.command(name="toggleleave")
    async def _toggleleave(self, ctx):
        """Toggle logging leave messages."""
        toggle_leave = await self.config.guild(ctx.guild).toggle_leave()
        toggle_leave = not toggle_leave
        await self.config.guild(ctx.guild).toggle_leave.set(toggle_leave)
        if toggle_leave:
            await ctx.send("Sentinel logging leave is **enabled**.")
        else:
            await ctx.send("Sentinel logging leave is **disabled**.")

    @checks.admin()
    @commands.guild_only()
    @_sentinel.command(name="toggleedit")
    async def _toggleedit(self, ctx):
        """Toggle logging message edits."""
        toggle_edit = await self.config.guild(ctx.guild).toggle_edit()
        toggle_edit = not toggle_edit
        await self.config.guild(ctx.guild).toggle_edit.set(toggle_edit)
        if toggle_edit:
            await ctx.send("Sentinel logging edit is **enabled**.")
        else:
            await ctx.send("Sentinel logging edit is **disabled**.")

    @checks.admin()
    @commands.guild_only()
    @_sentinel.command(name="toggleban")
    async def _toggleban(self, ctx):
        """Toggle logging bans."""
        toggle_ban = await self.config.guild(ctx.guild).toggle_ban()
        toggle_ban = not toggle_ban
        await self.config.guild(ctx.guild).toggle_ban.set(toggle_ban)
        if toggle_ban:
            await ctx.send("Sentinel logging bans is **enabled**.")
        else:
            await ctx.send("Sentinel logging bans is **disabled**.")

    @checks.admin()
    @commands.guild_only()
    @_sentinel.command(name="toggleunban")
    async def _toggleunban(self, ctx):
        """Toggle logging unbans."""
        toggle_unban = await self.config.guild(ctx.guild).toggle_unban()
        toggle_unban = not toggle_unban
        await self.config.guild(ctx.guild).toggle_unban.set(toggle_unban)
        if toggle_unban:
            await ctx.send("Sentinel logging unbanning is **enabled**.")
        else:
            await ctx.send("Sentinel logging unbanning is **disabled**.")

    @checks.admin()
    @commands.guild_only()
    @_sentinel.command(name="togglerolechange")
    async def _togglerolechange(self, ctx):
        """Toggle logging role changes."""
        toggle_role_change = await self.config.guild(ctx.guild).toggle_role_change()
        toggle_role_change = not toggle_role_change
        await self.config.guild(ctx.guild).toggle_role_change.set(toggle_role_change)
        if toggle_role_change:
            await ctx.send("Sentinel logging role changes is **enabled**.")
        else:
            await ctx.send("Sentinel logging role changes is **disabled**.")

    @checks.admin()
    @commands.guild_only()
    @_sentinel.command(name="togglenamechange")
    async def _togglenamechange(self, ctx):
        """Toggle logging name changes."""
        toggle_name_change = await self.config.guild(ctx.guild).toggle_name_change()
        toggle_name_change = not toggle_name_change
        await self.config.guild(ctx.guild).toggle_name_change.set(toggle_name_change)
        if toggle_name_change:
            await ctx.send("Sentinel logging name changes is **enabled**.")
        else:
            await ctx.send("Sentinel logging name changes is **disabled**.")

    @checks.admin()
    @commands.guild_only()
    @_sentinel.command(name="ignored")
    async def _ignored(self, ctx, *ignored):
        """Set a list of roles to ignore. Use space as a separator and quotes (") around roles with spaces.\\n
        Example: [p]sentinel ignored First \"A Second\" \"The Third\" Fourth"""
        if ignored:
            await self.config.guild(ctx.guild).ignored_roles.set(ignored)
            ignored = ' '.join(ignored)
            await ctx.send(f"Sentinel is ignoring roles {bold(ignored)}.")
        else:
            await ctx.send_help()
