from discord.ext.commands import Bot
from discord import Intents

class InviteTracker(Bot):

    def __init__(self, config):
        self.config=config
        
        intents = Intents.default()
        intents.members = True
        super().__init__(command_prefix=self.config.Prefix,
            case_sensitive=False,
            intents=intents
        )


    def ignite(self, token):
        self.token = token
        self.run(self.token)


    async def on_ready(self):
        print(f"{self.user.name} is now online!")


    def load_extensions(self, extensions:list = ["jishaku"]):
        
        for extension in extensions:
            try:
                self.load_extension(extension)
            except Exception as e:
                raise e
        
        return