        # main.py
# A modern Discord bot with a preset message command.
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

# =================================================================
# --- CONFIGURATION ---
# Fill in your bot's details below.
# =================================================================

# Bot Token=
TOKEN = "1234"

# Guild ID=
GUILD_ID = 1234 # Your Server/Guild ID

# Log channel ID=
LOG_CHANNEL_ID = 1234 # The channel for moderation logs

# Staff IDs= (These should be role IDs)
STAFF_ROLE_IDS = {
            1234, # The role ID for your staff members
    # You can add more staff role IDs here, separated by commas
}

# Owner ID= (This should be your user ID)
OWNER_ID = 1234 # The user ID of the bot owner

# --- TICKET SYSTEM CONFIG ---
# The ID of the category where new tickets will be created.
TICKET_CATEGORY_ID = 1234
# The ID of the channel where the "Create Ticket" message will be.
TICKET_PANEL_CHANNEL_ID = 1234
# The ID of the channel where new suggestions will be sent.
SUGGESTION_CHANNEL_ID = 1234
# The ID of the role to give to verified members.
VERIFIED_ROLE_ID = 1234
# The ID of the public channel to setup verification in
VERIFICATION_CHANNEL_ID = 1234

# --- PRESET MESSAGES ---
# Add or edit your preset messages here. The key is the number used in the command.
PRESET_MESSAGES = {
    1: "Reminder: Please keep the conversation respectful and follow all server rules.",
    2: "Please do not spam. Further spam will result in a mute.",
    3: "This channel is for English only. Please move your conversation to the appropriate channel.",
    4: "Your ticket has been received. A staff member will be with you shortly.",
    5: "This channel is now in lockdown mode while we perform maintenance.",
    6: "Hello, we have found a rule-breaking message. Please check the <#1375502957432406187> channel.",
}

# --- IN-MEMORY STORAGE ---
start_time = datetime.datetime.now(datetime.timezone.utc)
message_counts = {} # {user_id: count}
emoji_counts = {} # {emoji_id: count}
xp_cooldowns = {} # {user_id: timestamp}
afk_users = {} # {user_id: {"message": str, "timestamp": datetime}}

# =================================================================
# --- BOT SETUP ---
# =================================================================

intents = discord.Intents.default()
intents.members = True # Required to get member information
intents.message_content = True # Required for on_message events (XP, stats)

bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree
GUILD = discord.Object(id=GUILD_ID)

# =================================================================
# --- ECONOMY SYSTEM SETUP ---
# =================================================================
ECONOMY_FILE = "economy_data.json"

