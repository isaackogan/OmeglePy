from OmeglePy import OmegleClient, EventHandler

client = OmegleClient(EventHandler(), topics=['tiktok'], debug=True)
client.start()

while True:
    message = input()
    client.loop.create_task(client.send(message))
