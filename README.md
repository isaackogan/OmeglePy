OmeglePy
==================
Python API for Omegle's WebChat/API. Compatible with Python3.

Installation
==================
```sh
pip3 install OmeglePy
```

Usage
==================
``` python
New usage coming tomorrow!
```

Events
----------
List of events accessible by ``OmegleHandler``. Note that ``OmegleHandler`` uses a ``loop`` optional parameter, valid for start a new chat when a stranger disconnects.

* **waiting()** Called when we are waiting for a stranger to connect
* **connected()**  Called when we are connected with a stranger
* **typing()** Called when the user is typing a message
* **stopped_typing()** Called when the user stop typing a message
* **message(message)** Called when a message is received from the connected stranger
* **common_likes(likes)** Called when you and stranger likes the same thing
* **disconnected()** Called when a stranger disconnects 
* **captcha_required()** Called when the server asks for captcha
* **captcha_rejected()** Called when server reject captcha
* **server_message(message)** Called when the server report a message
* **status_info(status)** Status info received from server
* **ident_digest(digests)** Identity digest received from server

Inherit ``OmegleHandler`` class for implement your custom events.

``` python
class MyCustomHandler(OmegleHandler):

    def connected(self):
        super(MyCustomHandler, self).connected()

        self.omegle.send('Hi!')
```

Client
----------
``OmegleClient`` uses some optional initial parameters, the most useful are

* **lang='en'** for set a default chat language
* **wpm=42** set the ``words per minutes`` typing speed
* **topics=[]** list of interests
* **event_delay=3** server polling delay in seconds


List of client methods

* **start()** Start a new conversation
* **status()** Return connection status
* **write(message)** Simulates a message completely written whit typing time
* **typing()** Emulates typing in the conversation
* **stopped_typing()** Emulates stopped typing into the conversation
* **send(message)** Sends a message
* **recaptcha(challenge, response)** Captcha validation
* **next()** Starts with a new conversation
* **disconnect()**  Disconnect from the current conversation

License
---------------------
OmeglePy is released under the [MIT License](LICENSE.md).
