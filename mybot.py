import configparser
import logging
import discord
import pyrcon
import asyncio
from discord.ext import commands

config = configparser.ConfigParser()
config.read('config.ini')
VERSION = '0.0.0.9c'

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

    while not bot.is_closed():
        try:
            conn.status() # bypass bug with pyrcon
        except:
            print('conn.status() fail')

        #if not (lastmap == conn.current_map and lastplayercount == len(conn.Players)):
        game_status=discord.Game("dday[{}] ({})".format(conn.current_map, len(conn.Players)))
        #await bot.change_presence(activity=game_status)
        
        lastmap=conn.current_map
        lastplayercount=len(conn.Players)
        print('now lastmap:',lastmap,' currentmap:',conn.current_map,' lastplayer:',lastplayercount,' playercount:',len(conn.Players))
        if lastplayercount > 0:
            await bot.change_presence(status=discord.Status.online, activity=game_status)
        else:
            await bot.change_presence(status=discord.Status.idle, activity=game_status)
        await asyncio.sleep(60) # task runs every 60 seconds



@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')


@bot.command()
async def info(ctx):
    embed = discord.Embed(title="DirkBot", description="Nicest q2bot there is ever.", color=0xeee657)
    embed.add_field(name="Author", value=config['DEFAULT']['AUTHOR'])
    embed.add_field(name="Bot Version", value=VERSION)
    await ctx.send(embed=embed)

@bot.command()
async def status(ctx):
    """ Returns current map and players """
    await ctx.send('``` {} ```'.format(conn.send('status')))

@bot.command()
@commands.has_role(config['DEFAULT']['DISCORD_ROLE']) #[,
async def changemap(ctx, mapname: str):
    """ Changes map if given role: server-lord """
    conn.changemap(mapname)
    await ctx.send('requested map change to: {}'.format(mapname))

@bot.command()
@commands.has_role(config['DEFAULT']['DISCORD_ROLE']) #[,
async def rawcommand(ctx, *, arg : str):
    """ Issues a raw command if given role: server-lord """
    await ctx.send('Sending "{}"'.format(arg))
    result = conn.send(arg)
    await ctx.send('result of "{}": ```{}```'.format(arg,result))

bot.loop.create_task(my_background_task())

while True:
    while True:
        bot.run(config['DEFAULT']['SECRET_KEY'])
