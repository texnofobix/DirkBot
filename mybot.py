import configparser
import logging
import discord
import pyrcon
import asyncio
from discord.ext import commands

config = configparser.ConfigParser()
config.read('config.ini')
VERSION = '0.0.0.9'

logging.basicConfig(level=logging.INFO)
bot = commands.Bot(command_prefix=config['DEFAULT']['COMMAND_PREFIX'])
servername = config['DEFAULT']['SERVERNAME']
serverport = config['DEFAULT']['SERVERPORT']
rcon_password = config['DEFAULT']['RCON_PASSWORD']

conn = pyrcon.q2RConnection(servername, serverport, rcon_password)


async def my_background_task():
    await bot.wait_until_ready()
    #channel = discord.Object(id=config['DEFAULT']['DISCORD_CHANNELID'])
    lastmap=""
    lastplayercount=-1

    while not bot.is_closed:
        conn.status()

        if not (lastmap == conn.current_map and lastplayercount == len(conn.Players)):
            game_status=discord.Game(name="dday[{}] ({})".format(conn.current_map, len(conn.Players)))
            await bot.change_presence(game=game_status)
        
        lastmap=conn.current_map
        lastplayercount=len(conn.Players)
        print('now lastmap:',lastmap,' currentmap:',conn.current_map,' lastplayer:',lastplayercount,' playercount:',len(conn.Players))
        await asyncio.sleep(60) # task runs every 60 seconds


@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')


@bot.command()
async def info():
    embed = discord.Embed(title="DirkBot", description="Nicest q2bot there is ever.", color=0xeee657)
    embed.add_field(name="Author", value=config['DEFAULT']['AUTHOR'])
    embed.add_field(name="Bot Version", value=VERSION)
    await bot.say(embed=embed)

@bot.command()
async def status():
    """ Returns current map and players """
    await bot.say('``` {} ```'.format(conn.send('status')))

@bot.command()
@commands.has_role(name=config['DEFAULT']['DISCORD_ROLE']) #[,
async def changemap(mapname: str):
    """ Changes map if given role: server-lord """
    conn.changemap(mapname)
    await bot.say('requested map change to: {}'.format(mapname))

@bot.command()
@commands.has_role(name=config['DEFAULT']['DISCORD_ROLE']) #[,
async def rawcommand(*, arg : str):
    """ Issues a raw command if given role: server-lord """
    await bot.say('Sending "{}"'.format(arg))
    result = conn.send(arg)
    await bot.say('result of "{}": ```{}```'.format(arg,result))

bot.loop.create_task(my_background_task())

while True:
    bot.run(config['DEFAULT']['SECRET_KEY'])
