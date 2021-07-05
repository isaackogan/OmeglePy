import asyncio
import random
import threading
import urllib
import json
import uuid
from typing import List, Optional, Any, Callable, Union

import aiohttp
from asyncio import AbstractEventLoop, Task

from aiohttp import ClientTimeout, TCPConnector

from OmeglePy.AbstractEventHandler import AbstractEventHandler


class ThreadedOmegle(threading.Thread):
    """
    Class for running omegle in a new thread instead of blocking the main one

    """

    def __init__(self, instance):
        self.instance = instance
        super().__init__()

    def run(self) -> None:
        """
        Block this thread with an instance of the OmeglePy base Client

        """

        self.instance.run()


class OmeglePy:
    """
    Creator's Note:

    A low level client for the bare minimum required to interface with the Omegle API.
    Implement your needed functionality on top of this class rather than editing it by
    inheriting this class. Between that, and your own event handler, you can fully control
    every single interaction you would reasonably make with Omegle, without editing this.

    Great source for learning about Omegle's backend:
    https://gist.github.com/nucular/e19264af8d7fc8a26ece

    """

    SERVER_LIST = [f'front{n}.omegle.com' for n in range(1, 40)]
    STATUS_URL = 'http://%s/status?nocache=%s&randid=%s'
    START_URL = 'http://%s/start?caps=recaptcha2,t&firstevents=%s&spid=%s&randid=%s&lang=%s&m=%s'
    RECAPTCHA_URL = 'http://%s/recaptcha'
    EVENTS_URL = 'http://%s/events'
    TYPING_URL = 'http://%s/typing'
    STOPPED_TYPING_URL = 'http://%s/stoppedtyping'
    DISCONNECT_URL = 'http://%s/disconnect'
    SEND_URL = 'http://%s/send'

    def __init__(
            self,
            event_handler: AbstractEventHandler,
            event_frequency: Optional[int] = 3,
            loop: Optional[AbstractEventLoop] = None,
            server: Optional[int] = None,
            topics: Optional[List[str]] = None,
            language: Optional[str] = None,
            debug: Optional[bool] = False,
            proxy: Optional[str] = None,
            mobile: Optional[bool] = False,
            unmonitored: Optional[bool] = False,
            display_unhandled_events: Optional[bool] = True,
            socket_connect_timeout: Optional[int] = 15,
            socket_read_timeout: Optional[int] = 40
    ):
        """
        Create an instance of the omegle client

        :param event_handler: The event handler for events to be passed into
        :param event_frequency: The frequency in which requests are made to retrieve events
        :param loop: An asyncio loop if you want to pass one in if one has already been created
        :param server: The omegle server (integer #) to connect to
        :param topics: A list of topics you want to search for in common with others
        :param language: The two-letter language code (e.g: en)
        :param debug: Whether or not you want debug logs in the console
        :param proxy: An optional proxy if you want one of those
        :param mobile: Whether or not to connect as a mobile client
        :param unmonitored: Whether or not to enter the unmonitored section
        :param socket_connect_timeout: The max time (seconds) to connect to the socket during a request
        :param socket_read_timeout: The max time (seconds) to read from a socket during a request

        """

        # Backend objects passed in for functionality
        self.loop: AbstractEventLoop = asyncio.get_event_loop() if loop is None else loop
        self.handler: AbstractEventHandler = event_handler

        # The server to connect to
        self.server: Optional[str] = random.choice(self.SERVER_LIST) if server is None else self.SERVER_LIST[server - 1]

        # Preferences
        self.event_frequency: int = event_frequency
        self.proxy: str = proxy
        self.language: str = 'en' if not language else language
        self.mobile: bool = mobile
        self.unmonitored: bool = unmonitored
        self.debug: bool = debug
        self.topics: Optional[List[str]] = None if not topics else topics
        self.display_unhandled: bool = display_unhandled_events
        self.socket_read_timeout: int = socket_read_timeout
        self.socket_connect_timeout: int = socket_connect_timeout

        # Auto-updated variables for caching
        self.task: Optional[Task] = None
        self.client_id: Optional[str] = None
        self.random_id: Optional[str] = None
        self.thread: Optional[threading.Thread] = None
        self.connected: bool = False
        self.running: bool = False
        self.uuid: Optional[str] = None
        self.sep: Any = asyncio.Semaphore(10)  # 10 is the initial resource count for the Semaphore

    @staticmethod
    def __get_headers(url: str, tld: str, mobile: bool = False) -> dict:
        """
        Generate headers for a URL to better masquerade as a user

        :param url: The URL you are requesting
        :param tld: The TLD of the domain you are requesting it for

        :return: A dict of headers to pass into a request

        """
        return {

            'Accept-Language': "en-US:en;q=0.8",
            "Referer": "https://www.omegle.com/",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "authority": "https://www.omegle.com",
            "path": url[url.find(tld) + len(tld):].strip(),
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive",
            "Host": url[url.find("//") + 2:url.find(tld) + len(tld)],
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36"
                if not mobile else
                "Mozilla/5.0 (Linux; Android 7.0; SM-G930V Build/NRD90M) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.125 Mobile Safari/537.36"
            )

        }

    async def _request(self, url: str, data: Optional[dict] = None) -> dict:
        """
        Make an asynchronous request with an automatic swap
        between post & get depending on if data is supplied

        :param url: The URL to make the request to
        :param data: The (optional) data to make a POST request

        :return: The result of the request as a dict. If no JSON is provided, a dict will be generated with "result" = text response

        """

        # Debug Outbound
        if self.debug:
            print("\033[31m" + '-> Outbound Request', url + "\033[0m")

        # Cache the proxy (for logging, in case it changes)
        cached_current_proxy: str = str(self.proxy)

        try:

            # Set a timeout for the request to prevent A) Timing out the Semaphore and B) just generally creating stalled requests
            session_timeout: ClientTimeout = aiohttp.ClientTimeout(total=None, sock_connect=self.socket_connect_timeout, sock_read=self.socket_read_timeout)

            # Force it to close the TCP connection after each request
            connector: TCPConnector = aiohttp.TCPConnector(force_close=True)

            # Using the Semaphore
            async with self.sep:

                # Create an aiohttp client session
                async with aiohttp.ClientSession(connector=connector, timeout=session_timeout) as session:
                    request = session.get if data is None else session.post

                    # noinspection PyArgumentList
                    async with request(url, proxy=cached_current_proxy, data=data, headers=self.__get_headers(url, '.com', self.mobile)) as result:
                        try:
                            response = await result.json()
                        except:
                            response = {'response': await result.text(), 'url': url}

        # Request failed & an error was thrown
        except Exception as e:
            return {'response': '500', 'error': str(e), 'url': url, 'proxy': cached_current_proxy}

        # Debug Inbound
        if self.debug:
            print("\033[34m" + '<- Inbound Reply', str(response) + "\033[0m")

        return response

    async def manage_events(self, events: Optional[List[List[str]]] = None) -> Union[list, None]:
        """
        Manage events given a list of events, or get a list and manage them.

        :param events: Optionally pass in a set of events to parse instead of retrieving them
        :return: The result returned from handling each event

        """

        # Build the request data
        url: str = self.EVENTS_URL % self.server
        data: dict = {'id': self.client_id}

        # If events weren't selected, get them
        if not events:
            events = await self._request(url, data)

        # If we got events back
        if isinstance(events, list):

            # Handle the events and return their results
            return [self.loop.create_task(self._handle_event(event)) for event in events]

        # If we got a dict back, there was a system error & we didn't get anything back at all
        if isinstance(events, dict):
            await self._handle_event(['systemError', events])

    async def _handle_event(self, event: List[str], event_handler: Optional = None) -> Any:
        """
        Interact with the abstract event handler to retrieve (externally), run, and return the result of an event...

        :param event: The event to run
        :param event_handler: The optional ability to run the event with an EXTERNAL handler

        :return: The result of the event

        """

        # We force this event to be handled by us because we need to know when we are
        # connected for the basics of the client to work
        if event[0] == 'connected':
            self.connected = True

        # Get the event into clearer terms
        event_name: str = event[0]
        event_data: Optional[Any] = event[1] if len(event) > 1 else None

        # Select the event
        event_call: Optional[Callable] = self.__event_selector(event_name, event_data, event_handler)

        # If a value was returned
        if event_call:
            try:
                # Try to execute the event handler code & return the value
                return await event_call(event_data)

            except TypeError:
                print(f'Event handling failed for {event_name}. Is the method async?')

    def __event_selector(self, event_name: str, event_data: dict = None, event_handler: Optional = None) -> Union[Callable, None]:
        """
        Retrieve an event from the event handler class passed in

        :param event_name: The name of the event
        :param event_data: The data received in the event (if any)
        :param event_handler: The handler to run the event on (optional, otherwise goes to the normal one)

        :return: The callable function for the event to run it

        """

        # Optionally override the handler
        handler = self.handler if event_handler is None else event_handler

        # Try to get the handler
        try:
            return getattr(handler, event_name)
        except:

            if self.display_unhandled:
                print(f"Unhandled event \"{event_name}\"" + (f" with data \"{event_data}\"" if event_data is not None else ""))

    async def connect(self) -> str:
        """
        This method is responsible for creating an initial connection to Omegle
        on behalf of the client.

        :return: The client ID of the user

        """

        # bool: if 0 or not given, the response will not contain a statusInfo
        first_event: int = 1

        # str: some kind of ID from Adobe Stratus, never used though
        sp_id: str = ''

        # str: this is really just a random string containing 2-9 and A-Z, but excluding I and O
        self.random_id: str = ''.join([random.choice('23456789ABCDEFGHJKLMNPQRSTUVWXYZ') for _ in range(8)])

        mobile: int = int(self.mobile)

        # str: Two-character language code, standard across the web.
        language: str = self.language

        # Format the start URL based off supplied data
        start_url: str = self.START_URL % (self.server, first_event, sp_id, self.random_id, language, mobile)

        # If they select topics
        if self.topics:
            # noinspection PyUnresolvedReferences
            start_url += '&' + urllib.parse.urlencode({'topics': json.dumps(self.topics)})
        # If they want to be in unmon chat
        if self.unmonitored:
            start_url += '&group=unmon'

        cached_current_proxy: str = str(self.proxy)

        # Get the initial reply
        result: Any = await self._request(start_url)

        # Update the ID
        self.uuid = str(uuid.uuid4())

        # Set the client ID for future requests (used as authentication)
        # and manage the events we got from this one
        try:
            self.client_id: str = result['clientID']
            await self.manage_events(result['events'])

        # If we were missing a client ID or events, something went wrong
        except KeyError:

            if not len(result):
                await self._handle_event(['softBanned',  {'response': '500', 'error': 'softBanned', 'url': start_url, 'proxy': cached_current_proxy}])

        # Return the client ID
        return self.client_id

    async def disconnect(self) -> None:
        """
        Disconnects from Omegle on behalf of the client

        """

        # Configure the payload
        disconnect_url: str = self.DISCONNECT_URL % self.server
        data: dict = {'id': self.client_id}

        await self._request(disconnect_url, data)

        # Set to disconnected
        self.connected: bool = False

    async def __event_loop(self) -> None:
        """
        The main event loop, the origin of the client's heartbeat.

        """

        self.running = True

        if self.debug:
            print("\033[32m" + '<- Event Loop Initialized ->' + "\033[0m")

        while self.running:

            if self.debug:
                print("\033[35m" + '<- Event Loop Reached ->' + "\033[0m")

            # Manage events
            self.loop.create_task(self.manage_events())

            # Sleep
            await asyncio.sleep(self.event_frequency)

    def run(self):
        """
        Connects to omegle, blocks the main thread

        """

        # Set up the event handler
        self.handler.setup(self, self.debug)

        # Block until we connect
        self.loop.create_task(self.connect())

        # Block the thread
        self.loop.run_until_complete(self.__event_loop())


    def start(self):
        """
        Connects to omegle via a sub-thread (instead of blocking the main thread)

        """

        try:
            self.thread = ThreadedOmegle(self)
            self.thread.start()
        except:
            print('Thread failure')

        return self

    def stop(self):
        """
        Stop the event loop thus killing the client

        """

        self.running = False

