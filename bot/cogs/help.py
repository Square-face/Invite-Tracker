import discord
from discord.ext import commands
from utils.paginator import Paginator
from typing import Union


class MyHelp(commands.HelpCommand):
    '''Show information about all commands, the commands in a module or a specific command.
    Uses a paginator so you can navigate without reinvoking the help command.'''

    async def send_bot_help(self, mapping):
        '''Show all commands and what modules they are in.
        
        Go trough each cog/module and its corresponding commands.
        Make a embed showing all the cogs and their commands.
        '''

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
            # go through all extensions
            
            if extension.qualified_name == "Jishaku":
                # ignore the extension if it was Jishaku
                continue

            # a list of all the available commands in this extensions
            commands = []

            for cmd in extension.walk_commands():
                # go through all commands

                if cmd.hidden and not await bot.is_owner(ctx.author):
                    # if the command is hidden and the author is not a bot owner
                    continue
                
                if cmd.parent:
                    # if the command is a subcommand, ignore it
                    continue

                # add the command to command list
                commands.append(f"`{cmd.name:12}` - {cmd.brief}")

            if len(commands) == 0:
                # ignore this extension if it didn't have any commands
                continue

            # add the extension to embed with all of its commands
            embed.add_field(
                name=extension.qualified_name,
                value='\n'.join(commands),
                inline=False
            )

        # send help embed
        return await ctx.send(embed=embed)

    async def send_cog_help(self, cog):
        '''Send information about a module
        
        Show a cogs description and its command.
        The commands should also have their brief description as well
        as their signatures
        '''
        
        # defining variables
        ctx = self.context
        bot = self.context.bot
        prefix = self.clean_prefix
        is_owner = await bot.is_owner(ctx.author)
        
        if cog.qualified_name == "Jishaku" and not is_owner:
            # ignore all commands from Jishaku cog if the author is
            # not a bot owner
            await ctx.send(f'No command called "{cog.qualified_name}" found.')
            return
        
        # creating help embed
        embed = discord.Embed(
            color=bot.config.Color,
            title=f"{cog.qualified_name} help",
            description=cog.description
        )
        
        # lift of available commands 
        command_list = []
        
        for cmd in cog.get_commands():
            # go through all the commands in this cog
            if cmd.hidden and not await bot.is_owner(ctx.author):
                # ignore the command if it is hidden
                continue
            
            
            aliases = [cmd.qualified_name]
            # list of all the names this command has
            # the original name will always be added first
            
            for alias in cmd.aliases:
                # go trough its aliases and add them
                aliases.append(alias)
            
            # add the command to command list
            command_list.append(f"`{prefix}[{'|'.join(aliases)}]`\n - {cmd.brief}\n")
        
        
        if len(command_list) == 0:
            # if no commands existed for this cog,
            # ignore it and send error message
            await ctx.send(f'No command called "{cog.qualified_name}" found.')
            return
        
        # add the commands to help embed
        embed.add_field(
            name="Commands",
            value="\n".join(command_list)
        )
        
        # send embed
        await ctx.send(embed=embed)
        return
        
        
        
        
    def generate_command_embed(self, command) -> discord.Embed:
        """Generate embed object for command
        
        Generate a help embed for a command. Works with both commands and
        groups. Info that will be shown includes, command name, command
        description, syntax, command aliases, its module and if possible,
        its subcommands
        
        args
        ----
        command: Union[:class:`commands.Command`, :class:`commands.Group`]
            the command to generate embed for
        
        returns
        -------
        :class:`discord.Embed`
            the embed object for this command
        """
        
        # defining variables
        ctx     = self.context
        bot     = ctx.bot
        prefix  = self.clean_prefix
        
        # generate syntax
        base_command = f"{prefix}{command.qualified_name}"
        
        if not command.signature:
            # if it has no variables that has to be passed
            # just use the prefix + command WITHOUT a space after.
            syntax = f"`{base_command}`"
        else:
            # if the command has a signature,
            # use prefix + command + " " + signature
            # the space is important for the formating
            syntax = f"`{base_command} {command.signature}`"
        
        # create base embed
        embed=discord.Embed(
            title=f"{command.name} help",
            description=f"{command.help or 'This command has no description!'}",
            color=bot.config.Color
        ).add_field(
            name="Syntax",
            value=syntax
        )
        
        # what module this command is from
        embed.add_field(
            name    = "Module",
            value   = command.cog.qualified_name.capitalize(),
            inline=False
        )
        
        # if the command is a subcommand, show its parent(s)
        if command.parent:
            embed.add_field(
                name="Parent(s)",
                value=f'`{command.full_parent_name.replace(" ", "` > `")}`'
            )

        # --adding the aliases--
        
        # default text
        aliases="No aliases."

        # if the command has no aliases, set the value to "No aliases."
        if len(command.aliases) > 0:
            
            # the command has aliases
            aliases=f"`{'` | `'.join(list(command.aliases))}`"
        
        # add field
        embed.add_field(
            name    = "Aliase(s)", 
            value   = aliases
        )
        
        
        # --adding the subcommands
        if isinstance(command, commands.Group):
            # this is only done if the command is a group
            # normal commands can't have subcommands
            
            # default text
            sub = "No subcommands"
            
            # if the command has no subcommands,
            # set the value to "No subcommands."
            if len(command.commands) > 0:
                
                # the command has subcommands
                
                # generate list with all subcommand names
                subcommands = [cmd.name for cmd in list(command.commands)]
                sub=f"`{'` | `'.join(subcommands)}`"
            
            # add the field
            embed.add_field(
                name    = "Subcommand(s)",
                value   = sub
            )

        # return compleated embed
        return embed




    def _is_valid(self, command: Union[commands.Command, commands.Group], is_owner:bool=False):
        """Is a command good to show to anyone
        
        Checks if the supplied command is hidden
        
        args
        ----
        command: Union[:class:`discord.Command`, :class:`discord.Group`]
            the command to check
        is_owner: Optional[:class:`bool`]
            if the author is a bot owner. Defaults to False.
        
        returns
        -------
        :class:`bool`
            if the command is valid or not
        """

        if is_owner:
            # if the user is a owner all other commands will be valid
            return True
        
        # if the command is not hidden, return True
        return not command.hidden




    async def generate_embeds_for_normal_command(self, command):
        """Generate a list of embeds for all the commands for this bot.
        
        A list of embeds for each and every command in the bot. This includes all
        commands with subcommands or so called "groups", they will have a special
        area for listing their subcommands. The function will also return the index
        for the command requested.
        
        args
        ----
        commands: Union[:class:`discord.Command`, :class:`discord.Group`]
        
        returns
        -------
        List[:class:`discord.Embed`]:
            A list with a embed for each command this bot has.
        
        :class:`int`
            The index in the embed list for the requested command.
        """
        
        # define variables
        embeds = []
        index = None
        ctx = self.context
        bot = ctx.bot
        attempted_command = ctx.message.content.split()[1]
        is_owner = await bot.is_owner(ctx.author)
        
        if command.cog.qualified_name == "Jishaku" and not is_owner:
            await ctx.send(f'No command called "{attempted_command}" found.')
            return
        
        for cog in bot.cogs.values():
            # go trough each cog this bot currently has active
            
            for cmd in cog.walk_commands():
                # go through each command in this cog
                
                if self._is_valid(cmd, is_owner) and not cmd.parent:
                    # if command is valid, create embed
                    embed=self.generate_command_embed(cmd)
                    embeds.append(embed)
                    
                    if cmd == command:
                        # if this command is the requested one, set the index
                        index = embeds.index(embed)

        return embeds, index

    
    async def generate_embeds_for_subcommand(self, command):
        """Generate a list of embeds for all the subcommands for this commands parent
        
        A list of embeds for each and every command in this commands parent. This includes all
        commands with subcommands or so called "groups", they will have a special
        area for listing their subcommands. The function will also return the index
        for the command requested.
        
        args
        ----
        commands: Union[:class:`discord.Command`, :class:`discord.Group`]
        
        returns
        -------
        List[:class:`discord.Embed`]:
            A list with a embed for each command this bot has.
        
        :class:`int`
            The index in the embed list for the requested command.
        """
        
        # define variables
        embeds = []
        index = None
        ctx = self.context
        bot = ctx.bot
        attempted_command = " ".join(ctx.message.content.split()[1])
        is_owner = await bot.is_owner(ctx.author)
        
        if command.cog.qualified_name == "Jishaku" and not is_owner:
            await ctx.send(f'No command called "{attempted_command}" found.')
            return
        
        for cmd in command.parent.commands:
            # go through each command in this cog
            
            if self._is_valid(cmd, is_owner):
                # if command is valid, create embed
                embed=self.generate_command_embed(cmd)
                embeds.append(embed)
                
                if cmd == command:
                    # if this command is the requested one, set the index
                    index = embeds.index(embed)

        return embeds, index
    
    
    
    
    async def send_command_help(self, command):
        """Show info on a command.

        Make a paginator with all the commands and the first page is the requested command.
        """
        # get variables
        ctx = self.context
        bot = ctx.bot
        attempted_command = " ".join(ctx.message.content.split()[1:])
        is_owner = await bot.is_owner(ctx.author)
        
        
        # return error if the command is hidden
        if command.hidden and not is_owner:
            await ctx.send(f'No command called "{attempted_command}" found.')
            return

        if command.parent:
            embeds, index = await self.generate_embeds_for_subcommand(command)
        else:
            embeds, index = await self.generate_embeds_for_normal_command(command)
        
        
        paginator = Paginator(page=index, pages=embeds)
        await paginator.start(ctx)
    
    async def send_group_help(self, command):
        """Show info on a command.

        Make a paginator with all the commands and the first page is the requested command.
        """
        # get variables
        ctx = self.context
        bot = ctx.bot
        attempted_command = " ".join(ctx.message.content.split()[1:])
        is_owner = await bot.is_owner(ctx.author)
        
        
        # return error if the command is hidden
        if command.hidden and not is_owner:
            await ctx.send(f'No command called "{attempted_command}" found.')
            return
        
        if command.parent:
            embeds, index = await self.generate_embeds_for_subcommand(command)
        else:
            embeds, index = await self.generate_embeds_for_normal_command(command)
        
        
        paginator = Paginator(page=index, pages=embeds)
        await paginator.start(ctx)


def setup(bot):
    bot._original_help_command = bot.help_command

    bot.help_command = MyHelp(command_attrs={"brief":"Get information about my commands!"})
    bot.help_command.add_check(commands.bot_has_permissions(embed_links=True, send_messages=True))
    bot.help_command.cog = bot.cogs["Info"]
