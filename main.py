# My modules
import json_manager

import os, sys, random
from typing import Optional
import discord
from discord import app_commands
import aiocron

userCrons = {} # [userId][aicronkey] = cron
USER_DATA_PATH = os.getcwd() + '/user_data/'

settings = json_manager.ReadFile(os.getcwd() + '/settings.json')
adminIds = settings['adminIds']
online_presence = settings['online-presence']

class MyClient(discord.Client):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents)        
        self.synced = False

    async def on_ready(self):
        if(not self.synced):
            await tree.sync()
            self.synced = True
            # LOAD ALL USER DATA AND CREATE CRONS FOR THEM
            for userFile in os.listdir(USER_DATA_PATH):
                data = json_manager.ReadFile(USER_DATA_PATH + userFile) # attempt to load existing data
                user = await client.fetch_user(int(userFile.split(".data")[0]))
                for aicronkey in data:                   
                    # Data storing
                    if not (user.id in userCrons):
                        userCrons[user.id] = {}
                        guild = client.get_guild(int(data[aicronkey]["guildId"]))                        
                    userCrons[user.id][aicronkey] = aiocron.crontab(aicronkey, func=reminder, start=True, args= (user, guild, data[aicronkey]["title"], data[aicronkey]["brief"], aicronkey)) # Cron creation 

            await changePresence()
            aiocron.crontab('0 */1 * * *', func=changePresence, start=True)
            print(f'Logged in as {client.user} (ID: {client.user.id}) \n------')

client = MyClient(intents=discord.Intents.default())
tree = app_commands.CommandTree(client)

#/- FUNCTIONS
def createEmbed(user, title, brief, aicronkey, *args):
    embed = discord.Embed(
        title=f"{title}", 
        description= f"{brief}", 
        color= discord.Color.blue()
    )
    embed.set_author(name= user.display_name, icon_url= user.display_avatar, url= f"https://www.discordapp.com/users/{user.id}"); 
    embed.set_footer(text= args[0], icon_url= (len(args) > 1) and args[1] or None)
    return embed

async def reminder(*args):
    user = args[0]
    guild = args[1]
    title = args[2]
    brief = args[3]
    aicronkey = args[4]    
    embed = createEmbed(user, title, brief, aicronkey, f'To disable this, please visit \'{guild.name}\'\n Then type \'/unsubscribe {aicronkey}\'', guild.icon)
    await user.send(embed=embed)

async def changePresence():
    await client.change_presence(activity= discord.Game(online_presence[random.randint(0, len(online_presence) - 1)]));

#/- COMMANDS
@tree.command(name="subscribe", description="I will DM you your reminder at a given time")
@app_commands.rename(title='title', brief='brief', aicronkey='aiocron_key')
@app_commands.describe(title='What is the title of this reminder?', brief='Tell me more about this reminder...', aicronkey='https://crontab.guru/ <- Visit this for keys')
async def self(interaction: discord.Interaction, title: str, brief: str, aicronkey: str):
    embed = createEmbed(interaction.user, title, brief, aicronkey, f'Will trigger on this key: \'{aicronkey}\'')    
    
    if(not aiocron.croniter.is_valid(aicronkey)):
        await interaction.response.send_message(f'Failed creating reminder... Please check aiocron key!', ephemeral=True)
        return    
    
    # Data storing
    if not (interaction.user.id in userCrons):
        userCrons[interaction.user.id] = {}
    userCrons[interaction.user.id][aicronkey] = aiocron.crontab(aicronkey, func=reminder, start=True, args= (interaction.user, interaction.guild, title, brief, aicronkey)) # Cron creation 

    thisUserData = USER_DATA_PATH + str(interaction.user.id) + '.data'
    data = {} # Create empty data dictionary...
    try:
        data = json_manager.ReadFile(thisUserData) # attempt to load existing data
    except:
        print(f'{interaction.user} save file not found... Creating one!')
        embed.set_footer(text= "This bot saves your reminders (UNENCRYPTED!)\n If this is of concern to you, please unsubscribe the reminder with \n\'/unsubscribe {aicronkey}\' and dont use this bot!")
    
    data[aicronkey] = { # Add a key to data...    
        "guildId" : interaction.guild.id,   
        "title" : title,
        "brief" : brief
    }
    json_manager.WriteFile(thisUserData, data)  

    print(f'{interaction.user} (ID: {interaction.user.id}) has created a reminder in \'{interaction.guild.name}\'! ({title} | {brief} | {aicronkey})')
    await interaction.response.send_message(embed= embed, ephemeral= True)

@tree.command(name="unsubscribe", description="This will unsubscribe you from your reminder")
@app_commands.rename(aicronkey='aiocron_key')
@app_commands.describe(aicronkey='https://crontab.guru/ <- Visit this for keys')
async def self(interaction: discord.Interaction, aicronkey: str):
    if not (aicronkey in userCrons[interaction.user.id]): 
        await interaction.response.send_message(f"There is no reminder under \'{aicronkey}\'!", ephemeral=True)
        return
    # Data removal
    userCrons[interaction.user.id][aicronkey].stop()
    userCrons[interaction.user.id].pop(aicronkey)

    thisUserData = USER_DATA_PATH + str(interaction.user.id) + '.data'
    data = {} # Create empty data dictionary...    
    try:
        data = json_manager.ReadFile(thisUserData) # attempt to load existing data
    except:
        await interaction.response.send_message("You do not have any reminders... To set one, please use the command '/subscribe'.", ephemeral=True)
        return
        
    if(not aicronkey in data):
        await interaction.response.send_message(f"You do not have a reminder under the key '{aicronkey}'", ephemeral=True)
        return
    
    data.pop(aicronkey)    
    #IF DATA LENGTH IS NONE, delete file!
    if(len(data) <= 0):
        os.remove(thisUserData)
    else:    
        json_manager.WriteFile(thisUserData, data)  

    print(f'{interaction.user} (ID: {interaction.user.id}) has unsubscribed a reminder in \'{interaction.guild.name}\'! ({aicronkey})')
    await interaction.response.send_message("Successfully unsubscribed from reminder!", ephemeral=True)

@tree.command(name="reminders", description="Show all your reminders and their times")
async def self(interaction: discord.Interaction):    
    thisUserData = USER_DATA_PATH + str(interaction.user.id) + '.data'
    data = {}
    try:
        data = json_manager.ReadFile(thisUserData)
    except:
        await interaction.response.send_message("You do not have any reminders... To set one, please use the command '/subscribe'.", ephemeral=True)
        return

    reminders = "**Your reminders are:**\n"
    for aicronkey in data:
        reminders += f'**({aicronkey})** {data[aicronkey]["title"]}: {data[aicronkey]["brief"]}\n'
    reminders += "To remove a reminder, type '/unsubscribe (aicronkey here)'"        
    await interaction.response.send_message(reminders, ephemeral= True)    
    
@tree.command(name="shutdown", description="Shuts the bot down")
async def self(interaction: discord.Interaction): 
    if(not (interaction.user.id in adminIds)): # Stops anyone but the admins to turn shut off the bot.
        await interaction.response.send_message(f'You do not have permission to run that command!', ephemeral= True)    
        return 

    print(f'{interaction.user} has shutdown the bot!')
    await interaction.response.send_message(f'Shutting down...', ephemeral= True)    
    sys.exit(0)

token = open('token.txt', 'r')
client.run(token.read())
token.close()
