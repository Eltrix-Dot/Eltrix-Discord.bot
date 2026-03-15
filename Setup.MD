# Eltrix-Bot Setup Guide

Eltrix is a custom, multi-purpose Discord bot designed for server management, moderation, and entertainment.

## 🛠️ Prerequisites

- **Python 3.8 or higher**: Ensure you have Python installed on your system.
- **pip**: The Python package installer.

## 📥 Installation

1.  **Clone or Download** the bot files to a folder on your computer.
2.  **Open a terminal** in that folder (e.g., Command Prompt, PowerShell, or Bash).
3.  **Install the dependencies** by running:
    ```bash
    pip install -r requirements.txt
    ```

## 🤖 Discord Bot Setup

Before running the bot, you must create an application on the [Discord Developer Portal](https://discord.com/developers/applications):

1.  **Create a New Application**: Give it a name.
2.  **Go to the "Bot" section**:
    - Click **"Reset Token"** to get your unique **Bot Token**. **Warning: Keep this secret!**
    - Scroll down to **"Privileged Gateway Intents"**.
    - **CRITICAL**: Enable both **"SERVER MEMBERS INTENT"** and **"MESSAGE CONTENT INTENT"**. Without these, XP tracking, stats, and moderation commands will not work.
3.  **Invite the Bot**:
    - Go to **OAuth2 -> URL Generator**.
    - Select the `bot` and `applications.commands` scopes.
    - Select the necessary permissions (Administrator is easiest for full functionality).
    - Use the generated link to invite the bot to your server.

## ⚙️ Configuration

Open `ELTRIX.py` and fill in the configuration section at the top (Lines 32-86):

- **TOKEN**: Paste your bot token from the developer portal.
- **GUILD_ID**: Your server's ID (Enable Developer Mode in Discord to right-click and copy ID).
- **LOG_CHANNEL_ID**: The ID of the channel where moderation logs will be sent.
- **STAFF_ROLE_IDS**: Add the role IDs for your staff members.
- **OWNER_ID**: Your own Discord User ID.
- **Additional IDs**: Fill in ticket categories, suggestion channels, and welcome channels as needed.

## 🚀 Running the Bot

Once configured, run the bot from your terminal:

```bash
python ELTRIX.py
```

Check the terminal for the "✅ Bot Online & Ready!" message.
