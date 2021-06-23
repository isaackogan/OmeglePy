import json
import re
import threading
import time
from urllib.request import Request

import mechanize

from OmeglePy.utils import starts_with, AnsiColours


class EventThread(threading.Thread):
    """
    Event thread class for handling the main loop
    """

    def __init__(self, instance, start_url: str, proxy: str = None):
        threading.Thread.__init__(self)

        # Omegle instance
        self.instance = instance

        # Start URL for Conversations
        self.start_url = start_url

        # Set a proxy (optional)
        self.proxy = proxy

        # Determine proxy type
        try:
            self.proxy_type: str = 'https' if starts_with(proxy, 'https://') else 'http'
        except:
            self.proxy_type = None

        # ???
        self._stop = threading.Event()

    def run(self):
        """
        Overrides threading method to begin instance

        """

        # Create a request
        request: Request = mechanize.Request(self.start_url)

        # Add a proxy (optional)
        if self.proxy is not None:
            request.set_proxy(self.proxy, self.proxy_type)
            print(f'Set proxy {self.proxy} of type {self.proxy_type}')

        try:

            # Get Response
            response = self.instance.browser.open(request)
            data: dict = json.load(response)

        except Exception as e:

            # Fail to get response
            print('Failed to initialize:', str(e))
            return

        try:

            # Try to handle events
            self.instance.client_id = data['clientID']
            self.instance.handle_events(data['events'])

        except KeyError:

            # There were no events to handle (i.e we got blocked)
            if not len(response.read()):
                print("(Blank server response) Error connecting to server. Please try again.")
                print("If problem persists then your IP may be soft banned, try using a VPN.")

        # Init
        while not self.instance.connected:
            self.instance.events_manager()

            if self._stop.isSet():
                self.instance.disconnect()
                return

            time.sleep(self.instance.event_delay)

        # Main event loop
        while self.instance.connected:

            # Manage events
            self.instance.events_manager()

            # If they request to stop
            if self._stop.isSet():

                # Disconnect
                self.instance.disconnect()
                return

            # Wait the delay
            time.sleep(self.instance.event_delay)

    def stop(self):
        """
        Stop the events loop

        """

        self._stop.set()



class OmegleHandler:
    """
    Abstract class to define Omegle event handlers

    """

    RECAPTCHA_CHALLENGE_URL: str = 'http://www.google.com/recaptcha/api/challenge?k=%s'
    RECAPTCHA_IMAGE_URL: str = 'http://www.google.com/recaptcha/api/image?c=%s'
    recaptcha_challenge_regex: str = re.compile(r"challenge\s*:\s*'(.+)'")

    def __init__(self, debug=False):

        # Debug
        self.debug = debug

        # Omegle instance
        self.omegle = None

    def setup(self, omegle):
        """
        Called by omegle class to allow interaction through this class

        """

        self.omegle = omegle

    @staticmethod
    def waiting():
        """
        Called when waiting for a person to connect

        """

        print('Looking for someone you can chat with...')

    @staticmethod
    def connected():
        """
        Called when we found a person to connect to

        """

        print("You're now chatting with a random stranger. Say hi!")

    @staticmethod
    def typing():
        """
        Called when the user is typing a message

        """

        print('Stranger is typing...')

    @staticmethod
    def stopped_typing():
        """
        Called when the user stop typing a message

        """

        print('Stranger has stopped typing.')

    @staticmethod
    def message(message):
        """
        Called when a message is received from the connected stranger

        """

        print(f"{AnsiColours.fgBrightMagenta}Stranger:{AnsiColours.reset} {message}")

    @staticmethod
    def common_likes(likes):
        """
        Called when you and stranger likes the same thing

        """

        print('You both like %s.' % ', '.join(likes))

    def disconnected(self):
        """
        Called when a stranger disconnects

        """

        print('Stranger has disconnected.')
        self.omegle.start()

    @staticmethod
    def server_message(message):
        """
        Called when the server report a message

        """

        print(message)

    def status_info(self, status):
        """
        Status info received from server

        """

        if not self.debug:
            return

        print('Status update', status)

    def ident_digest(self, digests):
        """
        Identity digest received from server

        """

        if not self.debug:
            return

        print('Identity digest', digests)

    def captcha_required(self):
        """
        Called when the server asks for captcha

        """

        #url = self.RECAPTCHA_CHALLENGE_URL % challenge
        #source = self.browser.open(url).read()
        #challenge = recaptcha_challenge_regex.search(source).groups()[0]
        #url = self.RECAPTCHA_IMAGE_URL % challenge

        #print('Recaptcha required: %s' % url)
        #response = raw_input('Response: ')

        # self.omegle.recaptcha(challenge, response)

    @staticmethod
    def captcha_rejected():
        """
        Called when server reject captcha

        """

        print('Captcha rejected')

