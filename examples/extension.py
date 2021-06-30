from OmeglePy.ext import Bot, commands

"""
by Isaac Kogan

This is a higher level implementation of the Omegle Client. 
Commands are things runnable by *you* in the event loop.
You still have access to all attributes through instance variables,
however it is all wrapped up nicely in a more readable format.

"""



bot = Bot()


@commands.command(aliases=['next'])
async def skip(context):
    await bot.client.skip()


@commands.command(aliases=['quit', 'exit'])
async def leave(context):
    bot.client.stop()
    print('Disconnected!')


@commands.command()
async def topics(context):
    topics = context.args
    await bot.client.set_topics(topics)
    print('New Topics:', topics)


bot.run()
