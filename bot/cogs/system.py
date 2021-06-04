import discord, difflib
from discord.ext import commands

class Settings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener("on_message_edit")
    async def edit_command(self, before, after):
        del before
        
        await self.bot.process_commands(after)
    
    @commands.Cog.listener("on_command_error")
    async def command_not_found(self, ctx, error):
        if not isinstance(error, commands.CommandNotFound):
            return
        
        command = ctx.message.content.split()[0][len(ctx.prefix):]
        
        command_list = []
        
        for cmd in self.bot.walk_commands():
            if cmd.hidden or cmd.cog.qualified_name == "Jishaku":
                continue
            
            command_list.append(cmd.qualified_name)
            
            for alias in cmd.aliases:
                command_list.append(alias)
        
        matches = difflib.get_close_matches(command, command_list, 5, 0.6)
        guessed_commands=[]
        
        for match in matches:
            guessed_commands.append(self.bot.get_command(match).qualified_name)
        
        guessed_commands=list(set(guessed_commands))
        
            
        if len(matches) > 0:
            await ctx.send(f":warning: **Command Not Found!**\nDid you mean:\n- `"+'`\n- `'.join(guessed_commands)+"`")




def setup(bot):
    bot.add_cog(Settings(bot))