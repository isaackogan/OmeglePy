import inspect
from typing import List, Tuple, Any

from OmeglePy.client import OmegleClient
from OmeglePy.events import OmegleHandler
from OmeglePy.ext.commands import Context, Command


class Bot:

    def __init__(self, prefix: str = "/", **kwargs):

        # Create the stuff we need
        self.handler = OmegleHandler()
        self.client = OmegleClient(self.handler, **kwargs)

        # Set the prefix
        self.prefix = prefix

        # Create the mappings
        self.mappings = dict()

    @staticmethod
    def add_command(bot, function):
        name = function.__name__

        # noinspection PyProtectedMember
        attributes: dict = function._command_attributes
        executioners: set = {name}

        if attributes['name']:
            executioners = {attributes['name']}

        if attributes['aliases']:
            executioners = executioners.union(set(attributes['aliases']))

        bot.mappings[tuple(executioners)] = {
            'method': function,
            'attributes': Command(
                list(executioners)[0],
                list(executioners)[1:],
                attributes['description'],
                attributes['usage'],
                True if attributes['enabled'] else False
            )
        }

    def __setup(self):

        stack = inspect.stack()
        stack_length = len(stack)
        main_frame_info = stack[stack_length - 1]
        main_frame = main_frame_info.frame

        commands_to_load = []

        # Iterate through globals to get valid commands
        for name in main_frame.f_locals.keys():
            function = main_frame.f_locals[name]

            if '_command_attributes' in dir(function):
                commands_to_load.append((name, function))

        # Iterate through this class to get valid commands
        for name, function in inspect.getmembers(self, predicate=inspect.ismethod):

            # Only get commands
            if '_command_attributes' in dir(function):
                commands_to_load.append((name, function))

        for name, function in commands_to_load:
            self.add_command(self, function)

    def __is_command(self, message: str) -> bool:
        return message.startswith(self.prefix)

    def __get_command(self, name: str) -> Tuple[Any, Command]:

        for k, v in self.mappings.items():

            # Convert to a list because dealing with tuples is *ass cheeks*
            k: List[str] = list(k)

            if name in k:
                return (v['method'], v['attributes'])

    def __execute_command(self, message: str):
        message: str = message
        parsed_message: str = message.replace(self.prefix, '', 1)
        split_message = parsed_message.split(' ')

        command_name = split_message[0]
        command_args: List[str] = split_message[1:]

        command_tuple = self.__get_command(command_name)

        if command_tuple is None:
            return message

        context = Context(
            message,
            command_args,
            command_tuple[1]
        )

        command_tuple[0](context)

    def run(self):

        self.__setup()
        self.client.start()

        while True:

            user_input = input().strip()

            # Not a Command
            if not self.__is_command(user_input):
                self.client.write(user_input)
                continue

            # Try a command
            result = self.__execute_command(user_input)

            # Not a command
            if result is not None:
                self.client.write(result)
