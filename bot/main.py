import datetime, os
from discord.ext.commands import Bot
from discord import Intents

class InviteTracker(Bot):
    '''Bot subclass.

    Base class for the bot.
    Contains more variables and usefull functions.

    Args:
    ----
    config: :class:`utils.config.Config`
        The config class for the config.yml file that stores data necessary to start the bot.
    '''

    def __init__(self, config):
        """Creating variables for bot subclass.

        Assign all the values for the bot subclass and init bot instance.

        Args:
        ----
        config: :class:`utils.config.Config`
            The config class for the config.yml file that stores data necessary to start the bot.
        """
        self.config=config
        self.start_time=datetime.datetime.utcnow()

        intents = Intents.default()
        intents.members = True
        super().__init__(
            command_prefix=self.config.Prefix,
            case_sensitive=False,
            intents=intents,
            description=self.config.Description
        )


    def ignite(self, token):
        '''Start bot

        Start the bot using its token.
        The token should be set in the config.yml file.
        This function should only be run once on startup.

        Args:
        -----
        token: :class:`str`
            The bot token. Set the Token value in config.yml.

        '''
        self.token = token
        self.run(self.token)


    async def on_ready(self):
        '''Bot has connected to discord

        Sets start time to currently UTC datetime and prints out startup message.
        '''

        self.start_time=datetime.datetime.utcnow()

        print(f"{self.user.name} is now online!")



    def load_extensions(self, extensions:list = ["jishaku", "bot.cogs.owner", "bot.cogs.info", "bot.cogs.system", "bot.cogs.help"]):
        '''Load bot extensions

        Load a list of bot extensions.
        Most if not all extensions must have "bot.cogs." before the file name as bot/cogs/ is the folder most of the extensions are in.
        The one exception is the jishaku extension as it is not a file in this project but a imported library.


        Args:
        ----
        extensions: :class:`list`
            A list of all the extension that should be loaded.
        '''

        if "jishaku" in extensions:
            os.environ["JISHAKU_NO_UNDERSCORE"] = "True"

        for extension in extensions:
            # go through extensions to load them

            precentage = round(((extensions.index(extension)+1)/len(extensions))*100)

            start = f"{precentage:3}% - "

            try:
                # attemt to load extension
                self.load_extension(extension)

            except Exception as e:
                # send error if loading extension failed
                print(f"{start}Failed to load extension: {extension}\n{e}\n")

            else:
                print(f"{start}Loaded extension: {extension}")
        return

    def get_normal_commands(self, is_owner:bool=False) -> list:
        """Get a list of all available commands.

        Generates a list of all the commands and groups that are not owner only
        and from the jishaku cog. Not that this function won't return any subcommands.

        args
        ----
        is_owner: :class:`bool`
            if the user who is to see these commands is a bot owner.


        returns
        -------
        List[Union[:class:`commands.command`, :class:`commands.group`]]
        """

        command_list = []

        for cog in self.cogs.values():
            # go through all cogs and the commands inside of each cog

            
            if cog.qualified_name == "Jishaku":
                # ignore the jishaku cog
                continue

            for cmd in cog.walk_commands():
                
                if cmd.parent:
                    # ignore all commands that has a parent command
                    continue

                if not cmd.hidden or is_owner:
                    # add the command if it is not hidden or the user is a bot owner.
                    command_list.append(cmd)


        return command_list


    def get_subcommands(self, is_owner:bool=False) -> list:
        """Get a list of all available subcommands.

        Generates a list of all the commands and groups that are not owner only
        and from the jishaku cog. Not that this function won't return any subcommands.

        args
        ----
        is_owner: :class:`bool`
            if the user who is to see these commands is a bot owner.


        returns
        -------
        List[Union[:class:`commands.command`, :class:`commands.group`]]
        """

        command_list = []

        for cog in self.cogs.values():

            # ignore the jishaku cog
            if cog.qualified_name == "Jishaku":
                continue

            for cmd in cog.walk_commands():
                
                if not cmd.parent:
                    # ignore all commands that doesn't have a parent command.
                    continue

                if not cmd.hidden or is_owner:
                    # add the command if it is not hidden and the user is not a bot owner.
                    command_list.append(cmd)


        return command_list
