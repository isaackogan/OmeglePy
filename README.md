OmeglePy
==================
Python API for Omegle. Compatible with Python 3. This is an unofficial api wrapper for the popular WebChat service Omegle, written in Python. With this API you can basically fully interact with Omegle as a regular user.

 [![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white&style=flat-square)](https://www.linkedin.com/in/isaac-kogan-5a45b9193/ ) [![GitHub release (latest by date)](https://img.shields.io/github/v/release/isaackogan/OmeglePy)](https://github.com/isaackogan/OmeglePy/releases) ![Issues](https://img.shields.io/github/issues/isaackogan/OmeglePy) [![GitHub](https://img.shields.io/github/license/isaackogan/OmeglePy)](https://github.com/isaackogan/OmeglePy/blob/master/LICENSE) [![Downloads](https://pepy.tech/badge/omeglepy)](https://pepy.tech/project/omeglepy) [![Support Server](https://img.shields.io/discord/655522419460669481.svg?color=7289da&logo=discord&style=flat-square)](https://discord.gg/kaX9H65VhG)
 
 ## Are you looking to run more than one?

If you want to run ``more than 1 client`` at the same time and not get blocked by Omegle, I have
a private project with the ability to scale this up through a combination of proxies and (other)
private methods not included in this library. 

This is ``not public`` whatsoever and access to the repository with the code can be purchased. This purchase includes *all* future changes necessary as I update the OmeglePy library, so that you never have to worry about updating it yourself.

Join the support discord and DM ``fallen#9745`` for inquiries into this.

# Table of Contents
- [Installation](#installation)
- [Quick Start Guide](#quick-start-guide)
    - [Examples](#examples)
    - [Events](#events)
    - [OmegleClient](#omegleclient-inherits-omeglepy)
    - [OmeglePy](#omeglepy-1)
- [Project License](#license)

# Installation

```sh
$ pip install OmeglePy
```

# Quick Start Guide

To get started using the API follow the instructions below.

## Examples

For more examples, check the [examples](examples) folder.

``` python
from OmeglePy import OmegleClient, EventHandler

client = OmegleClient(EventHandler(), topics=['tiktok'], debug=False)
client.start()

while True:

    # Get input
    message = input()
    
    # Go to the next person
    if message.lower() == "/next":
        client.loop.creatae_task(client.skip())
        continue
    
    # Send a message
    client.loop.create_task(client.send(message))
```

## Events

List of events accessible by the default provided ``EventHandler``. 

* **identDigests** - Identification received from the server
* **systemError** - When a critical error happens & an event can't be retrieved (typically proxy stuff)
* **statusInfo** - When status info is received from the server
* **onlineCount** - When a count of all online people is received from the Client
* **waiting** - When the server states you are waiting for a connection
* **connected** - When you connect to someone
* **commonLikes** - A list of the common likes between you and a stranger
* **strangerDisconnected** - When a stranger disconnects
* **typing** - When a stranger starts typing
* **stoppedTyping** - When a stranger stops typing
* **clientTyping** - When you start typing
* **clientStoppedTyping** - When you stop typing
* **gotMessage** - When you receive a message
* **clientMessage** - When you send a message
* **clientChangedTopics** - When you change your topics
* **clientSkip** - When you skip
* **recaptchaRequired** - When the server requests a captcha (You got Blocked!)
* **antinudeBanned** - When the server sends an antinude ban (You got Blocked!)
* **softBanned** - When the server sends no data back (You got Blocked!)

Inherit the ``AbstractEventHandler`` class to implement your own custom events, or (my suggestion) inheret the ``EventHandler`` class and just edit specific events you want different from the ones already handled. Remember, you can add on by calling the super of that method too, instead of copy-pasting code ``await super(EventHandler, self).<method_name>(data)`` if you're trying to add to a handled event instead of edit it.

``` python
class MyCustomHandler(EventHandler):
    
    async def connected(self, data):
        """
        Run what the inherited handler does, but also send a message...
        """
        await super(EventHandler, self).connected(data)
        await self.instance.send('You should know, I'm super cool...')
    
    async def softBanned(self, data):
        """
        Ignore what the inherited handler does, run my own code...
        """
        await self.instance.stop()  # Stops the bot
    
```

## OmeglePy

``OmeglePy`` uses some optional initial parameters, these are them:

* **event_handler=EventHandler()** - The event handler for events to be passed into
* **event_frequency=5** - The frequency in which requests are made to retrieve events
* **loop=YourLoopHere** - An asyncio loop if you want to pass one in if one has already been created
* **server=1** - The omegle server (integer #) to connect to
* **topics=['tiktok']** - A list of topics you want to search for in common with others
* **language='en'** - The two-letter language code (e.g: en)
* **debug=False** - Whether or not you want debug logs in the console
* **proxy=``http://user:pass@hostname:port``** - An optional proxy if you want one of those
* **mobile=False** - Whether or not to connect as a mobile client
* **unmonitored=False** - Whether or not to enter the unmonitored section
* **socket_connect_timeout=15** - The max time (seconds) to connect to the socket during a request
* **socket_read_timeout=45** - The max time (seconds) to read from a socket during a request

Visit the provided documentation (included directly via DocStrings) for a list of methods.

## OmegleClient (Inherits OmeglePy)

``OmegleClient`` uses some optional initial parameters, these are them:

* **get_status=True** for to get the # of online people on the first connection
* **wpm=42** set the ``words per minutes`` typing speed

Visit the provided documentation (included directly via DocStrings) for a list of methods.

# License
pyomegle is released under the [MIT License](LICENSE).
