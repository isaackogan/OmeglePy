class AbstractEventHandler:
    """
    Abstract class for basic functionality required of an event handler.
    Inherit from this when creating your custom event handlers!

    """

    def __init__(self):
        self.instance = None
        self.debug = False

    def setup(self, instance, debug: bool):
        self.instance = instance
        self.debug = debug

    async def strangerDisconnected(self, data):
        """
        Automatically move to the next person

        """

        await self.instance.disconnect()
        await self.instance.connect()