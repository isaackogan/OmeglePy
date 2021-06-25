import asyncio

from OmeglePy import ProxyChecking

checker = ProxyChecking('proxies.txt', 'working.txt')
loop = asyncio.get_event_loop()

checker.check_proxy_list()

loop.run_forever()
