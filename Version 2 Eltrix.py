# ELTRIX.py
# A custom, multi-purpose Discord bot.
# Requires: discord.py >= 2.0

import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import View, Button
from typing import Optional
import datetime
import random
import platform
import asyncio
import psutil
import aiohttp
import os
import calendar
from PIL import Image, ImageDraw, ImageFont, ImageOps
import io   
import json

# =============================================================================
# 1. CONFIGURATION
# =============================================================================
# Fill in your bot's details and server-specific IDs below.

# Bot Token=
TOKEN = "1111"

# Guild ID=
GUILD_ID = 1111 # Your Server/Guild ID

# Log channel ID=
LOG_CHANNEL_ID = 1111 # The channel for moderation logs

# Staff IDs= (These should be role IDs)
STAFF_ROLE_IDS = {
            1234,
            1234, # The role ID for your staff members   
    # You can add more staff role IDs here, separated by commas
}

# Owner ID= (This should be your user ID)
OWNER_ID = "1234" # The user ID of the bot owner

# --- TICKET SYSTEM 2.0 CONFIG ---
TICKET_CATEGORIES = {
    # The key (e.g., "support") is a unique internal ID for the category.
    "support": {
        "label": "Technical Support", # The name shown in the dropdown
        "description": "For technical issues with the server or bot.", # The description in the dropdown
        "emoji": "🛠️", # The emoji in the dropdown
        "category_id": 1234, # The Discord Category ID to create channels in
        "staff_roles": [1234, 1234] # Role IDs that can see these tickets
    },
    "report": {
        "label": "User Report",
        "description": "Report a user for breaking the rules.",
        "emoji": "⚖️",
        "category_id": 1234, # Can be the same or a different category
        "staff_roles": [1234, 1234]
    },
    "question": {
        "label": "General Question",
        "description": "For any other questions you might have.",
        "emoji": "❓",
        "category_id": 1234,
        "staff_roles": [1234, 1234]
    },
    # You can add more categories here by copying the format above.
}
TICKET_PANEL_CHANNEL_ID = 1234
# The ID of the channel where new suggestions will be sent.
SUGGESTION_CHANNEL_ID = 1234
# The ID of the role to give to verified members.
VERIFIED_ROLE_ID = 1234
# The ID of the public channel to setup verification in
VERIFICATION_CHANNEL_ID = 1234
# The ID of the channel for bot startup messages
STARTUP_LOG_CHANNEL_ID = 1234


# --- PRESET MESSAGES ---
# Add or edit your preset messages here. The key is the number used in the command.
PRESET_MESSAGES = {
    1: "Reminder: Please keep the conversation respectful and follow all server rules.",
    2: "Please do not spam. Further spam will result in a mute.",
    3: "This channel is for English only. Please move your conversation to the appropriate channel.",
    4: "Your ticket has been received. A staff member will be with you shortly.",
    5: "This channel is now in lockdown mode while we perform maintenance.",
    6: "Hello, we have found a rule-breaking message. Please check the <#1234> channel.",
}

# =============================================================================
# 2. BOT SETUP
# =============================================================================

# --- Intents & Bot Initialization ---
intents = discord.Intents.default()
intents.members = True # Required to get member information
intents.message_content = True # Required for on_message events (XP, stats)

bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree
GUILD = discord.Object(id=GUILD_ID) 

# --- In-Memory Storage ---
start_time = datetime.datetime.now(datetime.timezone.utc)
message_counts = {} # {user_id: count}
emoji_counts = {} # {emoji_id: count}
xp_cooldowns = {} # {user_id: timestamp}
afk_users = {} # {user_id: {"message": str, "timestamp": datetime}}

# =============================================================================
# 3. DATA MANAGEMENT & HELPER FUNCTIONS
# =============================================================================

def load_json(filename: str) -> dict:
    """Loads data from a JSON file."""
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_json(filename: str, data: dict):
    """Saves data to a JSON file."""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)
        
# --- File Paths & Data Loading ---
ECONOMY_FILE = "economy_data.json"
LEVELING_FILE = "leveling_data.json"
LEVEL_REWARDS_FILE = "level_rewards.json"
TAGS_FILE = "tags.json"
WARNINGS_FILE = "warnings_data.json"
NOTES_FILE = "notes_data.json"
REPUTATION_FILE = "reputation.json"
ROLE_MENU_FILE = "role_menu_config.json"

economy_data = load_json(ECONOMY_FILE)
leveling_data = load_json(LEVELING_FILE)
level_rewards = load_json(LEVEL_REWARDS_FILE)
tags_data = load_json(TAGS_FILE)
warnings_data = load_json(WARNINGS_FILE)
notes_data = load_json(NOTES_FILE)
reputation_data = load_json(REPUTATION_FILE)
role_menu_data = load_json(ROLE_MENU_FILE)

# Initialize role_menu_data if the file is empty/new
if not role_menu_data:
    role_menu_data = {
        "platforms": {
            "placeholder": "Choose your platform(s)...",
            "max_values": 3,
            "roles": {
                "1425841974388195389": {"label": "Playstation", "emoji": "🎮"},
                "1425842052549312542": {"label": "Xbox", "emoji": "🎮"},
                "1425842130156523602": {"label": "PC", "emoji": "🖥️"},
            }
        },
        "genres": {
            "placeholder": "Choose your favorite genre(s)...",
            "max_values": 2,
            "roles": {
                "1425842521107468318": {"label": "Roleplay", "emoji": "🎭"},
                "1425842389033156688": {"label": "Action", "emoji": "💥"},
            }
        },
        "games": {
            "placeholder": "Choose the games you play...",
            "max_values": 2,
            "roles": {
                "1425841908382564534": {"label": "Minecraft", "emoji": "🧱"},
                "1425840756454719571": {"label": "War Thunder", "emoji": "✈️"},
            }
        }
    }
    save_json(ROLE_MENU_FILE, role_menu_data)

# --- Helper Functions ---
def get_user_balance(user_id: int) -> int:
    """Gets a user's balance, creating an entry if one doesn't exist."""
    user_id_str = str(user_id)
    return economy_data.get(user_id_str, {}).get("balance", 0)

def xp_for_level(level: int) -> int:
    """Calculates the total XP needed to reach a certain level."""
    # Using a common formula: 5 * (lvl^2) + 50 * lvl + 100
    return 5 * (level ** 2) + (50 * level) + 100

async def check_and_apply_level_up(interaction: discord.Interaction, user: discord.Member):
    """Checks if a user has enough XP to level up and applies it if so."""
    user_id_str = str(user.id)
    if user_id_str not in leveling_data:
        return

    while True:
        current_level = leveling_data[user_id_str].get("level", 0)
        xp_needed = xp_for_level(current_level)
        if leveling_data[user_id_str].get("xp", 0) >= xp_needed:
            leveling_data[user_id_str]["level"] += 1
            leveling_data[user_id_str]["xp"] -= xp_needed
            new_level = leveling_data[user_id_str]["level"]
            
            # Announce level up in the interaction channel
            await interaction.channel.send(f"🎉 Congratulations {user.mention}, you just reached **Level {new_level}**!")
            
            # Handle role rewards (similar to on_message)
            # This part can be expanded if needed
        else:
            break # Exit loop if not enough XP for the next level
    save_json(LEVELING_FILE, leveling_data)

# --- Permission Decorators ---
def check_if_staff(interaction: discord.Interaction) -> bool:
    """Function to check if the user is the owner or has a staff role."""
    if str(interaction.user.id) == OWNER_ID:
        return True
    # In a guild context, interaction.user is always a discord.Member
    if isinstance(interaction.user, discord.Member):
        return any(role.id in STAFF_ROLE_IDS for role in interaction.user.roles)
    return False

def is_owner(): 
    """Decorator to check if the user is the bot owner."""
    def predicate(interaction: discord.Interaction) -> bool:
        return str(interaction.user.id) == OWNER_ID
    return app_commands.check(predicate)

# --- Utility Functions ---
async def log_action(
    interaction: discord.Interaction,
    action: str,
    details: str,
    color: discord.Color = discord.Color.blurple(),
):
    """Sends a standardized log message to the log channel."""
    log_channel = bot.get_channel(LOG_CHANNEL_ID)
    if not log_channel:
        print(f"Warning: Log channel with ID {LOG_CHANNEL_ID} not found.")
        return

    embed = discord.Embed(
        title=f"Log: {action}",
        description=details,
        color=color,
        timestamp=datetime.datetime.now(datetime.timezone.utc)
    )
    embed.set_author(name=f"Executor: {interaction.user.display_name}", icon_url=interaction.user.display_avatar.url)
    embed.set_footer(text=f"User ID: {interaction.user.id}")

    try:
        await log_channel.send(embed=embed)
    except discord.Forbidden:
        print(f"Error: Bot does not have permission to send messages in the log channel ({LOG_CHANNEL_ID}).")
    except Exception as e:
        print(f"An error occurred while logging: {e}")

async def create_transcript(channel: discord.TextChannel, closer: discord.Member) -> Optional[discord.File]:
    """Creates an HTML transcript of a channel's history."""
    try:
        messages = [message async for message in channel.history(limit=None, oldest_first=True)]
        
        html = f"""
        <html>
            <head>
                <title>Transcript for #{channel.name}</title>
                <style>
                    body {{ font-family: sans-serif; background-color: #36393f; color: #dcddde; }}
                    .message {{ display: flex; margin-bottom: 15px; }}
                    .avatar {{ width: 50px; height: 50px; border-radius: 50%; margin-right: 15px; }}
                    .content {{ flex-grow: 1; }}
                    .header {{ font-weight: bold; }}
                    .timestamp {{ font-size: 0.8em; color: #72767d; margin-left: 5px; }}
                    .header .author {{ color: #ffffff; }}
                </style>
            </head>
            <body>
                <h1>Transcript for #{channel.name}</h1>
                <p>Closed by: {closer.display_name} ({closer.id})</p>
        """
        for msg in messages:
            html += f"""
            <div class="message">
                <img src="{msg.author.display_avatar.url}" class="avatar">
                <div class="content">
                    <div class="header">
                        <span class="author">{msg.author.display_name}</span>
                        <span class="timestamp">{msg.created_at.strftime('%Y-%m-%d %H:%M:%S')} UTC</span>
                    </div>
                    <div>{msg.content}</div>
                </div>
            </div>
            """
        html += "</body></html>"

        file_path = f"transcript-{channel.name}.html"
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(html)
        
        return discord.File(file_path, filename=file_path)
    except Exception as e:
        print(f"Error creating transcript: {e}")
        return None

def chunk_string(text: str, length: int):
    """A helper function to split a string into chunks of a specific length."""
    return (text[i:i+length] for i in range(0, len(text), length))

async def interaction_command(interaction: discord.Interaction, member: discord.Member, action: str, emoji: str, color: discord.Color):
    """Helper function for interaction commands like hug, pat, slap."""
    if member == interaction.user:
        await interaction.response.send_message(f"You can't {action} yourself!", ephemeral=True)
        return
    
    embed = discord.Embed(
        description=f"{interaction.user.mention} {action}s {member.mention} {emoji}",
        color=color
    )
    await interaction.response.send_message(embed=embed)


@tree.command(name="about", description="Shows information about the Eltrix bot. [Everyone]", guild=GUILD)
async def about(interaction: discord.Interaction):
    """Displays an embed with information about the bot."""
    embed = discord.Embed(
        title="About Eltrix-Bot",
        description="A custom-built, multi-purpose bot designed to manage and entertain your server.",
        color=discord.Color.purple()
    )
    embed.set_thumbnail(url=bot.user.display_avatar.url)
    embed.add_field(name="Version", value="2.0.0", inline=True)
    embed.add_field(name="Creator", value=f"<@{OWNER_ID}>", inline=True)
    embed.add_field(name="Support Server", value="[Join here!](https://discord.gg/kEj6UDdQvb)", inline=False)
    await interaction.response.send_message(embed=embed)

# =============================================================================
# 4. UI CLASSES (VIEWS, MODALS, SELECTS)
# =============================================================================

# --- Ticket System Views ---
class ConfirmCloseView(View):
    """A view to confirm closing a ticket."""
    def __init__(self):
        super().__init__(timeout=30)
        self.value = None

    @discord.ui.button(label="Confirm Close", style=discord.ButtonStyle.red, custom_id="ticket_confirm_close")
    async def confirm(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_message("🔒 Closing this ticket...", ephemeral=True)
        self.value = True
        self.stop()

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.grey, custom_id="ticket_cancel_close")
    async def cancel(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_message("Ticket closure cancelled.", ephemeral=True)
        self.value = False
        self.stop()

class ClosedTicketView(discord.ui.View):
    """A view for a closed ticket with a re-open button."""
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Re-open Ticket", style=discord.ButtonStyle.success, custom_id="ticket_reopen_button", emoji="🔓")
    async def reopen_ticket(self, interaction: discord.Interaction, button: Button):
        channel = interaction.channel
        try:
            # Extract creator ID from the channel topic
            creator_id = int(channel.topic.split("Creator ID: ")[1])
            creator = interaction.guild.get_member(creator_id)

            if creator:
                await channel.set_permissions(creator, read_messages=True, send_messages=True, reason=f"Ticket re-opened by {interaction.user}")
                await interaction.response.send_message(f"✅ {creator.mention} has been re-added to the ticket.", ephemeral=True)
                new_name = f"ticket-{creator.name.lower()}"
                await channel.edit(name=new_name, view=TicketControlsView())
                await channel.send(f"🔓 Ticket re-opened by {interaction.user.mention}.")
                await log_action(interaction, "Ticket Re-opened", f"**Channel:** {channel.mention}", color=discord.Color.green())
            else:
                await interaction.response.send_message("❌ Could not find the original ticket creator in the server.", ephemeral=True)
        except (IndexError, ValueError, TypeError):
            await interaction.response.send_message("❌ Could not determine the original ticket creator from the channel topic.", ephemeral=True)

class TicketControlsView(discord.ui.View):
    """A view with a button to close a ticket."""
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Close Ticket", style=discord.ButtonStyle.danger, custom_id="ticket_close_button")
    async def close_ticket(self, interaction: discord.Interaction, button: Button):
        """Handles the ticket closing process."""
        channel = interaction.channel
        try:
            # Extract creator ID from the channel topic
            creator_id = int(channel.topic.split("Creator ID: ")[1])
            creator = interaction.guild.get_member(creator_id)

            if creator:
                await channel.set_permissions(creator, overwrite=None, reason=f"Ticket closed by {interaction.user}")
                await interaction.response.send_message(f"✅ {creator.mention} has been removed from the ticket.", ephemeral=True)
            else:
                await interaction.response.send_message("✅ Ticket is being closed. Could not find the original creator to remove.", ephemeral=True)
        except (IndexError, ValueError, TypeError):
             await interaction.response.send_message("✅ Ticket is being closed. Could not determine the original ticket creator from the channel topic.", ephemeral=True)

        # Rename the channel to indicate it's closed
        try:
            new_name = f"closed-{channel.name.replace('ticket-', '')}"
            await channel.edit(name=new_name)
        except Exception as e:
            print(f"Could not rename channel: {e}")

        await interaction.message.edit(view=ClosedTicketView())
        await channel.send(f"🔒 Ticket closed by {interaction.user.mention}. A staff member can permanently delete it with `/ticketdelete`.")
        await log_action(interaction, "Ticket Closed", f"**Channel:** `{channel.name}`", color=discord.Color.dark_red())

class TicketCategorySelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(
                label=details["label"],
                description=details["description"],
                emoji=details["emoji"],
                value=cat_id
            ) for cat_id, details in TICKET_CATEGORIES.items()
        ]
        super().__init__(placeholder="Choose a ticket category...", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        category_key = self.values[0]
        category_details = TICKET_CATEGORIES[category_key]
        await interaction.response.send_modal(TicketCreationModal(category_key, category_details))

class TicketCategoryView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(TicketCategorySelect())

class TicketCreationView(discord.ui.View):
    """A persistent view with a button to create a ticket."""
    def __init__(self):
        # Persistent view, timeout=None
        super().__init__(timeout=None)

    @discord.ui.button(label="Create Ticket", style=discord.ButtonStyle.success, custom_id="ticket_create_button", emoji="🎟️")
    async def create_ticket(self, interaction: discord.Interaction, button: Button):
        """Shows the user a dropdown to select a ticket category."""
        await interaction.response.send_message("Please select a category for your ticket below.", view=TicketCategoryView(), ephemeral=True)

# --- Ticket Modal ---
class TicketCreationModal(discord.ui.Modal):
    def __init__(self, category_key: str, category_details: dict):
        super().__init__(title=f"New Ticket: {category_details['label']}")
        self.category_key = category_key
        self.category_details = category_details

        self.subject = discord.ui.TextInput(
            label="Subject",
            placeholder="A brief summary of your issue (e.g., 'User report for spamming')",
            style=discord.TextStyle.short,
            required=True,
            max_length=100,
        )
        self.description = discord.ui.TextInput(
            label="Description",
            placeholder="Provide all details here. Include user IDs, message links, or screenshots if you can.",
            style=discord.TextStyle.long,
            required=True,
            max_length=1000,
        )
        self.relevant_user_id = discord.ui.TextInput(
            label="Relevant User ID (Optional)",
            placeholder="If your ticket is about a specific user, please provide their ID.",
            style=discord.TextStyle.short,
            required=False,
            max_length=20,
        )
        self.add_item(self.subject)
        self.add_item(self.description)
        self.add_item(self.relevant_user_id)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True, thinking=True)
        discord_category = interaction.guild.get_channel(self.category_details["category_id"])
        if not discord_category:
            await interaction.followup.send("❌ Ticket system is not configured correctly (Category not found).", ephemeral=True)
            return

        ticket_name = f"ticket-{interaction.user.name.lower()}"
        for channel in discord_category.text_channels:
            if channel.name == ticket_name:
                await interaction.followup.send(f"❌ You already have an open ticket in this category: {channel.mention}", ephemeral=True)
                return

        overwrites = {
            interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            interaction.guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }
        for role_id in self.category_details["staff_roles"]:
            staff_role = interaction.guild.get_role(role_id)
            if staff_role:
                overwrites[staff_role] = discord.PermissionOverwrite(read_messages=True, send_messages=True)

        ticket_channel = await discord_category.create_text_channel(
            name=ticket_name, overwrites=overwrites, topic=f"Ticket by {interaction.user.name}. Subject: {self.subject.value}. Creator ID: {interaction.user.id}",
            reason=f"Ticket created by {interaction.user} in category '{self.category_key}'"
        )

        staff_mentions = " ".join(f"<@&{role_id}>" for role_id in self.category_details["staff_roles"])
        initial_embed = discord.Embed(title=self.subject.value, description=self.description.value, color=discord.Color.blue())
        initial_embed.set_author(name=f"Ticket by {interaction.user.display_name}", icon_url=interaction.user.display_avatar.url)
        # Add the new field to the embed if it was filled in
        if self.relevant_user_id.value:
            initial_embed.add_field(name="Relevant User ID", value=self.relevant_user_id.value, inline=False)
        
        await ticket_channel.send(content=f"Hello {interaction.user.mention}, thank you for creating a ticket. {staff_mentions} will soon be with you.", embed=initial_embed, view=TicketControlsView())
        await interaction.followup.send(f"✅ Your ticket has been created: {ticket_channel.mention}", ephemeral=True)
        await log_action(interaction, "Ticket Created", f"**Category:** {self.category_details['label']}\n**Channel:** {ticket_channel.mention}\n**Subject:** {self.subject.value}", color=discord.Color.green())

