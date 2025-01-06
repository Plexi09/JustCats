import discord
from discord.ext import commands
from datetime import datetime
import datetime
import requests
import logging
import os

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger()

from dotenv import load_dotenv
load_dotenv()

# Load the token from the .env file
TOKEN = os.getenv('DISCORD_TOKEN')
BOT_NAME = "Just In Cat"
BOT_VERSION = "1.0.0"

# API configuration
API_URL = "https://cataas.com/api"
headers = {'accept': 'application/json'}

# Create a bot instance
intents = discord.Intents.default()
bot = commands.Bot(command_prefix='!', intents=intents)

##############################
# CORE FUNCTIONS
##############################

def get_uptime():
    now = datetime.datetime.now()
    delta = now - bot.uptime
    days, seconds = delta.days, delta.seconds
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    return f"{days}d, {hours}h, {minutes}m, {seconds}s"

@bot.event
async def on_ready():
    logger.info(f'Logged in as {bot.user.name}')
    logger.info(f"Logged in {len(bot.guilds)} servers")
    bot.uptime = datetime.datetime.now()
    try:
        synced = await bot.tree.sync()
        logger.info(f"Synced {synced} shash commands")
    except Exception as e:
        logger.error(f"Failed to sync shash commands: {e}")

@bot.event
async def on_message(message):
    owner = [int(os.getenv('OWNER_ID'))]
    
    if message.author.id in owner:
        if message.content == "!shutdown":
            await message.channel.send("Shutting down...")
            logger.info("Shutting down...")
            await bot.close()
            return
    
    if message.author == bot.user:
        return
    
    await bot.process_commands(message)

@bot.tree.command(name='ping', description='Ping the bot and get the latency')
async def ping(interaction: discord.Interaction):
    logger.info("Pong!")
    embed = discord.Embed(title="Pong!", description=f"Latency: {round(bot.latency * 1000)}ms", color=discord.Color.green())
    logger.info(f"Latency: {round(bot.latency * 1000)}ms")
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name='info', description='Get information about the bot')
async def info(interaction: discord.Interaction):
    logger.info("Getting bot information")
    embed = discord.Embed(title="Bot Information", color=discord.Color.green())
    embed.add_field(name="Latency", value=f"{round(bot.latency * 1000)}ms")
    embed.add_field(name="Guilds", value=len(bot.guilds))
    embed.add_field(name="Uptime", value=get_uptime())
    embed.add_field(name="Version", value=BOT_VERSION)
    # Bot description
    embed.add_field(name="Description", value="This bots allows you to get cat pictures on demand. Use the `/randomcat` command to get a random cat picture.")
    await interaction.response.send_message(embed=embed)


##############################
# CAT GRABBER
##############################

@bot.tree.command(name='howmanycats', description='Show how many cat pictures are available')
async def howmanycats(interaction: discord.Interaction):
    logger.info("Getting the number of available cat pictures")
    try:
        response = requests.get(f"{API_URL}/count", headers=headers)
        data = response.json()
        count = data.get("count", "N/A")
        logger.info(f"There are {count} cat pictures available in the database")
        embed = discord.Embed(title=BOT_NAME, color=discord.Color.green())
        embed.add_field(name="Cat Pictures Count", value=f"There are {count} cat pictures available in the database")
    except Exception as e:
        logger.error(f"Failed to get cat pictures: {e}")
        embed = discord.Embed(title="Error", description="Failed to get cat pictures", color=discord.Color.red())
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name='randomcat', description='Get a random cat picture')
async def randomcat(interaction: discord.Interaction):
    logger.info("Getting a random cat picture")
    try:
        response = requests.get(f"{API_URL}/cat", headers=headers)
        data = response.json()
        url = data[0].get("url", "N/A")
        logger.info(f"Got cat picture: {url}")
        embed = discord.Embed(title=BOT_NAME, color=discord.Color.green())
        embed.set_image(url=url)
    except Exception as e:
        logger.error(f"Failed to get cat picture: {e}")
        embed = discord.Embed(title="Error", description="Failed to get cat picture", color=discord.Color.red())
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    await interaction.response.send_message(embed=embed)

if __name__ == "__main__":
    bot.run(TOKEN)