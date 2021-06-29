import asyncio
import random

import aiohttp


class AnsiColours:
    """
    Via "Breakable Baboon"
    https://www.codegrepper.com/code-examples/actionscript/ansi+reset+color+code

    """

    reset = "\033[0m"

    # Black
    fgBlack = "\033[30m"
    fgBrightBlack = "\033[30;1m"
    bgBlack = "\033[40m"
    bgBrightBlack = "\033[40;1m"

    # Red
    fgRed = "\033[31m"
    fgBrightRed = "\033[31;1m"
    bgRed = "\033[41m"
    bgBrightRed = "\033[41;1m"

    # Green
    fgGreen = "\033[32m"
    fgBrightGreen = "\033[32;1m"
    bgGreen = "\033[42m"
    bgBrightGreen = "\033[42;1m"

    # Yellow
    fgYellow = "\033[33m"
    fgBrightYellow = "\033[33;1m"
    bgYellow = "\033[43m"
    bgBrightYellow = "\033[43;1m"

    # Blue
    fgBlue = "\033[34m"
    fgBrightBlue = "\033[34;1m"
    bgBlue = "\033[44m"
    bgBrightBlue = "\033[44;1m"

    # Magenta
    fgMagenta = "\033[35m"
    fgBrightMagenta = "\033[35;1m"
    bgMagenta = "\033[45m"
    bgBrightMagenta = "\033[45;1m"

    # Cyan
    fgCyan = "\033[36m"
    fgBrightCyan = "\033[36;1m"
    bgCyan = "\033[46m"
    bgBrightCyan = "\033[46;1m"

    # White
    fgWhite = "\033[37m"
    fgBrightWhite = "\033[37;1m"
    bgWhite = "\033[47m"
    bgBrightWhite = "\033[47;1m"


class AnsiColors(AnsiColours):
    """
    Alternate spelling for americans

    """

    pass


class ProxyChecking:

    SERVER_LIST = [f'front{n}.omegle.com' for n in range(1, 33)]

    def __init__(self, input_file: str, output_file: str, ssl: bool = False):
        self.input_file = input_file
        self.output_file = output_file

        # Proxies in 123.231.212:1212 format
        self.raw_proxies = [proxy.strip() for proxy in open('proxies.txt').read().strip().split('\n')]

        # Proxy Type
        proxy_type: str = 'https' if ssl else 'http'
        self.formatted_proxies = [proxy_type + "://" + proxy for proxy in self.raw_proxies]

    async def check_proxy(self, proxy: str, working_file: str):
        """
        Check a proxy

        """

        async with aiohttp.ClientSession() as session:
            print(AnsiColours.fgWhite + 'Testing', proxy + AnsiColours.reset)
            check_url: str = "http://" + random.choice(self.SERVER_LIST) + "/start?caps=recaptcha2,t&firstevents=1&spid=&randid=T7RY4HL6&lang=en"

            # Try in-case of timeout
            try:
                async with session.get(check_url, proxy=proxy) as response:
                    data: dict = await response.json()
                    keys: list = list(data.keys())

                    # Parse events
                    if 'events' in keys:

                        if data['events'][0][0] == 'antinudeBanned':
                            proxy_status = 'Anti-Nude Banned'

                        elif data['events'][0][0] == 'recaptchaRequired':
                            proxy_status = 'Captcha Blocked'


                        else:

                            # Working
                            print(AnsiColours.bgGreen + proxy + str(data) + AnsiColours.reset)
                            with open(working_file, 'a') as file:

                                # Get rid of start
                                proxy = proxy.replace("https://", "").replace("http://", "")

                                file.write(proxy + "\n")
                                file.close()

                            return

                    # No events? Blocked
                    else:
                        proxy_status = 'Anti-VPN Blocked'

            except Exception as e:
                print(AnsiColours.fgWhite + 'Failed with Exception (Likely connectivity issue)', proxy, str(e) + AnsiColours.reset)
                return

            print(AnsiColours.fgWhite + 'Failed', proxy, proxy_status + AnsiColours.reset)

    def check_proxy_list(self):

        loop = asyncio.get_event_loop()

        for proxy in self.formatted_proxies:
            loop.create_task(self.check_proxy(proxy, self.output_file))



