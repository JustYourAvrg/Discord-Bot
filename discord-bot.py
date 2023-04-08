import discord
from discord import app_commands
from discord.ext import commands
from colorama import Back, Fore, Style
import time
import datetime
import platform
import json
import requests
import asyncio
import aiohttp
import random
from datetime import timedelta

# some of the commands will have a comment that tells you if you need to edit it or not so, read through the code real quick
# to avoid and issues later

# if you don't know already you need to make a bot from the discord dev portal
# then you can get the bots invite link and invite it to your discord server
# and get the bots token through the dev portal, the token is very important so don't ever give it away

client = commands.Bot(command_prefix='.', intents=discord.Intents.all())

class PersistentViewBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents().all()
        super().__init__(command_prefix=commands.when_mentioned_or("."), intents=intents)
    async def setup_hook(self) -> None:
        self.add_view(VerifyButton())

client = PersistentViewBot()

@client.event
async def on_ready():
    prfx = (Back.BLACK + Fore.BLUE + time.strftime('%H:%M:%S UTC', time.gmtime()) + Back.RESET + Fore.WHITE + Style.BRIGHT)
    print(prfx + ' Logged in as ' + Fore.RED + client.user.name)
    print(prfx + ' Discord Version ' + Fore.RED + discord.__version__)
    print(prfx + ' Python Version ' + Fore.RED + str(platform.python_version()))
    synced = await client.tree.sync()
    print(prfx + " Slash Commands Synced " + Fore.WHITE + str(len(synced)) + " Commands")

@client.command()
@commands.has_permissions(administrator=True)
async def shutdown(ctx):
    await ctx.send('Shutting down the bot')
    await client.close()

@client.tree.command(name='hello', description='says hello')
async def hello(interaction: discord.Interaction):
    member = interaction.user
    await interaction.response.send_message("Hello " + member.mention)


@client.tree.command()
@app_commands.checks.has_permissions(ban_members = True)
async def ban(interaction: discord.Interaction, member:discord.Member):
    embed = discord.Embed(title="Ban", color=discord.Color.red())
    await member.ban()
    embed.add_field(name="Banned: ", value=f"{member.mention}")
    await interaction.response.send_message(embed=embed)

@client.tree.command(name="unban", description="unbans a banned member")
@app_commands.checks.has_permissions(ban_members = True)
async def unban(interaction: discord.Interaction, user:discord.User):
    embed = discord.Embed(title="Unban", color=discord.Color.red())
    await interaction.guild.unban(user)
    embed.add_field(name="Unbanned: ", value=f"{user.mention}")
    await interaction.response.send_message(embed=embed)
    

@client.tree.command()
@app_commands.checks.has_permissions(kick_members = True)
async def kick(interaction: discord.Interaction, member:discord.Member):
    embed = discord.Embed(title="Kick", color=discord.Color.red())
    await member.kick()
    embed.add_field(name="Kicked: ", value=f"{member.mention}")
    await interaction.response.send_message(embed=embed)

@client.tree.command(name='userinfo', description='Gets info on a user')
async def userinfo(interaction: discord.Interaction, member:discord.Member=None):
    if member == None:
        member = interaction.user
    roles = [role for role in member.roles]
    embed = discord.Embed(title='User Info', description=f'User info on user {member.mention}', color = discord.Color.blue(), timestamp = datetime.datetime.utcnow())
    embed.set_thumbnail(url=member.avatar)
    embed.add_field(name='ID', value=member.id)
    embed.add_field(name='Name', value=f'{member.name}#{member.discriminator}')
    embed.add_field(name='Nickname', value=member.display_name)
    embed.add_field(name='Status', value=member.status)
    embed.add_field(name='Created At', value=member.created_at.strftime("%a, %B, %#d, %Y, %I:%M %p "))
    embed.add_field(name='Joined At', value=member.joined_at.strftime("%a, %B, %#d, %Y, %I:%M %p "))
    embed.add_field(name=f'Roles ({len(roles)})', value=" ".join([role.mention for role in roles]))
    embed.add_field(name='Top Roles', value= member.top_role.mention)
    embed.add_field(name='Messages', value="0")
    await interaction.response.send_message(embed = embed)

