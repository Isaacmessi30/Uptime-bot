# Uptime-bot

A Discord bot for monitoring bot uptimes and sending notifications when bots go online/offline.

## Features

- **Set Channel:** Configure a channel to receive uptime notifications
- **Bot Monitoring:** Add/remove bots to monitor their online/offline status
- **Uptime Statistics:** View uptime percentages and statistics for monitored bots
- **Admin Commands:** Reload extensions and sync commands

## Commands

### Uptime Commands
| Command | Description |
|---------|-------------|
| `/uptime set-channel <channel>` | Set the channel for uptime notifications |
| `/uptime remove-channel` | Remove the notification channel |
| `/uptime add-bot <bot>` | Add a bot to monitor |
| `/uptime remove-bot <bot>` | Remove a bot from monitoring |
| `/uptime list` | List all monitored bots |

### View Uptime Commands
| Command | Description |
|---------|-------------|
| `/view-uptime user <bot>` | View uptime statistics for a specific bot |
| `/view-uptime all` | View uptime statistics for all monitored bots |

### Admin Commands
| Command | Description |
|---------|-------------|
| `/config reload` | Reload bot extensions |
| `/config sync` | Sync slash commands with Discord |
| `/config status` | View bot status |

## Setup

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Copy `.env.example` to `.env` and add your Discord bot token:
   ```bash
   cp .env.example .env
   ```
4. Edit `.env` with your bot token:
   ```
   DISCORD_TOKEN=your_discord_bot_token_here
   ```
5. Run the bot:
   ```bash
   python bot.py
   ```

## Required Bot Permissions

- Read Messages/View Channels
- Send Messages
- Use Slash Commands
- Read Message History

## Required Intents

- Server Members Intent (for member presence)
- Presence Intent (for online/offline status)

## Project Structure

```
Uptime-bot/
├── bot.py              # Main bot file
├── commands/           # Command modules
│   ├── __init__.py
│   ├── config.py       # Admin configuration commands
│   ├── uptime.py       # Uptime monitoring commands
│   └── view_uptime.py  # View uptime statistics commands
├── .env.example        # Example environment configuration
├── requirements.txt    # Python dependencies
└── README.md
```
