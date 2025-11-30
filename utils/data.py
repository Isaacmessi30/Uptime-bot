"""
Data management utilities for the Uptime Bot.
"""

import json
import os
import asyncio

DATA_FILE = 'bot_data.json'

# Lock for thread-safe data access
_data_lock = asyncio.Lock()


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


async def load_data_async():
    """Load bot data from JSON file with async lock."""
    async with _data_lock:
        return load_data()


async def save_data_async(data):
    """Save bot data to JSON file with async lock."""
    async with _data_lock:
        save_data(data)
