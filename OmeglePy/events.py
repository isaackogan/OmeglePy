import json
import random
import re
import threading
import time
from urllib.request import Request

import mechanize

from OmeglePy.utils import AnsiColours


class EventThread(threading.Thread):
    """
    Event thread class for handling the main loop
    """

    def __init__(self, instance, start_url: str, proxy: str = None, debug=False):
        threading.Thread.__init__(self)

        # Omegle instance
        self.instance = instance

        # Start URL for Conversations
        self.start_url = start_url

        # Set a proxy (optional)
        self.proxy = proxy

        # Set debug status
        self.debug = debug

        # Determine proxy type
        try:
            self.proxy_type: str = 'http'
        except:
            self.proxy_type = None

        # ???
        self.stop = threading.Event()

    def run(self):
        """
        Overrides threading method to begin instance

        """

        # Create a request
        self.instance.browser.addheaders = self.instance.get_headers(self.start_url)
        self.instance.browser.set_handle_robots(False)
        request: Request = mechanize.Request(self.start_url)

        # Add a proxy (optional)
        if self.proxy is not None:
            request.set_proxy(self.proxy, self.proxy_type)


        try:

            if self.debug:

                print(AnsiColours.fgRed + '-> Outbound Request', request.full_url + AnsiColours.reset)
                response = self.instance.browser.open(request)
                data: dict = json.load(response)
                print(AnsiColours.fgBlue + '<- Inbound Reply', str(data) + AnsiColours.reset)

            else:

                response = self.instance.browser.open(request)
                data: dict = json.load(response)

        except Exception as e:
            raise e
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

            if self.stop.isSet():
                self.instance.disconnect()
                return

            time.sleep(self.instance.event_delay)

        # Main event loop
        while self.instance.connected:

            # Manage events
            self.instance.events_manager()

            # If they request to stop
            if self.stop.isSet():

                # Disconnect
                self.instance.disconnect()
                return

            # Wait the delay
            time.sleep(self.instance.event_delay)

    def stop(self):
        """
        Stop the events loop

        """

        self.stop.set()



class OmegleHandler:
    """
    Abstract class to define Omegle event handlers

    """

    RECAPTCHA_CHALLENGE_URL: str = 'http://www.google.com/recaptcha/api/challenge?k=%s'
    RECAPTCHA_IMAGE_URL: str = 'http://www.google.com/recaptcha/api/image?c=%s'
    recaptcha_challenge_regex: str = re.compile(r"challenge\s*:\s*'(.+)'")

    def __init__(self, auto_message: list or str = None, auto_message_delay: float = 0):

        # Declare variables
        self.omegle = None
        self.debug = None
        self.auto_message: list or str = auto_message
        self.auto_message_delay: float = auto_message_delay

    def setup(self, omegle, debug=False):
        """
        Called by omegle class to allow interaction through this class

        """

        self.omegle = omegle
        self.debug = debug

    @staticmethod
    def waiting():
        """
        Called when waiting for a person to connect

        """
        print('Looking for someone you can chat with...')

    def connected(self):
        """
        Called when we found a person to connect to

        """

        print(AnsiColours.fgWhite + "You're now chatting with a random stranger. Say hi!" + AnsiColours.reset)

        time.sleep(1.5)

        if self.auto_message:
            message = self.auto_message

            if type(self.auto_message) == list:
                message = random.choice(message)

            if self.auto_message_delay < 0:
                time.sleep(self.auto_message_delay)

            self.omegle.send(message)

    @staticmethod
    def typing():
        """
        Called when the user is typing a message

        """

        print(AnsiColours.fgWhite + 'Stranger is typing...' + AnsiColours.reset)

    @staticmethod
    def stopped_typing():
        """
        Called when the user stop typing a message

        """

        print(AnsiColours.fgWhite + 'Stranger has stopped typing.' + AnsiColours.reset)

    @staticmethod
    def message(message):
        """
        Called when a message is received from the connected stranger

        """
        print(AnsiColours.fgRed + "Stranger: " + AnsiColours.reset + message)

    @staticmethod
    def common_likes(likes):
        """
        Called when you and stranger likes the same thing

        """

        print(AnsiColours.fgWhite + 'You both like %s.' % ', '.join(likes) + AnsiColours.reset)

    def disconnected(self):
        """
        Called when a stranger disconnects

        """

        print(AnsiColours.fgWhite + 'Stranger has disconnected.' + AnsiColours.reset)
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

        print(AnsiColours.fgWhite + 'Status update' + str(status) + AnsiColours.reset)

    def ident_digest(self, digests):
        """
        Identity digest received from server

        """

        if not self.debug:
            return

        print(AnsiColours.fgWhite + 'Identity digest', digests + AnsiColours.reset)

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

