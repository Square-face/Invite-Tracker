'''Config manager.

Manage the config file and request attributes.
'''

import yaml
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper


class MissingKey(Exception):
    pass

class MissingValue(Exception):
    pass


class Sub():
    pass



class Config():
    """A Config manager

    A class for managing the bots config file.
    The Config file contains things as token and website info.
    This class is to help getting info and making sure the file has
    the right syntax.
    """



    def __init__(self, filename:str ="config.yml"):
        """Sett variables for config instance

        Args:
            filename (str, optional): The name of the config file. Defaults to "config.yml".
        """

        self.filename = filename
        self.file = open(self.filename, "r")
        self.stream = yaml.load(self.file.read(), Loader=Loader)

        self.CheckConfig()

        # values
        self.Token = self.stream["Token"]
        self.Prefix = self.stream["Prefix"]
        self.Color = self.stream["Color"]
        self.Description = self.stream["Description"]

        self.logging = Sub()
        self.logging.Servers    = self.stream["Servers"]
        self.logging.Commands   = self.stream["Commands"]
        self.logging.Errors     = self.stream["Errors"]
        self.logging.DMs        = self.stream["DMs"]
        self.logging.Website    = self.stream["Website"]
        self.logging.Events     = self.stream["Events"]

    def CheckConfig(self):
        """Check the config file

        Make sure all values are filled in config file.

        Returns:
            bool: Wether all values where filled or not.
        """

        file = open(self.filename, "r")
        stream = yaml.load(file.read(), Loader=Loader)

        args = [
            "Token", "Prefix", "Color", "Description", "Servers", "Commands", "Errors", "DMs", "Website", "Events"
        ] # all keys that has to be in config file
        can_be_empty = [
            "Color", "Servers", "Commands", "Errors", "DMs", "Website", "Events"
        ]            # they keys that can still be 0 or None

        for arg in args:
            if not arg in stream.keys():
                # the entire key is gone
                raise MissingKey(f"The '{arg}' key is missing in config file({self.filename}). Make sure you are using a up-to-date file.")

            if arg in can_be_empty:
                # the argument is allowed to be None
                continue

            if not stream[arg]:
                # there is no value for this argument
                raise MissingValue(f"No value for '{arg}' has been set. Make sure all values in the config file({self.filename}) is set right and restart the bot.")
