import discord, datetime, humanize
from discord.ext import commands



class Info(commands.Cog):
    """Most commands that shows information are found in this module."""
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name="bot_info", aliases=["bi", "botinfo"], brief="General information about me!")
    @commands.bot_has_permissions(use_external_emojis=True, embed_links=True, send_messages=True)
    async def ABCbot_info(self, ctx):
        '''Give information and statistics about the bot.
        Information given includes:
        - `Server count`
        - `User count`
        - `Start time`
        '''
        
        # how long the bot has been online
        online_time = humanize.naturaltime(datetime.datetime.utcnow()-self.bot.start_time)[:-4]
        
        # number of text and voice channels
        text_channels=[]
        voice_channels=[]
        
        # get Voice and Text Channel amount.
        for channel in self.bot.get_all_channels():
            if channel.type == discord.ChannelType.text:
                text_channels.append(channel)
                continue
            
            if channel.type == discord.ChannelType.voice:
                voice_channels.append(channel)
                continue
        
        
        # creating info embed
        embed = discord.Embed(
            title=f"{self.bot.user.name} Statistics and Information",
            description=f"{self.bot.user.name} has been online for `{online_time}` and is currently in `{len(self.bot.guilds)} server(s)` and can see `{len(self.bot.users)} user(s)`.",
            color=0xFF0000,
            timestamp=datetime.datetime.utcnow()
        ).set_author(
            name=self.bot.user.name,
            icon_url=self.bot.user.avatar_url
        ).add_field(
            name=f"Channels: {len(text_channels)+len(voice_channels)}",
            value=f"<:Text_Channel:778350926468743228> Text Channels: `{len(text_channels)}`\n<:Voice_Channel:778351389415440395> Voice Channels: `{len(voice_channels)}`"
        )
        
        # send embed
        return await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Info(bot))