# --- Verification System Views ---
class VerificationChallengeView(discord.ui.View):
    """A view with randomized buttons for verification. This view is created per user."""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Shuffle the buttons that were added by the decorators
        shuffled_children = self.children[:]
        random.shuffle(shuffled_children)
        self.clear_items().extend(shuffled_children)

    @discord.ui.button(label="\u200b", custom_id="verify_correct", style=discord.ButtonStyle.green, emoji="✅")
    async def correct_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        verified_role = interaction.guild.get_role(VERIFIED_ROLE_ID)
        if verified_role:
            await interaction.user.add_roles(verified_role, reason="Completed button verification")
            await interaction.response.edit_message(content="✅ **Verification Successful!**\n\nYou now have access to the rest of the server.", view=None)
            await log_action(interaction, "User Verified", f"**User:** {interaction.user.mention} completed the verification.", color=discord.Color.green())
        else:
            await interaction.response.edit_message(content="❌ Verification role not found. Please contact staff.", view=None)

    @discord.ui.button(label="\u200b", custom_id="verify_wrong_1", style=discord.ButtonStyle.red, emoji="❌")
    async def wrong_button1(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(content="❌ **Verification Failed.** You clicked the wrong button. Please try again by clicking the main verify button.", view=None)

    @discord.ui.button(label="\u200b", custom_id="verify_wrong_2", style=discord.ButtonStyle.red, emoji="❌")
    async def wrong_button2(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(content="❌ **Verification Failed.** You clicked the wrong button. Please try again by clicking the main verify button.", view=None)

    @discord.ui.button(label="\u200b", custom_id="verify_wrong_3", style=discord.ButtonStyle.red, emoji="❌")
    async def wrong_button3(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(content="❌ **Verification Failed.** You clicked the wrong button. Please try again by clicking the main verify button.", view=None)

class VerificationView(View):
    """A view with a button to start the verification process."""
    def __init__(self):
        super().__init__(timeout=None) # Persistent view

    @discord.ui.button(label="Verify", style=discord.ButtonStyle.green, emoji="✅", custom_id="public_verify_button")
    async def verify_button(self, interaction: discord.Interaction, button: Button):
        """Sends the button challenge to the user."""
        await interaction.response.send_message(
            "Please complete the challenge below to verify. Click the **green checkmark** button.",
            view=VerificationChallengeView(timeout=60),
            ephemeral=True
        )

# --- Role Menu System Views ---
class RoleSelect(discord.ui.Select):
    def __init__(self, category_key: str, category_config: dict):
        self.category_key = category_key
        self.category_roles = [int(k) for k in category_config["roles"].keys()]

        options = [
            discord.SelectOption(
                label=details["label"],
                value=role_id,
                emoji=details.get("emoji")
            ) for role_id, details in category_config.get("roles", {}).items()
        ]

        super().__init__(
            placeholder=category_config["placeholder"],
            min_values=0,
            max_values=category_config["max_values"],
            options=options,
            custom_id=f"role_menu_select_{category_key}"
        )

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        # Get the roles the user currently has from this category
        current_roles = [role for role in interaction.user.roles if role.id in self.category_roles]
        
        # Get the roles the user selected
        selected_role_ids = [int(value) for value in self.values]
        selected_roles = [interaction.guild.get_role(role_id) for role_id in selected_role_ids]

        # Determine which roles to add and remove
        roles_to_add = [role for role in selected_roles if role not in current_roles and role is not None]
        roles_to_remove = [role for role in current_roles if role.id not in selected_role_ids]

        # Apply the changes
        if roles_to_add:
            await interaction.user.add_roles(*roles_to_add, reason="User selected roles from menu.")
        if roles_to_remove:
            await interaction.user.remove_roles(*roles_to_remove, reason="User deselected roles from menu.")

        await interaction.followup.send("✅ Your roles have been updated!", ephemeral=True)

class RoleMenuView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        for category_key, category_config in role_menu_data.items():
            self.add_item(RoleSelect(category_key, category_config))

class RoleMenuSetupView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Choose your roles", style=discord.ButtonStyle.primary, emoji="🎨", custom_id="role_menu_start")
    async def show_role_menu(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Select the roles that fit you below!", view=RoleMenuView(), ephemeral=True)

# --- Other UI Views ---
class RPSView(View):
    def __init__(self, player1: discord.Member, player2: discord.Member):
        super().__init__(timeout=60)
        self.player1 = player1
        self.player2 = player2
        self.choices = {}

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True
        await self.message.edit(content="⏱️ The game timed out because one or both players didn't make a choice.", view=self)

    async def handle_choice(self, interaction: discord.Interaction, choice: str):
        if interaction.user not in [self.player1, self.player2]:
            await interaction.response.send_message("You are not part of this game.", ephemeral=True)
            return

        if interaction.user.id in self.choices:
            await interaction.response.send_message("You have already made your choice!", ephemeral=True)
            return

        self.choices[interaction.user.id] = choice
        await interaction.response.send_message(f"You chose **{choice}**! Waiting for the other player...", ephemeral=True)

        if len(self.choices) == 2:
            p1_choice = self.choices[self.player1.id]
            p2_choice = self.choices[self.player2.id]

            # Determine winner
            winner = None
            if p1_choice == p2_choice:
                result_text = "It's a tie!"
            elif (p1_choice == "Rock" and p2_choice == "Scissors") or \
                 (p1_choice == "Paper" and p2_choice == "Rock") or \
                 (p1_choice == "Scissors" and p2_choice == "Paper"):
                winner = self.player1
                result_text = f"{self.player1.mention} wins!"
            else:
                winner = self.player2
                result_text = f"{self.player2.mention} wins!"

            result_embed = discord.Embed(
                title="🏆 Game Over!",
                description=f"{self.player1.mention} chose **{p1_choice}**\n{self.player2.mention} chose **{p2_choice}**\n\n**{result_text}**",
                color=winner.color if winner else discord.Color.default()
            )
            for item in self.children:
                item.disabled = True
            await self.message.edit(embed=result_embed, view=self)
            self.stop()

    @discord.ui.button(label="Rock", emoji="🪨", style=discord.ButtonStyle.grey)
    async def rock(self, interaction: discord.Interaction, button: Button):
        await self.handle_choice(interaction, "Rock")

    @discord.ui.button(label="Paper", emoji="📄", style=discord.ButtonStyle.grey)
    async def paper(self, interaction: discord.Interaction, button: Button):
        await self.handle_choice(interaction, "Paper")

    @discord.ui.button(label="Scissors", emoji="✂️", style=discord.ButtonStyle.grey)
    async def scissors(self, interaction: discord.Interaction, button: Button):
        await self.handle_choice(interaction, "Scissors")

class StopwatchView(View):
    @discord.ui.button(label="Stop", style=discord.ButtonStyle.red)
    async def stop(self, interaction: discord.Interaction, button: Button):
        # The start_time would need to be passed into the view's __init__
        # This is a simplified example; a real implementation would need to store start_time.
        # For this re-organization, we'll keep the original logic inside the command.
        pass

# =============================================================================
# 5. COMMAND GROUPS
# =============================================================================

note_group = app_commands.Group(name="note", description="Manage private staff notes about users.")
setxp_group = app_commands.Group(name="setxp", description="Commands to manage user XP.")
bank_group = app_commands.Group(name="bank", description="Manage your bank account.")
tag_group = app_commands.Group(name="tag", description="Commands to manage server tags.")
rolemenu_group = app_commands.Group(name="rolemenu", description="Manage the role menu system.")

# =============================================================================
# 6. SLASH COMMANDS
# =============================================================================

# --- Moderation & Management Commands ---

@tree.command(name="presetmessage", description="Send a preset message by number. [Staff Only]", guild=GUILD)
@app_commands.describe(
    number=f"The preset number to send (1-{len(PRESET_MESSAGES)})",
    channel="The channel to send the message in (defaults to current channel).",
    embed="Choose 'Yes' to send as an embed, 'No' for a plain message."
)
@app_commands.choices(embed=[
    app_commands.Choice(name="Yes", value="yes"),
    app_commands.Choice(name="No", value="no"),
])
async def presetmessage(
    interaction: discord.Interaction,
    number: int,
    embed: app_commands.Choice[str],
    channel: Optional[discord.TextChannel] = None
):
    """Sends a predefined message to a channel, either as plain text or an embed."""
    if not check_if_staff(interaction):
        await interaction.response.send_message("You don't have the right permissions to use this command!", ephemeral=True)
        return

    target_channel = channel or interaction.channel

    # Check if the preset number is valid
    if number not in PRESET_MESSAGES:
        await interaction.response.send_message(
            f"❌ Invalid preset number. Please choose a number between 1 and {len(PRESET_MESSAGES)}.",
            ephemeral=True
        )
        return

    message_text = PRESET_MESSAGES[number]

    try:
        if embed.value == "yes":
            # Send as an embed
            embed_msg = discord.Embed(
                description=message_text,
                color=discord.Color.blue()
            )
            await target_channel.send(embed=embed_msg)
        else:
            # Send as a plain message
            await target_channel.send(message_text)

        # Confirm to the user and log the action
        await interaction.response.send_message(f"✅ Preset message #{number} sent to {target_channel.mention}.", ephemeral=True)
        log_details = (
            f"**Preset:** #{number}\n"
            f"**Channel:** {target_channel.mention}\n"
            f"**Format:** {'Embed' if embed.value == 'yes' else 'Plain Text'}\n"
            f"**Content:**\n>>> {message_text}"
        )
        await log_action(interaction, "Preset Message Sent", log_details, color=discord.Color.green())

    except discord.Forbidden:
        await interaction.response.send_message(f"❌ I don't have permission to send messages in {target_channel.mention}.", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"An unexpected error occurred: {e}", ephemeral=True)

@tree.command(name="warn", description="Warns a user and logs the warning. [Staff Only]", guild=GUILD)
@app_commands.describe(member="The member to warn.", reason="The reason for the warning.")
async def warn(interaction: discord.Interaction, member: discord.Member, reason: str):
    """Warns a user, sends them a DM, and logs it."""
    if not check_if_staff(interaction):
        await interaction.response.send_message("You don't have the right permissions to use this command!", ephemeral=True)
        return

    if member.bot:
        await interaction.response.send_message("❌ You cannot warn a bot.", ephemeral=True)
        return
    if member.id == interaction.user.id:
        await interaction.response.send_message("❌ You cannot warn yourself.", ephemeral=True)
        return

    # Store the warning
    user_id_str = str(member.id)
    warnings_data.setdefault(user_id_str, []).append(reason)
    save_json(WARNINGS_FILE, warnings_data)

    try:
        dm_embed = discord.Embed(title="⚠️ You Have Received a Warning", description=f"You have been warned in **{interaction.guild.name}** for the following reason:\n>>> {reason}", color=discord.Color.orange())
        await member.send(embed=dm_embed)
        dm_status = "They have been notified via DM."
    except discord.Forbidden:
        dm_status = "I could not notify them via DM."

    await interaction.response.send_message(f"✅ {member.mention} has been warned. {dm_status}", ephemeral=True)
    log_details = f"**Target:** {member.mention}\n**Reason:** {reason}"
    await log_action(interaction, "User Warned", log_details, color=discord.Color.orange())

@tree.command(name="warnings", description="View all warnings for a specific user. [Staff Only]", guild=GUILD)
@app_commands.describe(member="The member whose warnings you want to see.")
async def warnings(interaction: discord.Interaction, member: discord.Member):
    """Displays a list of warnings for a user."""
    if not check_if_staff(interaction):
        await interaction.response.send_message("You don't have the right permissions to use this command!", ephemeral=True)
        return

    user_warnings = warnings_data.get(str(member.id), [])

    if not user_warnings:
        await interaction.response.send_message(f"✅ {member.mention} has no warnings.", ephemeral=True)
        return

    embed = discord.Embed(
        title=f"⚠️ Warnings for {member.display_name}",
        description=f"Total warnings: {len(user_warnings)}",
        color=discord.Color.orange()
    )
    for i, reason in enumerate(user_warnings, start=1):
        embed.add_field(name=f"Warning #{i}", value=reason, inline=False)

    await interaction.response.send_message(embed=embed, ephemeral=True)

@tree.command(name="clearwarnings", description="Clears all warnings for a specific user. [Staff Only]", guild=GUILD)
@app_commands.describe(member="The member whose warnings you want to clear.")
async def clearwarnings(interaction: discord.Interaction, member: discord.Member):
    """Clears all warnings for a user."""
    if not check_if_staff(interaction):
        await interaction.response.send_message("You don't have the right permissions to use this command!", ephemeral=True)
        return

    user_id_str = str(member.id)
    if user_id_str in warnings_data:
        del warnings_data[user_id_str]
        save_json(WARNINGS_FILE, warnings_data)
        await interaction.response.send_message(f"✅ All warnings for {member.mention} have been cleared.", ephemeral=True)
        log_details = f"**Target:** {member.mention}"
        await log_action(interaction, "Warnings Cleared", log_details, color=discord.Color.dark_green())
    else:
        await interaction.response.send_message(f"❌ {member.mention} has no warnings to clear.", ephemeral=True)

@tree.command(name="softban", description="Bans and unbans a user to delete their recent messages. [Staff Only]", guild=GUILD)
@app_commands.describe(member="The member to softban.", reason="The reason for the softban.")
async def softban(interaction: discord.Interaction, member: discord.Member, reason: str):
    """Bans and immediately unbans a user to clear their messages."""
    if not check_if_staff(interaction):
        await interaction.response.send_message("You don't have the right permissions to use this command!", ephemeral=True)
        return

    if member.id == interaction.user.id:
        await interaction.response.send_message("❌ You cannot softban yourself.", ephemeral=True)
        return
    if member.top_role >= interaction.user.top_role and str(interaction.user.id) != OWNER_ID:
        await interaction.response.send_message("❌ You cannot softban a member with an equal or higher role.", ephemeral=True)
        return

    try:
        # Ban the user to delete messages
        await member.ban(reason=f"Softban by {interaction.user}. Reason: {reason}", delete_message_days=1)
        # Immediately unban the user
        await interaction.guild.unban(member, reason=f"Automatic unban after softban.")
        
        await interaction.response.send_message(f"✅ {member.mention} has been softbanned. Their recent messages have been deleted.", ephemeral=True)
        log_details = f"**Target:** {member.mention}\n**Reason:** {reason}"
        await log_action(interaction, "User Softbanned", log_details, color=discord.Color.dark_orange())
    except discord.Forbidden:
        await interaction.response.send_message("❌ I do not have the required 'Ban Members' permission.", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"An error occurred: {e}", ephemeral=True)

@note_group.command(name="add", description="Add a private note to a user. [Staff Only]")
@app_commands.describe(user="The user to add a note to.", note="The content of the note.")
async def note_add(interaction: discord.Interaction, user: discord.Member, note: str):
    """Adds a private staff note to a user's record."""
    if not check_if_staff(interaction):
        await interaction.response.send_message("You don't have the right permissions to use this command!", ephemeral=True)
        return

    user_id_str = str(user.id)
    notes_data.setdefault(user_id_str, []).append({
        "note": note,
        "author_id": interaction.user.id,
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()
    })
    save_json(NOTES_FILE, notes_data)
    await interaction.response.send_message(f"✅ Note added for {user.mention}.", ephemeral=True)
    log_details = f"**Target:** {user.mention}\n**Note:** {note}"
    await log_action(interaction, "Note Added", log_details, color=discord.Color.light_grey())

@note_group.command(name="list", description="View all private notes for a user. [Staff Only]")
@app_commands.describe(user="The user whose notes you want to see.")
async def note_list(interaction: discord.Interaction, user: discord.Member):
    """Displays all private staff notes for a specific user."""
    if not check_if_staff(interaction):
        await interaction.response.send_message("You don't have the right permissions to use this command!", ephemeral=True)
        return

    user_notes = notes_data.get(str(user.id), [])
    if not user_notes:
        await interaction.response.send_message(f"✅ {user.mention} has no notes.", ephemeral=True)
        return

    embed = discord.Embed(title=f"📝 Notes for {user.display_name}", color=discord.Color.light_grey())
    for i, note_data in enumerate(user_notes, 1):
        author = interaction.guild.get_member(note_data['author_id'])
        author_name = author.display_name if author else "Unknown Staff"
        timestamp = discord.utils.format_dt(datetime.datetime.fromisoformat(note_data['timestamp']), style='f')
        embed.add_field(
            name=f"Note #{i} by {author_name}",
            value=f"{note_data['note']}\n*Added on: {timestamp}*",
            inline=False
        )
    await interaction.response.send_message(embed=embed, ephemeral=True)

@tree.command(name="mute", description="Mutes a member for a specified duration (timeout). [Staff Only]", guild=GUILD)
@app_commands.describe(member="The member to mute.", minutes="Duration of the mute in minutes.", reason="The reason for the mute.")
async def mute(interaction: discord.Interaction, member: discord.Member, minutes: int, reason: str):
    """Mutes a member using Discord's timeout feature."""
    if not check_if_staff(interaction):
        await interaction.response.send_message("You don't have the right permissions to use this command!", ephemeral=True)
        return

    if member.top_role >= interaction.user.top_role and str(interaction.user.id) != OWNER_ID:
        await interaction.response.send_message("❌ You cannot mute a member with an equal or higher role.", ephemeral=True)
        return

    duration = datetime.timedelta(minutes=minutes)
    try:
        await member.timeout(duration, reason=reason)
        await interaction.response.send_message(f"🔇 {member.mention} has been muted for {minutes} minute(s).", ephemeral=True)
        log_details = f"**Target:** {member.mention}\n**Duration:** {minutes} minute(s)\n**Reason:** {reason}"
        await log_action(interaction, "User Muted (Timeout)", log_details, color=discord.Color.light_grey())
    except discord.Forbidden:
        await interaction.response.send_message("❌ I do not have the 'Moderate Members' permission.", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"❌ An error occurred: {e}", ephemeral=True)

@tree.command(name="unmute", description="Removes the mute (timeout) from a member. [Staff Only]", guild=GUILD)
@app_commands.describe(member="The member to unmute.")
async def unmute(interaction: discord.Interaction, member: discord.Member):
    """Removes a timeout from a member."""
    if not check_if_staff(interaction):
        await interaction.response.send_message("You don't have the right permissions to use this command!", ephemeral=True)
        return

    try:
        await member.timeout(None, reason=f"Unmuted by {interaction.user}")
        await interaction.response.send_message(f"🔊 {member.mention} has been unmuted.", ephemeral=True)
        log_details = f"**Target:** {member.mention}"
        await log_action(interaction, "User Unmuted", log_details, color=discord.Color.dark_green())
    except discord.Forbidden:
        await interaction.response.send_message("❌ I do not have the 'Moderate Members' permission.", ephemeral=True)

@tree.command(name="purge", description="Deletes a specified number of messages from the channel. [Staff Only]", guild=GUILD)
@app_commands.describe(amount="The number of messages to delete (1-100).")
async def purge(interaction: discord.Interaction, amount: int):
    """Deletes messages in bulk from the current channel."""
    if not check_if_staff(interaction):
        await interaction.response.send_message("You don't have the right permissions to use this command!", ephemeral=True)
        return

    if not 1 <= amount <= 100:
        await interaction.response.send_message("❌ Please provide a number between 1 and 100.", ephemeral=True)
        return

    try:
        deleted_messages = await interaction.channel.purge(limit=amount)
        await interaction.response.send_message(f"🧹 Successfully deleted {len(deleted_messages)} messages.", ephemeral=True)

        log_details = f"**Amount:** {len(deleted_messages)}\n**Channel:** {interaction.channel.mention}"
        await log_action(interaction, "Messages Purged", log_details, color=discord.Color.dark_orange())
    except discord.Forbidden:
        await interaction.response.send_message("❌ I don't have the 'Manage Messages' permission to do that here.", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"An error occurred: {e}", ephemeral=True)

@tree.command(name="lock", description="Locks a channel, preventing members from sending messages. [Staff Only]", guild=GUILD)
@app_commands.describe(channel="The channel to lock (defaults to current channel).")
async def lock(interaction: discord.Interaction, channel: Optional[discord.TextChannel] = None):
    """Locks a text channel for the @everyone role."""
    if not check_if_staff(interaction):
        await interaction.response.send_message("You don't have the right permissions to use this command!", ephemeral=True)
        return

    target_channel = channel or interaction.channel
    overwrite = target_channel.overwrites_for(interaction.guild.default_role)

    if overwrite.send_messages is False:
        await interaction.response.send_message(f"❌ {target_channel.mention} is already locked.", ephemeral=True)
        return

    overwrite.send_messages = False
    try:
        await target_channel.set_permissions(interaction.guild.default_role, overwrite=overwrite, reason=f"Locked by {interaction.user}")
        await interaction.response.send_message(f"🔒 {target_channel.mention} has been locked.", ephemeral=True)
        await target_channel.send("🔒 This channel has been locked by a moderator.")
        await log_action(interaction, "Channel Locked", f"**Channel:** {target_channel.mention}", color=discord.Color.dark_grey())
    except discord.Forbidden:
        await interaction.response.send_message("❌ I don't have the 'Manage Channels' permission to do this.", ephemeral=True)

@tree.command(name="unlock", description="Unlocks a channel, allowing members to send messages. [Staff Only]", guild=GUILD)
@app_commands.describe(channel="The channel to unlock (defaults to current channel).")
async def unlock(interaction: discord.Interaction, channel: Optional[discord.TextChannel] = None):
    """Unlocks a text channel for the @everyone role."""
    if not check_if_staff(interaction):
        await interaction.response.send_message("You don't have the right permissions to use this command!", ephemeral=True)
        return

    target_channel = channel or interaction.channel
    overwrite = target_channel.overwrites_for(interaction.guild.default_role)

    if overwrite.send_messages is not False: # Can be None or True
        await interaction.response.send_message(f"❌ {target_channel.mention} is not currently locked.", ephemeral=True)
        return

    overwrite.send_messages = None # Resets to default
    try:
        await target_channel.set_permissions(interaction.guild.default_role, overwrite=overwrite, reason=f"Unlocked by {interaction.user}")
        await interaction.response.send_message(f"🔓 {target_channel.mention} has been unlocked.", ephemeral=True)
        await target_channel.send("🔓 This channel has been unlocked.")
        await log_action(interaction, "Channel Unlocked", f"**Channel:** {target_channel.mention}", color=discord.Color.dark_green())
    except discord.Forbidden:
        await interaction.response.send_message("❌ I don't have the 'Manage Channels' permission to do this.", ephemeral=True)

@tree.command(name="lockdown", description="Locks all channels in the server for the @everyone role. [Staff Only]", guild=GUILD)
async def lockdown(interaction: discord.Interaction):
    """Initiates a server-wide lockdown."""
    if not check_if_staff(interaction):
        await interaction.response.send_message("You don't have the right permissions to use this command!", ephemeral=True)
        return

    await interaction.response.defer(ephemeral=True)
    locked_channels = 0
    for channel in interaction.guild.text_channels:
        # Only lock channels that @everyone can see
        if channel.overwrites_for(interaction.guild.default_role).read_messages is not False:
            overwrite = channel.overwrites_for(interaction.guild.default_role)
            if overwrite.send_messages is not False:
                overwrite.send_messages = False
                await channel.set_permissions(interaction.guild.default_role, overwrite=overwrite, reason=f"Server Lockdown by {interaction.user}")
                locked_channels += 1
    
    await interaction.followup.send(f"🚨 Server Lockdown Initiated. {locked_channels} channels have been locked.", ephemeral=True)
    await log_action(interaction, "Server Lockdown", f"Locked {locked_channels} channels.", color=discord.Color.red())

@tree.command(name="unlockdown", description="Lifts a server-wide lockdown. [Staff Only]", guild=GUILD)
async def unlockdown(interaction: discord.Interaction):
    """Lifts a server-wide lockdown."""
    if not check_if_staff(interaction):
        await interaction.response.send_message("You don't have the right permissions to use this command!", ephemeral=True)
        return

    await interaction.response.defer(ephemeral=True)
    unlocked_channels = 0
    for channel in interaction.guild.text_channels:
        overwrite = channel.overwrites_for(interaction.guild.default_role)
        if overwrite.send_messages is False:
            overwrite.send_messages = None # Reset to default
            await channel.set_permissions(interaction.guild.default_role, overwrite=overwrite, reason=f"Lockdown Lifted by {interaction.user}")
            unlocked_channels += 1

    if unlocked_channels == 0:
        await interaction.followup.send("✅ No channels were in lockdown.", ephemeral=True)
    else:
        await interaction.followup.send(f"🔓 Server Lockdown Lifted. {unlocked_channels} channels have been unlocked.", ephemeral=True)
        await log_action(interaction, "Lockdown Lifted", f"Unlocked {unlocked_channels} channels.", color=discord.Color.green())

@tree.command(name="ban", description="Bans a member from the server. [Staff Only]", guild=GUILD)
@app_commands.describe(member="The member to ban.", reason="The reason for the ban.")
async def ban(interaction: discord.Interaction, member: discord.Member, reason: str):
    """Bans a user from the server and logs it."""
    if not check_if_staff(interaction):
        await interaction.response.send_message("You don't have the right permissions to use this command!", ephemeral=True)
        return

    if member.id == interaction.user.id:
        await interaction.response.send_message("❌ You cannot ban yourself.", ephemeral=True)
        return
    if member.top_role >= interaction.user.top_role and str(interaction.user.id) != OWNER_ID:
        await interaction.response.send_message("❌ You cannot ban a member with an equal or higher role.", ephemeral=True)
        return

    try:
        dm_embed = discord.Embed(
            title="🚫 You Have Been Banned",
            description=f"You have been permanently banned from **{interaction.guild.name}**.",
            color=discord.Color.red()
        )
        dm_embed.add_field(name="Reason", value=reason, inline=False)
        await member.send(embed=dm_embed)
    except discord.Forbidden:
        # Fails silently if DMs are closed, but the ban will still proceed.
        pass

    try:
        await member.ban(reason=f"Banned by {interaction.user}. Reason: {reason}")
        await interaction.response.send_message(f"✅ {member.mention} has been banned.", ephemeral=True)
        log_details = f"**Target:** {member.mention}\n**Reason:** {reason}"
        await log_action(interaction, "User Banned", log_details, color=discord.Color.red())
    except discord.Forbidden:
        await interaction.response.send_message("❌ I do not have the 'Ban Members' permission.", ephemeral=True)

@tree.command(name="kick", description="Kicks a member from the server. [Staff Only]", guild=GUILD)
@app_commands.describe(member="The member to kick.", reason="The reason for the kick.")
async def kick(interaction: discord.Interaction, member: discord.Member, reason: str):
    """Kicks a user from the server and logs it."""
    if not check_if_staff(interaction):
        await interaction.response.send_message("You don't have the right permissions to use this command!", ephemeral=True)
        return

    if member.id == interaction.user.id:
        await interaction.response.send_message("❌ You cannot kick yourself.", ephemeral=True)
        return
    if member.top_role >= interaction.user.top_role and str(interaction.user.id) != OWNER_ID:
        await interaction.response.send_message("❌ You cannot kick a member with an equal or higher role.", ephemeral=True)
        return

    try:
        dm_embed = discord.Embed(
            title="👢 You Have Been Kicked",
            description=f"You have been kicked from **{interaction.guild.name}**.",
            color=discord.Color.orange()
        )
        dm_embed.add_field(name="Reason", value=reason, inline=False)
        dm_embed.set_footer(text="You can rejoin with a new invite link.")
        await member.send(embed=dm_embed)
    except discord.Forbidden:
        pass

    try:
        await member.kick(reason=f"Kicked by {interaction.user}. Reason: {reason}")
        await interaction.response.send_message(f"✅ {member.mention} has been kicked.", ephemeral=True)
        log_details = f"**Target:** {member.mention}\n**Reason:** {reason}"
        await log_action(interaction, "User Kicked", log_details, color=discord.Color.orange())
    except discord.Forbidden:
        await interaction.response.send_message("❌ I do not have the 'Kick Members' permission.", ephemeral=True)

@tree.command(name="wipebotmessages", description="Deletes the bot's own messages from the channel. [Staff Only]", guild=GUILD)
@app_commands.describe(limit="The number of messages to check (default 100).")
async def wipebotmessages(interaction: discord.Interaction, limit: int = 100):
    """Deletes the bot's own messages from the current channel."""
    if not check_if_staff(interaction):
        await interaction.response.send_message("You don't have the right permissions to use this command!", ephemeral=True)
        return

    await interaction.response.defer(ephemeral=True)

    def is_me(m):
        return m.author == bot.user

    try:
        deleted = await interaction.channel.purge(limit=limit, check=is_me)
        await interaction.followup.send(f"🧹 Successfully deleted {len(deleted)} of my own messages.", ephemeral=True)
        await log_action(interaction, "Bot Messages Wiped", f"**Channel:** {interaction.channel.mention}\n**Amount:** {len(deleted)}", color=discord.Color.dark_orange())
    except discord.Forbidden:
        await interaction.followup.send("❌ I don't have the 'Manage Messages' permission to do that here.", ephemeral=True)


@tree.command(name="slowmode", description="Sets a slowmode cooldown for a channel. [Staff Only]", guild=GUILD)
@app_commands.describe(
    seconds="The slowmode delay in seconds (0 to disable, max 21600).",
    channel="The channel to set slowmode in (defaults to current channel)."
)
async def slowmode(interaction: discord.Interaction, seconds: int, channel: Optional[discord.TextChannel] = None):
    """Sets or disables slowmode in a text channel."""
    if not check_if_staff(interaction):
        await interaction.response.send_message("You don't have the right permissions to use this command!", ephemeral=True)
        return

    target_channel = channel or interaction.channel

    if not 0 <= seconds <= 21600:
        await interaction.response.send_message("❌ Slowmode must be between 0 (off) and 21600 seconds (6 hours).", ephemeral=True)
        return

    try:
        await target_channel.edit(slowmode_delay=seconds, reason=f"Slowmode set by {interaction.user}")

        if seconds > 0:
            duration_str = f"{seconds} second{'s' if seconds != 1 else ''}"
            response_message = f"✅ Slowmode has been set to {duration_str} in {target_channel.mention}."
            channel_message = f"⏱️ This channel is now in slowmode. You can send a message every {duration_str}."
            log_details = f"**Channel:** {target_channel.mention}\n**Duration:** {duration_str}"
            await log_action(interaction, "Slowmode Enabled", log_details, color=discord.Color.light_grey())
        else:
            response_message = f"✅ Slowmode has been disabled in {target_channel.mention}."
            channel_message = "⏱️ Slowmode has been disabled in this channel."
            log_details = f"**Channel:** {target_channel.mention}"
            await log_action(interaction, "Slowmode Disabled", log_details, color=discord.Color.dark_green())

        await interaction.response.send_message(response_message, ephemeral=True)
        await target_channel.send(channel_message)
    except discord.Forbidden:
        await interaction.response.send_message("❌ I don't have the 'Manage Channel' permission to do this.", ephemeral=True)

@tree.command(name="massmove", description="Move all members from one voice channel to another. [Staff Only]", guild=GUILD)
@app_commands.describe(
    from_channel="The voice channel to move members from.",
    to_channel="The voice channel to move members to."
)
async def massmove(interaction: discord.Interaction, from_channel: discord.VoiceChannel, to_channel: discord.VoiceChannel):
    """Moves all members from a source voice channel to a target one."""
    if not check_if_staff(interaction):
        await interaction.response.send_message("You don't have the right permissions to use this command!", ephemeral=True)
        return

    if not from_channel.members:
        await interaction.response.send_message(f"❌ There is no one in {from_channel.mention} to move.", ephemeral=True)
        return

    moved_count = 0
    move_tasks = []
    for member in from_channel.members:
        move_tasks.append(member.move_to(to_channel, reason=f"Mass move by {interaction.user}"))
        moved_count += 1
    await asyncio.gather(*move_tasks, return_exceptions=True) # Move all members concurrently
    
    await interaction.response.send_message(f"✅ Successfully moved {moved_count} member(s) from {from_channel.mention} to {to_channel.mention}.", ephemeral=True)
    await log_action(interaction, "Mass Voice Move", f"Moved {moved_count} members from {from_channel.mention} to {to_channel.mention}", color=discord.Color.blue())

@tree.command(name="announce", description="Announces a new update in a formatted embed. [Staff Only]", guild=GUILD)
@app_commands.describe(
    title="The title of the announcement.",
    description="The detailed description. Use '\\n' for new lines.",
    channel="The channel to send the announcement to (defaults to current).",
    mention_role="An optional role to mention with the announcement."
)
async def announce(
    interaction: discord.Interaction,
    title: str,
    description: str,
    channel: Optional[discord.TextChannel] = None,
    mention_role: Optional[discord.Role] = None
):
    """Creates and sends a formatted update announcement."""
    if not check_if_staff(interaction):
        await interaction.response.send_message("You don't have the right permissions to use this command!", ephemeral=True)
        return

    target_channel = channel or interaction.channel
    formatted_description = description.replace('\\n', '\n')

    try:
        embed = discord.Embed(
            title=f"📢 {title}",
            description=formatted_description,
            color=discord.Color.blue(),
            timestamp=datetime.datetime.now(datetime.timezone.utc)
        )
        embed.set_author(name=f"Update from {interaction.guild.name}", icon_url=interaction.guild.icon.url if interaction.guild.icon else None)
        embed.set_footer(text=f"Announced by {interaction.user.display_name}")

        content = mention_role.mention if mention_role else None
        await target_channel.send(content=content, embed=embed)
        await interaction.response.send_message(f"✅ Announcement sent successfully in {target_channel.mention}.", ephemeral=True)
        await log_action(interaction, "Announcement Sent", f"**Title:** {title}\n**Channel:** {target_channel.mention}", color=discord.Color.blue())
    except discord.Forbidden:
        await interaction.response.send_message(f"❌ I don't have permission to send messages in {target_channel.mention}.", ephemeral=True)

@tree.command(name="altcheck", description="Checks if a user account is potentially an alt. [Staff Only]", guild=GUILD)
@app_commands.describe(user="The user to check.")
async def altcheck(interaction: discord.Interaction, user: discord.Member):
    """Checks the age of a user's account to flag potential alts."""
    if not check_if_staff(interaction):
        await interaction.response.send_message("You don't have the right permissions to use this command!", ephemeral=True)
        return

    account_age = datetime.datetime.now(datetime.timezone.utc) - user.created_at
    
    embed = discord.Embed(title=f"🕵️ Alt Check for {user.display_name}", color=user.color)
    embed.add_field(name="Account Created", value=discord.utils.format_dt(user.created_at, style='F'), inline=False)
    embed.add_field(name="Account Age", value=f"{account_age.days} days", inline=False)

    if account_age.days < 30:
        embed.description = "⚠️ **Warning:** This account is less than 30 days old."
        embed.color = discord.Color.orange()
    else:
        embed.description = "✅ This account seems to be established."
        embed.color = discord.Color.green()
        
    await interaction.response.send_message(embed=embed, ephemeral=True)

@tree.command(name="audit", description="Get an audit of a user's actions. [Staff Only]", guild=GUILD)
@app_commands.describe(user="The user to audit.")
async def audit(interaction: discord.Interaction, user: discord.Member):
    """Provides a summary of a user's recorded actions."""
    if not check_if_staff(interaction):
        await interaction.response.send_message("You don't have the right permissions to use this command!", ephemeral=True)
        return

    user_id_str = str(user.id)
    user_warnings = warnings_data.get(user_id_str, [])
    user_notes = notes_data.get(user_id_str, [])

    embed = discord.Embed(title=f"📋 Audit Log for {user.display_name}", color=user.color)
    embed.set_thumbnail(url=user.display_avatar.url)
    
    embed.add_field(name="Joined Server", value=discord.utils.format_dt(user.joined_at, style='F'), inline=False)

    if user_warnings:
        embed.add_field(name="Warnings", value=str(len(user_warnings)), inline=True)
    
    if user_notes:
        embed.add_field(name="Staff Notes", value=str(len(user_notes)), inline=True)

    await interaction.response.send_message(embed=embed, ephemeral=True)

@tree.command(name="history", description="View the full moderation history of a user. [Staff Only]", guild=GUILD)
@app_commands.describe(user="The user whose history you want to see.")
async def history(interaction: discord.Interaction, user: discord.Member):
    """Displays a combined history of warnings and notes for a user."""
    if not check_if_staff(interaction):
        await interaction.response.send_message("You don't have the right permissions to use this command!", ephemeral=True)
        return

    user_id_str = str(user.id)
    user_warnings = warnings_data.get(user_id_str, [])
    user_notes = notes_data.get(user_id_str, [])

    if not user_warnings and not user_notes:
        await interaction.response.send_message(f"✅ {user.mention} has a clean record.", ephemeral=True)
        return

    embed = discord.Embed(title=f"📜 Moderation History for {user.display_name}", color=user.color)
    
    if user_warnings:
        warning_text = "\n".join(f"• {reason}" for reason in user_warnings)
        embed.add_field(name=f"⚠️ Warnings ({len(user_warnings)})", value=warning_text, inline=False)

    if user_notes:
        note_text = ""
        for note_data in user_notes:
            author = interaction.guild.get_member(note_data['author_id'])
            note_text += f"• {note_data['note']} *(by {author.name if author else 'Unknown'})*\n"
        embed.add_field(name=f"📝 Notes ({len(user_notes)})", value=note_text, inline=False)

    await interaction.response.send_message(embed=embed, ephemeral=True)

# --- Utility & Info Commands ---
@tree.command(name="ping", description="Check the bot's latency. [Everyone]", guild=GUILD)
async def ping(interaction: discord.Interaction):
    latency = round(bot.latency * 1000)
    embed = discord.Embed(
        title="🏓 Pong!",
        description=f"My latency is **{latency}ms**.",
        color=discord.Color.green() if latency < 150 else discord.Color.orange()
    )
    await interaction.response.send_message(embed=embed, ephemeral=True)

@tree.command(name="uptime", description="Shows how long the bot has been online. [Everyone]", guild=GUILD)
async def uptime(interaction: discord.Interaction):
    """Displays the bot's uptime."""
    current_time = datetime.datetime.now(datetime.timezone.utc)
    delta = current_time - start_time
    hours, remainder = divmod(int(delta.total_seconds()), 3600)
    minutes, seconds = divmod(remainder, 60)
    days, hours = divmod(hours, 24)
    uptime_str = f"{days}d {hours}h {minutes}m {seconds}s"
    
    embed = discord.Embed(
        title="🕒 Bot Uptime",
        description=f"I have been online for **{uptime_str}**.",
        color=discord.Color.blue()
    )
    await interaction.response.send_message(embed=embed)


@tree.command(name="userinfo", description="View information about a user. [Everyone]", guild=GUILD)
@app_commands.describe(member="The member to get information about (defaults to you).")
async def userinfo(interaction: discord.Interaction, member: Optional[discord.Member] = None):
    """Displays detailed information about a server member."""
    target_member = member or interaction.user

    embed = discord.Embed(
        title=f"👤 User Info: {target_member.display_name}",
        color=target_member.color,
        timestamp=datetime.datetime.now(datetime.timezone.utc)
    )
    embed.set_thumbnail(url=target_member.display_avatar.url)
    embed.add_field(name="Full Name", value=str(target_member), inline=True)
    embed.add_field(name="User ID", value=target_member.id, inline=True)
    embed.add_field(name="Top Role", value=target_member.top_role.mention if target_member.top_role.name != "@everyone" else "None", inline=False)
    embed.add_field(name="Joined Server", value=discord.utils.format_dt(target_member.joined_at, style='R'), inline=True)
    embed.add_field(name="Account Created", value=discord.utils.format_dt(target_member.created_at, style='R'), inline=True)

    await interaction.response.send_message(embed=embed, ephemeral=True)

@tree.command(name="avatar", description="View a user's avatar. [Everyone]", guild=GUILD)
@app_commands.describe(member="The member whose avatar you want to see (defaults to you).")
async def avatar(interaction: discord.Interaction, member: Optional[discord.Member] = None):
    """Displays a user's avatar in a large embed."""
    target_member = member or interaction.user
    embed = discord.Embed(
        title=f"🖼️ Avatar of {target_member.display_name}",
        color=target_member.color
    )
    embed.set_image(url=target_member.display_avatar.url)
    await interaction.response.send_message(embed=embed, ephemeral=True)

@tree.command(name="serverinfo", description="Displays detailed statistics about the server. [Everyone]", guild=GUILD)
async def serverinfo(interaction: discord.Interaction):
    """Shows a beautiful embed with server statistics."""
    guild = interaction.guild

    # Counts
    member_count = guild.member_count
    bot_count = sum(1 for member in guild.members if member.bot)
    human_count = member_count - bot_count
    text_channels = len(guild.text_channels)
    voice_channels = len(guild.voice_channels)
    category_channels = len(guild.categories)
    role_count = len(guild.roles)

    embed = discord.Embed(
        title=f"📊 Server Info: {guild.name}",
        description=f"**Server ID:** {guild.id}",
        color=discord.Color.blue(),
        timestamp=guild.created_at
    )
    if guild.icon:
        embed.set_thumbnail(url=guild.icon.url)
    embed.set_footer(text="Server Created On")

    embed.add_field(name="👑 Owner", value=guild.owner.mention, inline=True)
    embed.add_field(name="👥 Members", value=f"**Total:** {member_count}\n**Humans:** {human_count}\n**Bots:** {bot_count}", inline=True)
    embed.add_field(name="📺 Channels", value=f"**Text:** {text_channels}\n**Voice:** {voice_channels}\n**Categories:** {category_channels}", inline=True)
    embed.add_field(name="💎 Roles", value=str(role_count), inline=True)
    embed.add_field(name="✅ Verification", value=str(guild.verification_level).capitalize(), inline=True)
    embed.add_field(name="🚀 Boosts", value=f"Level {guild.premium_tier} ({guild.premium_subscription_count} boosts)", inline=True)

    await interaction.response.send_message(embed=embed)

@tree.command(name="roleinfo", description="Shows detailed information about a role. [Everyone]", guild=GUILD)
@app_commands.describe(role="The role to get information about.")
async def roleinfo(interaction: discord.Interaction, role: discord.Role):
    """Displays detailed information about a server role."""
    embed = discord.Embed(title=f"📜 Role Info: {role.name}", color=role.color, timestamp=role.created_at)
    embed.add_field(name="ID", value=role.id, inline=True)
    embed.add_field(name="Color (Hex)", value=str(role.color), inline=True)
    embed.add_field(name="Members", value=len(role.members), inline=True)
    embed.add_field(name="Mentionable", value="Yes" if role.mentionable else "No", inline=True)
    embed.add_field(name="Hoisted", value="Yes" if role.hoisted else "No", inline=True)
    embed.add_field(name="Position", value=role.position, inline=True)
    embed.set_footer(text="Role Created On")
    await interaction.response.send_message(embed=embed, ephemeral=True)

@tree.command(name="poll", description="Create a simple poll. [Everyone]", guild=GUILD)
@app_commands.describe(
    question="The question for the poll.",
    option1="First choice.",
    option2="Second choice.",
    minutes="How many minutes the poll should last (optional, for auto-closing).",
    option3="Third choice (optional).",
    option4="Fourth choice (optional).",
    option5="Fifth choice (optional)."
)
async def poll(interaction: discord.Interaction, question: str, option1: str, option2: str, minutes: Optional[int] = None, option3: Optional[str] = None, option4: Optional[str] = None, option5: Optional[str] = None):
    """Creates a poll that can automatically close and announce a winner."""
    options = [opt for opt in [option1, option2, option3, option4, option5] if opt]
    reactions = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣"]

    description = ""
    if minutes:
        end_time = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=minutes)
        description = f"This poll will end {discord.utils.format_dt(end_time, style='R')}."

    embed = discord.Embed(
        title=f"📊 Poll: {question}",
        description=description,
        color=discord.Color.blurple(),
    )
    embed.set_author(name=f"Created by {interaction.user.display_name}", icon_url=interaction.user.display_avatar.url)

    for i, option in enumerate(options):
        embed.add_field(name=f"{reactions[i]} {option}", value="\u200b", inline=False)

    await interaction.response.send_message("✅ Poll created successfully!", ephemeral=True)
    poll_message = await interaction.channel.send(embed=embed)

    for i in range(len(options)):
        await poll_message.add_reaction(reactions[i])

    if minutes:
        await asyncio.sleep(minutes * 60)

        # Fetch the message again to get the latest reaction counts
        try:
            updated_message = await interaction.channel.fetch_message(poll_message.id)
        except discord.NotFound:
            # The message was deleted, so we can't announce a winner
            return

        results = {}
        for i, option_text in enumerate(options):
            # Find the reaction that corresponds to the option
            reaction = discord.utils.get(updated_message.reactions, emoji=reactions[i])
            if reaction:
                # Subtract 1 to not count the bot's own reaction
                results[option_text] = reaction.count - 1

        # Find the winner(s)
        max_votes = -1
        winners = []
        if results:
            max_votes = max(results.values())
            if max_votes > 0:
                winners = [option for option, votes in results.items() if votes == max_votes]

        # Announce the result
        result_embed = discord.Embed(title=f"🏁 Poll Ended: {question}", color=discord.Color.dark_gold())
        if not winners:
            result_embed.description = "The poll ended with no votes."
        else:
            winner_text = "\n".join(f"🏆 **{winner}**" for winner in winners)
            result_embed.description = f"The winner is...\n\n{winner_text}\n\nwith **{max_votes}** vote(s)!"
        await updated_message.reply(embed=result_embed)

@tree.command(name="commands", description="Shows a categorized list of all available commands. [Everyone]", guild=GUILD)
async def commands(interaction: discord.Interaction):
    """Displays a well-organized, categorized list of all bot commands."""
    
    # Define categories and the commands that belong to them
    categories = {
        "🛠️ Moderation & Management": [
            "altcheck", "announce", "audit", "ban", "clearwarnings", "history", "kick", "lock", "lockdown", "massmove", "mute", "note", "presetmessage", "removelevelrole", "softban", "unlockdown",
            "setlevelrole", "setupverification", "setxp",
            "purge", "roleinfo", "slowmode", "unlock", "unmute", "warn", "warnings"
        ],
        "🎟️ Ticket System": [
            "ticketadd", "ticketclaim", "ticketdelete", "ticketremove", "ticketsetup"
        ],
        "📊 Server & User Stats": [
            "avatar", "botstats", "emojistats", "membercount", "messagestats",
            "serverinfo", "topchatters", "uptime", "userinfo"
        ],
        "🎮 Fun & Community": [
            "giveaway", "meme", "poll", "roast", "ship", "tag"
        ],
        "⚙️ Utility": [
            "commands", "ping"
        ],
        "🌍 Everyone's Commands": [
            "8ball", "balance", "bank", "boosters", "daily", "dadjoke", "gamble", "give", "invest", "leaderboard", "rep", "repleaderboard",
            "levelboard", "mock", "privateverify", "rank", "rps", "slots", "suggest", "remindme",
            "about", "afk", "coinflip", "hug", "pat", "slap", "fact", "stopwatch", "timer", "urban", "truth",
            "dare", "spinbottle", "serverage", "accountage", "countdown", "calendar", "feedback", "botinvite",
            "levelroles"
        ]
    }

    all_commands = {cmd.name: cmd for cmd in tree.get_commands(guild=GUILD)}
    
    embed = discord.Embed(
        title="📜 Bot Command List",
        description=f"Here are all the available commands, sorted by category. There are `{len(all_commands)}` commands in total.",
        color=discord.Color.blurple()
    )

    for category_name, command_names in categories.items():
        command_list = []
        for name in sorted(command_names):
            cmd = all_commands.get(name)
            if cmd:
                # Shorten long descriptions for a cleaner look
                desc = (cmd.description[:70] + '...') if len(cmd.description) > 70 else cmd.description
                command_list.append(f"`/{cmd.name}` - {desc}")
        
        if command_list:
            # Split the command list into chunks of 1024 characters or less
            chunked_command_list = chunk_string("\n".join(command_list), 1024)
            for i, chunk in enumerate(chunked_command_list):
                field_name = category_name if i == 0 else f"{category_name} (cont.)"
                embed.add_field(name=field_name, value=chunk, inline=False)


    embed.set_footer(text=f"Requested by {interaction.user.display_name}")
    embed.timestamp = datetime.datetime.now(datetime.timezone.utc)

    await interaction.response.send_message(embed=embed, ephemeral=True)

# --- Ticket System Commands ---

@tree.command(name="ticketsetup", description="Sets up the ticket creation panel. [Staff Only]", guild=GUILD)
async def ticketsetup(interaction: discord.Interaction):
    """Sends the ticket creation message with the button."""
    if not check_if_staff(interaction):
        await interaction.response.send_message("You don't have the right permissions to use this command!", ephemeral=True)
        return

    panel_channel = bot.get_channel(TICKET_PANEL_CHANNEL_ID)
    if not panel_channel:
        await interaction.response.send_message(f"❌ Ticket panel channel with ID `{TICKET_PANEL_CHANNEL_ID}` not found.", ephemeral=True)
        return
        
    embed = discord.Embed(title="Support Tickets", description="Click the button below to create a private ticket and get help from our staff team.", color=discord.Color.blue())
    await panel_channel.send(embed=embed, view=TicketCreationView())
    await interaction.response.send_message(f"✅ Ticket panel has been set up in {panel_channel.mention}.", ephemeral=True)

@tree.command(name="ticketdelete", description="Permanently deletes a closed ticket channel. [Staff Only]", guild=GUILD)
async def ticketdelete(interaction: discord.Interaction):
    """Permanently deletes a ticket channel after it has been closed."""
    if not check_if_staff(interaction):
        await interaction.response.send_message("You don't have the right permissions to use this command!", ephemeral=True)
        return

    channel = interaction.channel
    if not channel.name.startswith("closed-"):
        await interaction.response.send_message("❌ This command can only be used in a closed ticket channel.", ephemeral=True)
        return

    await interaction.response.send_message("🗑️ Deleting this ticket channel...")

    # Create and send transcript before deleting
    transcript_file = await create_transcript(channel, interaction.user)
    log_channel = bot.get_channel(LOG_CHANNEL_ID)
    if log_channel and transcript_file:
        await log_channel.send(f"Transcript for deleted ticket `{channel.name}`:", file=transcript_file)
        os.remove(transcript_file.filename)

    await log_action(interaction, "Ticket Deleted", f"**Channel:** `{channel.name}`", color=discord.Color.red())
    await channel.delete(reason=f"Ticket permanently deleted by {interaction.user}")

@tree.command(name="ticketadd", description="Adds a user to the current ticket channel. [Staff Only]", guild=GUILD)
@app_commands.describe(member="The member to add to this ticket.")
async def ticketadd(interaction: discord.Interaction, member: discord.Member):
    """Adds a user to a ticket channel."""
    if not check_if_staff(interaction):
        await interaction.response.send_message("You don't have the right permissions to use this command!", ephemeral=True)
        return

    # Check if this is a ticket channel by checking if its category is one of the ticket categories
    if not any(interaction.channel.category_id == details["category_id"] for details in TICKET_CATEGORIES.values()):
        await interaction.response.send_message("❌ This command can only be used in a ticket channel.", ephemeral=True)
        return

    # Apply permissions
    try:
        await interaction.channel.set_permissions(member, read_messages=True, send_messages=True, reason=f"Added to ticket by {interaction.user}")
        await interaction.response.send_message(f"✅ {member.mention} has been added to this ticket.", ephemeral=True)
        await interaction.channel.send(f"👋 {member.mention} has been added to this ticket by {interaction.user.mention}.")
        await log_action(interaction, "User Added to Ticket", f"**Channel:** {interaction.channel.mention}\n**Added User:** {member.mention}", color=discord.Color.blue())
    except Exception as e:
        await interaction.response.send_message(f"❌ An error occurred while adding the user: {e}", ephemeral=True)

@tree.command(name="ticketremove", description="Removes a user from the current ticket channel. [Staff Only]", guild=GUILD)
@app_commands.describe(member="The member to remove from this ticket.")
async def ticketremove(interaction: discord.Interaction, member: discord.Member):
    """Removes a user from a ticket channel."""
    if not check_if_staff(interaction):
        await interaction.response.send_message("You don't have the right permissions to use this command!", ephemeral=True)
        return

    if not any(interaction.channel.category_id == details["category_id"] for details in TICKET_CATEGORIES.values()):
        await interaction.response.send_message("❌ This command can only be used in a ticket channel.", ephemeral=True)
        return

    # Prevent removing the ticket creator
    # The creator has explicit read_messages=True, others might have it via role
    channel_overwrites = interaction.channel.overwrites_for(member)
    # Check if the user has explicit read_messages=True and is not staff
    if channel_overwrites.read_messages is True and not any(role.id in staff_role_id for staff_role_id in STAFF_ROLE_IDS for role in member.roles):
        # This is likely the creator. A more robust check would be to store the creator ID when making the ticket.
        # For now, we'll assume the user with explicit perms is the creator.
        if not any(role.id in STAFF_ROLE_IDS for role in member.roles): # Staff can be removed
            await interaction.response.send_message("❌ You cannot remove the original creator of the ticket.", ephemeral=True)
            return

    try:
        await interaction.channel.set_permissions(member, overwrite=None, reason=f"Removed from ticket by {interaction.user}") # Resets permissions
        await interaction.response.send_message(f"✅ {member.mention} has been removed from this ticket.", ephemeral=True)
        await interaction.channel.send(f"👋 {member.mention} has been removed from this ticket by {interaction.user.mention}.")
        await log_action(interaction, "User Removed from Ticket", f"**Channel:** {interaction.channel.mention}\n**Removed User:** {member.mention}", color=discord.Color.dark_blue())
    except Exception as e:
        await interaction.response.send_message(f"❌ An error occurred while removing the user: {e}", ephemeral=True)

@tree.command(name="ticketrename", description="Renames the current ticket channel. [Staff Only]", guild=GUILD)
@app_commands.describe(new_name="The new name for the ticket (without the 'ticket-' prefix).")
async def ticketrename(interaction: discord.Interaction, new_name: str):
    """Renames an open ticket channel."""
    if not check_if_staff(interaction):
        await interaction.response.send_message("You don't have the right permissions to use this command!", ephemeral=True)
        return

    channel = interaction.channel
    if not any(channel.category_id == details["category_id"] for details in TICKET_CATEGORIES.values()) or channel.name.startswith("closed-"):
        await interaction.response.send_message("❌ This command can only be used in an open ticket channel.", ephemeral=True)
        return

    # Sanitize the name and add the prefix
    sanitized_name = new_name.lower().replace(" ", "-").strip()
    full_new_name = f"ticket-{sanitized_name}"

    try:
        await channel.edit(name=full_new_name, reason=f"Ticket renamed by {interaction.user}")
        await interaction.response.send_message(f"✅ Ticket has been renamed to `{full_new_name}`.", ephemeral=True)
        await channel.send(f"📝 This ticket has been renamed to `{full_new_name}` by {interaction.user.mention}.")
        await log_action(interaction, "Ticket Renamed", f"**Channel:** {channel.mention}\n**New Name:** `{full_new_name}`", color=discord.Color.blue())
    except Exception as e:
        await interaction.response.send_message(f"❌ An error occurred while renaming the ticket: {e}", ephemeral=True)
        print(f"Error renaming ticket: {e}")

@tree.command(name="ticketclaim", description="Claims the current ticket to notify the user who is handling it. [Staff Only]", guild=GUILD)
async def ticketclaim(interaction: discord.Interaction):
    """Claims a ticket, notifying the user that a staff member is assisting."""
    if not check_if_staff(interaction):
        await interaction.response.send_message("You don't have the right permissions to use this command!", ephemeral=True)
        return

    if not any(interaction.channel.category_id == details["category_id"] for details in TICKET_CATEGORIES.values()):
        await interaction.response.send_message("❌ This command can only be used in a ticket channel.", ephemeral=True)
        return

    try:
        claim_embed = discord.Embed(
            title="✅ Ticket Claimed",
            description=f"This ticket has been claimed by {interaction.user.mention}. They will be assisting you shortly.",
            color=discord.Color.teal()
        )
        claim_embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar.url)
        await interaction.channel.send(embed=claim_embed)
        await interaction.response.send_message("✅ You have successfully claimed this ticket.", ephemeral=True)
        await log_action(interaction, "Ticket Claimed", f"**Channel:** {interaction.channel.mention}", color=discord.Color.teal())
    except Exception as e:
        await interaction.response.send_message(f"❌ An error occurred while claiming the ticket: {e}", ephemeral=True)

@tree.command(name="botstats", description="Displays detailed statistics about the bot. [Staff Only]", guild=GUILD)
async def botstats(interaction: discord.Interaction):
    """Shows detailed statistics about the bot's performance and status."""
    if not check_if_staff(interaction):
        await interaction.response.send_message("You don't have the right permissions to use this command!", ephemeral=True)
        return

    # Uptime
    current_time = datetime.datetime.now(datetime.timezone.utc)
    delta = current_time - start_time
    hours, remainder = divmod(int(delta.total_seconds()), 3600)
    minutes, seconds = divmod(remainder, 60)
    days, hours = divmod(hours, 24)
    uptime_str = f"{days}d {hours}h {minutes}m {seconds}s"

    # System Info
    process = psutil.Process(os.getpid())
    memory_usage = process.memory_info().rss / (1024 * 1024)  # in MB
    cpu_usage = psutil.cpu_percent(interval=0.5)

    # Bot Info
    synced_commands = len(tree.get_commands(guild=GUILD))
    total_users = sum(guild.member_count for guild in bot.guilds)

    embed = discord.Embed(
        title="📈 Bot Statistics",
        description="Here are some real-time statistics about the bot.",
        color=discord.Color.purple(),
        timestamp=current_time
    )
    embed.set_thumbnail(url=bot.user.display_avatar.url)
    embed.add_field(name="🕒 Uptime", value=uptime_str, inline=True)
    embed.add_field(name="💻 CPU Usage", value=f"{cpu_usage}%", inline=True)
    embed.add_field(name="🧠 Memory Usage", value=f"{memory_usage:.2f} MB", inline=True)
    embed.add_field(name="🐍 Python Version", value=platform.python_version(), inline=True)
    embed.add_field(name="🔗 Discord.py Version", value=discord.__version__, inline=True)
    embed.add_field(name="⚙️ Commands", value=f"{synced_commands} loaded", inline=True)
    await interaction.response.send_message(embed=embed, ephemeral=True)

@tree.command(name="giveaway", description="Starts a giveaway in the current channel. [Staff Only]", guild=GUILD)
@app_commands.describe(prize="What is the prize for the giveaway?", minutes="How many minutes the giveaway should last.", winners="How many winners should be chosen (default 1).")
async def giveaway(interaction: discord.Interaction, prize: str, minutes: int, winners: int = 1): # This command should remain staff-only as it's a moderation/event tool
    """Starts a timed giveaway that automatically picks a winner."""
    if not check_if_staff(interaction):
        await interaction.response.send_message("You don't have the right permissions to use this command!", ephemeral=True)
        return

    if minutes <= 0:
        await interaction.response.send_message("❌ Giveaway duration must be greater than 0 minutes.", ephemeral=True)
        return

    end_time = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=minutes)

    embed = discord.Embed(
        title=f"🎉 Giveaway: {prize}",
        description=f"React with 🎉 to enter!\nEnds {discord.utils.format_dt(end_time, style='R')}\nHosted by: {interaction.user.mention}",
        color=discord.Color.gold()
    )
    embed.set_footer(text=f"{winners} winner{'s' if winners > 1 else ''} will be chosen.")

    # Send the giveaway message and react to it
    giveaway_message = await interaction.channel.send(embed=embed)
    await giveaway_message.add_reaction("🎉")
    await interaction.response.send_message(f"✅ Giveaway for **{prize}** started! It will end in {minutes} minute(s).", ephemeral=True)

    # Wait for the giveaway to end
    await asyncio.sleep(minutes * 60)

    # Fetch the message again to get the latest reactions
    updated_message = await interaction.channel.fetch_message(giveaway_message.id)
    users = [user async for user in updated_message.reactions[0].users() if not user.bot]

    if not users:
        await interaction.channel.send(f"The giveaway for **{prize}** has ended. No one entered! 😕")
    else:
        chosen_winners = random.sample(users, k=min(winners, len(users)))
        winner_mentions = ", ".join(w.mention for w in chosen_winners)
        await interaction.channel.send(f"Congratulations {winner_mentions}! You won the **{prize}**! 🎉")

# --- Fun & Community Commands ---

@tree.command(name="8ball", description="Ask the magic 8-ball a question. [Everyone]", guild=GUILD)
@app_commands.describe(question="Your yes/no question for the 8-ball.")
async def eightball(interaction: discord.Interaction, question: str):
    """Provides a random answer to a user's question."""
    responses = [
        "It is certain.", "It is decidedly so.", "Without a doubt.", "Yes – definitely.",
        "You may rely on it.", "As I see it, yes.", "Most likely.", "Outlook good.",
        "Yes.", "Signs point to yes.", "Reply hazy, try again.", "Ask again later.",
        "Better not tell you now.", "Cannot predict now.", "Concentrate and ask again.",
        "Don't count on it.", "My reply is no.", "My sources say no.", "Outlook not so good.", "Very doubtful."
    ]
    answer = random.choice(responses)
    embed = discord.Embed(title="🎱 The Magic 8-Ball Says...", color=discord.Color.purple())
    embed.add_field(name="Your Question", value=question, inline=False)
    embed.add_field(name="My Answer", value=answer, inline=False)
    await interaction.response.send_message(embed=embed)

@tree.command(name="meme", description="Fetches a random meme from Reddit. [Everyone]", guild=GUILD)
@app_commands.describe(subreddit="The subreddit to get a meme from (e.g., 'memes').")
async def meme(interaction: discord.Interaction, subreddit: Optional[str] = None):
    """Fetches a random meme from a given subreddit or a random one."""
    await interaction.response.defer()
    url = f"https://meme-api.com/gimme/{subreddit}" if subreddit else "https://meme-api.com/gimme"

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status != 200:
                await interaction.followup.send("❌ Could not fetch a meme. The subreddit might not exist or the API is down.", ephemeral=True)
                return
            
            data = await response.json()
            if data.get("nsfw") or data.get("spoiler"):
                # Fetch another one if the first is NSFW/spoiler
                async with session.get(url) as resp2:
                    data = await resp2.json()

            embed = discord.Embed(
                title=data.get("title"),
                url=data.get("postLink"),
                color=discord.Color.random()
            )
            embed.set_image(url=data.get("url"))
            embed.set_footer(text=f"From r/{data.get('subreddit')} | 👍 {data.get('ups')}")
            await interaction.followup.send(embed=embed)

@tree.command(name="roast", description="Sends a funny roast to the mentioned user. [Everyone]", guild=GUILD)
@app_commands.describe(member="The member to roast.")
async def roast(interaction: discord.Interaction, member: discord.Member):
    """Selects a random roast and sends it."""
    roasts = [
        "I'd agree with you but then we'd both be wrong.",
        "If I wanted to hear from an idiot, I'd watch the news.",
        "You're the reason the gene pool needs a lifeguard.",
        "I've been called worse by better people.",
        "If laughter is the best medicine, your face must be curing the world.",
        "You're not stupid; you just have bad luck when thinking.",
        "I'm not insulting you, I'm describing you."
    ]
    roast_message = random.choice(roasts)
    embed = discord.Embed(
        title=f"🔥 A Roast for {member.display_name}",
        description=roast_message,
        color=discord.Color.orange()
    )
    await interaction.response.send_message(content=member.mention, embed=embed)

@tree.command(name="ship", description="Calculates the love compatibility between two users. [Everyone]", guild=GUILD)
@app_commands.describe(user1="The first person.", user2="The second person.")
async def ship(interaction: discord.Interaction, user1: discord.Member, user2: discord.Member):
    """Generates a ship name and love percentage for two users."""
    love_percentage = random.randint(0, 100)
    
    # Generate ship name
    name1 = user1.display_name
    name2 = user2.display_name
    ship_name = name1[:len(name1)//2] + name2[len(name2)//2:]

    if love_percentage < 25:
        emoji = "💔"
        comment = "Not a great match..."
    elif love_percentage < 50:
        emoji = "🤔"
        comment = "There might be a chance."
    elif love_percentage < 75:
        emoji = "😊"
        comment = "Looking promising!"
    else:
        emoji = "💖"
        comment = "It's a perfect match!"

    embed = discord.Embed(
        title=f"Love Calculator: {name1} + {name2}",
        description=f"**Ship Name:** {ship_name}\n**Compatibility:** {love_percentage}% {emoji}\n\n*{comment}*",
        color=discord.Color.pink()
    )
    await interaction.response.send_message(embed=embed)

@tree.command(name="suggest", description="Submit a suggestion for the server. [Everyone]", guild=GUILD)
@app_commands.describe(idea="Your suggestion.")
async def suggest(interaction: discord.Interaction, idea: str):
    """Sends a suggestion to the designated suggestions channel."""
    suggestion_channel = interaction.guild.get_channel(SUGGESTION_CHANNEL_ID)
    if not suggestion_channel:
        await interaction.response.send_message("❌ The suggestion system is not configured correctly.", ephemeral=True)
        return

    embed = discord.Embed(
        title="💡 New Suggestion",
        description=idea,
        color=discord.Color.yellow(),
        timestamp=datetime.datetime.now(datetime.timezone.utc)
    )
    embed.set_author(name=f"Submitted by {interaction.user.display_name}", icon_url=interaction.user.display_avatar.url)

    try:
        suggestion_message = await suggestion_channel.send(embed=embed)
        await suggestion_message.add_reaction("👍")
        await suggestion_message.add_reaction("👎")
        await interaction.response.send_message(f"✅ Your suggestion has been submitted in {suggestion_channel.mention}!", ephemeral=True)
    except discord.Forbidden:
        await interaction.response.send_message(f"❌ I don't have permission to send messages or add reactions in the suggestions channel.", ephemeral=True)

@tree.command(name="boosters", description="Shows a list of all current server boosters. [Everyone]", guild=GUILD)
async def boosters(interaction: discord.Interaction):
    """Displays a list of members who are boosting the server."""
    booster_list = interaction.guild.premium_subscribers
    if not booster_list:
        await interaction.response.send_message("There are currently no server boosters. 😢", ephemeral=True)
        return

    embed = discord.Embed(
        title=f"🚀 Server Boosters ({len(booster_list)})",
        description="\n".join([f"• {booster.mention}" for booster in booster_list]),
        color=discord.Color.pink()
    )
    await interaction.response.send_message(embed=embed)

@tree.command(name="slots", description="Try your luck at the emoji slot machine! [Everyone]", guild=GUILD)
async def slots(interaction: discord.Interaction):
    """Runs a simple slot machine game."""
    emojis = ["🍒", "🍋", "🍊", "🍇", "🔔", "💎", "🍀"]
    reels = [random.choice(emojis) for _ in range(3)]

    result_text = f"**[ {reels[0]} | {reels[1]} | {reels[2]} ]**\n\n"
    if reels[0] == reels[1] == reels[2]:
        result_text += "🎉 JACKPOT! You won big! 🎉"
        color = discord.Color.gold()
    elif reels[0] == reels[1] or reels[1] == reels[2]:
        result_text += "🎊 You won a small prize! 🎊"
        color = discord.Color.green()
    else:
        result_text += "Better luck next time! 😕"
        color = discord.Color.red()

    embed = discord.Embed(title="🎰 Slot Machine 🎰", description=result_text, color=color)
    await interaction.response.send_message(embed=embed)

@tree.command(name="mock", description="Converts your text to mOcKiNg SpOnGeBoB text. [Everyone]", guild=GUILD)
async def mock(interaction: discord.Interaction, text: str):
    """Converts text to alternating case."""
    mocked_text = "".join(c.lower() if i % 2 == 0 else c.upper() for i, c in enumerate(text))
    await interaction.response.send_message(mocked_text)

@tree.command(name="dadjoke", description="Tells a random, cringey dad joke. [Everyone]", guild=GUILD)
async def dadjoke(interaction: discord.Interaction):
    """Sends a random dad joke from a predefined list."""
    jokes = [
        "Why don't scientists trust atoms? Because they make up everything!",
        "I'm reading a book on anti-gravity. It's impossible to put down!",
        "What do you call a fake noodle? An Impasta.",
        "Why did the scarecrow win an award? Because he was outstanding in his field!",
        "Did you hear about the restaurant on the moon? Great food, no atmosphere."
    ]
    await interaction.response.send_message(random.choice(jokes))

@tree.command(name="setupverification", description="Sets up the public verification message. [Staff Only]", guild=GUILD)
async def setupverification(interaction: discord.Interaction):
    """Sends a public verification message to the specified channel."""
    if not check_if_staff(interaction):
        await interaction.response.send_message("You don't have the right permissions to use this command!", ephemeral=True)
        return

    channel = bot.get_channel(VERIFICATION_CHANNEL_ID)
    if not channel:
        await interaction.response.send_message("❌ Verification channel not found. Please configure it correctly.", ephemeral=True)
        return

    embed = discord.Embed(
        title="Server Verification",
        description=(
            "Welcome!\n\n"
            "To gain full access to the server, please verify yourself by clicking the button below.\n"
            "This helps us prevent bots and maintain a safe community."
        ),
        color=discord.Color.green()
    )
    embed.set_thumbnail(url=interaction.guild.icon.url if interaction.guild.icon else bot.user.display_avatar.url)
    embed.set_footer(text="Click the button to verify!")

    view = VerificationView()  # Use the existing VerificationView

    try:
        await channel.send(embed=embed, view=view)
        await interaction.response.send_message(f"✅ Verification message sent to {channel.mention}.", ephemeral=True)
        await log_action(interaction, "Verification Message Setup", f"Sent to channel {channel.mention}", color=discord.Color.green())
    except discord.Forbidden:
        await interaction.response.send_message("❌ I do not have permission to send messages in that channel.", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"An error occurred: {e}", ephemeral=True)

@tree.command(name="membercount", description="Shows the current member count of the server. [Everyone]", guild=GUILD)
async def membercount(interaction: discord.Interaction):
    """Displays the server's member count."""
    guild = interaction.guild
    total_members = guild.member_count
    bot_count = sum(1 for member in guild.members if member.bot)
    human_count = total_members - bot_count

    embed = discord.Embed(
        title=f"👥 Member Count for {guild.name}",
        color=discord.Color.green()
    )
    embed.add_field(name="Total Members", value=str(total_members), inline=True)
    embed.add_field(name="Humans", value=str(human_count), inline=True)
    embed.add_field(name="Bots", value=str(bot_count), inline=True)
    await interaction.response.send_message(embed=embed)

@tree.command(name="messagestats", description="Shows the message count for a specific user. [Everyone]", guild=GUILD)
@app_commands.describe(user="The user to check stats for (defaults to you).")
async def messagestats(interaction: discord.Interaction, user: Optional[discord.Member] = None):
    """Shows how many messages a user has sent since the bot started."""
    target_user = user or interaction.user
    count = message_counts.get(target_user.id, 0)

    embed = discord.Embed(
        title=f"💬 Message Stats for {target_user.display_name}",
        description=f"They have sent **{count}** message(s) since the bot was last restarted.",
        color=target_user.color
    )
    await interaction.response.send_message(embed=embed)

@tree.command(name="topchatters", description="Shows a leaderboard of the most active chatters. [Everyone]", guild=GUILD)
async def topchatters(interaction: discord.Interaction):
    """Displays the top 10 most active members."""
    sorted_chatters = sorted(message_counts.items(), key=lambda item: item[1], reverse=True)
    
    embed = discord.Embed(
        title="🏆 Top 10 Chatters",
        description="Most active members since the bot's last restart.",
        color=discord.Color.gold()
    )

    if not sorted_chatters:
        embed.description = "No messages have been tracked yet."
    else:
        leaderboard_text = ""
        for i, (user_id, count) in enumerate(sorted_chatters[:10], 1):
            user = interaction.guild.get_member(user_id)
            leaderboard_text += f"**{i}.** {user.mention if user else f'Unknown User ({user_id})'}: {count} messages\n"
        embed.description = leaderboard_text

    await interaction.response.send_message(embed=embed)

@tree.command(name="emojistats", description="Shows a leaderboard of the most used custom emojis. [Everyone]", guild=GUILD)
async def emojistats(interaction: discord.Interaction):
    """Displays the top 10 most used custom emojis."""
    sorted_emojis = sorted(emoji_counts.items(), key=lambda item: item[1], reverse=True)

    embed = discord.Embed(
        title="🤩 Top 10 Custom Emojis",
        description="Most used emojis since the bot's last restart.",
        color=discord.Color.purple()
    )

    if not sorted_emojis:
        embed.description = "No custom emojis have been tracked yet."
    else:
        leaderboard_text = ""
        for i, (emoji_id, count) in enumerate(sorted_emojis[:10], 1):
            emoji = bot.get_emoji(emoji_id)
            leaderboard_text += f"**{i}.** {emoji if emoji else f'Unknown Emoji ({emoji_id})'}: {count} uses\n"
        embed.description = leaderboard_text

    await interaction.response.send_message(embed=embed)

# --- Leveling System Commands ---

# This command belongs to the 'setxp_group' defined in the Command Groups section
@setxp_group.command(name="user", description="Set the XP for a specific user. [Staff Only]")
@app_commands.describe(user="The user to set XP for.", amount="The amount of XP to set.")
async def setxp_user(interaction: discord.Interaction, user: discord.Member, amount: int):
    """Sets the XP for a single user."""
    if not check_if_staff(interaction):
        await interaction.response.send_message("You don't have the right permissions to use this command!", ephemeral=True)
        return

    if amount < 0:
        await interaction.response.send_message("❌ XP amount cannot be negative.", ephemeral=True)
        return

    user_id_str = str(user.id)
    if user_id_str not in leveling_data:
        leveling_data[user_id_str] = {}
    
    leveling_data[user_id_str]["level"] = 0 # Reset level when setting XP
    leveling_data[user_id_str]["xp"] = amount
    save_json(LEVELING_FILE, leveling_data)
    await check_and_apply_level_up(interaction, user) # Check for level up

    await interaction.response.send_message(f"✅ Set {user.mention}'s XP to **{amount}**.", ephemeral=True)
    await log_action(interaction, "XP Set (User)", f"**Target:** {user.mention}\n**Amount:** {amount}", color=discord.Color.dark_purple())

# This command belongs to the 'setxp_group' defined in the Command Groups section
@setxp_group.command(name="all", description="Set the XP for all members in the server. [Staff Only]")
@app_commands.describe(amount="The amount of XP to set for everyone.")
async def setxp_all(interaction: discord.Interaction, amount: int):
    """Sets the XP for all server members."""
    if not check_if_staff(interaction):
        await interaction.response.send_message("You don't have the right permissions to use this command!", ephemeral=True)
        return

    if amount < 0:
        await interaction.response.send_message("❌ XP amount cannot be negative.", ephemeral=True)
        return

    for member in interaction.guild.members:
        if not member.bot:
            leveling_data[str(member.id)] = {"level": 0, "xp": amount}
    save_json(LEVELING_FILE, leveling_data)
    # Note: check_and_apply_level_up is not called here to avoid spamming the channel for every user.
    await interaction.response.send_message(f"✅ Set everyone's XP to **{amount}**.", ephemeral=True)
    await log_action(interaction, "XP Set (All)", f"**Amount:** {amount}", color=discord.Color.red())

@tree.command(name="rank", description="Check your or another user's level and XP. [Everyone]", guild=GUILD)
@app_commands.describe(user="The user whose rank you want to see (optional).")
async def rank(interaction: discord.Interaction, user: Optional[discord.Member] = None):
    """Generates and displays a visual rank card for a user."""
    await interaction.response.defer()
    target_user = user or interaction.user
    user_id_str = str(target_user.id)

    user_data = leveling_data.get(user_id_str, {"level": 0, "xp": 0})
    level = user_data["level"]
    xp = user_data["xp"]
    xp_needed = xp_for_level(level)

    # --- Image Generation ---
    # Create a background
    img = Image.new('RGB', (934, 282), color='#23272A')
    draw = ImageDraw.Draw(img)

    # Build absolute path to the font file to avoid pathing issues
    font_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "font.ttf")
    # Load fonts (make sure 'font.ttf' is in your bot's directory)
    try:
        font_large = ImageFont.truetype(font_path, 60)
        font_medium = ImageFont.truetype(font_path, 40)
        font_small = ImageFont.truetype(font_path, 30)
    except IOError:
        await interaction.followup.send("❌ Font file `font.ttf` not found. Cannot generate rank card.", ephemeral=True)
        return

    # Draw user's name
    draw.text((260, 150), target_user.display_name, font=font_medium, fill='#FFFFFF')

    # Draw Level and XP text
    draw.text((260, 40), f"Level: {level}", font=font_large, fill='#FFFFFF')
    xp_text = f"{xp} / {xp_needed} XP"
    draw.text((260, 100), xp_text, font=font_small, fill='#B9BBBE')

    # Draw progress bar background
    draw.rectangle((260, 210, 850, 250), fill='#484B4E')

    # Draw progress bar
    if xp_needed > 0:
        progress_width = (xp / xp_needed) * (850 - 260)
        draw.rectangle((260, 210, 260 + progress_width, 250), fill='#7289DA')

    # Add avatar
    async with aiohttp.ClientSession() as session:
        async with session.get(str(target_user.display_avatar.url)) as response:
            avatar_data = await response.read()
    
    avatar_img = Image.open(io.BytesIO(avatar_data)).resize((180, 180))
    
    # Create a circular mask for the avatar
    mask = Image.new('L', (180, 180), 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.ellipse((0, 0, 180, 180), fill=255)
    
    img.paste(avatar_img, (50, 50), mask)

    # Save image to a buffer
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)

    await interaction.followup.send(file=discord.File(buffer, 'rank_card.png'))

@tree.command(name="levelboard", description="Shows the server's XP leaderboard. [Everyone]", guild=GUILD)
async def levelboard(interaction: discord.Interaction):
    """Displays the top 10 users by level and XP."""
    # Sort users by level, then by XP
    sorted_users = sorted(
        leveling_data.items(), 
        key=lambda item: (item[1].get('level', 0), item[1].get('xp', 0)), 
        reverse=True
    )

    embed = discord.Embed(title="🏆 Server Leaderboard", description="Top 10 most active members!", color=discord.Color.gold())

    leaderboard_text = ""
    for i, (user_id, data) in enumerate(sorted_users[:10], 1):
        user = interaction.guild.get_member(int(user_id))
        if user:
            level = data.get('level', 0)
            xp = data.get('xp', 0)
            leaderboard_text += f"**{i}.** {user.mention} - **Level {level}** ({xp} XP)\n"
    
    if not leaderboard_text:
        embed.description = "No one has gained any XP yet. Start chatting!"
    else:
        embed.description = leaderboard_text

    await interaction.response.send_message(embed=embed)

@tree.command(name="setlevelrole", description="Assign a role reward for reaching a certain level. [Staff Only]", guild=GUILD)
@app_commands.describe(level="The level to reward.", role="The role to give as a reward.")
async def setlevelrole(interaction: discord.Interaction, level: int, role: discord.Role):
    """Sets a role to be automatically given at a specific level."""
    if not check_if_staff(interaction):
        await interaction.response.send_message("You don't have the right permissions to use this command!", ephemeral=True)
        return

    if level <= 0:
        await interaction.response.send_message("❌ Level must be a positive number.", ephemeral=True)
        return
    
    level_str = str(level)
    level_rewards[level_str] = role.id
    save_json(LEVEL_REWARDS_FILE, level_rewards)

    await interaction.response.send_message(f"✅ **Level {level}** will now award the {role.mention} role.", ephemeral=True)
    await log_action(interaction, "Level Reward Set", f"**Level:** {level}\n**Role:** {role.mention}", color=discord.Color.blue())

@tree.command(name="removelevelrole", description="Remove a role reward from a level. [Staff Only]", guild=GUILD)
@app_commands.describe(level="The level to remove the reward from.")
async def removelevelrole(interaction: discord.Interaction, level: int):
    """Removes a role reward from a specific level."""
    if not check_if_staff(interaction):
        await interaction.response.send_message("You don't have the right permissions to use this command!", ephemeral=True)
        return

    level_str = str(level)
    if level_str in level_rewards:
        removed_role_id = level_rewards.pop(level_str)
        save_json(LEVEL_REWARDS_FILE, level_rewards)
        role = interaction.guild.get_role(removed_role_id)
        await interaction.response.send_message(f"✅ The role reward for **Level {level}** ({role.mention if role else 'Unknown Role'}) has been removed.", ephemeral=True)
        await log_action(interaction, "Level Reward Removed", f"**Level:** {level}", color=discord.Color.dark_blue())
    else:
        await interaction.response.send_message(f"❌ There is no role reward set for **Level {level}**.", ephemeral=True)

@tree.command(name="levelroles", description="View all configured level role rewards. [Everyone]", guild=GUILD)
async def levelroles(interaction: discord.Interaction):
    """Displays a list of all configured level-up role rewards."""
    if not level_rewards:
        await interaction.response.send_message("There are no level rewards configured yet.", ephemeral=True)
        return

    embed = discord.Embed(title="🎁 Level Role Rewards", color=discord.Color.gold())
    description = "\n".join(f"**Level {lvl}:** <@&{role_id}>" for lvl, role_id in sorted(level_rewards.items(), key=lambda item: int(item[0])))
    embed.description = description
    await interaction.response.send_message(embed=embed)

# --- More Utility & Fun Commands ---
@tree.command(name="remindme", description="Sets a personal reminder. [Everyone]", guild=GUILD)
@app_commands.describe(
    time="The time until the reminder (e.g., 10s, 5m, 1h, 1d).",
    reminder="What you want to be reminded of."
)
async def remindme(interaction: discord.Interaction, time: str, reminder: str):
    """Sets a reminder for the user that will be sent in DMs."""
    seconds = 0
    if time.lower().endswith('d'):
        seconds += int(time[:-1]) * 60 * 60 * 24
    elif time.lower().endswith('h'):
        seconds += int(time[:-1]) * 60 * 60
    elif time.lower().endswith('m'):
        seconds += int(time[:-1]) * 60
    elif time.lower().endswith('s'):
        seconds += int(time[:-1])

    if seconds == 0:
        await interaction.response.send_message("❌ Invalid time format. Use `s`, `m`, `h`, or `d`.", ephemeral=True)
        return

    await interaction.response.send_message(f"✅ Got it! I'll remind you about `{reminder}` in {time}.", ephemeral=True)
    await asyncio.sleep(seconds)

    try:
        embed = discord.Embed(title="⏰ Reminder!", description=reminder, color=discord.Color.yellow())
        await interaction.user.send(embed=embed)
    except discord.Forbidden:
        await interaction.channel.send(f"Hey {interaction.user.mention}, your reminder for `{reminder}` is up, but I couldn't DM you!")

@tree.command(name="afk", description="Set or remove your AFK status. [Everyone]", guild=GUILD)
@app_commands.describe(status="Your AFK message (leave blank to remove AFK).")
async def afk(interaction: discord.Interaction, status: Optional[str] = None):
    """Sets or removes a user's AFK status."""
    user_id = interaction.user.id
    if status is None:
        if user_id in afk_users:
            del afk_users[user_id]
            await interaction.response.send_message("✅ Welcome back! Your AFK status has been removed.", ephemeral=True)
        else:
            await interaction.response.send_message("❌ You are not currently AFK.", ephemeral=True)
    else:
        afk_users[user_id] = {"message": status, "timestamp": datetime.datetime.now(datetime.timezone.utc)}
        await interaction.response.send_message(f"✅ You are now AFK. Reason: `{status}`", ephemeral=True)

@tree.command(name="coinflip", description="Flips a coin. [Everyone]", guild=GUILD)
async def coinflip(interaction: discord.Interaction):
    """Flips a coin and shows the result."""
    result = random.choice(["Heads", "Tails"])
    emoji = "👑" if result == "Heads" else "🪙"
    embed = discord.Embed(title="🪙 Coin Flip", description=f"The coin landed on... **{result}**! {emoji}", color=discord.Color.gold())
    await interaction.response.send_message(embed=embed)

@tree.command(name="hug", description="Give someone a hug. [Everyone]", guild=GUILD)
@app_commands.describe(member="The person you want to hug.")
async def hug(interaction: discord.Interaction, member: discord.Member):
    await interaction_command(interaction, member, "hug", "🤗", discord.Color.pink())

@tree.command(name="pat", description="Give someone a pat on the head. [Everyone]", guild=GUILD)
@app_commands.describe(member="The person you want to pat.")
async def pat(interaction: discord.Interaction, member: discord.Member):
    await interaction_command(interaction, member, "pat", "❤️", discord.Color.light_grey())

@tree.command(name="slap", description="Slap someone. [Everyone]", guild=GUILD)
@app_commands.describe(member="The person you want to slap.")
async def slap(interaction: discord.Interaction, member: discord.Member):
    await interaction_command(interaction, member, "slap", "👋", discord.Color.dark_red())

@tree.command(name="fact", description="Get a random interesting fact. [Everyone]", guild=GUILD)
async def fact(interaction: discord.Interaction):
    """Fetches a random fact from an API."""
    await interaction.response.defer()
    async with aiohttp.ClientSession() as session:
        async with session.get("https://uselessfacts.jsph.pl/random.json?language=en") as response:
            if response.status == 200:
                data = await response.json()
                embed = discord.Embed(title="🧠 Did You Know?", description=data['text'], color=discord.Color.blue())
                await interaction.followup.send(embed=embed)
            else:
                await interaction.followup.send("❌ Could not fetch a fact right now.", ephemeral=True)

@tree.command(name="stopwatch", description="A simple stopwatch. [Everyone]", guild=GUILD)
async def stopwatch(interaction: discord.Interaction):
    """Starts an interactive stopwatch."""
    start_time = datetime.datetime.now()
    embed = discord.Embed(title="⏱️ Stopwatch Started", description="Click the button to stop.", color=discord.Color.green())
    
    class StopwatchView(View):
        @discord.ui.button(label="Stop", style=discord.ButtonStyle.red)
        async def stop(self, interaction: discord.Interaction, button: Button):
            end_time = datetime.datetime.now()
            duration = end_time - start_time
            stop_embed = discord.Embed(title="⏱️ Stopwatch Stopped", description=f"Elapsed time: **{str(duration).split('.')[0]}**", color=discord.Color.red())
            await interaction.response.edit_message(embed=stop_embed, view=None)

    await interaction.response.send_message(embed=embed, view=StopwatchView())

@tree.command(name="timer", description="Starts a countdown timer. [Everyone]", guild=GUILD)
@app_commands.describe(time="Duration for the timer (e.g., 10s, 5m, 1h).")
async def timer(interaction: discord.Interaction, time: str):
    """Starts a timer and pings the user when it's done."""
    seconds = 0
    if time.lower().endswith('h'):
        seconds += int(time[:-1]) * 3600
    elif time.lower().endswith('m'):
        seconds += int(time[:-1]) * 60
    elif time.lower().endswith('s'):
        seconds += int(time[:-1])

    if seconds == 0 or seconds > 86400: # Max 24 hours
        await interaction.response.send_message("❌ Invalid time format or duration too long. Use `s`, `m`, `h` (max 24h).", ephemeral=True)
        return

    await interaction.response.send_message(f"⏳ Timer set for **{time}**!")
    await asyncio.sleep(seconds)
    await interaction.channel.send(f"⏰ Time's up, {interaction.user.mention}!")

@tree.command(name="urban", description="Look up a word on Urban Dictionary. [Everyone]", guild=GUILD)
@app_commands.describe(term="The word or phrase to look up.")
async def urban(interaction: discord.Interaction, term: str):
    """Fetches a definition from Urban Dictionary."""
    if not interaction.channel.is_nsfw():
        await interaction.response.send_message("❌ This command can only be used in NSFW channels.", ephemeral=True)
        return

    await interaction.response.defer()
    async with aiohttp.ClientSession() as session:
        async with session.get(f"http://api.urbandictionary.com/v0/define?term={term}") as response:
            if response.status != 200:
                await interaction.followup.send("❌ Could not fetch a definition.", ephemeral=True)
                return
            
            data = await response.json()
            if not data['list']:
                await interaction.followup.send(f"❌ No definition found for **{term}**.", ephemeral=True)
                return

            result = data['list'][0]
            definition = result['definition'].replace('[', '').replace(']', '')
            embed = discord.Embed(title=f"📖 Urban Dictionary: {result['word']}", url=result['permalink'], color=discord.Color.dark_blue())
            embed.description = (definition[:2045] + '...') if len(definition) > 2048 else definition
            embed.add_field(name="Example", value=result['example'].replace('[', '').replace(']', ''), inline=False)
            embed.set_footer(text=f"👍 {result['thumbs_up']} | 👎 {result['thumbs_down']}")
            await interaction.followup.send(embed=embed)

@tree.command(name="truth", description="Asks a random truth question. [Everyone]", guild=GUILD)
async def truth(interaction: discord.Interaction):
    """Sends a random truth question."""
    questions = [
        "What's the most embarrassing thing you've ever done?",
        "What's a secret you've never told anyone?",
        "What's your biggest fear?",
        "Who is your secret crush?",
        "What's the last lie you told?",
        "What's the most childish thing you still do?",
    ]
    embed = discord.Embed(title="🤔 Truth", description=random.choice(questions), color=discord.Color.light_grey())
    await interaction.response.send_message(embed=embed)

@tree.command(name="dare", description="Gives a random dare. [Everyone]", guild=GUILD)
async def dare(interaction: discord.Interaction):
    """Sends a random dare."""
    dares = [
        "Send a DM to the last person you talked to, saying 'I know your secret'.",
        "Change your profile picture to a picture of a potato for 24 hours.",
        "Speak in rhymes for the next 10 minutes.",
        "Post a selfie in the general chat.",
        "Let the person who dared you post a status on your behalf.",
        "Talk in a different accent for the next 5 minutes.",
    ]
    embed = discord.Embed(title="😈 Dare", description=random.choice(dares), color=discord.Color.dark_red())
    await interaction.response.send_message(embed=embed)

@tree.command(name="spinbottle", description="Spin the bottle to pick a random user. [Everyone]", guild=GUILD)
async def spinbottle(interaction: discord.Interaction):
    """Picks a random online user from the current channel."""
    online_members = [
        member for member in interaction.channel.members 
        if not member.bot and member.status != discord.Status.offline
    ]
    if not online_members:
        await interaction.response.send_message("❌ No one else is online in this channel to spin the bottle with!", ephemeral=True)
        return

    chosen_one = random.choice(online_members)
    embed = discord.Embed(
        title="🍾 Spin the Bottle",
        description=f"The bottle spins... and it lands on {chosen_one.mention}!",
        color=discord.Color.green()
    )
    await interaction.response.send_message(embed=embed)

@tree.command(name="serverage", description="Shows how old the server is. [Everyone]", guild=GUILD)
async def serverage(interaction: discord.Interaction):
    """Displays the age of the server."""
    age = datetime.datetime.now(datetime.timezone.utc) - interaction.guild.created_at
    embed = discord.Embed(
        title="🎂 Server Age",
        description=f"This server was created on {discord.utils.format_dt(interaction.guild.created_at, style='F')}.\nThat was **{age.days}** days ago!",
        color=discord.Color.blue()
    )
    await interaction.response.send_message(embed=embed)

@tree.command(name="accountage", description="Shows how old a user's account is. [Everyone]", guild=GUILD)
@app_commands.describe(user="The user to check (defaults to you).")
async def accountage(interaction: discord.Interaction, user: Optional[discord.Member] = None):
    """Displays the age of a user's Discord account."""
    target_user = user or interaction.user
    age = datetime.datetime.now(datetime.timezone.utc) - target_user.created_at
    embed = discord.Embed(
        title=f"🎂 Account Age for {target_user.display_name}",
        description=f"This account was created on {discord.utils.format_dt(target_user.created_at, style='F')}.\nThat was **{age.days}** days ago!",
        color=target_user.color
    )
    await interaction.response.send_message(embed=embed)

@tree.command(name="countdown", description="Countdown to a specific date. [Everyone]", guild=GUILD)
@app_commands.describe(date="The date to count down to (YYYY-MM-DD).", event="The name of the event.")
async def countdown(interaction: discord.Interaction, date: str, event: str):
    """Calculates the time remaining until a given date."""
    try:
        target_date = datetime.datetime.strptime(date, "%Y-%m-%d").replace(tzinfo=datetime.timezone.utc)
        now = datetime.datetime.now(datetime.timezone.utc)
        if now > target_date:
            await interaction.response.send_message("❌ The date is in the past!", ephemeral=True)
            return
        
        delta = target_date - now
        embed = discord.Embed(
            title=f"⏳ Countdown to {event}",
            description=f"There are **{delta.days} days** remaining until {event}!\n({date})",
            color=discord.Color.purple()
        )
        await interaction.response.send_message(embed=embed)
    except ValueError:
        await interaction.response.send_message("❌ Invalid date format. Please use `YYYY-MM-DD`.", ephemeral=True)

@tree.command(name="calendar", description="Shows a calendar for a given month and year. [Everyone]", guild=GUILD)
@app_commands.describe(month="The month (1-12, defaults to current).", year="The year (defaults to current).")
async def calendar_command(interaction: discord.Interaction, month: Optional[int] = None, year: Optional[int] = None):
    """Displays a simple text-based calendar."""
    now = datetime.datetime.now()
    _month = month or now.month
    _year = year or now.year
    cal_text = calendar.month(_year, _month)
    embed = discord.Embed(title=f"📅 Calendar for {calendar.month_name[_month]} {_year}", description=f"```\n{cal_text}\n```", color=discord.Color.dark_grey())
    await interaction.response.send_message(embed=embed)

@tree.command(name="feedback", description="Send feedback directly to the bot owner. [Everyone]", guild=GUILD)
@app_commands.describe(message="Your feedback message.")
async def feedback(interaction: discord.Interaction, message: str):
    """Sends a feedback message to the bot owner via DM."""
    owner = await bot.fetch_user(int(OWNER_ID))
    if not owner:
        await interaction.response.send_message("❌ Could not find the bot owner.", ephemeral=True)
        return
    
    embed = discord.Embed(title="📬 New Feedback Received", description=message, color=discord.Color.orange())
    embed.set_author(name=f"From: {interaction.user.display_name} ({interaction.user.id})", icon_url=interaction.user.display_avatar.url)
    await owner.send(embed=embed)
    await interaction.response.send_message("✅ Your feedback has been sent to the bot owner. Thank you!", ephemeral=True)

@tree.command(name="botinvite", description="Get an invite link for the bot. [Everyone]", guild=GUILD)
async def botinvite(interaction: discord.Interaction):
    """Generates a basic, no-permission invite link for the bot."""
    invite_url = discord.utils.oauth_url(bot.user.id, permissions=discord.Permissions(permissions=0))
    await interaction.response.send_message(f"Here is a basic invite link for me:\n<{invite_url}>", ephemeral=True)

# --- Role Menu System Commands ---
@tree.command(name="setupuserroles", description="Sets up the user roles panel. [Staff Only]", guild=GUILD)
@app_commands.describe(channel="The channel where the panel should be placed.")
async def setupuserroles(interaction: discord.Interaction, channel: discord.TextChannel):
    if not check_if_staff(interaction):
        await interaction.response.send_message("You don't have the right permissions to use this command!", ephemeral=True)
        return

    embed = discord.Embed(
        title="🎨 Custom User Roles",
        description="Enhance your server experience by choosing roles that represent you! These roles let others know what platforms you use, your favorite game genres, and which specific games you enjoy.\n\nClick the button below to get started and connect with like-minded players!",
        color=discord.Color.green()
    )
    await channel.send(embed=embed, view=RoleMenuSetupView())
    await interaction.response.send_message(f"✅ The role panel has been successfully set up in {channel.mention}.", ephemeral=True)

@rolemenu_group.command(name="addcategory", description="Adds a new category to the role menu. [Staff Only]")
@app_commands.describe(name="The unique internal name for the category (e.g., 'new_games').", placeholder="The text shown in the dropdown (e.g., 'Choose a new game...').", max_choices="Maximum number of roles a user can select from this category.")
async def rolemenu_addcategory(interaction: discord.Interaction, name: str, placeholder: str, max_choices: int = 1):
    if not check_if_staff(interaction):
        await interaction.response.send_message("You don't have the right permissions to use this command!", ephemeral=True)
        return

    name = name.lower().replace(" ", "_")
    if name in role_menu_data:
        await interaction.response.send_message(f"❌ A category with the name `{name}` already exists.", ephemeral=True)
        return

    role_menu_data[name] = {
        "placeholder": placeholder,
        "max_values": max_choices,
        "roles": {}
    }
    save_json(ROLE_MENU_FILE, role_menu_data)
    await interaction.response.send_message(f"✅ Category `{name}` has been created.", ephemeral=True)

@rolemenu_group.command(name="removecategory", description="Removes a category from the role menu. [Staff Only]")
@app_commands.describe(category="The category to remove.")
async def rolemenu_removecategory(interaction: discord.Interaction, category: str):
    if not check_if_staff(interaction):
        await interaction.response.send_message("You don't have the right permissions to use this command!", ephemeral=True)
        return

    if category not in role_menu_data:
        await interaction.response.send_message(f"❌ Category `{category}` not found.", ephemeral=True)
        return

    del role_menu_data[category]
    save_json(ROLE_MENU_FILE, role_menu_data)
    await interaction.response.send_message(f"✅ Category `{category}` has been removed.", ephemeral=True)

@rolemenu_group.command(name="addrole", description="Adds a role to a category in the role menu. [Staff Only]")
@app_commands.describe(category="The category to add the role to.", role="The role to add.", label="The text to display for this role.", emoji="The emoji for this role (optional).")
async def rolemenu_addrole(interaction: discord.Interaction, category: str, role: discord.Role, label: str, emoji: Optional[str] = None):
    if not check_if_staff(interaction):
        await interaction.response.send_message("You don't have the right permissions to use this command!", ephemeral=True)
        return

    if category not in role_menu_data:
        await interaction.response.send_message(f"❌ Category `{category}` not found.", ephemeral=True)
        return

    role_id_str = str(role.id)
    role_menu_data[category]["roles"][role_id_str] = {"label": label, "emoji": emoji}
    save_json(ROLE_MENU_FILE, role_menu_data)
    await interaction.response.send_message(f"✅ Role {role.mention} has been added to the `{category}` category.", ephemeral=True)

@rolemenu_group.command(name="removerole", description="Removes a role from a category in the role menu. [Staff Only]")
@app_commands.describe(category="The category to remove the role from.", role="The role to remove.")
async def rolemenu_removerole(interaction: discord.Interaction, category: str, role: discord.Role):
    if not check_if_staff(interaction):
        await interaction.response.send_message("You don't have the right permissions to use this command!", ephemeral=True)
        return

    if category not in role_menu_data:
        await interaction.response.send_message(f"❌ Category `{category}` not found.", ephemeral=True)
        return

    role_id_str = str(role.id)
    if role_id_str not in role_menu_data[category]["roles"]:
        await interaction.response.send_message(f"❌ Role {role.mention} is not in the `{category}` category.", ephemeral=True)
        return

    del role_menu_data[category]["roles"][role_id_str]
    save_json(ROLE_MENU_FILE, role_menu_data)
    await interaction.response.send_message(f"✅ Role {role.mention} has been removed from the `{category}` category.", ephemeral=True)

@rolemenu_group.command(name="reordercategory", description="Changes the order of a category in the role menu. [Staff Only]")
@app_commands.describe(category="The category to move.", position="The new position (1 is the first).")
async def rolemenu_reordercategory(interaction: discord.Interaction, category: str, position: int):
    if not check_if_staff(interaction):
        await interaction.response.send_message("You don't have the right permissions to use this command!", ephemeral=True)
        return

    if category not in role_menu_data:
        await interaction.response.send_message(f"❌ Category `{category}` not found.", ephemeral=True)
        return

    if not 1 <= position <= len(role_menu_data):
        await interaction.response.send_message(f"❌ Position must be between 1 and {len(role_menu_data)}.", ephemeral=True)
        return

    # Convert dict to list of items to preserve order
    items = list(role_menu_data.items())
    
    # Find the index of the category to move
    current_index = next((i for i, (key, _) in enumerate(items) if key == category), -1)
            
    # Pop the item from its current position
    item_to_move = items.pop(current_index)
    
    # Insert it at the new position (adjusting for 0-based index)
    items.insert(position - 1, item_to_move)
    
    # Create a new ordered dictionary and save it
    role_menu_data.clear()
    role_menu_data.update(items)
    save_json(ROLE_MENU_FILE, role_menu_data)
    await interaction.response.send_message(f"✅ Category `{category}` has been moved to position {position}.", ephemeral=True)

@rolemenu_group.command(name="view", description="View the current role menu configuration. [Staff Only]")
async def rolemenu_view(interaction: discord.Interaction):
    if not check_if_staff(interaction):
        await interaction.response.send_message("You don't have the right permissions to use this command!", ephemeral=True)
        return

    embed = discord.Embed(title="🎨 Role Menu Configuration", color=discord.Color.blurple())
    if not role_menu_data:
        embed.description = "The role menu is currently empty."
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    for category, details in role_menu_data.items():
        field_value = f"**Placeholder:** `{details['placeholder']}`\n**Max Choices:** `{details['max_values']}`\n**Roles:**\n"
        if not details['roles']:
            field_value += "  *No roles in this category.*"
        else:
            for role_id, role_details in details['roles'].items():
                role = interaction.guild.get_role(int(role_id))
                emoji_str = f"{role_details['emoji']} " if role_details.get('emoji') else ''
                field_value += f"  {emoji_str}`{role_details['label']}` - {role.mention if role else 'Unknown Role'}\n"
        embed.add_field(name=f"Category: `{category}`", value=field_value, inline=False)

    await interaction.response.send_message(embed=embed, ephemeral=True)

@rolemenu_removecategory.autocomplete('category')
@rolemenu_addrole.autocomplete('category')
@rolemenu_removerole.autocomplete('category')
@rolemenu_reordercategory.autocomplete('category')
async def rolemenu_category_autocomplete(interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
    categories = list(role_menu_data.keys())
    return [
        app_commands.Choice(name=category, value=category)
        for category in categories if current.lower() in category.lower()
    ]

# =============================================================================
# 7. BOT EVENTS
# =============================================================================

@bot.event
async def on_ready():
    """Runs when the bot successfully connects and shows stats in the terminal."""
    # Add persistent views
    bot.add_view(TicketCreationView()) # For the create button
    bot.add_view(TicketControlsView()) # For the close button
    bot.add_view(ClosedTicketView())   # For the re-open button
    bot.add_view(VerificationView()) # For the public verification button
    bot.add_view(RoleMenuSetupView()) # For the role menu button
    tree.add_command(rolemenu_group, guild=GUILD)
    tree.add_command(note_group, guild=GUILD)
    tree.add_command(setxp_group, guild=GUILD)
    tree.add_command(bank_group, guild=GUILD)
    tree.add_command(tag_group, guild=GUILD)

    # Sync the commands to the specific guild
    synced = await tree.sync(guild=GUILD)
    print("==============================================")
    print(f"✅ Bot logged in as: {bot.user} (ID: {bot.user.id})")
    print(f"🐍 Python Version: {platform.python_version()}")
    print(f"🔗 Synced {len(synced)} commands to Guild: {GUILD_ID}")
    print("==============================================")

    # Send startup message to the designated channel
    startup_channel = bot.get_channel(STARTUP_LOG_CHANNEL_ID)
    if startup_channel:
        total_users = sum(guild.member_count for guild in bot.guilds)
        embed = discord.Embed(
            title="✅ Bot Online & Ready!",
            description="All systems are operational.",
            color=discord.Color.green(),
            timestamp=datetime.datetime.now(datetime.timezone.utc)
        )
        embed.set_thumbnail(url=bot.user.display_avatar.url)
        embed.add_field(name="Synced Commands", value=str(len(synced)), inline=True)
        embed.add_field(name="Total Users", value=str(total_users), inline=True)
        embed.add_field(name="Python Version", value=platform.python_version(), inline=False)
        embed.set_footer(text=f"{bot.user.name} | Version 1.0.0")
        await startup_channel.send(embed=embed)
    else:
        print(f"WARNING: Startup log channel with ID {STARTUP_LOG_CHANNEL_ID} not found.")

@bot.event
async def on_message(message: discord.Message):
    """Processes every message to track stats."""
    # Ignore bots and DMs
    if message.author.bot or not message.guild:
        return

    # --- AFK System Logic ---
    if message.author.id in afk_users:
        del afk_users[message.author.id]
        await message.channel.send(f"Welcome back, {message.author.mention}! I've removed your AFK status.", delete_after=10)

    for mentioned_user in message.mentions:
        if mentioned_user.id in afk_users:
            afk_data = afk_users[mentioned_user.id]
            await message.reply(f"{mentioned_user.display_name} is AFK: `{afk_data['message']}` ({discord.utils.format_dt(afk_data['timestamp'], style='R')})")

    # Track user message counts
    user_id = message.author.id
    message_counts[user_id] = message_counts.get(user_id, 0) + 1

    # Track custom emoji usage
    for emoji in message.guild.emojis:
        if str(emoji) in message.content:
            emoji_counts[emoji.id] = emoji_counts.get(emoji.id, 0) + 1

    # --- Leveling System Logic ---
    user_id = message.author.id
    user_id_str = str(user_id)
    current_time = datetime.datetime.now(datetime.timezone.utc)

    # Check cooldown (e.g., 60 seconds)
    last_message_time = xp_cooldowns.get(user_id)
    if last_message_time and (current_time - last_message_time).total_seconds() < 60:
        return # Don't process XP, but also don't process prefix commands as there are none.

    xp_cooldowns[user_id] = current_time

    # Grant XP
    xp_to_add = random.randint(15, 25)
    if user_id_str not in leveling_data:
        leveling_data[user_id_str] = {"level": 0, "xp": 0}
    
    leveling_data[user_id_str]["xp"] += xp_to_add

    # Check for level up
    # Check for level up and handle multiple level-ups at once
    current_level = leveling_data[user_id_str]["level"]
    xp_needed = xp_for_level(current_level)
    if leveling_data[user_id_str]["xp"] >= xp_needed:
        leveling_data[user_id_str]["level"] += 1
        leveling_data[user_id_str]["xp"] -= xp_needed # Carry over extra XP
        new_level = leveling_data[user_id_str]["level"]
        await message.channel.send(f"🎉 Congratulations {message.author.mention}, you just reached **Level {new_level}**!")
        # Check for role rewards
        new_level_str = str(new_level)
        if new_level_str in level_rewards:
            role_id = level_rewards[new_level_str]
            role = message.guild.get_role(role_id)
            if role:
                try:
                    await message.author.add_roles(role, reason=f"Reached Level {new_level}")
                    await message.channel.send(f"🎁 As a reward, you've received the **{role.name}** role!")
                except discord.Forbidden:
                    print(f"Failed to add role {role.name} to {message.author.name}. Missing permissions.")

    save_json(LEVELING_FILE, leveling_data)

@bot.event
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    """A global error handler for all slash commands."""
    # Create a standardized error embed
    error_embed = discord.Embed(
        title="❌ Command Error",
        color=discord.Color.red()
    )

    if isinstance(error, app_commands.CheckFailure):
        # This is the most common error for permission issues with is_staff() or is_owner()
        # We need to respond quickly to avoid the "Application did not respond" error.
        # Creating an embed can sometimes be slow, so we send a simple message first if needed.
        if not interaction.response.is_done():
            error_embed.title = "🔒 Permission Denied"
            error_embed.description = "You don't have the right permissions to use this command!\nPlease use `/commands` to see which commands you can use."
            await interaction.response.send_message(embed=error_embed, ephemeral=True)

    elif isinstance(error, app_commands.CommandOnCooldown):
        # Handle commands that are on cooldown
        error_embed.title = "⏳ Command on Cooldown"
        error_embed.description = f"This command is on cooldown. Please try again in **{error.retry_after:.2f} seconds**."
        await interaction.response.send_message(embed=error_embed, ephemeral=True)

    else:
        # For all other errors, log them and give a generic response
        print(f"An unhandled error occurred in command '{interaction.command.name}': {error}")
        error_embed.description = "An unexpected error occurred while running this command. The issue has been logged."
        if not interaction.response.is_done():
            await interaction.response.send_message(embed=error_embed, ephemeral=True)

# =================================================================
# --- Economy System Commands ---
@tree.command(name="balance", description="Check your or another user's coin balance. [Everyone]", guild=GUILD)
@app_commands.describe(user="The user whose balance you want to see (optional).")
async def balance(interaction: discord.Interaction, user: Optional[discord.Member] = None):
    """Shows the coin balance for a user."""
    target_user = user or interaction.user
    user_id_str = str(target_user.id)
    wallet_bal = economy_data.get(user_id_str, {}).get("balance", 0)
    bank_bal = economy_data.get(user_id_str, {}).get("bank", 0)
    
    embed = discord.Embed(
        title=f"💰 Wallet Balance for {target_user.display_name}",
        color=discord.Color.gold()
    )
    embed.add_field(name="Wallet", value=f"{wallet_bal} coins", inline=True)
    embed.add_field(name="Bank", value=f"{bank_bal} coins", inline=True)
    await interaction.response.send_message(embed=embed)

@tree.command(name="daily", description="Claim your daily coins. [Everyone]", guild=GUILD)
async def daily(interaction: discord.Interaction):
    """Gives the user their daily coin reward."""
    user_id_str = str(interaction.user.id)
    
    # Initialize user data if not present
    economy_data.setdefault(user_id_str, {"balance": 0, "bank": 0, "last_daily": None})

    last_daily_str = economy_data[user_id_str].get("last_daily")
    
    # Check cooldown (22 hours)
    if last_daily_str:
        last_daily_time = datetime.datetime.fromisoformat(last_daily_str)
        if datetime.datetime.now(datetime.timezone.utc) < last_daily_time + datetime.timedelta(hours=22):
            time_remaining = (last_daily_time + datetime.timedelta(hours=22)) - datetime.datetime.now(datetime.timezone.utc)
            hours, remainder = divmod(int(time_remaining.total_seconds()), 3600)
            minutes, _ = divmod(remainder, 60)
            await interaction.response.send_message(f"❌ You've already claimed your daily reward! Try again in **{hours}h {minutes}m**.", ephemeral=True)
            return

    daily_amount = random.randint(100, 500)
    economy_data[user_id_str]["balance"] = economy_data[user_id_str].get("balance", 0) + daily_amount
    economy_data[user_id_str]["last_daily"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    save_json(ECONOMY_FILE, economy_data)

    embed = discord.Embed(
        title="🎉 Daily Reward Claimed!",
        description=f"You received **{daily_amount}** coins! Your new balance is **{economy_data[user_id_str]['balance']}** coins.",
        color=discord.Color.green()
    )
    await interaction.response.send_message(embed=embed)

@tree.command(name="give", description="Give coins to another user. [Everyone]", guild=GUILD)
@app_commands.describe(user="The user to give coins to.", amount="The amount of coins to give.")
async def give(interaction: discord.Interaction, user: discord.Member, amount: int):
    """Transfers coins from one user to another."""
    if amount <= 0:
        await interaction.response.send_message("❌ You must give a positive amount of coins.", ephemeral=True)
        return
    if user.id == interaction.user.id:
        await interaction.response.send_message("❌ You can't give coins to yourself.", ephemeral=True)
        return

    sender_id_str = str(interaction.user.id)
    receiver_id_str = str(user.id)

    sender_balance = get_user_balance(interaction.user.id)

    if sender_balance < amount:
        await interaction.response.send_message(f"❌ You don't have enough coins! You only have **{sender_balance}** coins.", ephemeral=True)
        return

    # Update balances
    economy_data.setdefault(sender_id_str, {"balance": 0})["balance"] -= amount
    economy_data.setdefault(receiver_id_str, {"balance": 0})["balance"] += amount
    save_json(ECONOMY_FILE, economy_data)

    await interaction.response.send_message(f"✅ You have successfully given **{amount}** coins to {user.mention}!")

@tree.command(name="leaderboard", description="Shows the richest users in the server. [Everyone]", guild=GUILD)
async def leaderboard(interaction: discord.Interaction):
    """Displays the top 10 richest users."""
    sorted_users = sorted(economy_data.items(), key=lambda item: item[1].get('balance', 0), reverse=True)

    embed = discord.Embed(title="🏆 Coin Leaderboard", description="The richest users in the server!", color=discord.Color.gold())

    leaderboard_text = ""
    for i, (user_id, data) in enumerate(sorted_users[:10], 1):
        user = interaction.guild.get_member(int(user_id)) # This might be slow on huge servers
        if user:
            leaderboard_text += f"**{i}.** {user.mention}: **{data.get('balance', 0)}** coins\n"
    
    if not leaderboard_text:
        embed.description = "The economy is just starting. No one is on the leaderboard yet!"
    else:
        embed.description = leaderboard_text

    await interaction.response.send_message(embed=embed)

@tree.command(name="gamble", description="Gamble your coins for a chance to double them! [Everyone]", guild=GUILD)
@app_commands.describe(amount="The amount of coins to gamble.")
async def gamble(interaction: discord.Interaction, amount: int):
    """Allows a user to gamble their coins."""
    if amount <= 0:
        await interaction.response.send_message("❌ You must gamble a positive amount.", ephemeral=True)
        return

    user_id_str = str(interaction.user.id)
    user_balance = economy_data.get(user_id_str, {}).get("balance", 0)

    if amount > user_balance:
        await interaction.response.send_message(f"❌ You can't gamble more than you have! Your balance is **{user_balance}** coins.", ephemeral=True)
        return

    economy_data.setdefault(user_id_str, {"balance": 0, "bank": 0})

    if random.choice([True, False]): # 50/50 chance
        economy_data[user_id_str]["balance"] += amount
        await interaction.response.send_message(f"🎉 **You won!** You doubled your bet and won **{amount}** coins! Your new balance is **{economy_data[user_id_str]['balance']}**.")
    else:
        economy_data[user_id_str]["balance"] -= amount
        await interaction.response.send_message(f"😢 **You lost!** You lost **{amount}** coins. Your new balance is **{economy_data[user_id_str]['balance']}**.")
    
    save_json(ECONOMY_FILE, economy_data)

@tree.command(name="invest", description="Invest your coins with a chance of profit or loss. [Everyone]", guild=GUILD)
@app_commands.describe(amount="The amount of coins to invest.")
async def invest(interaction: discord.Interaction, amount: int):
    """Allows a user to invest coins, which will resolve after 24 hours."""
    if amount <= 0:
        await interaction.response.send_message("❌ You must invest a positive amount.", ephemeral=True)
        return

    user_id_str = str(interaction.user.id)
    user_balance = economy_data.get(user_id_str, {}).get("balance", 0)

    if amount > user_balance:
        await interaction.response.send_message(f"❌ You can't invest more than you have! Your balance is **{user_balance}** coins.", ephemeral=True)
        return

    # Take the money now
    economy_data.setdefault(user_id_str, {"balance": 0, "bank": 0})["balance"] -= amount
    save_json(ECONOMY_FILE, economy_data)

    await interaction.response.send_message(f"📈 You have invested **{amount}** coins. Check back in 24 hours to see the result!", ephemeral=True)

    # Wait 24 hours
    await asyncio.sleep(24 * 60 * 60)

    # Determine outcome
    # Higher chance to win a small amount, lower chance to win big or lose big
    outcome_roll = random.random() # 0.0 to 1.0
    if outcome_roll <= 0.05: # 5% chance to lose it all
        payout = 0
        result_message = f"📉 **Disaster!** Your investment of **{amount}** coins was a total loss."
    elif outcome_roll <= 0.25: # 20% chance to lose a portion
        payout = int(amount * random.uniform(0.5, 0.9))
        result_message = f"📉 **Bad Investment!** Your **{amount}** coins returned only **{payout}** coins."
    elif outcome_roll <= 0.85: # 60% chance for a modest gain
        payout = int(amount * random.uniform(1.01, 1.5))
        result_message = f"📈 **Good Investment!** Your **{amount}** coins grew to **{payout}** coins!"
    else: # 15% chance for a big gain
        payout = int(amount * random.uniform(1.5, 2.5))
        result_message = f"🚀 **Excellent Investment!** Your **{amount}** coins skyrocketed to **{payout}** coins!"

    # Give the payout
    economy_data.setdefault(user_id_str, {"balance": 0})["balance"] += payout
    save_json(ECONOMY_FILE, economy_data)

    await interaction.user.send(f"**Investment Update:**\n{result_message}\nYour new balance is **{get_user_balance(interaction.user.id)}** coins.")
    
@bank_group.command(name="deposit", description="Deposit coins into your bank account. [Everyone]")
@app_commands.describe(amount="The amount to deposit. Use 'all' to deposit everything.")
async def bank_deposit(interaction: discord.Interaction, amount: str):
    """Deposits coins from wallet to bank."""
    user_id_str = str(interaction.user.id)
    economy_data.setdefault(user_id_str, {"balance": 0, "bank": 0})
    
    wallet_balance = economy_data[user_id_str].get("balance", 0)
    
    if amount.lower() == 'all':
        deposit_amount = wallet_balance
    else:
        try:
            deposit_amount = int(amount)
        except ValueError:
            await interaction.response.send_message("❌ Please enter a valid number or 'all'.", ephemeral=True)
            return

    if deposit_amount <= 0:
        await interaction.response.send_message("❌ You must deposit a positive amount.", ephemeral=True)
        return
    if deposit_amount > wallet_balance:
        await interaction.response.send_message(f"❌ You don't have that many coins in your wallet! You have **{wallet_balance}**.", ephemeral=True)
        return

    economy_data[user_id_str]["balance"] -= deposit_amount
    economy_data[user_id_str]["bank"] += deposit_amount
    save_json(ECONOMY_FILE, economy_data)

    await interaction.response.send_message(f"✅ You have deposited **{deposit_amount}** coins into your bank. Your new bank balance is **{economy_data[user_id_str]['bank']}**.", ephemeral=True)

@bank_group.command(name="withdraw", description="Withdraw coins from your bank account. [Everyone]")
@app_commands.describe(amount="The amount to withdraw. Use 'all' to withdraw everything.")
async def bank_withdraw(interaction: discord.Interaction, amount: str):
    """Withdraws coins from bank to wallet."""
    user_id_str = str(interaction.user.id)
    economy_data.setdefault(user_id_str, {"balance": 0, "bank": 0})

    bank_balance = economy_data[user_id_str].get("bank", 0)

    if amount.lower() == 'all':
        withdraw_amount = bank_balance
    else:
        try:
            withdraw_amount = int(amount)
        except ValueError:
            await interaction.response.send_message("❌ Please enter a valid number or 'all'.", ephemeral=True)
            return

    if withdraw_amount <= 0:
        await interaction.response.send_message("❌ You must withdraw a positive amount.", ephemeral=True)
        return
    if withdraw_amount > bank_balance:
        await interaction.response.send_message(f"❌ You don't have that many coins in your bank! You have **{bank_balance}**.", ephemeral=True)
        return

    economy_data[user_id_str]["bank"] -= withdraw_amount
    economy_data[user_id_str]["balance"] += withdraw_amount
    save_json(ECONOMY_FILE, economy_data)

    await interaction.response.send_message(f"✅ You have withdrawn **{withdraw_amount}** coins from your bank. Your new wallet balance is **{economy_data[user_id_str]['balance']}**.", ephemeral=True)

@tree.command(name="rep", description="Give a reputation point to a helpful user. [Everyone]", guild=GUILD)
@app_commands.describe(user="The user to give reputation to.")
async def rep(interaction: discord.Interaction, user: discord.Member):
    """Gives a reputation point to another user."""
    if user.id == interaction.user.id:
        await interaction.response.send_message("❌ You cannot give reputation to yourself.", ephemeral=True)
        return
    if user.bot:
        await interaction.response.send_message("❌ You cannot give reputation to a bot.", ephemeral=True)
        return

    user_id_str = str(interaction.user.id)
    reputation_data.setdefault(user_id_str, {"last_rep": None})
    
    last_rep_str = reputation_data[user_id_str].get("last_rep")
    if last_rep_str and (datetime.datetime.now(datetime.timezone.utc) < datetime.datetime.fromisoformat(last_rep_str) + datetime.timedelta(hours=24)):
        await interaction.response.send_message("❌ You can only give one reputation point per day.", ephemeral=True)
        return

    target_id_str = str(user.id)
    reputation_data.setdefault(target_id_str, {"score": 0})
    reputation_data[target_id_str]["score"] += 1
    reputation_data[user_id_str]["last_rep"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    save_json(REPUTATION_FILE, reputation_data)

    await interaction.response.send_message(f"✅ You have given a reputation point to {user.mention}! They now have **{reputation_data[target_id_str]['score']}** reputation.")

# --- Tag System Commands ---

@tag_group.command(name="create", description="Create a new tag. [Staff Only]")
@app_commands.describe(name="The name of the tag.", content="The content of the tag. Use '\\n' for new lines.")
async def tag_create(interaction: discord.Interaction, name: str, content: str):
    """Creates a new custom command/tag."""
    if not check_if_staff(interaction):
        await interaction.response.send_message("You don't have the right permissions to use this command!", ephemeral=True)
        return

    tag_name = name.lower()
    if tag_name in tags_data:
        await interaction.response.send_message(f"❌ A tag with the name `{tag_name}` already exists.", ephemeral=True)
        return  
    
    tags_data[tag_name] = content.replace('\\n', '\n')
    save_json(TAGS_FILE, tags_data)
    await interaction.response.send_message(f"✅ Tag `{tag_name}` has been created.", ephemeral=True)
    await log_action(interaction, "Tag Created", f"**Name:** {tag_name}", color=discord.Color.green())

@tag_group.command(name="use", description="Use a tag. [Everyone]")
@app_commands.describe(name="The name of the tag to use.")
async def tag_use(interaction: discord.Interaction, name: str):
    """Uses a tag, posting its content."""
    tag_name = name.lower()
    if tag_name not in tags_data:
        await interaction.response.send_message(f"❌ A tag with the name `{tag_name}` does not exist.", ephemeral=True)
        return
    
    await interaction.response.send_message(tags_data[tag_name])

@tag_group.command(name="edit", description="Edit an existing tag. [Staff Only]")
@app_commands.describe(name="The name of the tag to edit.", new_content="The new content for the tag. Use '\\n' for new lines.")
async def tag_edit(interaction: discord.Interaction, name: str, new_content: str):
    """Edits an existing tag."""
    if not check_if_staff(interaction):
        await interaction.response.send_message("You don't have the right permissions to use this command!", ephemeral=True)
        return

    tag_name = name.lower()
    if tag_name not in tags_data:
        await interaction.response.send_message(f"❌ A tag with the name `{tag_name}` does not exist.", ephemeral=True)
        return
        
    tags_data[tag_name] = new_content.replace('\\n', '\n')
    save_json(TAGS_FILE, tags_data)
    await interaction.response.send_message(f"✅ Tag `{tag_name}` has been updated.", ephemeral=True)
    await log_action(interaction, "Tag Edited", f"**Name:** {tag_name}", color=discord.Color.blue())

@tag_group.command(name="delete", description="Delete a tag. [Staff Only]")
@app_commands.describe(name="The name of the tag to delete.")
async def tag_delete(interaction: discord.Interaction, name: str):
    """Deletes a tag."""
    if not check_if_staff(interaction):
        await interaction.response.send_message("You don't have the right permissions to use this command!", ephemeral=True)
        return

    tag_name = name.lower()
    if tag_name not in tags_data:
        await interaction.response.send_message(f"❌ A tag with the name `{tag_name}` does not exist.", ephemeral=True)
        return
        
    del tags_data[tag_name]
    save_json(TAGS_FILE, tags_data)
    await interaction.response.send_message(f"✅ Tag `{tag_name}` has been deleted.", ephemeral=True)
    await log_action(interaction, "Tag Deleted", f"**Name:** {tag_name}", color=discord.Color.red())

@tag_group.command(name="list", description="List all available tags. [Everyone]")
async def tag_list(interaction: discord.Interaction):
    """Lists all available tags."""
    if not tags_data:
        await interaction.response.send_message("There are no tags configured yet.", ephemeral=True)
        return

    embed = discord.Embed(title="🏷️ Available Tags", color=discord.Color.blurple())
    # Using discord.utils.escape_markdown to prevent issues with tag names
    description = ", ".join(f"`{discord.utils.escape_markdown(tag)}`" for tag in sorted(tags_data.keys()))
    embed.description = description
    await interaction.response.send_message(embed=embed, ephemeral=True)

# --- Owner-Only Commands ---

@tree.command(name="privatemessage", description="Send a private message to a user as the bot. [Owner Only]", guild=GUILD)
@app_commands.describe(
    user="The user to send the message to.",
    message="The content of the message. Use '\\n' for new lines.",
    as_embed="Send the message as an embed.",
    color="The color of the embed (if used)."
)
@app_commands.choices(color=[
    app_commands.Choice(name="Blue", value="blue"),
    app_commands.Choice(name="Red", value="red"),
    app_commands.Choice(name="Green", value="green"),
    app_commands.Choice(name="Orange", value="orange"),
    app_commands.Choice(name="Purple", value="purple"),
    app_commands.Choice(name="Gold", value="gold"),
])
@is_owner()
async def privatemessage(interaction: discord.Interaction, user: discord.Member, message: str, as_embed: bool, color: Optional[app_commands.Choice[str]] = None):
    """Sends a private message to a user. Owner only."""
    formatted_message = message.replace('\\n', '\n')
    
    try:
        if as_embed:
            color_map = {
                "blue": discord.Color.blue(), "red": discord.Color.red(), "green": discord.Color.green(),
                "orange": discord.Color.orange(), "purple": discord.Color.purple(), "gold": discord.Color.gold()
            }
            embed_color = color_map.get(color.value if color else "blue", discord.Color.blue())
            embed = discord.Embed(description=formatted_message, color=embed_color)
            await user.send(embed=embed)
        else:
            await user.send(formatted_message)
        
        await interaction.response.send_message(f"✅ Successfully sent a private message to {user.mention}.", ephemeral=True)
        log_details = f"**Target:** {user.mention}\n**Type:** {'Embed' if as_embed else 'Plain Text'}\n**Content:**\n>>> {formatted_message}"
        await log_action(interaction, "Private Message Sent", log_details, color=discord.Color.dark_purple())

    except discord.Forbidden:
        await interaction.response.send_message(f"❌ Could not send a message to {user.mention}. Their DMs are likely closed.", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"An unexpected error occurred: {e}", ephemeral=True)

@tree.command(name="privatewarn", description="Send a standardized private warning to a user. [Owner Only]", guild=GUILD)
@app_commands.describe(user="The user to warn.", reason="The reason for the warning.")
@is_owner()
async def privatewarn(interaction: discord.Interaction, user: discord.Member, reason: str):
    """Sends a standardized private warning. Owner only."""
    embed = discord.Embed(
        title="⚠️ WARNING",
        description=f"You have received a warning in **{interaction.guild.name}**.",
        color=discord.Color.orange(),
        timestamp=datetime.datetime.now(datetime.timezone.utc)
    )
    embed.add_field(name="Moderator Message", value=reason, inline=False)
    embed.set_footer(text=f"Responsible Moderator: {interaction.user.display_name} | Please check the server rules.")

    try:
        await user.send(embed=embed)
        await interaction.response.send_message(f"✅ Successfully sent a private warning to {user.mention}.", ephemeral=True)
        log_details = f"**Target:** {user.mention}\n**Reason:** {reason}"
        await log_action(interaction, "Private Warning Sent", log_details, color=discord.Color.orange())
    except discord.Forbidden:
        await interaction.response.send_message(f"❌ Could not send a warning to {user.mention}. Their DMs are likely closed.", ephemeral=True)

@tree.command(name="repleaderboard", description="Shows the server's reputation leaderboard. [Everyone]", guild=GUILD)
async def repleaderboard(interaction: discord.Interaction):
    """Displays the top 10 most reputable users."""
    # Filter out users with no score and sort
    valid_users = {uid: data for uid, data in reputation_data.items() if 'score' in data}
    sorted_users = sorted(valid_users.items(), key=lambda item: item[1]['score'], reverse=True)

    embed = discord.Embed(title="🌟 Reputation Leaderboard", description="Most respected members of the community!", color=discord.Color.gold())

    leaderboard_text = ""
    for i, (user_id, data) in enumerate(sorted_users[:10], 1):
        user = interaction.guild.get_member(int(user_id))
        if user:
            leaderboard_text += f"**{i}.** {user.mention}: **{data['score']}** rep\n"

    if not leaderboard_text:
        embed.description = "No one has received any reputation yet. Use `/rep` to start!"
    else:
        embed.description = leaderboard_text
    await interaction.response.send_message(embed=embed)

# =============================================================================
# 8. RUN BOT
# =============================================================================
if __name__ == "__main__":
    bot.run(TOKEN)
