import asyncio
import random
from typing import Optional, Tuple

import aiohttp
from asyncio import AbstractEventLoop


def cPrint(string: str, ansi_colour: Optional[str] = None) -> None:
    print(ansi_colour + string + "\033[0m" + ProxyChecking.RESET if ansi_colour else string)


class ProxyChecking:
    """
    A handy little script to check the status of some proxies.
    All you need is a newline-delimited proxies.txt file with your
    proxies and a working.txt file for successful proxies.

    """

    # List of omegle servers to check proxies against
    SERVER_LIST = [f'front{n}.omegle.com' for n in range(1, 33)]

    WHITE = "\033[37m"
    RESET = "\033[0m"
    BGREEN = "\033[42m"

    def __init__(self, input_file: str, output_file: str):

        # Files for I/O
        self.input_file: str = input_file
        self.output_file: str = output_file

        # Read the proxy file to get your proxies
        self.proxies = ['http://' + proxy.strip() for proxy in open('proxies.txt').read().strip().split('\n')]

    @staticmethod
    async def check_proxy(proxy: str, working_file: str) -> Tuple[str, bool]:
        """
        Check a singular proxy

        :param proxy: The proxy to check
        :param working_file: The file to output its status

        """

        async with aiohttp.ClientSession() as session:

            # Status Message
            cPrint('Testing %s' % proxy, ProxyChecking.WHITE)

            # Generate the URL
            check_url: str = "http://" + random.choice(ProxyChecking.SERVER_LIST) + "/start?caps=recaptcha2,t&firstevents=1&spid=&randid=T7RY4HL6&lang=en"

            # Try-catch in case of timeout error
            try:

                # With the session & the proxy, request the URL
                async with session.get(check_url, proxy=proxy) as response:

                    # Get the data
                    data: dict = await response.json()

                    try:

                        # Get all event names
                        events = [event[0] for event in data['events']]

                        # Proxy works
                        if 'connected' in events:
                            cPrint(proxy + " " + str(data), ProxyChecking.BGREEN)

                            # Append proxy to the file
                            with open(working_file, 'a') as file:
                                file.write(proxy.replace("http://", "") + "\n")
                                file.close()

                            return proxy, True

                        cPrint(proxy + str(events), ProxyChecking.WHITE)
                        return proxy, False

                    except KeyError:
                        cPrint(proxy + 'Anti-VPN Blocked', ProxyChecking.WHITE)
                        return proxy, False

            except:
                cPrint(proxy + 'Proxy Timed Out', ProxyChecking.WHITE)
                return proxy, False

    def check_proxies(self):
        """
        Check the full proxy list.

        :return: Bool result of each proxy and whether it failed

        """

        loop: AbstractEventLoop = asyncio.get_event_loop()
        return [loop.create_task(self.check_proxy(proxy, self.output_file)) for proxy in self.proxies]




