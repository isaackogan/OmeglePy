from OmeglePy import OmegleClient, EventHandler

client = OmegleClient(EventHandler(), topics=['tiktok'], proxy="http://45.114.88.6:80", debug=True)
client.start()

while True:
    message = input()
    client.loop.create_task(client.send(message))