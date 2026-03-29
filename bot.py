import discord
import aiohttp
import asyncio
import os

DISCORD_TOKEN = os.environ.get("DISCORD_TOKEN")
BATTLEMETRICS_SERVER_ID = "38464860"

intents = discord.Intents.default()
intents.members = True
intents.presences = True
intents.message_content = True

client = discord.Client(intents=intents)

async def fetch_server_status():
    url = f"https://api.battlemetrics.com/servers/{BATTLEMETRICS_SERVER_ID}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                attributes = data["data"]["attributes"]
                status = attributes["status"]
                players = attributes["players"]
                max_players = attributes["maxPlayers"]
                return status, players, max_players
            return None, None, None

async def update_status():
    await client.wait_until_ready()
    while not client.is_closed():
        status, players, max_players = await fetch_server_status()
        if status == "online":
            activity = discord.Game(name=f"🟢 {players}/{max_players} players online")
            await client.change_presence(status=discord.Status.online, activity=activity)
        else:
            activity = discord.Game(name="🔴 Server is offline")
            await client.change_presence(status=discord.Status.do_not_disturb, activity=activity)
        await asyncio.sleep(60)  # Update every 60 seconds

@client.event
async def on_ready():
    print(f"Logged in as {client.user}")
    client.loop.create_task(update_status())

client.run(DISCORD_TOKEN)
