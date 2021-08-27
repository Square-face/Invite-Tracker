"""Automatic Emoji permission check
Automaticaly check if a amoji is availible or not.
"""

class UnavailiblEmoji(Exception):
    """Emoji doesn't exist
    
    This exception is called if a emoji is unavailible.
    """
    pass

class Emojis():
    """Manage bot emojis

    Manage the availible emojis the bot has access to.
    ⚠️ means no emoji is set
    ❗❗ means the bot is missing necessary permissions to use the emoji
    ❗ means the bot does not have access to the emoji

    Args:
    -----
    bot: :class:`commands.Bot`
        The bot
    """

    def __init__(self, bot):
        self.bot = bot
        self.bot.smart_emojis = self
        self.emojis = bot.config.emojis

    def get_emoji(self, emoji:str, location):
        """Get emoji if availible

        Use this function to get a emoji instead of getting it
        directly from config as it can result in problems.
        """

        if self.emojis[emoji] == "": # the emoji is not set
            return "⚠️" # emoji isn't configured
        
        emojis = [e.__str__() for e in self.bot.emojis] # list of emoji names
        if not self.emojis[emoji] in emojis: # the emoji is not availible to bot
            return "❗" # emoji doesn't exist
        

        if location.guild is None: # the emoji can be used no matter what
            return self.emojis[emoji]
        
        # If the bot does not have 'use_external_emojis',
        # does the emoji exist in the guild emojis
        if not location.guild.me.permissions_in(location).use_external_emojis:
            if not self.emojis[emoji] in location.guild.emojis:
                return "‼️" # missing perms
        
        # return emoji
        return self.emojis[emoji]