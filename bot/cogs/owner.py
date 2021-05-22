'''Owner commands

Commands that can only be accessed by the bot owner(s).
'''


import discord, datetime
from discord.ext import commands


class Owner(commands.Cog):
    """Owner commands
    
    Commands that can only be invoked by bot owner(s).
    """
    
    def __init__(self, bot):
        """Init
        
        Initiate Cog variables

        Args:
        ----
        bot: :class:`commands.Bot`
            The bot object this Cog is part of.
        """
        self.bot = bot
    
    @commands.command()
    @commands.is_owner()
    async def dev(self, ctx:commands.Context):
        '''Developer bot info
        
        Shows information about the bot that only the developer has to know about.
        '''

        # create embed
        embed = discord.Embed(
            title=f"{self.bot.user.name} statistics",
            description=f"{self.bot.user.name} is currently in `{len(self.bot.guilds)} guilds(s)` and can see `{len(self.bot.users)} user(s)`.\nThe bot has a total of `{len(self.bot.commands)} command(s)` in `{len(self.bot.extensions)} module(s)`",
            color=0xFF0000,
            timestamp=datetime.datetime.utcnow()
        ).set_author(
            name=self.bot.user.name,
            icon_url=self.bot.user.avatar_url
        )
        
        # send embed
        return await ctx.send(embed=embed)



def setup(bot):
    bot.add_cog(Owner(bot))