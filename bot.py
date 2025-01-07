import discord
from discord.ext import commands
from datetime import datetime
import requests
import logging
import os
import io

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
API_URL = "https://cataas.com"

# Create a bot instance
intents = discord.Intents.default()
bot = commands.Bot(command_prefix='!', intents=intents)

##############################
# CORE FUNCTIONS
##############################

def get_uptime():
    now = datetime.now()
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
    bot.uptime = datetime.now()
    try:
        synced = await bot.tree.sync()
        logger.info(f"Synced {len(synced)} slash commands")
    except Exception as e:
        logger.error(f"Failed to sync slash commands: {e}")

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
    logger.info("Ping command used")
    embed = discord.Embed(title="Pong!", description=f"Latency: {round(bot.latency * 1000)}ms", color=discord.Color.green())
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name='info', description='Get information about the bot')
async def info(interaction: discord.Interaction):
    logger.info("Info command used")
    embed = discord.Embed(title="Bot Information", color=discord.Color.green())
    embed.add_field(name="Latency", value=f"{round(bot.latency * 1000)}ms")
    embed.add_field(name="Guilds", value=len(bot.guilds))
    embed.add_field(name="Uptime", value=get_uptime())
    embed.add_field(name="Version", value=BOT_VERSION)
    embed.add_field(name="Description", value="Get cat pictures on demand using the CATAAS API. Try `/randomcat` or `/customcat` for cat pictures!", inline=False)
    await interaction.response.send_message(embed=embed)

##############################
# HELPER FUNCTIONS
##############################

async def download_and_send_image(url: str, interaction: discord.Interaction, title: str):
    """Helper function to download and send an image"""
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad status codes
        
        # Create a file-like object from the image data
        image_data = io.BytesIO(response.content)
        
        # Create the Discord file object
        file = discord.File(image_data, filename="cat.png")
        
        # Create embed with title
        embed = discord.Embed(title=title, color=discord.Color.green())
        # Attach the file to the embed using the "attachment://" protocol
        embed.set_image(url="attachment://cat.png")
        
        # Send both the file and embed
        return file, embed
        
    except Exception as e:
        logger.error(f"Failed to download image: {e}")
        raise

##############################
# CAT GRABBER
##############################

@bot.tree.command(name='howmanycats', description='Show how many cat pictures are available')
async def howmanycats(interaction: discord.Interaction):
    logger.info("Getting the number of available cat pictures")
    try:
        response = requests.get(f"{API_URL}/api/count")
        data = response.json()
        count = data.get("count", "N/A")
        embed = discord.Embed(title="Cat Pictures Statistics", color=discord.Color.green())
        embed.add_field(name="Available Pictures", value=f"There are {count:,} cat pictures in the database")
    except Exception as e:
        logger.error(f"Failed to get cat count: {e}")
        embed = discord.Embed(title="Error", description="Failed to get cat pictures count", color=discord.Color.red())
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name='randomcat', description='Get a random cat picture')
async def randomcat(interaction: discord.Interaction):
    logger.info("Getting a random cat picture")
    try:
        # First, defer the response since image fetching might take time
        await interaction.response.defer()
        
        # Prepare the URL with timestamp to prevent caching
        image_url = f"{API_URL}/cat?timestamp={datetime.now().timestamp()}"
        
        # Download and prepare the image
        file, embed = await download_and_send_image(image_url, interaction, "Random Cat Picture")
        
        # Send both the file and embed
        await interaction.followup.send(file=file, embed=embed)
        
    except Exception as e:
        logger.error(f"Failed to get cat picture: {e}")
        await interaction.followup.send("Failed to get cat picture", ephemeral=True)

