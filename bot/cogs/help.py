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
            color=bot.config.Color,
            title=f"{bot.user.name} help",
            description=bot.description
        )
        
        for extension in bot.cogs.values():
            
            if extension.qualified_name == "Jishaku":
                continue
            
            # a list of all the available commands in this extensions
            commands = []
            
            for cmd in extension.walk_commands():
                if cmd.hidden and not await bot.is_owner(ctx.author):
                    continue
                
                commands.append(f"`{cmd.name:10}` - {cmd.brief}")
            
            if len(commands) == 0:
                continue
            
            embed.add_field(
                name=extension.qualified_name,
                value='\n'.join(commands),
                inline=False
            )
        
        return await ctx.send(embed=embed)

def setup(bot):
    bot._original_help_command = bot.help_command
    
    bot.help_command = MyHelp(command_attrs={"brief":"Get information about my commands!"})
    bot.help_command.add_check(commands.bot_has_permissions(embed_links=True, send_messages=True))
    bot.help_command.cog = bot.cogs["Info"]