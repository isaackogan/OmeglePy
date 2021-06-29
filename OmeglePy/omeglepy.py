from __future__ import division

from typing import Any

import mechanize
import urllib
import random
import json

import requests
from mechanize import Request

from OmeglePy.events import EventThread


class Omegle(object):

    SERVER_LIST = [f'front{n}.omegle.com' for n in range(1, 33)]

    STATUS_URL =            'http://%s/status?nocache=%s&randid=%s'
    START_URL =             'http://%s/start?caps=recaptcha2,t&firstevents=%s&spid=%s&randid=%s&lang=%s'
    RECAPTCHA_URL =         'http://%s/recaptcha'
    EVENTS_URL =            'http://%s/events'
    TYPING_URL =            'http://%s/typing'
    STOPPED_TYPING_URL =    'http://%s/stoppedtyping'
    DISCONNECT_URL =        'http://%s/disconnect'
    SEND_URL =              'http://%s/send'


    @staticmethod
    def get_headers(url: str):

        OMEGLE_TLD = '.com'

        return {

            'Accept-Language': "en-US:en;q=0.8",
            "Referer": "https://www.omegle.com/",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "authority": "https://www.omegle.com",
            "path": url[url.find(OMEGLE_TLD) + len(OMEGLE_TLD):].strip(),
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive",
            "Host": url[url.find("//") + 2:url.find(OMEGLE_TLD) + len(OMEGLE_TLD)],
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36"
    }

    def __init__(
            self,
            event_handler,
            event_first=1,
            sp_id='',
            random_id=None,
            topics=None,
            lang='en',
            event_delay=3,
            debug=False,
            request_timeout=5,
            proxy=None
    ):

        # Event Setup
        self.event_handler = event_handler
        self.event_first = event_first
        self.event_delay = event_delay

        # General Setup
        self.random_id = random_id or self._randID(8)
        self.server = random.choice(self.SERVER_LIST)
        self.sp_id = sp_id
        self.connected = False
        self.client_id = None
        self.connected = False

        # Configuration
        self.topics = topics
        self.lang = lang
        self.debug = debug
        self.request_timeout = request_timeout
        self.proxy = proxy

        # Browser Setup
        self.browser = mechanize.Browser()

        # Call additional setup
        self.event_handler.setup(self, debug)

    @staticmethod
    def _randID(length):
        """
        Generates a random ID for chat session

        """

        return ''.join([random.choice('23456789ABCDEFGHJKLMNPQRSTUVWXYZ') for _ in range(length)])

    def handle_events(self, events):
        """
        Handle the chat events

        """

        for event in events:

            try:

                self._event_selector(event)

            except TypeError as e:

                raise e
                print('DEBUG', event)

            continue

    def _event_selector(self, event):
        """
        Select the correct events and call the handler

        """

        print(event, 'g')
        event_type = event[0]

        if event_type == 'waiting':
            self.event_handler.waiting()
        elif event_type == 'typing':
            self.event_handler.typing()
        elif event_type == 'connected':
            self.connected = True
            self.event_handler.connected()
        elif event_type == 'gotMessage':
            message = event[1]
            self.event_handler.message(message)
        elif event_type == 'commonLikes':
            likes = event[1]
            self.event_handler.common_likes(likes)
        elif event_type == 'stoppedTyping':
            self.event_handler.stopped_typing()
        elif event_type == 'strangerDisconnected':
            self.disconnect()
            self.event_handler.disconnected()
        elif event_type == 'recaptchaRequired':
            self.event_handler.captcha_required()
        elif event_type == 'recaptchaRejected':
            self.event_handler.captcha_rejected()
        elif event_type == 'serverMessage':
            message = event[1]
            self.event_handler.server_message(message)
        elif event_type == 'statusInfo':
            status = event[1]
            self.event_handler.status_info(status)
        elif event_type == 'identDigests':
            digests = event[1]
            self.event_handler.ident_digest(digests)
        else:
            print('Unhandled event: %s' % event)

    def __request(self, url, data=None) -> Any:
        """
        Opens the url with data info

        """

        if not url:
            assert 'URL not valid for request'

        if data:
            data = urllib.parse.urlencode(data)

        # Add the headers
        self.browser.addheaders = self.get_headers(url)
        self.browser.set_handle_robots(False)

        # Build the request
        request: Request = mechanize.Request(url)

        # Add a proxy (optional)
        if self.thread.proxy is not None:
            request.set_proxy(self.thread.proxy, self.thread.proxy_type)


        # Make the request
        response = self.browser.open(request, data, timeout=self.request_timeout)

        return response

    def _attempt_request(self, url: str, data: dict = None) -> Any:
        """
        Attempt a request and return the success, data if there is any

        """

        try:

            return (True, self.__request(url, data))

        except Exception:

            return (False, False)


    def events_manager(self) -> bool:
        """
        Event manager class

        """

        url: str = self.EVENTS_URL % self.server
        data: dict = {'id': self.client_id}

        try:

            if self.debug:
                print("\033[31m" + '-> Outbound Request', url + "\033[0m")
                response = self.__request(url, data)
                data = json.load(response)
                print("\033[34m" + '<- Inbound Reply', str(data) + "\033[0m")
            else:
                response = self.__request(url, data)
                data = json.load(response)

        except Exception:
            return False

        if data:
            self.handle_events(data)

        return True

    def status(self):
        """
        Return connection status

        """

        no_cache = '%r' % random.random()
        url = self.STATUS_URL % (self.server, no_cache, self.random_id)

        response = self.__request(url)
        data = json.load(response)

        return data

    def start(self) -> EventThread:
        """
        Begin a new conversation

        """
        url: str = self.START_URL % (self.server, self.event_first, self.sp_id, self.random_id, self.lang)

        # Add topics to the URL
        if self.topics:
            # noinspection PyUnresolvedReferences
            url += '&' + urllib.parse.urlencode({'topics': json.dumps(self.topics)})

        self.thread: EventThread = EventThread(self, url, debug=self.debug, proxy=self.proxy)
        self.thread.start()

        return self.thread

    def recaptcha(self, challenge, response) -> bool:
        """
        Attempt to do the reCaptcha

        """

        url: str = self.RECAPTCHA_URL % self.server
        data: dict = {
            'id': self.client_id,
            'challenge': challenge,
            'response': response
        }

        return self._attempt_request(url, data)[0]

    def typing(self) -> bool:
        """
        Emulates typing in the conversation

        """

        url: str = self.TYPING_URL % self.server
        data: dict = {'id': self.client_id}

        return self._attempt_request(url, data)[0]

    def stopped_typing(self) -> bool:
        """
        Attempt to stop typing in the conversation

        """

        url: str = self.STOPPED_TYPING_URL % self.server
        data: dict = {'id': self.client_id}

        return self._attempt_request(url, data)[0]

    def send(self, message) -> bool:
        """
        Attempt to send a message directly through Omegle's API

        """

        url: str = self.SEND_URL % self.server
        data: dict = {'msg': message, 'id': self.client_id}

        return self._attempt_request(url, data)[0]

    def disconnect(self) -> bool:
        """
        Attempt to disconnect from the current conversation

        """

        # Disconnect
        self.connected: bool = False

        # Update the URL
        url: str = self.DISCONNECT_URL % self.server

        # Set the data
        data: dict = {'id': self.client_id}

        try:

            # Disconnect & go to the disconnect URL
            self.thread.stop()
            self.__request(url, data)

            return True

        except Exception:

            return False


