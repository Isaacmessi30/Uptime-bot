"""
Uptime Bot - A Discord bot for monitoring bot uptimes
"""

import os
import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv
import json
from datetime import datetime

# Load environment variables
load_dotenv()

# Bot configuration
TOKEN = os.getenv('DISCORD_TOKEN')

# Intents
intents = discord.Intents.default()
intents.members = True
intents.presences = True

# Bot instance
bot = commands.Bot(command_prefix='/', intents=intents)

# Data storage path
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


# Global data
bot_data = load_data()


@bot.event
async def on_ready():
    """Called when the bot is ready."""
    print(f'{bot.user} has connected to Discord!')
    print(f'Connected to {len(bot.guilds)} guilds')
    
    # Sync slash commands
    try:
        synced = await bot.tree.sync()
        print(f'Synced {len(synced)} command(s)')
    except Exception as e:
        print(f'Failed to sync commands: {e}')
    
    # Start monitoring task
    if not check_bot_status.is_running():
        check_bot_status.start()


@tasks.loop(minutes=1)
async def check_bot_status():
    """Check the status of monitored bots."""
    global bot_data
    
    for guild_id, bots in bot_data.get('monitored_bots', {}).items():
        guild = bot.get_guild(int(guild_id))
        if not guild:
            continue
            
        channel_id = bot_data.get('channels', {}).get(guild_id)
        if not channel_id:
            continue
            
        channel = guild.get_channel(int(channel_id))
        if not channel:
            continue
        
        for bot_id in bots:
            member = guild.get_member(int(bot_id))
            if not member:
                continue
            
            # Initialize uptime stats if not exists
            if guild_id not in bot_data['uptime_stats']:
                bot_data['uptime_stats'][guild_id] = {}
            if bot_id not in bot_data['uptime_stats'][guild_id]:
                bot_data['uptime_stats'][guild_id][bot_id] = {
                    'online_time': 0,
                    'offline_time': 0,
                    'last_status': str(member.status),
                    'last_check': datetime.now().isoformat()
                }
            
            current_status = str(member.status)
            last_status = bot_data['uptime_stats'][guild_id][bot_id].get('last_status')
            
            # Update time tracking
            if current_status != 'offline':
                bot_data['uptime_stats'][guild_id][bot_id]['online_time'] += 1
            else:
                bot_data['uptime_stats'][guild_id][bot_id]['offline_time'] += 1
            
            # Notify on status change
            if last_status != current_status:
                if current_status == 'offline':
                    await channel.send(f'⚠️ **{member.name}** is now **offline**!')
                else:
                    await channel.send(f'✅ **{member.name}** is now **online**!')
                
                bot_data['uptime_stats'][guild_id][bot_id]['last_status'] = current_status
            
            bot_data['uptime_stats'][guild_id][bot_id]['last_check'] = datetime.now().isoformat()
        
        save_data(bot_data)


@check_bot_status.before_loop
async def before_check_bot_status():
    """Wait for the bot to be ready before starting the loop."""
    await bot.wait_until_ready()


async def load_extensions():
    """Load all command extensions."""
    for filename in os.listdir('./commands'):
        if filename.endswith('.py') and not filename.startswith('__'):
            try:
                await bot.load_extension(f'commands.{filename[:-3]}')
                print(f'Loaded extension: {filename}')
            except Exception as e:
                print(f'Failed to load extension {filename}: {e}')


async def main():
    """Main function to run the bot."""
    async with bot:
        await load_extensions()
        await bot.start(TOKEN)


if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
