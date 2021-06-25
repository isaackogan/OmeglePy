from OmeglePy.ext import Bot, commands

"""
by Isaac Kogan

This is a higher level implementation of the Omegle Client. 
Commands are things runnable by *you* in the event loop.
You still have access to all attributes through instance variables,
however it is all wrapped up nicely in a more readable format.

"""



bot = Bot(debug=False)


@commands.command(aliases=['next'])
def skip(context):
    bot.client.next()


@commands.command(aliases=['quit', 'exit'])
def leave(context):
    bot.client.disconnect()
    print('Disconnected!')


@commands.command()
def topics(context):
    topics = context.args
    bot.client.set_topics(topics)
    print('New Topics:', topics)


bot.run()
