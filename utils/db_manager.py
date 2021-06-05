import asyncio
import aiomysql as mysql
from discord.ext.commands import Bot

class SubCache(object):
    
    def __init__(self, bot, table):
        self.bot = bot
        self.db = bot.db
        self.parent = bot.cache
        self.table = table
        self.data = []
    
    async def fetch(self):
        """Fetch all data from table for this subcache"""
        
        self.data = []
        
        
        cursor = await self.db.execute(f"SELECT * FROM {self.table}")
        results = cursor.fetchall()
        
        for result in results:
            self.data.append(result)

class blacklist(SubCache):
    pass


class Cache():
    """Cache manager
    
    A class to store cache data.
    Has multiple functions to make data managing easy.
    """
    def __init__(self, bot:Bot, db):
        self.bot    = bot   # the bot object
        self.bot.cache = self
        self.db     = db    # the database
        self.blacklist = blacklist(bot, "blacklist")

class DataBase():
    """Database manager.
    
    Connected to database and has some functions with prewritten
    queries that is used a lot.
    """
    
    class NotConnected(Exception):
        """Database hasn't been connected yet.
        
        If the database connection takes a while to setup or failed
        all together.
        """
        pass
    
    class ConnectionFailed(Exception):
        """if connecting to database failed"""
        
        pass
        
    
    def __init__(self, bot):
        self.bot = bot
        self.bot.db = self
        self.connected = False
        self.db = None
        self.loop = asyncio.get_event_loop()
        task = self.loop.create_task(self.connect())
        if not self.loop.run_until_complete(task):
            raise self.ConnectionFailed("Failed to connect to db")
    
    async def connect(self):
        """Connect database manager to database.
        
        Use config data to connect to database.
        """
        
        # creating asyncio loop
        loop = asyncio.get_event_loop()
        config = self.bot.config


        # Attempting to connect to database
        try:
            self.db = await mysql.create_pool(
                host = config.db.Host,
                port = config.db.Port,
                user = config.db.User,
                password = config.db.Password,
                db   = config.db.DBName,
                loop = loop
            )
        except Exception as e:
            print(e)
            return False
        else:
            # connection was successfully established
            
            print("\nSuccessfully connected to database!")
            self.connected = True
            
            # return database object
            return True
    
    
    async def execute(self, query:str, args:tuple=(), *, commit:bool=False):
        """Run a query to the database
        
        Execute a SQL query to the connected MariaDB server.
        Arguments can also be used but they have to be a tuple.
        
        args
        ----
        query: :class:`str`
            The query string to be executed.
        args: :class:`tuple`
            The arguments to be used with the query.
        
        kwargs
        ------
        commit: :class:`bool`
            If a commit should be run afterwards to commit any changes made.
        
        returns
        -------
        :class:``
        """
        
        if not self.connected:
            # if the database hasn't been connected yet, raise error
            raise self.NotConnected("Database connection has not been established yet.")
        
        async with self.db.acquire() as con:
            # get pool connection object
            
            async with con.cursor() as cursor:
                # get cursor object for this pool
                
                
                # execute query and save result
                await cursor.execute(query, args)
                
                
                if commit:
                    # commit to database if specified
                    await cursor.commit()
                
                # return cursor
                return cursor