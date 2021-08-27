'''Owner commands

Commands that can only be accessed by the bot owner(s).
'''


import discord, datetime, asyncio
from discord.ext import commands
from typing import Optional


# symbols
STOP    = "\U0001f6d1" # 🔁
RELOAD  = "\U0001f501" # 🛑


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

    def reload_cogs(self, cogs, ctx):
        '''Reload a list of cogs/modules

        Go through a list of cogs and reload the.
        For the ones that fails, save the error message
        and set success variable to false.
        The success variable is set to false when a cog has failed to reload.

        There might be a error if the cog failed to load last time around or if the cog hasn't been loaded from before.
        The function will ignore all

        Args:
        ----
        cogs: List[:class:`str`]
            A list of all the cogs that shall be reloaded.
        '''
        success, responses = True, []

        for cog in cogs:
            # go through each cog in cog list
            try:

                # try to load and unload the cog
                try:
                    self.bot.unload_extension(cog)

                except commands.errors.ExtensionNotLoaded:
                    pass

                # load the cog
                self.bot.load_extension(cog)

            except Exception as e:
                # the cog errored when loading

                # set success variable to false and add error message in response
                success = False
                responses.append(f"{self.bot.smart_emojis.get_emoji('no', ctx.channel)} {cog}:```cmd\n{e}```")

            else:
                responses.append(f"{self.bot.smart_emojis.get_emoji('yes', ctx.channel)} {cog}")


        # return response
        return responses, success

    async def retry_cogs(self, ctx:commands.Context, msg:discord.Message, cogs:list):
        '''Reload a list of cogs more than once

        This function tries to load a list of cogs, and if loading one fails the developer can react with the repeat reaction to try loading the cogs again.
        This can be done as many times as necessary to fix the issue

        Args:
        -----
        ctx: :class:`commands.Context`
            The current context
        msg: :class:`discord.Message`
            The active message
        cogs: List[:class:`str`]
            A list of the cogs to check for
        '''

        # refresh reactions
        await msg.clear_reactions()
        await msg.add_reaction(RELOAD)
        await msg.add_reaction(STOP)

        def validate_request(reaction, user) -> bool:
            '''Validating reaction

            Validate that the detected reaction was done by the author,
            was one of two options and on the right message.

            Args:
            -----
            reaction: :class:`discord.Reaction`
                The reaction object returned from reaction
            user: :class:`discord.User`
                The user who reacted
            '''
            valid_response = False
            
            if user == ctx.author:
                if reaction.emoji in [RELOAD, STOP]:
                    if reaction.message == msg:
                        valid_response = True
            
            return valid_response

        while True:
            try:
                # wait 2 minutes for a reaction on the message
                reaction, _ = await self.bot.wait_for("reaction_add", timeout=120.0, check=validate_request)

            except asyncio.TimeoutError:
                # 2 minutes passed without a reaction
                return await msg.clear_reactions()

            else:
                # a reaction was detected

                if reaction.emoji == STOP:
                    return await msg.clear_reactions()

                # reload the cogs and edit message
                await msg.edit(content=self.bot.smart_emojis.get_emoji("loading", ctx.channel))
                response, success = self.reload_cogs(cogs)
                await msg.edit(content="\n".join(response))

                if success:
                    return await msg.clear_reactions()

    @commands.command(hidden=True, brief="Some owner(s) only information about the bot.", aliases=["owner"])
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


    @commands.command(hidden=True, brief="Reload/load one or more modules.")
    @commands.is_owner()
    async def reload(self, ctx:commands.Context, *, cogs: Optional[str]):
        '''Use this command to reload one or more bot cogs/modules.

        Leave the `cogs` argument empty to reload all currently loaded cogs.
        Use the cog name and cog path (for example "bot.cogs.owner") to reload a
        specific cog. Use multiple cog paths to reload a specified list of cogs
        (for example "bot.cogs.owner bot.cogs.info") and remember to separate
        the cog names with spaces.
        '''


        if cogs:
            # if one or more cogs are specified
            # split them where there is spaces
            cogs = cogs.split()

        else:
            # if no cogs where specified reload the
            cogs = list(self.bot.extensions)

        # reload the cogs
        response, success = self.reload_cogs(cogs, ctx)

        if success:
            # all the cogs was successfully reloaded
            return await ctx.send("\n".join(response))

        # one or more cogs failed to reload correctly
        msg = await ctx.send("\n".join(response))

        # ask retry question
        await self.retry_cogs(ctx, msg, cogs)

    @commands.group(hidden=True, aliases=["bl"], brief="View and edit the blacklists for this bot")
    @commands.is_owner()
    async def blacklist(self, ctx):
        if ctx.invoked_subcommand:
            return

        await ctx.send("This is a decoy command")

    @blacklist.group(hidden=True, aliases=["u"], brief="Show blacklists for users")
    @commands.is_owner()
    async def user(self, ctx):
        """Show all blacklisted users

        Display every user who is currently blacklisted and their individual reasons.
        """

        if ctx.invoked_subcommand:
            return

        blacklists = {}

        for entry in self.bot.cache.blacklist.data:
            # go trough blacklisted users

            if entry[2] == "server":
                continue

            try:
                user = await self.bot.fetch_user(entry[1])
            except discord.errors.NotFound:
                user = entry[1]
            blacklists[user]=entry[3]

        await ctx.send(blacklists)

    @user.command(hidden=True, name="blacklist", aliases=["bl", "add", "a"], brief="blacklist a user")
    @commands.is_owner()
    async def add(self, ctx, subject_id:int, reason:str="No reason specified."):
        """Blacklist a user

        Add a user or a server to the bot's blacklist.
        """

        if subject_id in [d[1] for d in self.bot.cache.blacklist.data]:
            # fetch user from discord
            user = await self.bot.fetch_user(subject_id)

            # create response embed
            embed = discord.Embed(
                title=f"{user.name} is already blacklisted",
                description="This user is already blacklisted.",
                color=0xFF0000
            ).set_author(
                name=user.__str__(),
                icon_url=user.avatar_url
            )

            # send response
            return await ctx.send(embed=embed)


        # check if subject is user or server or invalid
        try:
            # attempt to fetch user from discord
            user = await self.bot.fetch_user(subject_id)

        except discord.errors.NotFound:
            # failed to fetch user, not a userid
            # invalid user
            return await ctx.send(f"Invalid user id.")


        # add user to database
        await self.bot.cache.blacklist.add(user.id, "user", reason)

        # create response embed
        embed = discord.Embed(
            title=f'{user.name} is now blacklisted.',
            description=reason,
            color=0x00FF00
        ).set_author(
            name=user.__str__(),
            icon_url=user.avatar_url
        )

        # send response
        return await ctx.send(embed=embed)



    @blacklist.command(hidden=True, aliases=["ubl", "remove", "r"], brief="UnBlacklist a user or server")
    @commands.is_owner()
    async def unblacklist(self, ctx, subject):
        await ctx.send(f"Unblacklisted \"{subject}\"")

def setup(bot):
    bot.add_cog(Owner(bot))
