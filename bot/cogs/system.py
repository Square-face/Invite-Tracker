import discord, difflib, datetime
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
        """Atempt at invoking a command that doesn't exist

        A user tried to invoke a command that doesn't exist.
        Try to find commands with matching names to the atempted commands.
        For example if the user misspelled a command name.
        """
        if not isinstance(error, commands.CommandNotFound):
            # if the error isn't a CommandNotFound error
            return

        # get the atempted command name
        command = ctx.message.content.split()[0][len(ctx.prefix):]

        # get list of all commands
        command_list = self.bot.get_normal_commands(await self.bot.is_owner(ctx.author))

        # the matches from command list to atempted command
        matches = difflib.get_close_matches(command, command_list, 5, 0.6)
        guessed_commands=[]

        for match in matches:
            # get actual command name for match
            guessed_commands.append(self.bot.get_command(match).qualified_name)

        # remove any dupes
        guessed_commands=list(set(guessed_commands))


        if len(matches) > 0:
            # if one or more matches was found, return them
            await ctx.send(f":warning: **Command Not Found!**\nDid you mean:\n- `"+'`\n- `'.join(guessed_commands)+"`")




    def get_config_channel(self, id: int=None):
        """Get a channel from id

        Take a channel id and make sure it is a valid id, a channel the bot has
        access to and that the bot has necessary permissions to send embeds in
        the channel.

        args
        ----
        id: :class:´int´
            The id for the channel. Can be None but that will automatically
            return None. Defaults to None.

        returns
        -------
        :class:`discord.TextChannel`
            The channel object retreaved from the id.
        :class:`NoneType`
            If the channel was invalid or didn't exist.
        """


        if id is None:
            # if the id is None
            return None

        # get channel object from id
        channel = self.bot.get_channel(id)

        if not channel:
            # the channe was None
            # the channel is invalid
            return None

        if channel.guild.me.permissions_in(channel).embed_links and channel.guild.me.permissions_in(channel).send_messages:
            # the bot has send messages permission as well as embed links permission
            return channel

        print(f"Missing permissions in {channel.name} for logging")
        return None




    @commands.Cog.listener("on_command")
    async def command_log(self, ctx):
        """A command was invoked

        This function gets called each time a user invokes a command on the bot.
        The function generates a log embed to send to a bot owner only channel
        for logging
        """

        # get channel
        channel = self.get_config_channel(self.bot.config.logging.Commands)

        if not channel:
            # invalid channel
            return


        # generate embed
        embed = discord.Embed(
            title=f'A command was used!',
            description = ctx.message.content,
            color=0x00FF00,
            timestamp=datetime.datetime.utcnow()
        ).set_author(
            name=ctx.author,
            icon_url=ctx.author.avatar_url
        ).add_field(
            name="User",
            value=f'Name: `{ctx.author.name}`\nDiscriminator: `{ctx.author.discriminator}`\nID: `{ctx.author.id}`',
            inline=False
        ).add_field(
            name="Server",
            value=f'Name: `{ctx.guild.name}`\nID: `{ctx.guild.id}`\nOwner: `{ctx.guild.owner}`',
            inline=True
        ).add_field(
            name="Channel",
            value=f'Name: `{ctx.channel.name}`\nMention: {ctx.channel.mention}\nID: `{ctx.channel.id}`',
            inline=True,
        )

        # send logging embed
        await channel.send(embed=embed)





    @commands.Cog.listener("on_guild_join")
    async def guild_join_log(self, guild):
        """A guild was joined

        This function gets called each time the bot is added to a guild.
        The function generates a log embed to send to a bot owner only channel
        for logging
        """

        # get channel object
        channel = self.get_config_channel(self.bot.config.logging.Servers)

        if not channel:
            # invalid channel
            return

        # generate embed
        embed = discord.Embed(
            title=f'I was added to a server!',
            description=f'  Name: `{guild.name}`\n \
                            ID: `{guild.id}`\n \
                            Owner: `{guild.owner}`',
            color=0x00FF00,
            timestamp=datetime.datetime.utcnow()
        ).set_footer(
            text=guild.owner,
            icon_url=guild.owner.avatar_url
        ).set_thumbnail(
            url=guild.icon_url
        )

        # send embed
        await channel.send(embed=embed)




    @commands.Cog.listener("on_guild_remove")
    async def guild_leave_log(self, guild):
        """A guild was left

        This function gets called each time the bot gets removed from a guild.
        The function generates a log embed to send to a bot owner only channel
        for logging
        """

        # get channel object
        channel = self.get_config_channel(self.bot.config.logging.Servers)

        if not channel:
            # invalid channel
            return

        # generate embed
        embed = discord.Embed(
            title=f'I was removed from a server',
            description=f'  Name: `{guild.name}`\n \
                            ID: `{guild.id}`\n \
                            Owner: `{guild.owner}`',
            color=0xFF0000,
            timestamp=datetime.datetime.utcnow()
        ).set_footer(
            text=guild.owner,
            icon_url=guild.owner.avatar_url
        ).set_thumbnail(
            url=guild.icon_url
        )

        # send embed
        await channel.send(embed=embed)




def setup(bot):
    bot.add_cog(Settings(bot))
