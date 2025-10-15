<div align="center">
  <img src="https://cdn.discordapp.com/attachments/1393265882280493069/1406691590013059123/DiscoHook-Banner.png?ex=68f082e2&is=68ef3162&hm=1c4e5899a43aadbab5626b08e56c23a657b13e0de9ae11554abcb8289707acc2&" alt="Eltrix Discord Bot Banner" />
  
  <br/>
  
  <p>
    <img src="https://img.shields.io/badge/Version-v3.0-blue" alt="Version 3.0" />
    <img src="https://img.shields.io/badge/License-MIT-brightgreen" alt="License: MIT" />
    <img src="https://img.shields.io/badge/Built_with-Python-informational?logo=python" alt="Built with Python" />
    <img src="https://img.shields.io/badge/Commands-50+-red" alt="More than 50 commands" />
    </p>
</div>

<div align="center">
  
# ✨ Eltrix Discord Bot | The All-in-One Server Manager

Eltrix is a **powerful, modular** Discord bot crafted in Python (`discord.py`) designed to automate your server management while engaging your community with fun and unique features. From advanced moderation to a vibrant economy system, Eltrix has it all.

</div>

---

## 📖 Table of Contents

- [🚀 Key Features](#-key-features)
- [🛠️ Installation & Setup](#️-installation--setup)
    - [1. Prerequisites](#1-prerequisites)
    - [2. Repository Cloning](#2-repository-cloning)
    - [3. Package Installation](#3-package-installation)
    - [4. Bot Configuration](#4-bot-configuration)
    - [5. Starting the Bot](#5-starting-the-bot)
- [📋 Command Overview](#-command-overview)
    - [🛡️ Moderation & Management](#️-moderation--management)
    - [🎟️ Ticket System](#️-ticket-system)
    - [📈 Leveling & XP](#-leveling--xp)
    - [💰 Economy](#-economy)
    - [🎉 Fun & Community](#-fun--community)
    - [⚙️ General & Utility](#️-general--utility)
- [🤝 Contributing](#-contributing)
- [📜 License](#-license)

---

## 🚀 Key Features

| Icon | Section | Description |
| :---: | :--- | :--- |
| 🛡️ | **Comprehensive Moderation** | A complete suite of tools, including warnings, mutes, kicks, bans, softbans, detailed logging, and channel management. |
| 🎟️ | **Advanced Ticket System** | A multi-category ticket system with staff roles, transcripts, and full ticket lifecycle control. |
| 📈 | **Engaging Leveling System** | Reward active users with XP, levels, and automated role rewards. |
| 💰 | **Fun Economy** | Earn daily coins, gamble, invest, and climb the global leaderboard. |
| 🎨 | **Custom Role Menus** | Let users self-assign roles via interactive dropdown menus to personalize their profile. |
| 🎉 | **Fun & Community** | Keep your community engaged with polls, memes, suggestions, and interactive games. |

---

## 🛠️ Installation & Setup

Follow these steps to run the Eltrix bot on your own server.

### 1. Prerequisites

* **Python 3.11** or newer. Download Python from [python.org](https://www.python.org/).
* A **Discord Bot Token**. You can create a bot application and get a token via the [Discord Developer Portal](https://discord.com/developers/applications).
    * ⚠️ **ATTENTION:** Ensure you enable the **Privileged Gateway Intents** (`Server Members Intent` and `Message Content Intent`) for your bot in the Developer Portal.

### 2. Repository Cloning

Download the code to your machine.

```bash
git clone [https://github.com/Eltrix-Dot/Eltrix-Discord.bot](https://github.com/Eltrix-Dot/Eltrix-Discord.bot)
cd Eltrix-Discord.bot
3. Package Installation
The bot requires a few Python libraries to run. Make sure your requirements.txt includes the necessary packages and execute the following command:

Bash

pip install -r requirements.txt
4. Bot Configuration
Open the ELTRIX.py file and fill in the configuration section at the top. This is the most crucial step.

Python

# =============================================================================
# 1. CONFIGURATION
# =============================================================================
# Bot Token (Keep this SECRET!)
TOKEN = "YOUR_BOT_TOKEN_HERE"
# Guild ID (The ID of your server)
GUILD_ID = 123456789012345678
# Log channel ID (The ID of the channel for logs)
LOG_CHANNEL_ID = 123456789012345678
# Staff IDs (Role IDs of your staff)
STAFF_ROLE_IDS = {
    123456789012345678, # Staff Role ID
    123456789012345679, # Admin Role ID
}
# Owner ID (Your own user ID)
OWNER_ID = "YOUR_USER_ID_HERE"
# ... (Further configuration like TICKET_CATEGORIES etc. follows in the file)
🔎 How to find IDs? Enable "Developer Mode" in Discord: User Settings > Advanced > Developer Mode. Then, right-click on a server, channel, role, or user and select "Copy ID".

5. Starting the Bot
Once everything is installed and configured, you can start the bot using the following command in your terminal:

Bash

python ELTRIX.py
If successful, you will see a confirmation in the terminal that the bot is online and has synchronized its commands.

📋 Command Overview
All commands are available via Discord's / Slash Commands.

🛡️ Moderation & Management (Staff Only)
These commands are generally only for staff.

Command	Description
/warn <user> <reason>	Warns a user, logs it, and sends a DM.
/warnings <user>	Views all warnings for a user.
/mute <user> <minutes> <reason>	Places a user in timeout.
/unmute <user>	Removes the timeout from a user.
/kick <user> <reason>	Kicks a user from the server.
/ban <user> <reason>	Bans a user from the server.
/softban <user> <reason>	Bans and unbans a user immediately to clear recent messages.
/purge <amount>	Deletes a specified number of messages (1-100).
/lock [channel]	Locks a text channel for the @everyone role.
/lockdown	Locks all text channels in the server.
/announce <title> <description>	Creates an announcement in an embed.
/history <user>	Shows a combined history of warnings and notes.
/altcheck <user>	Checks account age to flag possible alt accounts.

Exporteren naar Spreadsheets
🎟️ Ticket System
Command	Description
/ticketsetup	Creates the panel for users to create tickets.
/ticketclaim	Claims the current ticket to signal you are working on it.
/ticketadd <user>	Adds a user to the current ticket.
/ticketdelete	Permanently deletes a closed ticket channel and saves a transcript.

Exporteren naar Spreadsheets
📈 Leveling & XP
Command	Description
/rank [user]	Displays a visual rank card with level and XP.
/levelboard	Shows the leaderboard for levels.
/setxp user <user> <amount>	Sets the XP of a specific user. (Staff)
/setlevelrole <level> <role>	Sets a role as a reward for reaching a level. (Staff)

Exporteren naar Spreadsheets
💰 Economy
Command	Description
/balance [user]	Checks the balance (wallet and bank).
/daily	Claims your daily coin reward.
/gamble <amount>	Takes a gamble with a 50% chance to double your stake.
/invest <amount>	Invests your coins with a chance of profit or loss after 24 hours.
`/bank deposit/withdraw <amount	all>`
/rep <user>	Gives a reputation point to a user (once every 24 hours).

Exporteren naar Spreadsheets
🎉 Fun & Community
Command	Description
/poll <question> <options...>	Creates a poll with up to 5 options.
/suggest <idea>	Submits a suggestion for the server.
/meme [subreddit]	Fetches a random meme from Reddit.
/8ball <question>	Asks the magical 8-ball for advice.
/ship <user1> <user2>	Calculates love compatibility.
/roast <user>	Delivers a funny (but friendly) roast.
/hug, /pat, /slap <user>	Interaction commands.
/urban <term>	Searches Urban Dictionary for a term (NSFW channels only).

Exporteren naar Spreadsheets
⚙️ General & Utility
Command	Description
/about	Shows information about the bot, including the original creator.
/ping	Checks the bot's reaction speed (latency).
/userinfo [user]	Shows detailed information about a user.
/remindme <time> <reminder>	Sets a personal reminder.
/afk [status]	Sets or removes your AFK status.
/tag use <name>	Uses a reusable, custom tag.
/botinvite	Generates an invite link for the bot.

🤝 Contributing
Contributions are what make the open-source community such an amazing place to learn, inspire, and create. Any contributions you make are greatly appreciated.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".

Fork the Project

Create your Feature Branch (git checkout -b feature/AmazingFeature)

Commit your Changes (git commit -m 'Add some AmazingFeature')

Push to the Branch (git push origin feature/AmazingFeature)

Open a Pull Request

📜 License
This project is distributed under the MIT License. This means you are free to use, modify, and distribute the code, as long as you include the original license and copyright notice.

Copyright (c) 2025 [Eltrix-Dot]