def load_economy_data():
    """Loads economy data from the JSON file."""
    if os.path.exists(ECONOMY_FILE):
        with open(ECONOMY_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_economy_data(data):
    """Saves economy data to the JSON file."""
    with open(ECONOMY_FILE, 'w') as f:
        json.dump(data, f, indent=4)

economy_data = load_economy_data()

def get_user_balance(user_id: int) -> int:
    """Gets a user's balance, creating an entry if one doesn't exist."""
    user_id_str = str(user_id)
    return economy_data.get(user_id_str, {}).get("balance", 0)

# =================================================================
# --- LEVELING SYSTEM SETUP ---
# =================================================================
LEVELING_FILE = "leveling_data.json"

def load_leveling_data():
    """Loads leveling data from the JSON file."""
    if os.path.exists(LEVELING_FILE):
        with open(LEVELING_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_leveling_data(data):
    """Saves leveling data to the JSON file."""
    with open(LEVELING_FILE, 'w') as f:
        json.dump(data, f, indent=4)

leveling_data = load_leveling_data()

def xp_for_level(level: int) -> int:
    """Calculates the total XP needed to reach a certain level."""
    # Using a common formula: 5 * (lvl^2) + 50 * lvl + 100
    return 5 * (level ** 2) + (50 * level) + 100

# =================================================================
# --- LEVEL REWARDS SETUP ---
# =================================================================
LEVEL_REWARDS_FILE = "level_rewards.json"

def load_level_rewards():
    """Loads level reward data from the JSON file."""
    if os.path.exists(LEVEL_REWARDS_FILE):
        with open(LEVEL_REWARDS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_level_rewards(data):
    """Saves level reward data to the JSON file."""
    with open(LEVEL_REWARDS_FILE, 'w') as f:
        json.dump(data, f, indent=4)

level_rewards = load_level_rewards()

# =================================================================
# --- TAG SYSTEM SETUP ---
# =================================================================
TAGS_FILE = "tags.json"

def load_tags():
    """Loads tags from the JSON file."""
    if os.path.exists(TAGS_FILE):
        with open(TAGS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_tags(data):
    """Saves tags to the JSON file."""
    with open(TAGS_FILE, 'w') as f:
        json.dump(data, f, indent=4)

tags_data = load_tags()

# =================================================================
# --- WARNINGS SYSTEM SETUP ---
# =================================================================
WARNINGS_FILE = "warnings_data.json"

def load_warnings_data():
    """Loads warnings data from the JSON file."""
    if os.path.exists(WARNINGS_FILE):
        with open(WARNINGS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_warnings_data(data):
    """Saves warnings data to the JSON file."""
    with open(WARNINGS_FILE, 'w') as f:
        json.dump(data, f, indent=4)

warnings_data = load_warnings_data()

# =================================================================
# --- PERMISSION & HELPER FUNCTIONS ---
# =================================================================

def is_staff_or_owner():
    """A decorator to check if the user is the owner or has the staff role."""
    def predicate(interaction: discord.Interaction) -> bool:
        # Check if the user is the bot owner
        if interaction.user.id == int(OWNER_ID):
            return True
        # Check if the user has the staff role
        # The 'interaction.user' object in a slash command is a discord.Member
        return any(role.id in STAFF_ROLE_IDS for role in interaction.user.roles)
    return app_commands.check(predicate)

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

@tree.command(name="testlog", description="test", guild=GUILD)
@is_staff_or_owner()
async def testlog(interaction: discord.Interaction):
    await log_action(interaction, "Test", "This is a test log")

@tree.command(name="about", description="Shows information about the Eltrix bot.", guild=GUILD)
async def about(interaction: discord.Interaction):
    """Displays an embed with information about the bot."""
    embed = discord.Embed(
        title="About Eltrix",
        description="A custom-built, multi-purpose bot designed to manage and entertain your server.",
        color=discord.Color.purple()
    )
    embed.set_thumbnail(url=bot.user.display_avatar.url)
    embed.add_field(name="Version", value="1.0.0", inline=True)
    embed.add_field(name="Creator", value="<@1348019013321490573>", inline=True)
    await interaction.response.send_message(embed=embed)

# =================================================================
# --- SLASH COMMANDS ---
# =================================================================

@tree.command(name="presetmessage", description="Send a preset message by number.", guild=GUILD)
@app_commands.describe(
    number=f"The preset number to send (1-{len(PRESET_MESSAGES)})",
    channel="The channel to send the message in (defaults to current channel).",
    embed="Choose 'Yes' to send as an embed, 'No' for a plain message."
)
@app_commands.choices(embed=[
    app_commands.Choice(name="Yes", value="yes"),
    app_commands.Choice(name="No", value="no"),
])
@is_staff_or_owner()
async def presetmessage(
    interaction: discord.Interaction,
    number: int,
    embed: app_commands.Choice[str],
    channel: Optional[discord.TextChannel] = None
):
    """Sends a predefined message to a channel, either as plain text or an embed."""
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

@presetmessage.error
async def presetmessage_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    """Error handler for the presetmessage command."""
    if isinstance(error, app_commands.CheckFailure):
        await interaction.response.send_message("❌ You do not have the required permissions (Staff/Owner) to use this command.", ephemeral=True)
    else:
        await interaction.response.send_message(f"An error occurred: {error}", ephemeral=True)
        print(f"Error in /presetmessage command: {error}")

@tree.command(name="ping", description="Check the bot's latency.", guild=GUILD)
@is_staff_or_owner()
async def ping(interaction: discord.Interaction):
    """Checks and displays the bot's latency."""
    latency = round(bot.latency * 1000)
    embed = discord.Embed(
        title="🏓 Pong!",
        description=f"My latency is **{latency}ms**.",
        color=discord.Color.green() if latency < 150 else discord.Color.orange()
    )
    await interaction.response.send_message(embed=embed, ephemeral=True)

@tree.command(name="userinfo", description="View information about a user.", guild=GUILD)
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
    embed.add_field(name="Full Name", value=f"{target_member.name}#{target_member.discriminator}", inline=True)
    embed.add_field(name="User ID", value=target_member.id, inline=True)
    embed.add_field(name="Top Role", value=target_member.top_role.mention if target_member.top_role.name != "@everyone" else "None", inline=False)
    embed.add_field(name="Joined Server", value=discord.utils.format_dt(target_member.joined_at, style='R'), inline=True)
    embed.add_field(name="Account Created", value=discord.utils.format_dt(target_member.created_at, style='R'), inline=True)

    await interaction.response.send_message(embed=embed, ephemeral=True)

@tree.command(name="avatar", description="View a user's avatar.", guild=GUILD)
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

@tree.command(name="poll", description="Create a simple poll.", guild=GUILD)
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
        await interaction.channel.send(embed=result_embed)

@tree.command(name="8ball", description="Ask the magic 8-ball a question.", guild=GUILD)
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

@tree.command(name="warn", description="Warns a user and logs the warning.", guild=GUILD)
@app_commands.describe(member="The member to warn.", reason="The reason for the warning.")
@is_staff_or_owner()
async def warn(interaction: discord.Interaction, member: discord.Member, reason: str):
    """Warns a user, sends them a DM, and logs it."""
    if member.bot:
        await interaction.response.send_message("❌ You cannot warn a bot.", ephemeral=True)
        return
    if member.id == interaction.user.id:
        await interaction.response.send_message("❌ You cannot warn yourself.", ephemeral=True)
        return

    # Store the warning
    user_id_str = str(member.id)
    warnings_data.setdefault(user_id_str, []).append(reason)
    save_warnings_data(warnings_data)

    try:
        dm_embed = discord.Embed(title="⚠️ You Have Received a Warning", description=f"You have been warned in **{interaction.guild.name}** for the following reason:\n>>> {reason}", color=discord.Color.orange())
        await member.send(embed=dm_embed)
        dm_status = "They have been notified via DM."
    except discord.Forbidden:
        dm_status = "I could not notify them via DM."

    await interaction.response.send_message(f"✅ {member.mention} has been warned. {dm_status}", ephemeral=True)
    log_details = f"**Target:** {member.mention}\n**Reason:** {reason}"
    await log_action(interaction, "User Warned", log_details, color=discord.Color.orange())

@tree.command(name="warnings", description="View all warnings for a specific user.", guild=GUILD)
@app_commands.describe(member="The member whose warnings you want to see.")
@is_staff_or_owner()
async def warnings(interaction: discord.Interaction, member: discord.Member):
    """Displays a list of warnings for a user."""
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

@tree.command(name="clearwarnings", description="Clears all warnings for a specific user.", guild=GUILD)
@app_commands.describe(member="The member whose warnings you want to clear.")
@is_staff_or_owner()
async def clearwarnings(interaction: discord.Interaction, member: discord.Member):
    """Clears all warnings for a user."""
    user_id_str = str(member.id)
    if user_id_str in warnings_data:
        del warnings_data[user_id_str]
        save_warnings_data(warnings_data)
        await interaction.response.send_message(f"✅ All warnings for {member.mention} have been cleared.", ephemeral=True)
        log_details = f"**Target:** {member.mention}"
        await log_action(interaction, "Warnings Cleared", log_details, color=discord.Color.dark_green())
    else:
        await interaction.response.send_message(f"❌ {member.mention} has no warnings to clear.", ephemeral=True)

@tree.command(name="mute", description="Mutes a member for a specified duration (timeout).", guild=GUILD)
@app_commands.describe(member="The member to mute.", minutes="Duration of the mute in minutes.", reason="The reason for the mute.")
@is_staff_or_owner()
async def mute(interaction: discord.Interaction, member: discord.Member, minutes: int, reason: str):
    """Mutes a member using Discord's timeout feature."""
    if member.top_role >= interaction.user.top_role and interaction.user.id != OWNER_ID:
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

@tree.command(name="unmute", description="Removes the mute (timeout) from a member.", guild=GUILD)
@app_commands.describe(member="The member to unmute.")
@is_staff_or_owner()
async def unmute(interaction: discord.Interaction, member: discord.Member):
    """Removes a timeout from a member."""
    try:
        await member.timeout(None, reason=f"Unmuted by {interaction.user}")
        await interaction.response.send_message(f"🔊 {member.mention} has been unmuted.", ephemeral=True)
        log_details = f"**Target:** {member.mention}"
        await log_action(interaction, "User Unmuted", log_details, color=discord.Color.dark_green())
    except discord.Forbidden:
        await interaction.response.send_message("❌ I do not have the 'Moderate Members' permission.", ephemeral=True)

@tree.command(name="purge", description="Deletes a specified number of messages from the channel.", guild=GUILD)
@app_commands.describe(amount="The number of messages to delete (1-100).")
@is_staff_or_owner()
async def purge(interaction: discord.Interaction, amount: int):
    """Deletes messages in bulk from the current channel."""
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

@tree.command(name="serverinfo", description="Displays detailed statistics about the server.", guild=GUILD)
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

@tree.command(name="lock", description="Locks a channel, preventing members from sending messages.", guild=GUILD)
@app_commands.describe(channel="The channel to lock (defaults to current channel).")
@is_staff_or_owner()
async def lock(interaction: discord.Interaction, channel: Optional[discord.TextChannel] = None):
    """Locks a text channel for the @everyone role."""
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

@tree.command(name="unlock", description="Unlocks a channel, allowing members to send messages.", guild=GUILD)
@app_commands.describe(channel="The channel to unlock (defaults to current channel).")
@is_staff_or_owner()
async def unlock(interaction: discord.Interaction, channel: Optional[discord.TextChannel] = None):
    """Unlocks a text channel for the @everyone role."""
    target_channel = channel or interaction.channel
    overwrite = target_channel.overwrites_for(interaction.guild.default_role)

    if overwrite.send_messages is not False: # Can be None or True
        await interaction.response.send_message(f"❌ {target_channel.mention} is not locked.", ephemeral=True)
        return

    overwrite.send_messages = None # Resets to default
    try:
        await target_channel.set_permissions(interaction.guild.default_role, overwrite=overwrite, reason=f"Unlocked by {interaction.user}")
        await interaction.response.send_message(f"🔓 {target_channel.mention} has been unlocked.", ephemeral=True)
        await target_channel.send("🔓 This channel has been unlocked.")
        await log_action(interaction, "Channel Unlocked", f"**Channel:** {target_channel.mention}", color=discord.Color.dark_green())
    except discord.Forbidden:
        await interaction.response.send_message("❌ I don't have the 'Manage Channels' permission to do this.", ephemeral=True)

@tree.command(name="commands", description="Shows a categorized list of all available commands.", guild=GUILD)
async def commands(interaction: discord.Interaction):
    """Displays a well-organized, categorized list of all bot commands."""
    
    # Define categories and the commands that belong to them
    categories = {
        "🛠️ Moderation & Management": [
            "announce", "ban", "clearwarnings", "kick", "lock", "mute", "presetmessage", "removelevelrole",
            "setlevelrole", "setupverification", "setxp",
            "purge", "roleinfo", "slowmode", "unlock", "unmute", "warn", "warnings"
        ],
        "🎟️ Ticket System": [
            "ticketadd", "ticketclaim", "ticketremove", "ticketsetup"
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
            "8ball", "balance", "boosters", "daily", "dadjoke", "gamble", "give", "leaderboard",
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

# =================================================================
# --- TICKET SYSTEM ---
# =================================================================

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

class TicketControlsView(View):
    """A view with a button to close a ticket."""
    def __init__(self):
        # Persistent view, timeout=None
        super().__init__(timeout=None)

    @discord.ui.button(label="Close Ticket", style=discord.ButtonStyle.danger, custom_id="ticket_close_button")
    async def close_ticket(self, interaction: discord.Interaction, button: Button):
        """Handles the ticket closing process."""
        view = ConfirmCloseView()
        await interaction.response.send_message("Are you sure you want to close this ticket?", view=view, ephemeral=True)
        await view.wait()

        if view.value:
            channel_to_delete = interaction.channel
            
            # Create and send transcript before deleting
            transcript_file = await create_transcript(channel_to_delete, interaction.user)
            log_channel = bot.get_channel(LOG_CHANNEL_ID)
            if log_channel and transcript_file:
                await log_channel.send(f"Transcript for closed ticket `{channel_to_delete.name}`:", file=transcript_file)
                # Clean up the local file
                os.remove(transcript_file.filename)

            await log_action(interaction, "Ticket Closed", f"**Channel:** `{channel_to_delete.name}`", color=discord.Color.dark_red())
            
            # Now delete the channel
            await channel_to_delete.delete(reason=f"Ticket closed by {interaction.user}")

class TicketCreationView(View):
    """A persistent view with a button to create a ticket."""
    def __init__(self):
        # Persistent view, timeout=None
        super().__init__(timeout=None)

    @discord.ui.button(label="Create Ticket", style=discord.ButtonStyle.success, custom_id="ticket_create_button", emoji="🎟️")
    async def create_ticket(self, interaction: discord.Interaction, button: Button):
        """Creates a new private ticket channel for the user."""
        await interaction.response.defer(ephemeral=True)

        category = interaction.guild.get_channel(TICKET_CATEGORY_ID)
        if not category:
            await interaction.followup.send("❌ Ticket system is not configured correctly (Category not found).", ephemeral=True)
            return

        # Prevent duplicate tickets
        for channel in category.text_channels:
            if channel.name == f"ticket-{interaction.user.name.lower()}":
                await interaction.followup.send(f"❌ You already have an open ticket: {channel.mention}", ephemeral=True)
                return

        # Permissions for the new channel
        staff_role = interaction.guild.get_role(next(iter(STAFF_ROLE_IDS))) # Gets the first staff role for mentions
        overwrites = {
            interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            staff_role: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            interaction.guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True) # Ensure bot can see it
        }

        # Create the channel
        ticket_channel = await category.create_text_channel(
            name=f"ticket-{interaction.user.name.lower()}",
            overwrites=overwrites,
            reason=f"Ticket created by {interaction.user}"
        )

        # Send welcome message in the new ticket channel
        welcome_embed = discord.Embed(
            title=f"Ticket for {interaction.user.display_name}",
            description="Welcome! Please describe your issue in detail, and a staff member will be with you shortly.",
            color=discord.Color.green()
        )
        await ticket_channel.send(content=f"{interaction.user.mention} {staff_role.mention}", embed=welcome_embed, view=TicketControlsView())

        # Confirm creation and log it
        await interaction.followup.send(f"✅ Your ticket has been created: {ticket_channel.mention}", ephemeral=True)
        await log_action(interaction, "Ticket Created", f"**Channel:** {ticket_channel.mention}", color=discord.Color.green())

@tree.command(name="ticketsetup", description="Sets up the ticket creation panel in the configured channel.", guild=GUILD)
@is_staff_or_owner()
async def ticketsetup(interaction: discord.Interaction):
    """Sends the ticket creation message with the button."""
    panel_channel = interaction.guild.get_channel(TICKET_PANEL_CHANNEL_ID)
    embed = discord.Embed(title="Support Tickets", description="Click the button below to create a private ticket and get help from our staff team.", color=discord.Color.blue())
    await panel_channel.send(embed=embed, view=TicketCreationView())
    await interaction.response.send_message(f"✅ Ticket panel has been set up in {panel_channel.mention}.", ephemeral=True)

@tree.command(name="ticketadd", description="Adds a user to the current ticket channel.", guild=GUILD)
@app_commands.describe(member="The member to add to this ticket.")
@is_staff_or_owner()
async def ticketadd(interaction: discord.Interaction, member: discord.Member):
    """Adds a user to a ticket channel."""
    # Check if this is a ticket channel
    if not (interaction.channel.category_id == TICKET_CATEGORY_ID and interaction.channel.name.startswith("ticket-")):
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

@tree.command(name="ticketremove", description="Removes a user from the current ticket channel.", guild=GUILD)
@app_commands.describe(member="The member to remove from this ticket.")
@is_staff_or_owner()
async def ticketremove(interaction: discord.Interaction, member: discord.Member):
    """Removes a user from a ticket channel."""
    # Check if this is a ticket channel
    if not (interaction.channel.category_id == TICKET_CATEGORY_ID and interaction.channel.name.startswith("ticket-")):
        await interaction.response.send_message("❌ This command can only be used in a ticket channel.", ephemeral=True)
        return

    # Prevent removing the ticket creator
    creator_name_from_channel = interaction.channel.name.split('-')[1]
    if member.name.lower() == creator_name_from_channel:
        await interaction.response.send_message("❌ You cannot remove the original creator of the ticket.", ephemeral=True)
        return

    try:
        await interaction.channel.set_permissions(member, overwrite=None, reason=f"Removed from ticket by {interaction.user}") # Resets permissions
        await interaction.response.send_message(f"✅ {member.mention} has been removed from this ticket.", ephemeral=True)
        await interaction.channel.send(f"👋 {member.mention} has been removed from this ticket by {interaction.user.mention}.")
        await log_action(interaction, "User Removed from Ticket", f"**Channel:** {interaction.channel.mention}\n**Removed User:** {member.mention}", color=discord.Color.dark_blue())
    except Exception as e:
        await interaction.response.send_message(f"❌ An error occurred while removing the user: {e}", ephemeral=True)

@tree.command(name="ticketclaim", description="Claims the current ticket to notify the user who is handling it.", guild=GUILD)
@is_staff_or_owner()
async def ticketclaim(interaction: discord.Interaction):
    """Claims a ticket, notifying the user that a staff member is assisting."""
    # Check if this is a ticket channel
    if not (interaction.channel.category_id == TICKET_CATEGORY_ID and interaction.channel.name.startswith("ticket-")):
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

@tree.command(name="slowmode", description="Sets a slowmode cooldown for a channel.", guild=GUILD)
@app_commands.describe(
    seconds="The slowmode delay in seconds (0 to disable, max 21600).",
    channel="The channel to set slowmode in (defaults to current channel)."
)
@is_staff_or_owner()
async def slowmode(interaction: discord.Interaction, seconds: int, channel: Optional[discord.TextChannel] = None):
    """Sets or disables slowmode in a text channel."""
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

@tree.command(name="announce", description="Announces a new update in a formatted embed.", guild=GUILD)
@app_commands.describe(
    title="The title of the announcement.",
    description="The detailed description. Use '\\n' for new lines.",
    channel="The channel to send the announcement to (defaults to current).",
    mention_role="An optional role to mention with the announcement."
)
@is_staff_or_owner()
async def announce(
    interaction: discord.Interaction,
    title: str,
    description: str,
    channel: Optional[discord.TextChannel] = None,
    mention_role: Optional[discord.Role] = None
):
    """Creates and sends a formatted update announcement."""
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

@tree.command(name="botstats", description="Displays detailed statistics about the bot.", guild=GUILD)
@is_staff_or_owner()
async def botstats(interaction: discord.Interaction):
    """Shows detailed statistics about the bot's performance and status."""
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

@tree.command(name="ban", description="Bans a member from the server.", guild=GUILD)
@app_commands.describe(member="The member to ban.", reason="The reason for the ban.")
@is_staff_or_owner()
async def ban(interaction: discord.Interaction, member: discord.Member, reason: str):
    """Bans a user from the server and logs it."""
    if member.id == interaction.user.id:
        await interaction.response.send_message("❌ You cannot ban yourself.", ephemeral=True)
        return
    if member.top_role >= interaction.user.top_role and interaction.user.id != OWNER_ID:
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

@tree.command(name="kick", description="Kicks a member from the server.", guild=GUILD)
@app_commands.describe(member="The member to kick.", reason="The reason for the kick.")
@is_staff_or_owner()
async def kick(interaction: discord.Interaction, member: discord.Member, reason: str):
    """Kicks a user from the server and logs it."""
    if member.id == interaction.user.id:
        await interaction.response.send_message("❌ You cannot kick yourself.", ephemeral=True)
        return
    if member.top_role >= interaction.user.top_role and interaction.user.id != OWNER_ID:
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

@tree.command(name="giveaway", description="Starts a giveaway in the current channel.", guild=GUILD)
@app_commands.describe(prize="What is the prize for the giveaway?", minutes="How many minutes the giveaway should last.", winners="How many winners should be chosen (default 1).")
@is_staff_or_owner()
async def giveaway(interaction: discord.Interaction, prize: str, minutes: int, winners: int = 1): # This command should remain staff-only as it's a moderation/event tool
    """Starts a timed giveaway that automatically picks a winner."""
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

@tree.command(name="meme", description="Fetches a random meme from Reddit.", guild=GUILD)
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

@tree.command(name="roast", description="Sends a funny roast to the mentioned user.", guild=GUILD)
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

@tree.command(name="ship", description="Calculates the love compatibility between two users.", guild=GUILD)
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

@tree.command(name="roleinfo", description="Shows detailed information about a role.", guild=GUILD)
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

@tree.command(name="suggest", description="Submit a suggestion for the server.", guild=GUILD)
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

@tree.command(name="boosters", description="Shows a list of all current server boosters.", guild=GUILD)
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

@tree.command(name="rps", description="Challenge another user to a game of Rock, Paper, Scissors.", guild=GUILD)
@app_commands.describe(user="The user you want to challenge.")
async def rps(interaction: discord.Interaction, user: discord.Member):
    """Starts a Rock, Paper, Scissors duel."""
    if user.bot:
        await interaction.response.send_message("❌ You can't play against a bot!", ephemeral=True)
        return
    if user == interaction.user:
        await interaction.response.send_message("❌ You can't play against yourself!", ephemeral=True)
        return

    view = RPSView(interaction.user, user)
    embed = discord.Embed(
        title="⚔️ Rock, Paper, Scissors Duel!",
        description=f"{interaction.user.mention} has challenged {user.mention} to a duel!",
        color=discord.Color.dark_purple()
    )
    await interaction.response.send_message(content=f"{interaction.user.mention} {user.mention}", embed=embed, view=view)

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

@tree.command(name="slots", description="Try your luck at the emoji slot machine!", guild=GUILD)
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

@tree.command(name="mock", description="Converts your text to mOcKiNg SpOnGeBoB text.", guild=GUILD)
async def mock(interaction: discord.Interaction, text: str):
    """Converts text to alternating case."""
    mocked_text = "".join(c.lower() if i % 2 == 0 else c.upper() for i, c in enumerate(text))
    await interaction.response.send_message(mocked_text)

@tree.command(name="dadjoke", description="Tells a random, cringey dad joke.", guild=GUILD)
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

# =================================================================
# --- VERIFICATION SYSTEM ---
# =================================================================

class VerificationModal(discord.ui.Modal, title="Server Verification"):
    """A modal that asks the user to solve a simple captcha."""
    def __init__(self, captcha_text: str):
        super().__init__()
        self.captcha_text = captcha_text
        self.captcha_input = discord.ui.TextInput(
            label=f"Type the following text: {self.captcha_text}",
            placeholder="Case-insensitive",
            required=True,
            min_length=len(self.captcha_text),
            max_length=len(self.captcha_text)
        )
        self.add_item(self.captcha_input)

    async def on_submit(self, interaction: discord.Interaction):
        if self.captcha_input.value.lower() == self.captcha_text.lower():
            verified_role = interaction.guild.get_role(VERIFIED_ROLE_ID)
            if verified_role:
                await interaction.user.add_roles(verified_role, reason="Completed verification")
                await interaction.response.send_message("✅ **Verification Successful!**\n\nYou now have access to the rest of the server.", ephemeral=True)
                await log_action(interaction, "User Verified", f"**User:** {interaction.user.mention} completed the captcha.", color=discord.Color.green())
            else:
                await interaction.response.send_message("❌ Verification role not found. Please contact staff.", ephemeral=True)
        else:
            await interaction.response.send_message("❌ Verification failed. The text did not match. Please try again.", ephemeral=True)

class VerificationView(View):
    """A view with a button to start the verification process."""
    def __init__(self):
        super().__init__(timeout=180) # View times out after 3 minutes

    @discord.ui.button(label="Verify", style=discord.ButtonStyle.green, emoji="✅")
    async def verify_button(self, interaction: discord.Interaction, button: Button):
        # Generate a random 6-character string for the captcha
        captcha = "".join(random.choices("ABCDEFGHJKLMNPQRSTUVWXYZ123456789", k=6))
        modal = VerificationModal(captcha)
        await interaction.response.send_modal(modal)

@tree.command(name="privateverify", description="Starts the private verification process to get access to the server.", guild=GUILD)
async def privateverify(interaction: discord.Interaction):
    """Sends a private message to the user to start verification."""
    verified_role = interaction.guild.get_role(VERIFIED_ROLE_ID)
    if verified_role in interaction.user.roles:
        await interaction.response.send_message("You are already verified!", ephemeral=True)
        return

    embed = discord.Embed(
        title="Welcome to the Server Verification",
        description=(
            "To gain access to the rest of the server, you need to complete a quick verification step.\n\n"
            "Click the **Verify** button below to begin."
        ),
        color=discord.Color.blue()
    )
    embed.set_footer(text="This helps us protect the server from bots.")

    view = VerificationView()
    await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

@tree.command(name="setupverification", description="Sets up the public verification message in the specified channel.", guild=GUILD)
@is_staff_or_owner()
async def setupverification(interaction: discord.Interaction):
    """Sends a public verification message to the specified channel."""
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

@tree.command(name="uptime", description="Shows how long the bot has been online.", guild=GUILD)
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

@tree.command(name="membercount", description="Shows the current member count of the server.", guild=GUILD)
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

@tree.command(name="messagestats", description="Shows the message count for a specific user.", guild=GUILD)
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

@tree.command(name="topchatters", description="Shows a leaderboard of the most active chatters.", guild=GUILD)
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

@tree.command(name="emojistats", description="Shows a leaderboard of the most used custom emojis.", guild=GUILD)
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

# =================================================================
# --- LEVELING SYSTEM COMMANDS ---
# =================================================================

setxp_group = app_commands.Group(name="setxp", description="Commands to manage user XP.")

@setxp_group.command(name="user", description="Set the XP for a specific user.")
@app_commands.describe(user="The user to set XP for.", amount="The amount of XP to set.")
@is_staff_or_owner()
async def setxp_user(interaction: discord.Interaction, user: discord.Member, amount: int):
    """Sets the XP for a single user."""
    if amount < 0:
        await interaction.response.send_message("❌ XP amount cannot be negative.", ephemeral=True)
        return

    user_id_str = str(user.id)
    if user_id_str not in leveling_data:
        leveling_data[user_id_str] = {"level": 0, "xp": 0}
    
    leveling_data[user_id_str]["xp"] = amount
    # Note: This does not automatically adjust the level. It's a direct XP set.
    save_leveling_data(leveling_data)

    await interaction.response.send_message(f"✅ Set {user.mention}'s XP to **{amount}**.", ephemeral=True)
    await log_action(interaction, "XP Set (User)", f"**Target:** {user.mention}\n**Amount:** {amount}", color=discord.Color.dark_purple())

@setxp_group.command(name="all", description="Set the XP for all members in the server.")
@app_commands.describe(amount="The amount of XP to set for everyone.")
@is_staff_or_owner()
async def setxp_all(interaction: discord.Interaction, amount: int):
    """Sets the XP for all server members."""
    if amount < 0:
        await interaction.response.send_message("❌ XP amount cannot be negative.", ephemeral=True)
        return

    for member in interaction.guild.members:
        if not member.bot:
            leveling_data[str(member.id)] = {"level": 0, "xp": amount}
    save_leveling_data(leveling_data)
    await interaction.response.send_message(f"✅ Set everyone's XP to **{amount}**.", ephemeral=True)
    await log_action(interaction, "XP Set (All)", f"**Amount:** {amount}", color=discord.Color.red())

@tree.command(name="rank", description="Check your or another user's level and XP.", guild=GUILD)
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

@tree.command(name="levelboard", description="Shows the server's XP leaderboard.", guild=GUILD)
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

@tree.command(name="setlevelrole", description="Assign a role reward for reaching a certain level.", guild=GUILD)
@app_commands.describe(level="The level to reward.", role="The role to give as a reward.")
@is_staff_or_owner()
async def setlevelrole(interaction: discord.Interaction, level: int, role: discord.Role):
    """Sets a role to be automatically given at a specific level."""
    if level <= 0:
        await interaction.response.send_message("❌ Level must be a positive number.", ephemeral=True)
        return
    
    level_str = str(level)
    level_rewards[level_str] = role.id
    save_level_rewards(level_rewards)

    await interaction.response.send_message(f"✅ **Level {level}** will now award the {role.mention} role.", ephemeral=True)
    await log_action(interaction, "Level Reward Set", f"**Level:** {level}\n**Role:** {role.mention}", color=discord.Color.blue())

@tree.command(name="removelevelrole", description="Remove a role reward from a level.", guild=GUILD)
@app_commands.describe(level="The level to remove the reward from.")
@is_staff_or_owner()
async def removelevelrole(interaction: discord.Interaction, level: int):
    """Removes a role reward from a specific level."""
    level_str = str(level)
    if level_str in level_rewards:
        removed_role_id = level_rewards.pop(level_str)
        save_level_rewards(level_rewards)
        role = interaction.guild.get_role(removed_role_id)
        await interaction.response.send_message(f"✅ The role reward for **Level {level}** ({role.mention if role else 'Unknown Role'}) has been removed.", ephemeral=True)
        await log_action(interaction, "Level Reward Removed", f"**Level:** {level}", color=discord.Color.dark_blue())
    else:
        await interaction.response.send_message(f"❌ There is no role reward set for **Level {level}**.", ephemeral=True)

@tree.command(name="levelroles", description="View all configured level role rewards.", guild=GUILD)
async def levelroles(interaction: discord.Interaction):
    """Displays a list of all configured level-up role rewards."""
    if not level_rewards:
        await interaction.response.send_message("There are no level rewards configured yet.", ephemeral=True)
        return

    embed = discord.Embed(title="🎁 Level Role Rewards", color=discord.Color.gold())
    description = "\n".join(f"**Level {lvl}:** <@&{role_id}>" for lvl, role_id in sorted(level_rewards.items(), key=lambda item: int(item[0])))
    embed.description = description
    await interaction.response.send_message(embed=embed)
# =================================================================
# --- 10 NEW COMMANDS ---
# =================================================================

@tree.command(name="remindme", description="Sets a personal reminder.", guild=GUILD)
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

@tree.command(name="afk", description="Set or remove your AFK status.", guild=GUILD)
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

@tree.command(name="coinflip", description="Flips a coin.", guild=GUILD)
async def coinflip(interaction: discord.Interaction):
    """Flips a coin and shows the result."""
    result = random.choice(["Heads", "Tails"])
    emoji = "👑" if result == "Heads" else "🪙"
    embed = discord.Embed(title="🪙 Coin Flip", description=f"The coin landed on... **{result}**! {emoji}", color=discord.Color.gold())
    await interaction.response.send_message(embed=embed)

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

@tree.command(name="hug", description="Give someone a hug.", guild=GUILD)
@app_commands.describe(member="The person you want to hug.")
async def hug(interaction: discord.Interaction, member: discord.Member):
    await interaction_command(interaction, member, "hug", "🤗", discord.Color.pink())

@tree.command(name="pat", description="Give someone a pat on the head.", guild=GUILD)
@app_commands.describe(member="The person you want to pat.")
async def pat(interaction: discord.Interaction, member: discord.Member):
    await interaction_command(interaction, member, "pat", "❤️", discord.Color.light_grey())

@tree.command(name="slap", description="Slap someone.", guild=GUILD)
@app_commands.describe(member="The person you want to slap.")
async def slap(interaction: discord.Interaction, member: discord.Member):
    await interaction_command(interaction, member, "slap", "👋", discord.Color.dark_red())

@tree.command(name="fact", description="Get a random interesting fact.", guild=GUILD)
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

@tree.command(name="stopwatch", description="A simple stopwatch.", guild=GUILD)
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

@tree.command(name="timer", description="Starts a countdown timer.", guild=GUILD)
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

@tree.command(name="urban", description="Look up a word on Urban Dictionary.", guild=GUILD)
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

@tree.command(name="truth", description="Asks a random truth question.", guild=GUILD)
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

@tree.command(name="dare", description="Gives a random dare.", guild=GUILD)
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

@tree.command(name="spinbottle", description="Spin the bottle to pick a random user.", guild=GUILD)
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

@tree.command(name="serverage", description="Shows how old the server is.", guild=GUILD)
async def serverage(interaction: discord.Interaction):
    """Displays the age of the server."""
    age = datetime.datetime.now(datetime.timezone.utc) - interaction.guild.created_at
    embed = discord.Embed(
        title="🎂 Server Age",
        description=f"This server was created on {discord.utils.format_dt(interaction.guild.created_at, style='F')}.\nThat was **{age.days}** days ago!",
        color=discord.Color.blue()
    )
    await interaction.response.send_message(embed=embed)

@tree.command(name="accountage", description="Shows how old a user's account is.", guild=GUILD)
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

@tree.command(name="countdown", description="Countdown to a specific date.", guild=GUILD)
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

@tree.command(name="calendar", description="Shows a calendar for a given month and year.", guild=GUILD)
@app_commands.describe(month="The month (1-12, defaults to current).", year="The year (defaults to current).")
async def calendar_command(interaction: discord.Interaction, month: Optional[int] = None, year: Optional[int] = None):
    """Displays a simple text-based calendar."""
    now = datetime.datetime.now()
    _month = month or now.month
    _year = year or now.year
    cal_text = calendar.month(_year, _month)
    embed = discord.Embed(title=f"📅 Calendar for {calendar.month_name[_month]} {_year}", description=f"```\n{cal_text}\n```", color=discord.Color.dark_grey())
    await interaction.response.send_message(embed=embed)

@tree.command(name="feedback", description="Send feedback directly to the bot owner.", guild=GUILD)
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

@tree.command(name="botinvite", description="Get an invite link for the bot.", guild=GUILD)
async def botinvite(interaction: discord.Interaction):
    """Generates a basic, no-permission invite link for the bot."""
    invite_url = discord.utils.oauth_url(bot.user.id, permissions=discord.Permissions(permissions=0))
    await interaction.response.send_message(f"Here is a basic invite link for me:\n<{invite_url}>", ephemeral=True)

# =================================================================
# --- BOT EVENTS ---
# =================================================================
@bot.event
async def on_ready():
    """Runs when the bot successfully connects and shows stats in the terminal."""
    # Add persistent views
    bot.add_view(TicketCreationView()) # For the create button
    bot.add_view(TicketControlsView()) # For the close button
    # Sync the commands to the specific guild
    synced = await tree.sync(guild=GUILD)
    print("==============================================")
    print(f"✅ Bot logged in as: {bot.user} (ID: {bot.user.id})")
    print(f"🐍 Python Version: {platform.python_version()}")
    print(f"🔗 Synced {len(synced)} commands to Guild: {GUILD_ID}")
    print("==============================================")

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
        await bot.process_commands(message)
        return

    xp_cooldowns[user_id] = current_time

    # Grant XP
    xp_to_add = random.randint(15, 25)
    if user_id_str not in leveling_data:
        leveling_data[user_id_str] = {"level": 0, "xp": 0}
    
    leveling_data[user_id_str]["xp"] += xp_to_add

    # Check for level up
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

    save_leveling_data(leveling_data)

    # This is needed if you have other on_message based commands (prefix commands)
    await bot.process_commands(message)

@bot.event
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    """A global error handler for all slash commands."""
    if isinstance(error, app_commands.CheckFailure):
        await interaction.response.send_message(
            "You can't use these commands. Try `/commands` to see which ones you can use.",
            ephemeral=True
        )
    else:
        print(f"An unhandled error occurred in command '{interaction.command.name}': {error}")
        if not interaction.response.is_done():
            await interaction.response.send_message("❌ An unexpected error occurred. Please try again later.", ephemeral=True)

# =================================================================
# --- ECONOMY SYSTEM COMMANDS ---
# =================================================================

@tree.command(name="balance", description="Check your or another user's coin balance.", guild=GUILD)
@app_commands.describe(user="The user whose balance you want to see (optional).")
async def balance(interaction: discord.Interaction, user: Optional[discord.Member] = None):
    """Shows the coin balance for a user."""
    target_user = user or interaction.user
    bal = get_user_balance(target_user.id)
    
    embed = discord.Embed(
        title=f"💰 Wallet Balance for {target_user.display_name}",
        description=f"They currently have **{bal}** coins.",
        color=discord.Color.gold()
    )
    await interaction.response.send_message(embed=embed)

@tree.command(name="daily", description="Claim your daily coins.", guild=GUILD)
async def daily(interaction: discord.Interaction):
    """Gives the user their daily coin reward."""
    user_id_str = str(interaction.user.id)
    
    # Initialize user data if not present
    if user_id_str not in economy_data:
        economy_data[user_id_str] = {"balance": 0, "last_daily": None}

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
    save_economy_data(economy_data)

    embed = discord.Embed(
        title="🎉 Daily Reward Claimed!",
        description=f"You received **{daily_amount}** coins! Your new balance is **{economy_data[user_id_str]['balance']}** coins.",
        color=discord.Color.green()
    )
    await interaction.response.send_message(embed=embed)

@tree.command(name="give", description="Give coins to another user.", guild=GUILD)
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
    save_economy_data(economy_data)

    await interaction.response.send_message(f"✅ You have successfully given **{amount}** coins to {user.mention}!")

@tree.command(name="leaderboard", description="Shows the richest users in the server.", guild=GUILD)
async def leaderboard(interaction: discord.Interaction):
    """Displays the top 10 richest users."""
    sorted_users = sorted(economy_data.items(), key=lambda item: item[1].get('balance', 0), reverse=True)

    embed = discord.Embed(title="🏆 Coin Leaderboard", description="The richest users in the server!", color=discord.Color.gold())

    leaderboard_text = ""
    for i, (user_id, data) in enumerate(sorted_users[:10], 1):
        user = interaction.guild.get_member(int(user_id))
        if user:
            leaderboard_text += f"**{i}.** {user.mention}: **{data.get('balance', 0)}** coins\n"
    
    if not leaderboard_text:
        embed.description = "The economy is just starting. No one is on the leaderboard yet!"
    else:
        embed.description = leaderboard_text

    await interaction.response.send_message(embed=embed)

@tree.command(name="gamble", description="Gamble your coins for a chance to double them!", guild=GUILD)
@app_commands.describe(amount="The amount of coins to gamble.")
async def gamble(interaction: discord.Interaction, amount: int):
    """Allows a user to gamble their coins."""
    if amount <= 0:
        await interaction.response.send_message("❌ You must gamble a positive amount.", ephemeral=True)
        return

    user_id_str = str(interaction.user.id)
    user_balance = get_user_balance(interaction.user.id)

    if amount > user_balance:
        await interaction.response.send_message(f"❌ You can't gamble more than you have! Your balance is **{user_balance}** coins.", ephemeral=True)
        return

    if random.choice([True, False]): # 50/50 chance
        economy_data[user_id_str]["balance"] += amount
        await interaction.response.send_message(f"🎉 **You won!** You doubled your bet and won **{amount}** coins! Your new balance is **{economy_data[user_id_str]['balance']}**.")
    else:
        economy_data[user_id_str]["balance"] -= amount
        await interaction.response.send_message(f"😢 **You lost!** You lost **{amount}** coins. Your new balance is **{economy_data[user_id_str]['balance']}**.")
    
    save_economy_data(economy_data)

# =================================================================
# --- TAG SYSTEM COMMANDS ---
# =================================================================

tag_group = app_commands.Group(name="tag", description="Commands to manage server tags.")

@tag_group.command(name="create", description="Create a new tag.")
@app_commands.describe(name="The name of the tag.", content="The content of the tag. Use '\\n' for new lines.")
@is_staff_or_owner()
async def tag_create(interaction: discord.Interaction, name: str, content: str):
    """Creates a new custom command/tag."""
    tag_name = name.lower()
    if tag_name in tags_data:
        await interaction.response.send_message(f"❌ A tag with the name `{tag_name}` already exists.", ephemeral=True)
        return
    
    tags_data[tag_name] = content.replace('\\n', '\n')
    save_tags(tags_data)
    await interaction.response.send_message(f"✅ Tag `{tag_name}` has been created.", ephemeral=True)
    await log_action(interaction, "Tag Created", f"**Name:** {tag_name}", color=discord.Color.green())

@tag_group.command(name="use", description="Use a tag.")
@app_commands.describe(name="The name of the tag to use.")
async def tag_use(interaction: discord.Interaction, name: str):
    """Uses a tag, posting its content."""
    tag_name = name.lower()
    if tag_name not in tags_data:
        await interaction.response.send_message(f"❌ A tag with the name `{tag_name}` does not exist.", ephemeral=True)
        return
    
    await interaction.response.send_message(tags_data[tag_name])

@tag_group.command(name="edit", description="Edit an existing tag.")
@app_commands.describe(name="The name of the tag to edit.", new_content="The new content for the tag. Use '\\n' for new lines.")
@is_staff_or_owner()
async def tag_edit(interaction: discord.Interaction, name: str, new_content: str):
    """Edits an existing tag."""
    tag_name = name.lower()
    if tag_name not in tags_data:
        await interaction.response.send_message(f"❌ A tag with the name `{tag_name}` does not exist.", ephemeral=True)
        return
        
    tags_data[tag_name] = new_content.replace('\\n', '\n')
    save_tags(tags_data)
    await interaction.response.send_message(f"✅ Tag `{tag_name}` has been updated.", ephemeral=True)
    await log_action(interaction, "Tag Edited", f"**Name:** {tag_name}", color=discord.Color.blue())

@tag_group.command(name="delete", description="Delete a tag.")
@app_commands.describe(name="The name of the tag to delete.")
@is_staff_or_owner()
async def tag_delete(interaction: discord.Interaction, name: str):
    """Deletes a tag."""
    tag_name = name.lower()
    if tag_name not in tags_data:
        await interaction.response.send_message(f"❌ A tag with the name `{tag_name}` does not exist.", ephemeral=True)
        return
        
    del tags_data[tag_name]
    save_tags(tags_data)
    await interaction.response.send_message(f"✅ Tag `{tag_name}` has been deleted.", ephemeral=True)
    await log_action(interaction, "Tag Deleted", f"**Name:** {tag_name}", color=discord.Color.red())

@tag_group.command(name="list", description="List all available tags.")
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

# =================================================================
# --- RUN BOT ---
# =================================================================

if __name__ == "__main__":
    bot.run(TOKEN)
