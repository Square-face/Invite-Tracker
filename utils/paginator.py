import discord, asyncio
from discord.ext import commands, menus
from typing import Union, List


class Paginator(menus.Menu):
    """Navigate menu with reactions.

    Navigate a menu by reaction to reactions. a list of pages is passed and a
    start page. The start page is 0 by default. When the start function is ran
    and there is no specified message a new one will be sent. If there is one
    the reactions will be added to that message.
    There exists 5 buttons and 2 more planed.

    The 5 existing ones are:
    FIRST:  Witch navigates to the first page in the list of pages
    BACK:   Witch navigates to the previous page in the list of pages
    STOP:   Witch stops the paginator from listening to reactions
    NEXT:   Witch moves to the next page in the list of pages
    LAST:   Witch moves to the last page in the list of pages.

    planed buttons:
    NUMBER: Choice a page to go to by sending a number in chat.
    INFO:   Show info on what all the buttons do.
    """
    def __init__(self, *, user:discord.User=None, users:List[discord.User]=None, page:int=0, pages:List[Union[discord.Embed, str]]=None, timeout:float=180.0, delete_message_after:bool=False, clear_reactions_after:bool=True, check_embeds:bool=True, message:discord.Message=None, replace_footer:bool=True):
        """
        Defining all variables for paginator.

        args
        ----
        page: Optional[:class:`int`]
            The currently selected page. First page is 1. Defaults to 1


        kwargs
        ------
        user: Optional[:class:`discord.User`]
            The user who can edit this paginator.
            Can be None if anyone should be able to edit the paginator. Defaults
            to None.
        users: Optional[List[:class:`discord.User`]]
            A list of user who can edit this paginator. If user arg was
            specified this arg will be ignored. Can be None if anyone should be
            able to edit the paginator. Defaults to None.
        timeout: Optional[:class:`float`]
            The amount of time in seconds the user has between each reaction.
            If more time has passed the paginator will stop listen for reactions.
            Defaults to 120.0.
        delete_message_after: Optional[:class:`bool`]
            If the paginator should be deleted when the exit/stop button is
            pressed or the timeout is reached. Defaults to False.
        clear_reactions_after: Optional[:class:`bool`]
            If the paginator should clear all reactions when the exit/stop
            button is pressed or the timeout is reached. Defaults to True.
        check_embeds: Optional[:class:`bool`]
            If wther to verify embed permissions. Should not be active if the
            paginator doesn't contain any embeds. Defaults to True.
        message: Optional[:class:`discord.Message`]
            The message this paginator is active on. Set to None if a new
            message should be created. Defaults to None
        replace_footer: Optional[:class:`bool`]
            If the paginator should try to replace embed footers to
            "Page: {current_page}/{total_pages}" when using them. Note that no
            embeds with a aledy set footer will have the replaced. This only
            applyes to embeds without footers. Defaults to True.
        """

        self.pages = pages or []
        self.page = page
        self.timeout = timeout
        self.delete_message_after = delete_message_after
        self.clear_reactions_after = clear_reactions_after
        self.replace_footer = replace_footer
        self.check_embeds = check_embeds
        self._can_remove_reactions = False
        self._Menu__tasks = []
        self._running = True
        self.message = message
        self.ctx = None
        self.bot = None
        self._author_id = None
        self._buttons = self.__class__.get_buttons()
        self._lock = asyncio.Lock()
        self._event = asyncio.Event()



    def add_page(self, page, index:int=None):
        """Add a new page

        Add a new page to this paginator.

        args
        ----
        page: List[:class:`discord.Embed`, :class:`str`]
            The page that will be added to the paginator.
        index: Optional[:class:`int`]
            The position for this page, if None the page will be added to the end.
            If the index is to large it will be treted as if it was None.
            Defaults to None.
        """

        if index is None:
            self.pages.append(page)
            return

        if index > len(self.pages)-1:
            self.pages.append(page)
            return

        if index < 0:
            self.pages.insert(0, page)
            return

        self.pages.insert(index, page)
        print(self.pages)


    def remove_page(self, index:int):
        """ Remove a page.

        Remove a page from the page list. If the index is under 0, the first
        page will be removed. If it is over the number of pages, the last page
        will be removed. If there are no pages nothing will be deleted.

        args
        ----
        index: :class:`int`
            the index of the page to be removed.
        """

        if len(self.pages) == 0:
            # if there are no pages, don't remove anything.
            return

        if index < 0:
            # if the index is below 0, remove first page
            self.pages.pop(0)
            return

        if index > len(self.pages)-1:
            # if index is over the ucrrent amount of pages, remove last page
            self.pages.pop(len(self.pages)-1)
            return

        # remove page with index specified
        self.pages.pop(index)




    def __fix_embed(self, embed, page):
        """Replace footer if posible

        Check if the embed has a footer, if it doesn't have,
        add one that says "Page: {current_page+1}/{total_pages}"

        args
        ----
        embed: :class:`discord.Embed`
            the embed object that will have its footer replaced if posible.
        page: :class:`int`
            the page for this embed.
        """
        if embed.footer:
            return embed

        current_page = page
        total_pages = len(self.pages)

        embed.set_footer(text=f"Page: {current_page+1}/{total_pages}")
        return embed


    def _get_message(self):
        """generate message edit coroutine

        Generates a coroutine to edit the paginator message. If replace_footer
        is active and the current page is a embed a attempt at setting a new one
        will be made.
        """

        page = self.pages[self.page]
        # get current page

        if isinstance(page, discord.Embed):
            # the page is a embed

            if self.replace_footer:
                # replace footer is active, try to replace the embed footer
                page = self.__fix_embed(page, self.page)

            # return message edit coroutine for embed page
            return self.message.edit(content=None, embed=page)

        # return message edit coroutine for text only page
        return self.message.edit(content=page, embed=None)




    async def send_initial_message(self, ctx, channel):
        """Start the paginator.

        Initiate the paginator if a message variable isn't alredy set.

        args
        ----
        ctx: :class:`discord.Context`
            the context for this paginator.
        channel: :class:`discord.TextChannel`
            the channel to send the initial message in.
        """

        page = self.pages[self.page]
        # get current page

        if isinstance(page, discord.Embed):
            # the page is a embed
            if self.replace_footer:
                # the footer should be replaced if posible
                page = self.__fix_embed(page, self.page)

            # send and return message object for embed page
            return await channel.send(embed=page)

        # send and return message object for text only page
        return await channel.send(page)




    @menus.button('\U000023ea')
    async def first(self, payload):
        """Go to first page in paginator.

        Set current page to 0 and update message.
        """

        # reset page
        self.page = 0

        # get coroutine for editing message
        send = self._get_message()

        # edit message
        await send


    @menus.button('\U000025c0')
    async def back(self, payload):
        """Go back one page in paginator.

        Set current page to one less than what it currently is and update message.
        If current page is 0 or lower, don't do anything.
        """
        if self.page <= 0:
            # if page is 0 or below, don't do anything
            return

        # lower current page by 1
        self.page -= 1

        # get coroutine for editing message
        send = self._get_message()

        # edit message
        await send


    @menus.button('\U000023f9')
    async def kill(self, payload):
        """Stop paginator.

        Stop listening for reactions and if clear_reactions_after is active all
        reactions will be removed. If delete_message_after is active the message
        will be removed.
        """

        # kill paginator
        self.stop()


    @menus.button('\U000025b6')
    async def forward(self, payload):
        """Go forward one page in paginator.

        Increase the current page by one and update message. If the current page is the total number of pages or above don't do anything.
        """
        if self.page >= len(self.pages)-1:
            # if current page is above or equal to total number of pages,
            # don't do anything.
            return

        # increase current page by 1
        self.page += 1

        # get coroutine for editing message
        send = self._get_message()

        # edit message
        await send


    @menus.button('\U000023e9')
    async def last(self, payload):
        """Go to last page in paginator.

        Set current page to last page and update message.
        """
        # set current page to total number of pages.
        self.page = len(self.pages)-1

        # get coroutine for editing message
        send = self._get_message()

        # edit message
        await send
