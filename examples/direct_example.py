from OmeglePy.client import OmegleClient
from OmeglePy.events import OmegleHandler

"""
by Isaac Kogan

This is a lower level implementation of the Omegle Client. 
Instead of using the "Bot" extension class provided, it
interfaces directly with the client.

"""

c = OmegleClient(OmegleHandler(), wpm=47, lang='en')
c.start()

while True:

    input_str = input('')

    if input_str.strip() == '/next':
        c.next()

    elif input_str.strip() == '/exit':

        c.disconnect()
        break

    else:

        c.send(input_str)