@client.tree.command(name="serverinfo")
async def serverinfo(interaction: discord.Interaction):
    embed = discord.Embed(title="Server Info", description=f"Info on this server {interaction.guild.name}", color = discord.Color.blue(), timestamp = datetime.datetime.utcnow())
    embed.set_thumbnail(url=interaction.guild.icon)
    embed.add_field(name="Members", value=interaction.guild.member_count)
    embed.add_field(name="Owner", value=interaction.guild.owner.mention)
    embed.add_field(name="Created At", value=interaction.guild.created_at.strftime("%a, %B, %#d, %Y, %I:%M %p "))
    await interaction.response.send_message(embed=embed)


class VerifyButton(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    @discord.ui.button(label="Verify", style=discord.ButtonStyle.green, custom_id="verify")
    async def Verify(self, interaction: discord.Interaction, Button: discord.ui.Button):
        role = interaction.guild.get_role(1059831637736706118)
        await interaction.user.add_roles(role, atomic=True)
        await interaction.response.send_message("You have been verified", ephemeral=True)

@client.tree.command(name = "verify")
@commands.has_permissions(administrator = True)
async def verify(interaction: discord.Interaction):
    embed = discord.Embed(title="Verify", color=discord.Color.green())
    embed.add_field(name="Click the button to verify", value="You need to verify to access the server")
    await interaction.response.send_message(embed=embed, view=VerifyButton())


@client.event
async def on_member_join(member):
    channel = client.get_channel(1055999101025648671)
    embed = discord.Embed(title="Welcome", color=discord.Color.green(), timestamp=datetime.datetime.utcnow())
    embed.add_field(name="Welcome to the server", value=f"{member.mention}")
    await channel.send(embed=embed)

@client.event
async def on_member_remove(member):
    channel = client.get_channel(1055999101025648671)
    embed = discord.Embed(title="Goodbye", color=discord.Color.red(), timestamp=datetime.datetime.utcnow())
    embed.add_field(name="Goodbye :(", value=f"{member.mention}")
    await channel.send(embed=embed)

@client.command()
@commands.is_nsfw()
async def nsfw(ctx):
    embed = discord.Embed(title='NSFW', description=f'NSFW Picture requested by {ctx.author.mention}', color=discord.Color.red())
    async with aiohttp.ClientSession() as cs:
        async with cs.get('https://www.reddit.com/r/nsfw/new.json?sort=hot') as r:
            res = await r.json()
            embed.set_image(url=res['data']['children'] [random.randint(0, 25)]['data']['url'])
            await ctx.send(embed=embed)

@client.tree.command(name="discordidlookup", description="Lookup a users discord ID")
@app_commands.describe(id = "ID: ")
async def discordprofile(interaction: discord.Interaction, id: str):
    id_api_response = requests.get(f"https://api.leaked.wiki/discorduser?id={id}")
    json_id_data = json.loads(id_api_response.text)
    embed = discord.Embed(title="ID Info", description=f"Requested by {interaction.user.mention}", color=discord.Color.blue(), timestamp= datetime.datetime.utcnow())
    embed.set_thumbnail(url=interaction.guild.icon)
    embed.add_field(name="ID: ", value=json_id_data['id'])
    embed.add_field(name="Username: : ", value=json_id_data['username'])
    embed.add_field(name="Profile Picture: : ", value=json_id_data['avatar'])
    embed.add_field(name="Banner: : ", value=json_id_data['banner'])
    embed.add_field(name="Partial Token: ", value=json_id_data['partial_token'])
    await interaction.response.send_message(embed=embed, ephemeral=True)

@client.command()
@commands.is_nsfw()
async def hentai(ctx):
    embed = discord.Embed(title='NSFW', description=f'NSFW Picture requested by {ctx.author.mention}', color=discord.Color.red())
    async with aiohttp.ClientSession() as cs:
        async with cs.get('https://www.reddit.com/r/hentai/new.json?sort=hot') as r:
            res = await r.json()
            embed.set_image(url=res['data']['children'] [random.randint(0, 100)]['data']['url'])
            await ctx.send(embed=embed)

@client.tree.command(name="randomfact", description="Get a random fact")
async def randomfact(interaction: discord.Interaction):
    rand_fact_api = requests.get(url="https://api.leaked.wiki/randomfact")
    json_api_response = json.loads(rand_fact_api.text)
    embed = discord.Embed(title="Random fact", description=f"Requested by {interaction.user.mention}", color=discord.Color.blurple())
    embed.set_thumbnail(url=interaction.guild.icon)
    embed.add_field(name="Facts: ", value=json_api_response['fact'])
    await interaction.response.send_message(embed=embed)


@client.tree.command(name="randominsult", description="Get a random insult")
async def randominsult(interaction: discord.Interaction):
    rand_fact_api = requests.get(url="https://api.leaked.wiki/randominsult")
    json_api_response = json.loads(rand_fact_api.text)
    embed = discord.Embed(title="Random insult", description=f"Requested by {interaction.user.mention}", color=discord.Color.red())
    embed.set_thumbnail(url=interaction.guild.icon)
    embed.add_field(name="Insult: ", value=json_api_response['insult'])
    await interaction.response.send_message(embed=embed)

    
@client.tree.command(name="8ball", description="get a 8ball type response")
async def eightball(interaction: discord.Interaction):
    rand_fact_api = requests.get(url="https://api.leaked.wiki/8ball")
    json_api_response = json.loads(rand_fact_api.text)
    embed = discord.Embed(title="8ball", description=f"Requested by {interaction.user.mention}", color=discord.Color.blurple())
    embed.set_thumbnail(url=interaction.guild.icon)
    embed.add_field(name="8Ball: ", value=json_api_response['response'])
    await interaction.response.send_message(embed=embed)

@client.tree.command(name="iplookup")
@app_commands.describe(ip = "IP: ")
async def ipinfo(interaction: discord.Interaction, ip : str):
    ip_api_response = requests.get(f"http://ip-api.com/json/{ip}?fields=status,message,country,regionName,city,zip,isp,query") 
    json_ip_data = json.loads(ip_api_response.text)
    embed = discord.Embed(title="IP Lookup", description=f"Requested by {interaction.user.mention}", color=discord.Color.blue(), timestamp = datetime.datetime.utcnow())
    embed.add_field(name="IP: ", value=json_ip_data["query"])
    embed.add_field(name="ISP: ", value=json_ip_data["isp"])
    embed.add_field(name="STATE: ", value=json_ip_data["regionName"])
    embed.add_field(name="CITY: ", value=json_ip_data["city"])
    embed.add_field(name="ZIPCODE: ", value=json_ip_data["zip"])
    await interaction.response.send_message(embed=embed, ephemeral=True)


@client.tree.command(name="mute")
@app_commands.checks.has_permissions(manage_roles = True)
async def mute(interaction: discord.Interaction, member:discord.Member):
    embed = discord.Embed(title="Mute", description=f"Muted {member.mention}", color=discord.Color.red())
    remove_role = discord.utils.get(member.guild.roles, id=1059831637736706118)
    add_role = discord.utils.get(member.guild.roles, id=1060706938750509116)
    await member.remove_roles(remove_role)
    await member.add_roles(add_role)
    await interaction.response.send_message(f"Unmuted {member.mention}")
    await interaction.response.send_message(embed=embed)


@client.tree.command(name="unmute")
@app_commands.checks.has_permissions(manage_roles = True)
async def unmute(interaction: discord.Interaction, member:discord.Member):
    embed = discord.Embed(title="unmute", description=f"Unmuted {member.mention}", color=discord.Color.blurple())
    remove_role = discord.utils.get(member.guild.roles, id=1060706938750509116)
    add_role = discord.utils.get(member.guild.roles, id=1059831637736706118)
    await member.remove_roles(remove_role)
    await member.add_roles(add_role)
    await interaction.response.send_message(embed=embed)



@client.tree.command(name="ping", description="shows the bots response time in MS")
async def ping(interaction: discord.Interaction):
    embed = discord.Embed(color=discord.Color.blue())
    embed.add_field(name="Ping", value=f"{round(client.latency * 1000)} ms")
    await interaction.response.send_message(embed=embed)


@client.tree.command(name="clear", description="Clear a certain amount of messages")
@app_commands.checks.has_role('Staff')
@app_commands.describe(amount = "Amount: ")
async def clear(interaction: discord.Interaction, amount: int):
    embed = discord.Embed(color=discord.Color.red(), timestamp=datetime.datetime.utcnow())
    embed.add_field(name="Cleared", value=f"{amount} messages cleared")
    await interaction.response.send_message(embed=embed, ephemeral=True)
    await interaction.channel.purge(limit=amount)


@client.tree.command()
@app_commands.checks.has_permissions(manage_messages=True)
async def test(interaction: discord.Interaction):
    await interaction.response.send_message('You can manage messages.')

@client.tree.command(name="avatar", description="Displays a users discord profile picture")
async def avatar(interaction: discord.Interaction, user: discord.Member):
    pfp = user.display_avatar
    embed = discord.Embed(title="Avatar", color=discord.Color.dark_grey())
    embed.set_image(url=pfp)
    await interaction.response.send_message(embed=embed)

# you have to edit the code here
@client.tree.command(name="botinvite", description="gets the bot invite to add it to your server")
async def botinvite(interaction: discord.Interaction):
    embed = discord.Embed(title="Invite Links", color=discord.Color.blue())
    embed.set_thumbnail(url=interaction.guild.icon)
    # just edit this part for the "value"
    embed.add_field(name="---------------", value="[put the message for the invite command here](put the bots invite link here)", inline=True)
    await interaction.response.send_message(embed=embed, ephemeral=True)

# you need to get your own API key for this to work
@client.tree.command(name="ipping", description="pings an IP")
@app_commands.describe(ip="IP: ")
async def pinger(interaction: discord.Interaction, ip:str):
    ip_api_response = requests.get(f"https://api.viewdns.info/ping/?host={ip}&apikey=your-api-key-here&output=json") 
    json_ip_data = json.loads(ip_api_response.text)
    embed = discord.Embed(color=discord.Color.blurple())
    embed.add_field(name="IP: ", value=json_ip_data['query']['host'])
    embed.add_field(name="Ping: ", value=json_ip_data['response']['replys'])
    await interaction.response.send_message(embed=embed, ephemeral=True)

# you need to get your own API key for this to work
@client.tree.command(name="portscanner", description="Scans an IPs ports")
@app_commands.describe(ip="IP: ")
async def portscanner(interaction: discord.Interaction, ip:str):
    port_api_response = requests.get(url=f"https://api.viewdns.info/portscan/?host={ip}&apikey=api-key-here&output=json")
    json_api_data = json.loads(port_api_response.text)
    embed = discord.Embed(color=discord.Color.blue())
    embed.add_field(name="IP: ", value=json_api_data['query']['host'])
    embed.add_field(name="Ports: ", value=json_api_data['response']['port'])
    await interaction.response.send_message(embed=embed, ephemeral=True)

# add whatever words you want here
banned_words = [
    'child porn'
]

@client.event
async def on_message(message):
    if message.content in banned_words:
        await message.delete()
        embed = discord.Embed(title="Banned Word", description=f"Username: {message.author}" + "\n" + f"Banned Word: {message.content}" + "\n" + f"Message ID: {message.id}", color=0xFF0000)
        embed.set_footer(text=f"User ID: {message.author.id}")
        await message.channel.send(embed=embed)



# add your bot token here
client.run('YOUR BOTS TOKEN HERE')
