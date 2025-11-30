"""
Admin commands for bot configuration.
"""

import discord
from discord import app_commands
from discord.ext import commands
import os


class ConfigCog(commands.Cog):
    """Cog for admin configuration commands."""
    
    def __init__(self, bot):
        self.bot = bot
    
    config_group = app_commands.Group(name="config", description="Configuration commands")
    
    @config_group.command(name="reload", description="Reload bot extensions")
    @app_commands.checks.has_permissions(administrator=True)
    async def reload(self, interaction: discord.Interaction):
        """Reload all command extensions."""
        await interaction.response.defer(ephemeral=True)
        
        reloaded = []
        failed = []
        
        for filename in os.listdir('./commands'):
            if filename.endswith('.py') and not filename.startswith('__'):
                extension_name = f'commands.{filename[:-3]}'
                try:
                    await self.bot.reload_extension(extension_name)
                    reloaded.append(filename)
                except commands.ExtensionNotLoaded:
                    try:
                        await self.bot.load_extension(extension_name)
                        reloaded.append(filename)
                    except Exception as e:
                        failed.append(f'{filename}: {str(e)}')
                except Exception as e:
                    failed.append(f'{filename}: {str(e)}')
        
        embed = discord.Embed(
            title="🔄 Extension Reload",
            color=discord.Color.green() if not failed else discord.Color.orange()
        )
        
        if reloaded:
            embed.add_field(
                name="✅ Reloaded",
                value="\n".join(reloaded),
                inline=False
            )
        
        if failed:
            embed.add_field(
                name="❌ Failed",
                value="\n".join(failed),
                inline=False
            )
        
        await interaction.followup.send(embed=embed, ephemeral=True)
    
    @config_group.command(name="sync", description="Sync slash commands")
    @app_commands.checks.has_permissions(administrator=True)
    async def sync_commands(self, interaction: discord.Interaction):
        """Sync slash commands with Discord."""
        await interaction.response.defer(ephemeral=True)
        
        try:
            synced = await self.bot.tree.sync()
            await interaction.followup.send(
                f'✅ Synced {len(synced)} command(s)',
                ephemeral=True
            )
        except Exception as e:
            await interaction.followup.send(
                f'❌ Failed to sync commands: {str(e)}',
                ephemeral=True
            )
    
    @config_group.command(name="status", description="View bot status")
    async def status(self, interaction: discord.Interaction):
        """View the current bot status."""
        embed = discord.Embed(
            title="🤖 Bot Status",
            color=discord.Color.blue()
        )
        
        embed.add_field(name="Guilds", value=str(len(self.bot.guilds)), inline=True)
        embed.add_field(name="Latency", value=f'{round(self.bot.latency * 1000)}ms', inline=True)
        embed.add_field(name="Extensions", value=str(len(self.bot.extensions)), inline=True)
        
        await interaction.response.send_message(embed=embed)


async def setup(bot):
    """Setup function to add the cog to the bot."""
    await bot.add_cog(ConfigCog(bot))
