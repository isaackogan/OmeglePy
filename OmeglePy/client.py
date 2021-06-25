import time

from OmeglePy import Omegle
from OmeglePy.utils import AnsiColours


class OmegleClient(Omegle):
    """
    Class for high-level interaction with Omegle
    """

    def __init__(
            self,
            event_handler,
            event_first=1,
            event_delay=3,
            sp_id='',
            wpm=42,
            random_id=None,
            lang='en',
            topics=None,
            debug=False,
            proxy=None
    ):

        if debug:
            print(
                f"Handler: '{event_handler}'\n"
                f"First: '{event_first}'\n"
                f"Delay: '{event_delay}'\n"
                f"sp_id = '{sp_id}'\n"
                f"wpm = '{wpm}'\n"
                f"random_id = '{random_id}'\n"
                f"lang = '{lang}'\n"
                f"topic = '{topics}'\n"
                f"debug = '{debug}'"
            )

        super(OmegleClient, self).__init__(
            event_handler=event_handler,
            event_first=event_first,
            event_delay=event_delay,
            sp_id=sp_id,
            random_id=random_id,
            topics=topics,
            lang=lang,
            debug=debug,
            proxy=proxy

        )

        self.wpm = wpm


    def _typing_time(self, length: int) -> float:
        """
        Calculates the time it should take to type a message based on the WPM

        """

        return (60 / self.wpm) * (length / 5)

    def write(self, message: str) -> None:
        """
        Writes a message with a simulated delay based on human typing speeds.
        This is great for avoiding spam-bot blocks by Omegle.

        """

        # Can't send nothing
        if len(message.strip()) == 0:
            return

        # Calculate required time for typing
        typing_time: float = self._typing_time(len(message))

        # Send typing event to server
        self.typing()

        # Wait the required time
        time.sleep(typing_time)

        # Send the message
        self.send(message)

    def typing(self):
        """
        Emulate typing in the conversation by sending an event to the
        Omegle servers.

        """

        # Typing
        super(OmegleClient, self).typing()
        print(AnsiColours.fgWhite + 'You are currently typing...' + AnsiColours.reset)

    def send(self, message):
        """
        Send a message to the chat through Omegle

        """

        # Sending
        res = super(OmegleClient, self).send(message)

        if res is None:
            print(AnsiColours.fgWhite + "Failed to send message, timed out" + AnsiColours.reset)
            return

        print(AnsiColours.fgBlue + "You: " + AnsiColours.reset + str(message))

    def next(self):
        """
        Switch to the next conversation
        """

        # Disconnect & start a new connection
        self.disconnect()
        self.start()

    def set_topics(self, topics: list = None):
        """
        Update your topics

        """
        self.topics = topics
