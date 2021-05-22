
# import discord modules
import discord
from discord.ext import commands




# create bot instance
bot = commands.Bot(
    command_prefix=",",         # the prefix used for commands
    activity=discord.Game("Discord")
)


@bot.event
async def on_ready():
    print(f"{bot.user.name} is now online!")