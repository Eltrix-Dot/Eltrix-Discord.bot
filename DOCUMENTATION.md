# Eltrix Bot Documentation

Welcome to the detailed documentation for the Eltrix Discord Bot. This guide will help you configure, set up, and use the advanced features of the bot.

## ⚙️ Configuration

Before running the bot, you must configure the settings at the top of `ELTRIX.py`.

### Essential Settings
| Variable | Description |
| :--- | :--- |
| `TOKEN` | Your Discord Bot Token from the Developer Portal. |
| `GUILD_ID` | The ID of your Discord server. Enable Developer Mode to copy this. |
| `LOG_CHANNEL_ID` | The ID of the text channel where moderation logs will be sent. |
| `STAFF_ROLE_IDS` | A list of Role IDs that are allowed to use staff commands. |
| `OWNER_ID` | Your personal User ID. Grants access to owner-only commands. |

### Feature Specific IDs
| Variable | Description |
| :--- | :--- |
| `TICKET_PANEL_CHANNEL_ID` | Channel ID where the ticket create button will appear. |
| `SUGGESTION_CHANNEL_ID` | Channel ID where user suggestions are sent. |
| `VERIFIED_ROLE_ID` | Role ID given to users after they verify. |
| `VERIFICATION_CHANNEL_ID` | Channel ID where the verification button is posted. |
| `WELCOME_CHANNEL_ID` | Channel ID for welcome messages. |

---

## 🛠️ Feature Setup Guides

### 1. Ticket System
The ticket system allows users to open private channels for support.

1.  **Configure Categories**: In `ELTRIX.py`, find the `TICKET_CATEGORIES` dictionary. You can define multiple categories (e.g., Support, Report).
    *   `category_id`: The ID of the Discord Category where ticket channels will be created.
    *   `staff_roles`: List of Role IDs that can view tickets in this category.
2.  **Setup Panel**: Run the command `/ticketsetup` in the channel where you want the "Create Ticket" button to appear.
3.  **Usage**:
    *   Users click the button to open a ticket.
    *   Staff use `/ticketclaim`, `/ticketadd`, `/ticketremove` to manage it.
    *   Staff use `/ticketclose` (button) and `/ticketdelete` to close/delete it. Transcripts are saved to the log channel.

### 2. Verification System
Protect your server by requiring users to click a button to gain access.

1.  **Create a Role**: Create a role (e.g., "Verified") and deny `@everyone` permission to see channels, but allow "Verified" to see them.
2.  **Config**: Set `VERIFIED_ROLE_ID` in the config to this role's ID.
3.  **Setup**: Run `/setupverification` in your verification channel.
4.  **Usage**: New members click "Verify", solve a simple button challenge, and get the role.

### 3. Role Menus (Self-Assignable Roles)
Allow users to pick their own roles (e.g., for games, notifications, or colors).

1.  **Create Categories**: Use `/rolemenu addcategory <name> <placeholder>` (e.g., `/rolemenu addcategory name:games placeholder:Select Games`).
2.  **Add Roles**: Use `/rolemenu addrole <category> <role> <label> <emoji>`.
3.  **Setup Panel**: Run `/setupuserroles` in the channel where you want the menu to appear.
4.  **Management**: You can reorder categories with `/rolemenu reordercategory` or remove them with `/rolemenu removecategory`.

---

## 💰 Economy & Leveling

### Economy
*   **Currency**: Coins.
*   **Earning**:
    *   `/daily`: Claim free coins every 22 hours.
    *   `/gamble <amount>`: 50% chance to double your bet.
    *   `/invest <amount>`: High risk, high reward investment (returns in 24h).
*   **Banking**:
    *   `/balance`: View wallet and bank balance.
    *   `/bank deposit <amount>`: Move money to safety (cannot be lost in gambles).
    *   `/bank withdraw <amount>`: Move money to wallet.

### Leveling
*   **XP**: Users gain random XP (15-25) per message (1 minute cooldown).
*   **Rewards**:
    *   Use `/setlevelrole <level> <role>` to automatically give roles when a user reaches a level.
    *   Use `/rank` to see your current progress card.
    *   Use `/levelboard` to see the top active members.

---

## 🚨 Troubleshooting

*   **"Application did not respond"**: The bot might be restarting or an error occurred. Check the terminal/console for error messages.
*   **Permissions Errors**: Ensure the bot's role is **higher** than the roles it is trying to manage (assign, kick, ban) in the Discord Server Settings.
*   **Intents**: Ensure "Server Members Intent" and "Message Content Intent" are enabled in the Discord Developer Portal.
