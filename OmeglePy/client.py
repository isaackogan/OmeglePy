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
            topics=(),
    ):

        super(OmegleClient, self).__init__(
            event_handler, event_first, sp_id, random_id, topics, lang, event_delay
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
        print('You are currently typing...')

    def send(self, message):
        """
        Send a message to the chat through Omegle

        """

        # Sending
        super(OmegleClient, self).send(message)
        print(f'{AnsiColours.fgBrightCyan}You:{AnsiColours.reset} {message}')

    def next(self):
        """
        Switch to the next conversation
        """

        # Disconnect & start a new connection
        self.disconnect()
        self.start()
