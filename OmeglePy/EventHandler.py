from typing import Optional

from OmeglePy.AbstractEventHandler import AbstractEventHandler


def cPrint(string: str, ansi_colour: Optional[str] = None) -> None:
    print(ansi_colour + string + "\033[0m" + EventHandler.RESET if ansi_colour else string)
    
    
class EventHandler(AbstractEventHandler):

    # Colours for the console messages
    WHITE = "\033[37m"
    RED = "\033[31m"
    BLUE = "\033[34m"
    RESET = "\033[0m"

    RECAPTCHA_URL = "http://www.google.com/recaptcha/api/challenge?k=%s"

    async def identDigests(self, data):
        """
        Identification received from the server

        """
        if self.debug:
            cPrint('Identity Digests: ' + data)

    async def systemError(self, data):
        """
        When a critical error happens & an event can't be retrieved

        """

        cPrint('Critical error when retrieving events %s' % data, self.RED)


    async def statusInfo(self, data):
        """
        Received status info from the server

        """
        if self.debug:
            cPrint('Received status info from server... %s' % data)

    async def onlineCount(self, count):
        """
        Retrieved the currently online users

        """
        cPrint('There are currently %s users online' % count, self.WHITE)
        
    async def waiting(self, data):
        """
        Waiting for a connection to be made

        """
        cPrint('Looking for someone you can chat with...', self.WHITE)
        
    async def connected(self, data):
        """
        Connected to a stranger

        """
        cPrint("You're now chatting with a random stranger. Say hi!", self.WHITE)

    async def commonLikes(self, interests):
        """
        Have common interests with a stranger

        """
        cPrint("You both like " + ' '.join(interests), self.WHITE)

    async def strangerDisconnected(self, data):
        """
        A stranger disconnected from your chat session

        """
        await super(EventHandler, self).strangerDisconnected(data)
        cPrint('Stranger has disconnected', self.WHITE)

    async def typing(self, data):
        """
        The stranger started typing

        """
        cPrint('Stranger is typing...', self.WHITE)

    async def stoppedTyping(self, data):
        """
        The stranger stopped typing

        """
        cPrint('Stranger stopped typing...', self.WHITE)

    async def clientTyping(self, data):
        """
        You started typing

        """
        cPrint('You are typing...', self.WHITE)

    async def clientStoppedTyping(self, data):
        """
        You stopped typing

        """
        if self.debug:
            cPrint('You stopped typing', self.WHITE)

    async def gotMessage(self, data):
        """
        Stranger sent you a message

        """
        cPrint(f'Stranger: ' + self.RESET + data, self.RED)

    async def clientMessage(self, data):
        """
        You sent the stranger a message

        """
        cPrint(f'You: ' + self.RESET + data, self.BLUE)

    async def clientChangedTopics(self, data):
        """
        You updated your interests

        """
        cPrint('You updated your interests to %s' % data, self.WHITE)

    async def clientSkip(self, data):
        """
        You skipped to the next person

        """
        cPrint('You skipped to the next person', self.WHITE)

    async def recaptchaRequired(self, data):
        """
        You were captcha blocked

        """
        cPrint('Received a captcha, stopping client. %s' % data, self.RED)
        self.instance.stop()

    async def antinudeBanned(self, data):
        """
        You were anti-nude banned

        """
        cPrint('Received an anti-nude ban status, stopping client. %s' % data, self.RED)
        self.instance.stop()

    async def softBanned(self, data):
        """
        You were soft-banned and so no response was sent from the server

        """
        cPrint(
            "(Blank server response) Error connecting to server. Please try again.\n"
            "If problem persists then your IP may be soft banned, try using a VPN.",
            self.RED
        )
        self.instance.stop()
