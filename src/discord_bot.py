import discord
from discord.ext import commands
import asyncio
import os
from ticker_image import create_stock_alert_image
import uuid


ALERT_CHANNEL_ID = int(os.getenv("ALERT_CHANNEL")) # Convert to int as getenv returns string
TOKEN = os.getenv("DISCORD_TOKEN")



intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")

    await bot.wait_until_ready()
    print("Bot is fully ready and cache is populated!")

    if bot.guilds:
        print(f"Connected to {len(bot.guilds)} servers:")
        for guild in bot.guilds:
            print(f"- {guild.name} (ID: {guild.id})")
            print(f"  Channels in {guild.name}:")
            for channel in guild.text_channels:
                print(f"    - #{channel.name} (ID: {channel.id})")
    else:
        print("Bot is not connected to any servers yet.")

    bot.message_queue = asyncio.Queue()


    bot.loop.create_task(process_flask_messages())

async def send_alert(ticker: str, price: float, multiplier: float, float_value: float, volume: float):
    image_name = None
    try:

        message = (
            f"📈 Stock Alert! **{ticker}** hitting new momentum!\n"
            f"Current Price: **${price:.2f}**\n"
            f"Multiplier: {multiplier:.1f}x\n"
            f"Float: {float_value:,.0f}\n" # Formatted for readability
            f"Volume: {volume:,.0f}\n\n" # Formatted for readability
            f"View more details: <https://fjord.tekuro.io/>" # Link without preview
        )
        
        channel = bot.get_channel(ALERT_CHANNEL_ID)
        if channel:
            image_name = f"alert_{uuid.uuid4()}.png"

            create_stock_alert_image(ticker, price, multiplier, float_value, volume, output_filename=image_name)
            await channel.send(message, file=discord.File(image_name))
            print(f"Successfully sent alert for {ticker} and image: {image_name}")


            if os.path.exists(image_name):
                os.remove(image_name)
                print(f"Deleted temporary image file: {image_name}")

        else:
            print(f"Error: Could not find Discord channel with ID: {ALERT_CHANNEL_ID}. "
                  "Please check the ID and ensure the bot is in the server.")
    except discord.Forbidden:
        print(f"Error: I don't have permission to send messages in channel ID: {ALERT_CHANNEL_ID}.")
        print("Please check bot permissions in the server and channel settings.")
    except Exception as e:
        print(f"An unexpected error occurred while sending Discord message for {ticker}: {e}")

        if 'image_name' in locals() and image_name and os.path.exists(image_name):
            os.remove(image_name)
            print(f"Cleaned up temporary image file due to error: {image_name}")

async def process_flask_messages():

    # --- FIX: Wait until bot.message_queue is initialized ---
    while not hasattr(bot, 'message_queue') or bot.message_queue is None:
        print("Waiting for bot.message_queue to be initialized...")
        await asyncio.sleep(0.5) 


    while True:

        payload = await bot.message_queue.get() 
        
        ticker = payload.get('ticker')
        price = payload.get('price')
        multiplier = payload.get('multiplier')
        float_value = payload.get('float_value')
        volume = payload.get('volume')

        await send_alert(ticker, price, multiplier, float_value, volume)
        
        bot.message_queue.task_done() 

if TOKEN is None:
    print("Error: DISCORD_TOKEN environment variable not set. Please set it in your .env file or system environment.")
    exit(1)

if ALERT_CHANNEL_ID is None:
    print("Error: ALERT_CHANNEL_ID environment variable not set. Please set it in your .env file or system environment.")
    exit(1)

def run_discord_bot():
    bot.run(TOKEN)

if __name__ == '__main__':
    run_discord_bot()