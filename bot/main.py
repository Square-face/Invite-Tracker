import datetime
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
        super().__init__(command_prefix=self.config.Prefix,
            case_sensitive=False,
            intents=intents
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
        '''Bot has connected to discord API
        
        Sets start time to currently UTC datetime and prints out startup message.
        '''
        
        self.start_time=datetime.datetime.utcnow()
        
        print(f"{self.user.name} is now online!")


    def load_extensions(self, extensions:list = ["jishaku", "bot.cogs.owner", "bot.cogs.info", "bot.cogs.help"]):
        '''Load bot extensions
        
        Load a list of bot extensions.
        Most if not all extensions must have "bot.cogs." before the file name as bot/cogs/ is the folder most of the extensions are in.
        The one exception is the jishaku extension as it is not a file in this project but a imported library.
        
        
        Args:
        ----
        extensions: :class:`list`
            A list of all the extension that should be loaded.
        '''
        
        for extension in extensions:
            try:
                self.load_extension(extension)
            except Exception as e:
                raise e
        
        return