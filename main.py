import discord
import os
from dotenv import load_dotenv  # This is for reading the .env file
from discord.ext import commands
from collections import defaultdict
import time

# Load environment variables
load_dotenv()

# Intents setup
intents = discord.Intents.all()
intents.members = True

# Bot instance
bot = commands.Bot(
    command_prefix=commands.when_mentioned_or("!"),
    intents=intents,
    help_command=None
)

# Tracker for user mentions (user_id: [(timestamp, message)])
mention_tracker = defaultdict(list)

# Bot activity
@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')
    await bot.change_presence(
        status=discord.Status.idle,
        activity=discord.Streaming(
            name=f"in {len(bot.guilds)} servers",
            url='https://www.youtube.com/watch?v=DaEjIcSQbpk'
        )
    )

# Message monitoring
@bot.event
async def on_message(message):
    if message.author.bot:  # Ignore messages from bots
        return

    # Check for @everyone mentions
    if message.mention_everyone:
        user_id = message.author.id
        current_time = message.created_at.timestamp()

        # Add the current message timestamp and message object to the tracker
        mention_tracker[user_id].append((current_time, message))  # Track timestamp and message

        # Keep only timestamps within the last 24 hours (86400 seconds)
        mention_tracker[user_id] = [
            (ts, msg) for ts, msg in mention_tracker[user_id] if current_time - ts <= 86400
        ]

        # If the user has sent more than 5 mention messages in the last 24 hours
        if len(mention_tracker[user_id]) > 5:
            try:
                # Delete all messages from the user that are tracked in the last 24 hours
                for ts, msg in mention_tracker[user_id]:
                    await msg.delete()
                await message.channel.send(
                    f"{message.author.mention}, you have been spamming @everyone mentions. All your mention messages from the last 24 hours have been deleted."
                )
            except discord.Forbidden:
                print("Bot lacks permission to delete messages.")
            except discord.HTTPException as e:
                print(f"Failed to delete messages: {e}")

            # Clear the user's tracker after action
            mention_tracker[user_id].clear()

    # Process other bot commands
    await bot.process_commands(message)

# Load token and start the bot
TOKEN = os.getenv('TOKEN')
if not TOKEN:
    raise ValueError("Bot token not found. Set the 'TOKEN' environment variable.")

bot.run(TOKEN)
