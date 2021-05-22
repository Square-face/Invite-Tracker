'''Start the bot.

Start the bot and all files that has to be started before it.
'''

from utils.config import Config
import bot.main as Bot

if __name__ == "__main__":
    
    # initiating config instance
    config = Config()
    
    # initiating bot instance and setting config variable
    bot = Bot.InviteTracker(config)
    
    
    # load extensions
    bot.load_extensions()
    
    # running bot
    bot.ignite(config.Token)