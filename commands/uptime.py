"""
Uptime commands for setting channels and managing bot monitoring.
"""

import discord
from discord import app_commands
from discord.ext import commands
import json
import os

DATA_FILE = 'bot_data.json'


def load_data():
    """Load bot data from JSON file."""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {'channels': {}, 'monitored_bots': {}, 'uptime_stats': {}}


def save_data(data):
    """Save bot data to JSON file."""
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)


class UptimeCog(commands.Cog):
    """Cog for uptime monitoring commands."""
    
    def __init__(self, bot):
        self.bot = bot
    
    uptime_group = app_commands.Group(name="uptime", description="Uptime monitoring commands")
    
    @uptime_group.command(name="set-channel", description="Set the channel for uptime notifications")
    @app_commands.describe(channel="The channel to receive uptime notifications")
    @app_commands.checks.has_permissions(administrator=True)
    async def set_channel(self, interaction: discord.Interaction, channel: discord.TextChannel):
        """Set the notification channel for uptime alerts."""
        data = load_data()
        guild_id = str(interaction.guild_id)
        
        if 'channels' not in data:
            data['channels'] = {}
        
        data['channels'][guild_id] = str(channel.id)
        save_data(data)
        
        await interaction.response.send_message(
            f'✅ Uptime notifications will be sent to {channel.mention}',
            ephemeral=True
        )
    
    @uptime_group.command(name="remove-channel", description="Remove the notification channel")
    @app_commands.checks.has_permissions(administrator=True)
    async def remove_channel(self, interaction: discord.Interaction):
        """Remove the notification channel."""
        data = load_data()
        guild_id = str(interaction.guild_id)
        
        if guild_id in data.get('channels', {}):
            del data['channels'][guild_id]
            save_data(data)
            await interaction.response.send_message(
                '✅ Notification channel has been removed',
                ephemeral=True
            )
        else:
            await interaction.response.send_message(
                '⚠️ No notification channel is set for this server',
                ephemeral=True
            )
    
    @uptime_group.command(name="add-bot", description="Add a bot to monitor")
    @app_commands.describe(bot_user="The bot to monitor")
    @app_commands.checks.has_permissions(administrator=True)
    async def add_bot(self, interaction: discord.Interaction, bot_user: discord.Member):
        """Add a bot to the uptime monitoring list."""
        if not bot_user.bot:
            await interaction.response.send_message(
                '⚠️ The specified user is not a bot',
                ephemeral=True
            )
            return
        
        data = load_data()
        guild_id = str(interaction.guild_id)
        bot_id = str(bot_user.id)
        
        if 'monitored_bots' not in data:
            data['monitored_bots'] = {}
        
        if guild_id not in data['monitored_bots']:
            data['monitored_bots'][guild_id] = []
        
        if bot_id in data['monitored_bots'][guild_id]:
            await interaction.response.send_message(
                f'⚠️ {bot_user.mention} is already being monitored',
                ephemeral=True
            )
            return
        
        data['monitored_bots'][guild_id].append(bot_id)
        save_data(data)
        
        await interaction.response.send_message(
            f'✅ Now monitoring {bot_user.mention} for uptime',
            ephemeral=True
        )
    
    @uptime_group.command(name="remove-bot", description="Remove a bot from monitoring")
    @app_commands.describe(bot_user="The bot to stop monitoring")
    @app_commands.checks.has_permissions(administrator=True)
    async def remove_bot(self, interaction: discord.Interaction, bot_user: discord.Member):
        """Remove a bot from the uptime monitoring list."""
        data = load_data()
        guild_id = str(interaction.guild_id)
        bot_id = str(bot_user.id)
        
        if guild_id not in data.get('monitored_bots', {}) or bot_id not in data['monitored_bots'][guild_id]:
            await interaction.response.send_message(
                f'⚠️ {bot_user.mention} is not being monitored',
                ephemeral=True
            )
            return
        
        data['monitored_bots'][guild_id].remove(bot_id)
        
        # Clean up uptime stats for the removed bot
        if guild_id in data.get('uptime_stats', {}) and bot_id in data['uptime_stats'][guild_id]:
            del data['uptime_stats'][guild_id][bot_id]
        
        save_data(data)
        
        await interaction.response.send_message(
            f'✅ Stopped monitoring {bot_user.mention}',
            ephemeral=True
        )
    
    @uptime_group.command(name="list", description="List all monitored bots")
    async def list_bots(self, interaction: discord.Interaction):
        """List all bots being monitored in this server."""
        data = load_data()
        guild_id = str(interaction.guild_id)
        
        monitored = data.get('monitored_bots', {}).get(guild_id, [])
        
        if not monitored:
            await interaction.response.send_message(
                '📋 No bots are currently being monitored in this server',
                ephemeral=True
            )
            return
        
        embed = discord.Embed(
            title="📊 Monitored Bots",
            color=discord.Color.blue()
        )
        
        bot_list = []
        for bot_id in monitored:
            member = interaction.guild.get_member(int(bot_id))
            if member:
                status_emoji = "🟢" if str(member.status) != "offline" else "🔴"
                bot_list.append(f"{status_emoji} {member.mention} ({member.name})")
            else:
                bot_list.append(f"❓ Unknown bot (ID: {bot_id})")
        
        embed.description = "\n".join(bot_list)
        
        # Add notification channel info
        channel_id = data.get('channels', {}).get(guild_id)
        if channel_id:
            channel = interaction.guild.get_channel(int(channel_id))
            if channel:
                embed.add_field(name="Notification Channel", value=channel.mention, inline=False)
        
        await interaction.response.send_message(embed=embed)


async def setup(bot):
    """Setup function to add the cog to the bot."""
    await bot.add_cog(UptimeCog(bot))
