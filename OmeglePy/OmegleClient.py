import asyncio
import random
from typing import Optional, Union, List

from OmeglePy import OmeglePy, AbstractEventHandler


class OmegleClient(OmeglePy):
    """
    A client for high-level interaction with the base OmeglePy client.

    """

    def __init__(self, event_handler: AbstractEventHandler, wpm: Optional[int] = 42, **kwargs) -> None:
        """

        :param event_handler: The event handler to run the client with
        :param wpm: The words-per-minute for typing messages with the write() method
        :param kwargs: Optional kwargs belonging to the parent OmeglePy. Anything passed here will be passed there

        """
        super().__init__(event_handler, **kwargs)
        self.wpm: int = wpm

    def _typing_time(self, length: int) -> float:
        """
        Calculates the time it should take to type a message based on the WPM

        :param length: The length of the item
        :return: The time calculated for this item
        """

        return (60 / self.wpm) * (length / 5)

    async def skip(self):
        """
        Go to the next user

        """
        await self.disconnect()
        await self.connect()

        # Send a custom event
        await self._handle_event(['clientSkip'])

    async def write(self, text: str):
        """
        Wraps a layer on top of the send class
        to emulate a regular user's typing experience

        :param text: The message to simulate writing for

        """

        # Can't send an empty message
        if not len(text):
            return

        # Start typing
        await self.typing()

        # Sleep the proper amount necessary to write the message
        await asyncio.sleep(self._typing_time(len(text)))

        # Send the message
        await self.send(text)

        # Stop typing
        await self.stop_typing()

    async def send(self, text: str) -> None:
        """
        Attempt to send a message directly through Omegle's API

        :param text: The message to send

        """

        url: str = self.SEND_URL % self.server
        data: dict = {'msg': text, 'id': self.client_id}

        # Make the request
        await self._request(url, data)
        await self._handle_event(['clientMessage', text])

    async def typing(self) -> None:
        """
        Emulates typing in the conversation

        """

        url: str = self.TYPING_URL % self.server
        data: dict = {'id': self.client_id}

        # Make the request
        await self._request(url, data)
        await self._handle_event(['clientTyping'])

    async def stop_typing(self) -> None:
        """
        Emulates stopping typing in the conversation

        """

        url: str = self.STOPPED_TYPING_URL % self.server
        data: dict = {'id': self.client_id}

        # Make the request
        await self._request(url, data)
        await self._handle_event(['clientStoppedTyping'])

    async def status(self) -> Union[dict, None]:
        """
        Return connection status

        """

        no_cache = '%r' % random.random()
        url = self.STATUS_URL % (self.server, no_cache, self.random_id)

        return await self._request(url)

    async def connect(self) -> str:
        """
        Override the main method to introduce a QOL connected user count

        """

        # Get the status
        status = await self.status()

        # Send an event with the # of connected users
        try:
            self.loop.create_task(self._handle_event(['onlineCount', status['count']]))
        except:
            pass

        return await super(OmegleClient, self).connect()

    async def set_topics(self, topics: List[str]):
        """
        Set your client's topics

        :param topics: The new topics for the client

        """

        self.topics = topics
        await self._handle_event(['clientChangedTopics', self.topics])




