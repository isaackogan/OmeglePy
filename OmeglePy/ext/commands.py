from typing import List, Any


def command(
        name: str = None,
        aliases: List[str] = None,
        description="",
        usage="",
        enabled=True
):
    def decorator(func):
        func._command_attributes = {
            'name': name,
            'aliases': aliases,
            'description': description,
            'usage': usage,
            'enabled': enabled
        }

        return func

    return decorator


class Command:

    def __init__(
            self,
            name: str = None,
            aliases: List[str] = None,
            description: str = None,
            usage: str = None,
            enabled: bool = None
    ):
        self.name = name
        self.aliases = aliases
        self.description = description
        self.usage = usage
        self.enabled = enabled

    def __str__(self):
        return str(self.name) + str(self.aliases) + str(self.description) + str(self.usage) + str(self.enabled)


class Context:

    def __init__(
            self,
            message: str,
            args: List[str],
            command: Any,
    ):
        self.message = message
        self.args = args
        self.command = command