@bot.tree.command(name='customcat', description='Get a cat picture with advanced options')
@discord.app_commands.describe(
    width='The picture width',
    height='The picture height',
    filter='The picture filter',
    blur='The picture blur (0-10)',
    brightness='The picture brightness (0-100)',
    saturation='The picture saturation (0-100)',
    lightness='The picture lightness (0-100)',
    hue='The picture hue (0-360)',
    red='The picture red (0-255)',
    green='The picture green (0-255)',
    blue='The picture blue (0-255)'
)
@discord.app_commands.choices(filter=[
    discord.app_commands.Choice(name='Mono', value='mono'),
    discord.app_commands.Choice(name='Negative', value='negate'),
    discord.app_commands.Choice(name='Custom', value='custom')
])
async def customcat(
    interaction: discord.Interaction, 
    width: int = None,
    height: int = None,
    filter: str = None,
    blur: int = None,
    brightness: int = None,
    saturation: int = None,
    lightness: int = None,
    hue: int = None,
    red: int = None,
    green: int = None,
    blue: int = None
):
    logger.info(f"Getting a custom cat picture with parameters")
    
    # Input validation
        
    if filter and filter.lower() not in ['mono', 'negative', 'custom']:
        await interaction.response.send_message("Filter must be either Mono, Negative or Custom", ephemeral=True)
        if filter.lower() == 'negative':
            filter = 'negate'
        return
        
    if blur is not None and not (0 <= blur <= 10):
        await interaction.response.send_message("Blur must be between 0 and 10", ephemeral=True)
        return
        
    if brightness is not None and not (0 <= brightness <= 100):
        await interaction.response.send_message("Brightness must be between 0 and 100", ephemeral=True)
        return
        
    if saturation is not None and not (0 <= saturation <= 100):
        await interaction.response.send_message("Saturation must be between 0 and 100", ephemeral=True)
        return
        
    if lightness is not None and not (0 <= lightness <= 100):
        await interaction.response.send_message("Lightness must be between 0 and 100", ephemeral=True)
        return
        
    if hue is not None and not (0 <= hue <= 360):
        await interaction.response.send_message("Hue must be between 0 and 360", ephemeral=True)
        return
        
    if red is not None and not (0 <= red <= 255):
        await interaction.response.send_message("Red must be between 0 and 255", ephemeral=True)
        return
        
    if green is not None and not (0 <= green <= 255):
        await interaction.response.send_message("Green must be between 0 and 255", ephemeral=True)
        return
        
    if blue is not None and not (0 <= blue <= 255):
        await interaction.response.send_message("Blue must be between 0 and 255", ephemeral=True)
        return

    try:
        await interaction.response.defer()
        
        # Build the URL with parameters
        params = []
        for param_name, param_value in {
            'width': width,
            'height': height,
            'filter': filter,
            'blur': blur,
            'brightness': brightness,
            'saturation': saturation,
            'lightness': lightness,
            'hue': hue,
            'red': red,
            'green': green,
            'blue': blue
        }.items():
            if param_value is not None:
                params.append(f"{param_name}={param_value}")
        
        # Construct final URL
        image_url = f"{API_URL}/cat"
        if params:
            image_url += "?" + "&".join(params)
        
        # Download and prepare the image
        file, embed = await download_and_send_image(image_url, interaction, "Custom Cat Picture")
        
        # Add parameters used to embed
        param_text = "\n".join([f"{param}: {value}" for param, value in {
            'Width': width,
            'Height': height,
            'Filter': filter,
            'Blur': blur,
            'Brightness': brightness,
            'Saturation': saturation,
            'Lightness': lightness,
            'Hue': hue,
            'Red': red,
            'Green': green,
            'Blue': blue
        }.items() if value is not None])
        
        embed.add_field(name="⚠️ Disclaimer", value="This command is still Work in Progress. Some parameters may not be applied to the image.", inline=False)
        if param_text:
            embed.add_field(name="⚙️ Parameters Used", value=f"```\n{param_text}\n```", inline=False)
        
        # Send both the file and embed
        await interaction.followup.send(file=file, embed=embed)
        logger.info(f"Custom cat picture sent with parameters: {param_text}")
        logger.info(f"Image URL: {image_url}")
        
    except Exception as e:
        logger.error(f"Failed to get custom cat picture: {e}")
        await interaction.followup.send("Failed to get cat picture", ephemeral=True)

@bot.tree.command(name='tags', description='See a list of available cat picture tags')
async def tags(interaction: discord.Interaction):
    logger.info("Getting cat picture tags")
    embed = discord.Embed(title="Cat Picture Tags", description=f"Due to Discord's limitations, it is not possible to display all the tags in a single message. You can still check the list of avalable tags on this URL: {API_URL}/api/tags", color=discord.Color.green())
    await interaction.response.send_message(embed=embed)



if __name__ == "__main__":
    bot.run(TOKEN)