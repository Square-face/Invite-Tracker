'''Start the bot.

Start the bot and all files that has to be started before it.
'''

from utils.config import Config
from utils.db_manager import Cache, DataBase
import bot.main as Bot

if __name__ == "__main__":
    
    # initiating config instance
    config = Config()
    
    # initiating bot instance, set config and load extensions
    bot = Bot.InviteTracker(config)
    bot.load_extensions()
    
    # intiate cache and database
    DataBase(bot)
    Cache(bot, bot.db)
    
    # add db and cache to bot
    
    
    
    # connect database and run bot
    bot.ignite(config.Token)