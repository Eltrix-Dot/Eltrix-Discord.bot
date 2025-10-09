# Eltrix Discord Bot

A powerful, custom-built Discord bot designed to manage, entertain, and grow your server community. Eltrix is packed with features, from advanced moderation and a ticketing system to a complete economy and leveling system.

NOT UP TO-DATE WITH VERSION 2

---

## ✨ Key Features

* **Advanced Moderation**: Keep your server safe and clean with a full suite of tools, including a comprehensive warning system.
* **Professional Ticketing**: Handle support easily with tickets, complete with automatic HTML transcripts on closure.
* **Server Economy**: Engage members with a persistent economy: daily claims, transfers, gambling, slots, and leaderboards.
* **XP & Leveling**: Reward active users with XP, levels, rank cards, and automatic role rewards at milestones.
* **Data Persistence**: All essential data (economy, levels, warnings, tags) is saved to a database and survives bot restarts.
* **High Customizability**: Configure role rewards, preset messages, verification panels, and more.

---

## 🛠️ Moderation & Management

| Command                           | Description                              |
| --------------------------------- | ---------------------------------------- |
| `/warn [user] [reason]`           | Issues and records a warning for a user. |
| `/warnings [user]`                | Views all warnings for a specific user.  |
| `/clearwarnings [user]`           | Clears all warnings for a user.          |
| `/ban [user] [reason]`            | Permanently bans a user.                 |
| `/kick [user] [reason]`           | Kicks a user.                            |
| `/mute [user] [minutes] [reason]` | Puts a user in timeout.                  |
| `/unmute [user]`                  | Removes a user's timeout.                |
| `/purge [amount]`                 | Deletes a number of messages.            |
| `/lock [channel]`                 | Locks a channel.                         |
| `/unlock [channel]`               | Unlocks a channel.                       |
| `/slowmode [seconds] [channel]`   | Sets a slowmode.                         |
| `/announce [title] [description]` | Sends a professional embed announcement. |
| `/setupverification`              | Places the verification panel.           |

---

## 🎟️ Ticketing System

| Command                | Description                                |
| ---------------------- | ------------------------------------------ |
| `/ticketsetup`         | Places the ticket creation panel.          |
| `/ticketadd [user]`    | Adds a user to the ticket.                 |
| `/ticketremove [user]` | Removes a user from the ticket.            |
| `/ticketclaim`         | Claims the current ticket.                 |
| *(Close Button)*       | Closes ticket + generates HTML transcript. |

---

## 🏆 Leveling & XP

| Command                        | Description                         |
| ------------------------------ | ----------------------------------- |
| `/rank [user]`                 | Displays a visual rank card.        |
| `/levelboard`                  | Leaderboard of highest level users. |
| `/setlevelrole [level] [role]` | Set role rewards for levels.        |
| `/removelevelrole [level]`     | Removes level rewards.              |
| `/setxp user [user] [amount]`  | Sets XP for a user.                 |
| `/setxp all [amount]`          | Sets XP for all members.            |

---

## 💰 Economy

| Command                 | Description             |
| ----------------------- | ----------------------- |
| `/balance [user]`       | Shows balance of user.  |
| `/daily`                | Claim daily income.     |
| `/give [user] [amount]` | Transfer coins.         |
| `/leaderboard`          | Wealth leaderboard.     |
| `/gamble [amount]`      | Gamble to double coins. |
| `/slots`                | Play slot machine.      |

---

## 😂 Fun & Community

| Command                         | Description            |
| ------------------------------- | ---------------------- |
| `/8ball [question]`             | Magic 8-ball answers.  |
| `/poll [question] [options...]` | Create a poll.         |
| `/giveaway [prize] [minutes]`   | Start a giveaway.      |
| `/meme [subreddit]`             | Fetch random meme.     |
| `/roast [user]`                 | Send a roast.          |
| `/ship [user1] [user2]`         | Compatibility check.   |
| `/rps [user]`                   | Rock, Paper, Scissors. |
| `/hug, /pat, /slap`             | Fun interactions.      |
| `/truth, /dare`                 | Truth or Dare.         |
| `/tag use [name]`               | Use a server tag.      |
| `/tag create/edit/delete/list`  | Manage tags.           |

---

## ⚙️ Stats & Utility

| Command                       | Description                  |
| ----------------------------- | ---------------------------- |
| `/about`                      | Info about the bot.          |
| `/userinfo [user]`            | User info.                   |
| `/serverinfo`                 | Server statistics.           |
| `/botstats`                   | Bot stats (CPU, RAM, etc.).  |
| `/uptime`                     | Bot uptime.                  |
| `/membercount`                | Member, human, bot count.    |
| `/topchatters`                | Leaderboard of active users. |
| `/remindme [time] [reminder]` | Personal reminder.           |
| `/countdown [date] [event]`   | Countdown to event.          |
| `/feedback [message]`         | Sends feedback to bot owner. |

---

## 📊 Features Overview

| Feature       | Available |
| ------------- | --------- |
| Moderation    | ✅         |
| Ticketing     | ✅         |
| Economy       | ✅         |
| Leveling      | ✅         |
| Fun & Utility | ✅         |

---

## 🚀 Getting Started

1. Clone the repository:

   ```bash
   git clone https://github.com/YOURUSERNAME/eltrix-bot.git
   ```
2. Install requirements:

   ```bash
   pip install -r requirements.txt
   ```
3. Create a `.env` file with your Discord bot token:

   ```env
   TOKEN=your_discord_token_here
   ```
4. Run the bot:

   ```bash
   python bot.py
   ```

---

## 📜 License

This project is licensed under the MIT License. Feel free to use and modify it for your own server!
