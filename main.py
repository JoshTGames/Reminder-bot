# My modules
import os, sys

from typing import Optional
import discord
from discord import app_commands
import aiocron

userData = {}
class MyClient(discord.Client):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents)        
        self.synced = False

    async def on_ready(self):
        if(not self.synced):
            await tree.sync()
            self.synced = True
            print(f'Logged in as {client.user} (ID: {client.user.id}) \n------')
            await client.change_presence(activity= discord.Game("Reminding u to do things so u dont have to!"));

            



client = MyClient(intents=discord.Intents.default())
tree = app_commands.CommandTree(client)




@tree.command(name="subscribe", description="I will DM you your reminder at a given time")
@app_commands.rename(title='title', brief='brief', aiocronkey='aiocron_key')
@app_commands.describe(title='What is the title of this reminder?', brief='Tell me more about this reminder...', aiocronkey='https://crontab.guru/ <- Visit this for keys')
async def self(interaction: discord.Interaction, title: str, brief: str, aiocronkey: str):
    embed = discord.Embed(
        title=f"{title}", 
        description= f"{brief}", 
        color= discord.Color.blue()
    )
    embed.set_author(name= interaction.user.display_name, icon_url= interaction.user.display_avatar, url= f"https://www.discordapp.com/users/{interaction.user.id}"); 
    embed.set_footer(text= f'Will trigger on this key: \'{aiocronkey}\'')
    
    if(not aiocron.croniter.is_valid(aiocronkey)):
        await interaction.response.send_message(f'Failed creating reminder... Please check aiocron key!', ephemeral=True)
        return
    
    cron = aiocron.crontab(aiocronkey, func=reminder, start=True, args= (interaction, title, brief, aiocronkey))     
    # Data storing
    if not (interaction.user.id in userData):
        userData[interaction.user.id] = {}
    userData[interaction.user.id][aiocronkey] = cron
    print(f'{interaction.user} (ID: {interaction.user.id}) has created a reminder in \'{interaction.guild.name}\'! ({title} | {brief} | {aiocronkey})')
    await interaction.response.send_message(embed= embed, ephemeral= True)

@tree.command(name="unsubscribe", description="This will unsubscribe you from your reminder")
@app_commands.rename(aiocronkey='aiocron_key')
@app_commands.describe(aiocronkey='https://crontab.guru/ <- Visit this for keys')
async def self(interaction: discord.Interaction, aiocronkey: str):
    if not (aiocronkey in userData[interaction.user.id]): 
        await interaction.response.send_message(f"There is no reminder under \'{aiocronkey}\'!", ephemeral=True)
        return
    # Data removal
    userData[interaction.user.id][aiocronkey].stop()
    userData[interaction.user.id].pop(aiocronkey)

    print(f'{interaction.user} (ID: {interaction.user.id}) has unsubscribed a reminder in \'{interaction.guild.name}\'! ({aiocronkey})')
    await interaction.response.send_message("Successfully unsubscribed from reminder!", ephemeral=True)

async def reminder(*args):
    interaction = args[0]
    title = args[1]
    brief = args[2]
    aiocronkey = args[3]

    embed = discord.Embed(
        title=f"{title}", 
        description= f"{brief}", 
        color= discord.Color.blue()
    )
    embed.set_author(name= interaction.user.display_name, icon_url= interaction.user.display_avatar, url= f"https://www.discordapp.com/users/{interaction.user.id}"); 
    embed.set_footer(text= f'To disable this, please visit \'{interaction.guild.name}\'\n Then type \'/unsubscribe {aiocronkey}\'', icon_url= interaction.guild.icon)

    await interaction.user.send(embed=embed)

"""
@tree.command(name="restart", description="Restarts the bot")
async def self(interaction: discord.Interaction):
    await interaction.response.send_message(f'Restarting the bot...', ephemeral= True)
    os.execl(sys.executable, 'python', 'main.py')
"""

@tree.command(name="shutdown", description="Shuts the bot down")
async def self(interaction: discord.Interaction):    
    await interaction.response.send_message(f'Shutting down...', ephemeral= True)    
    sys.exit(0)




token = open('token.txt', 'r')
client.run(token.read())
token.close()
