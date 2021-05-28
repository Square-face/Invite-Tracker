import discord
from discord.ext import commands


class MyHelp(commands.HelpCommand):
    '''Show information about all commands, the commands in a module or a specific command.
    Uses a paginator so you can navigate without reinvoking the help command.'''
    
    async def send_bot_help(self, mapping):
        '''Show all commands and what modules they are in.'''
        
        # defining variables
        ctx = self.context
        bot = self.context.bot
        prefix = self.clean_prefix
        
        # create embed
        embed = discord.Embed(
            title=f"{bot.user.name} help"
        )
        
        return await ctx.send(embed=embed)

def setup(bot):
    bot._original_help_command = bot.help_command
    
    bot.help_command = MyHelp()
    bot.help_command.add_check(commands.bot_has_permissions(embed_links=True, send_messages=True))
    bot.help_command.cog = bot.cogs["Info"]