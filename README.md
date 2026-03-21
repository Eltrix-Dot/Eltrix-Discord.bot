
# ✨ Eltrix Discord Bot

### The All-in-One Discord Server Manager
(Hint #V.4 is coming soon)
<div align="center">

"<img width="1500" height="450" alt="image" src="https://github.com/user-attachments/assets/0b66b6f0-7db0-4c9e-8f92-8bc74e7e63bf" />

<br>

![Version](https://img.shields.io/badge/Version-3.1-blue)
![Python](https://img.shields.io/badge/Python-3.11+-yellow?logo=python)
![License](https://img.shields.io/badge/License-MIT-green)
![Commands](https://img.shields.io/badge/Commands-70+-red)
![Status](https://img.shields.io/badge/Status-Active-brightgreen)

</div>

---

## 🚀 About Eltrix

**Eltrix** is a powerful **multi-purpose Discord bot** built with **Python and discord.py**.

It helps you **manage, moderate and grow your Discord server** with a complete suite of tools including moderation, leveling systems, tickets, economy features, and fun community commands.

Eltrix focuses on:

* ⚡ Performance
* 🧩 Modular architecture
* 🛡️ Advanced moderation
* 🎮 Community engagement

---

# 📦 Features

| Category           | Description                                              |
| ------------------ | -------------------------------------------------------- |
| 🛡️ Moderation     | Warn, mute, kick, ban, purge, slowmode, lockdown system  |
| 🎟️ Ticket System  | Multi-category support with transcripts and staff claims |
| 📈 Leveling System | XP system with role rewards                              |
| 💰 Economy         | Coins, daily rewards, gambling and investments           |
| 🎨 Role Menus      | Self-assign roles with dropdown menus                    |
| 🎉 Community       | Polls, memes, games and social commands                  |

---

# 🛠️ Installation

## 1️⃣ Requirements

Before installing, make sure you have:

* **Python 3.11+**
* **Git**
* A **Discord Bot Token**

Create a bot here:

👉 [https://discord.com/developers/applications](https://discord.com/developers/applications)

Enable these **Privileged Gateway Intents**

* Server Members Intent
* Message Content Intent

---

# 2️⃣ Clone the Repository

```bash
git clone https://github.com/Eltrix-Dot/Eltrix-Discord.bot
cd Eltrix-Discord.bot
```

---

# 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

---

# 4️⃣ Configure the Bot

Open:

```
Eltrix-Bot_V3.1.py
```

Edit the configuration section.

```python
# ==============================
# CONFIGURATION
# ==============================

TOKEN = "YOUR_BOT_TOKEN"

GUILD_ID = 123456789012345678

LOG_CHANNEL_ID = 123456789012345678

STAFF_ROLE_IDS = {
    123456789012345678,
    123456789012345679
}

OWNER_ID = 123456789012345678
```

---

### 🔎 How to find Discord IDs

Enable **Developer Mode**

```
Discord Settings
→ Advanced
→ Developer Mode
```

Then:

Right click → **Copy ID**

Works for:

* Users
* Roles
* Channels
* Servers

---

# ▶️ Starting the Bot

Run the bot with:

```bash
python ELTRIX.py
```

If everything works you should see:

```
Bot connected
Commands synced
Eltrix is online
```

---

# 📋 Command Overview

All commands use **Discord Slash Commands**

---

## 🛡️ Moderation

| Command        | Description           |
| -------------- | --------------------- |
| /warn          | Warn a user           |
| /warnings      | View user warnings    |
| /clearwarnings | Remove warnings       |
| /mute          | Timeout a user        |
| /kick          | Kick a member         |
| /ban           | Ban a member          |
| /softban       | Ban + delete messages |
| /purge         | Delete messages       |
| /lock          | Lock a channel        |
| /unlock        | Unlock a channel      |
| /lockdown      | Lock entire server    |

---

## 🎟️ Ticket System

| Command       | Description         |
| ------------- | ------------------- |
| /ticketsetup  | Create ticket panel |
| /ticketclaim  | Claim a ticket      |
| /ticketadd    | Add user to ticket  |
| /ticketremove | Remove user         |
| /ticketdelete | Delete ticket       |

---

## 📈 Leveling System

| Command          | Description       |
| ---------------- | ----------------- |
| /rank            | Show rank card    |
| /levelboard      | XP leaderboard    |
| /setxp           | Set XP            |
| /setlevelrole    | Add level role    |
| /removelevelrole | Remove level role |

---

## 💰 Economy

| Command        | Description     |
| -------------- | --------------- |
| /balance       | Show balance    |
| /daily         | Daily reward    |
| /leaderboard   | Richest users   |
| /give          | Send coins      |
| /gamble        | 50% gamble      |
| /invest        | 24h investment  |
| /bank deposit  | Deposit coins   |
| /bank withdraw | Withdraw coins  |
| /rep           | Give reputation |

---

## 🎉 Fun Commands

| Command         | Description          |
| --------------- | -------------------- |
| /poll           | Create a poll        |
| /suggest        | Submit suggestion    |
| /meme           | Random meme          |
| /8ball          | Ask the magic ball   |
| /ship           | Love compatibility   |
| /roast          | Friendly roast       |
| /hug /pat /slap | Interaction commands |

---

## ⚙️ Utility

| Command     | Description   |
| ----------- | ------------- |
| /ping       | Check latency |
| /uptime     | Bot uptime    |
| /userinfo   | User info     |
| /serverinfo | Server stats  |
| /remindme   | Reminder      |
| /afk        | AFK status    |
| /botinvite  | Invite link   |

---

# 🤝 Contributing

Contributions are welcome!

1. Fork the repository
2. Create a branch

```bash
git checkout -b feature/AmazingFeature
```

3. Commit your changes

```bash
git commit -m "Added AmazingFeature"
```

4. Push the branch

```bash
git push origin feature/AmazingFeature
```

5. Open a **Pull Request**

---

# 📜 License

Distributed under the **MIT License**

Copyright © 2026
**Eltrix-Dot**

---

# ⭐ Support

If you like the project:

⭐ **Star the repository**
🍴 **Fork it**
🛠 **Contribute**

---

💡 Built with **Python & Discord.py**

---

