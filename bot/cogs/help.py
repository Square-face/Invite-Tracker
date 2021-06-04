import discord
from discord.ext import commands
import utils.paginator as pages


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

                # add the command to command list
                commands.append(f"`{cmd.name:10}` - {cmd.brief}")

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
        
        Information includes: commands ond cog description'''
        
        # defining variables
        ctx = self.context
        bot = self.context.bot
        prefix = self.clean_prefix
        
        if cog.qualified_name == "Jishaku" and not await bot.is_owner(ctx.author):
            return await ctx.send(f'No command called "{cog.qualified_name}" found.')
        
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
            # if no commands existed for this cog, ignore it and send error message
            return await ctx.send(f'No command called "{cog.qualified_name}" found.')
        
        # add the commands to help embed
        embed.add_field(
            name="Commands",
            value="\n".join(command_list)
        )
        
        # send embed
        return await ctx.send(embed=embed)
        
    def generate_command_embed(self, bot, prefix, command):
        embed=discord.Embed(
            title=f"{command.name} help",
            description=f"{command.help}",
            color=bot.config.Color
        ).add_field(
            name="Syntax",
            value=f"`{prefix}{command.name} {command.signature}`",
            inline=False
        )



        aliases="No aliases."

        if len(command.aliases) > 0:
            aliases=f"`{'` | `'.join(list(command.aliases))}`"

        sub = "No subcommands."

        if isinstance(command, commands.Group):

            if len(command.commands) > 0:
                aliases=f"`{'` | `'.join(list(command.commands))}`"

        embed.add_field(name="Aliases", value=aliases)
        embed.add_field(name="Subcommands", value=sub)
        embed.add_field(name="Module", value=command.cog.qualified_name.capitalize())

        return embed

    async def send_command_help(self, command):
        """Show info on a command.

        Make a paginator with all the commands and the first page is the requested command.
        """

        # get variables
        ctx = self.context
        bot = ctx.bot
        prefix = self.clean_prefix

        # list of commands
        command_list = []


        for cog in bot.cogs.values():
            # go through all bot cogs.

            for cmd in cog.walk_commands():
                # go through all commands in this cog.

                if cmd.hidden and not await bot.is_owner(ctx.author):
                    # ignore all hidden commands as long as the author is not a bot owner
                    continue

                if cmd.cog.qualified_name == "Jishaku":
                    # ignore all jishaku commands
                    continue

                command_list.append(cmd)


        try:
            # try to find command in command list
            command_index = command_list.index(command)
        except ValueError:
            # the command was not found,
            # therefor its a hidden command.
            return await ctx.send(f"No command called \"{ctx.message.content.split(' ')[1]}\" found")



        paginator = pages.Paginator(page=command_index)
        # create paginator


        for cmd in command_list:
            # loop through commands in command list

            if isinstance(cmd, commands.Command):
                # create embed and add to paginator
                embed = self.generate_command_embed(bot, prefix, cmd)
                paginator.add_page(embed)

        # start paginator
        await paginator.start(ctx)

def setup(bot):
    bot._original_help_command = bot.help_command

    bot.help_command = MyHelp(command_attrs={"brief":"Get information about my commands!"})
    bot.help_command.add_check(commands.bot_has_permissions(embed_links=True, send_messages=True))
    bot.help_command.cog = bot.cogs["Info"]
