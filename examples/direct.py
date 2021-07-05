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
