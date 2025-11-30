"""
Member commands for viewing uptime statistics.
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


class ViewUptimeCog(commands.Cog):
    """Cog for viewing uptime statistics."""
    
    def __init__(self, bot):
        self.bot = bot
    
    view_uptime_group = app_commands.Group(name="view-uptime", description="View uptime statistics")
    
    @view_uptime_group.command(name="user", description="View uptime statistics for a bot")
    @app_commands.describe(bot_user="The bot to view uptime for")
    async def view_user_uptime(self, interaction: discord.Interaction, bot_user: discord.Member):
        """View uptime statistics for a specific bot."""
        if not bot_user.bot:
            await interaction.response.send_message(
                '⚠️ The specified user is not a bot',
                ephemeral=True
            )
            return
        
        data = load_data()
        guild_id = str(interaction.guild_id)
        bot_id = str(bot_user.id)
        
        # Check if the bot is being monitored
        if guild_id not in data.get('monitored_bots', {}) or bot_id not in data['monitored_bots'][guild_id]:
            await interaction.response.send_message(
                f'⚠️ {bot_user.mention} is not being monitored. Use `/uptime add-bot` to start monitoring.',
                ephemeral=True
            )
            return
        
        # Get uptime stats
        stats = data.get('uptime_stats', {}).get(guild_id, {}).get(bot_id, {})
        
        online_time = stats.get('online_time', 0)
        offline_time = stats.get('offline_time', 0)
        total_time = online_time + offline_time
        
        if total_time == 0:
            uptime_percentage = 0.0
        else:
            uptime_percentage = (online_time / total_time) * 100
        
        # Current status
        current_status = str(bot_user.status)
        status_emoji = "🟢" if current_status != "offline" else "🔴"
        status_text = "Online" if current_status != "offline" else "Offline"
        
        embed = discord.Embed(
            title=f"📊 Uptime Statistics for {bot_user.name}",
            color=discord.Color.green() if current_status != "offline" else discord.Color.red()
        )
        
        embed.set_thumbnail(url=bot_user.display_avatar.url if bot_user.display_avatar else None)
        
        embed.add_field(
            name="Current Status",
            value=f"{status_emoji} {status_text}",
            inline=True
        )
        
        embed.add_field(
            name="Uptime Percentage",
            value=f"{uptime_percentage:.2f}%",
            inline=True
        )
        
        embed.add_field(
            name="Total Checks",
            value=str(total_time),
            inline=True
        )
        
        embed.add_field(
            name="Online Checks",
            value=str(online_time),
            inline=True
        )
        
        embed.add_field(
            name="Offline Checks",
            value=str(offline_time),
            inline=True
        )
        
        last_check = stats.get('last_check', 'Never')
        embed.add_field(
            name="Last Check",
            value=last_check,
            inline=True
        )
        
        await interaction.response.send_message(embed=embed)
    
    @view_uptime_group.command(name="all", description="View uptime statistics for all monitored bots")
    async def view_all_uptime(self, interaction: discord.Interaction):
        """View uptime statistics for all monitored bots in the server."""
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
            title="📊 Uptime Statistics - All Bots",
            color=discord.Color.blue()
        )
        
        for bot_id in monitored:
            member = interaction.guild.get_member(int(bot_id))
            stats = data.get('uptime_stats', {}).get(guild_id, {}).get(bot_id, {})
            
            online_time = stats.get('online_time', 0)
            offline_time = stats.get('offline_time', 0)
            total_time = online_time + offline_time
            
            if total_time == 0:
                uptime_percentage = 0.0
            else:
                uptime_percentage = (online_time / total_time) * 100
            
            if member:
                current_status = str(member.status)
                status_emoji = "🟢" if current_status != "offline" else "🔴"
                embed.add_field(
                    name=f"{status_emoji} {member.name}",
                    value=f"Uptime: {uptime_percentage:.2f}%\nChecks: {total_time}",
                    inline=True
                )
            else:
                embed.add_field(
                    name=f"❓ Unknown Bot",
                    value=f"ID: {bot_id}\nUptime: {uptime_percentage:.2f}%",
                    inline=True
                )
        
        await interaction.response.send_message(embed=embed)


async def setup(bot):
    """Setup function to add the cog to the bot."""
    await bot.add_cog(ViewUptimeCog(bot))
