# My modules
import json_manager, myutils, os
botSettings = json_manager.ReadFile(os.getcwd() + "\settings.json")


from typing import Optional
import discord
from discord import app_commands
from discord.ext import tasks
import schedule, asyncio
import datetime


MY_GUILD = discord.Object(id=botSettings["guildId"])  # TEMPORARY, WOULD LIKE TO GET ALL GUILDS THIS BOT IS ATTACHED TO
MAIN_GUILD = ""

class MyClient(discord.Client):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents)        
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        await client.loop.create_task(schedule_loop())
        # This copies the global commands over to the guild.
        self.tree.copy_global_to(guild=MY_GUILD)
        await self.tree.sync(guild=MY_GUILD)


intents = discord.Intents.all()
client = MyClient(intents=intents)

@client.event
async def on_ready():
    global MAIN_GUILD
    print(f'Logged in as {client.user} (ID: {client.user.id})')
    print('------')    

    MAIN_GUILD = client.get_guild(int(botSettings["guildId"]))       
    reminder.start()
    schedule.every(5).seconds.do(test)

@client.tree.command()
async def subscribe(interaction: discord.Interaction, role: discord.Role):
    """Subscribe to a role"""
    await interaction.response.send_message(f'Hi, {interaction.user.mention}', ephemeral=True)


@tasks.loop(minutes=1) # At minute 0 past every hour, call this function
async def reminder():    
    print("Reminding users to drink water...")
    time = datetime.datetime.now()
    roleId = (time.hour > int(botSettings["roles"][1]["startTime"]) and time.hour < int(botSettings["roles"][0]["startTime"])) and botSettings["roles"][1]["id"] or botSettings["roles"][0]["id"] # Picks the role to mention based on time of day
    role = MAIN_GUILD.get_role(int(roleId))
    
    await MAIN_GUILD.get_channel(int(botSettings["channelId"])).send(f'{role.mention}\n Don\'t forget to drink water! **Stay hydrated** 💦')



async def test():
    print("test")


async def schedule_loop():
    while True:
        schedule.run_pending()
        await asyncio.sleep(1)

client.run(botSettings["botId"])