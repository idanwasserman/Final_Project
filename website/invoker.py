from .exceptions import bad_request_exception, empty_field_exception
from .constants import COMMAND_NAME, DEFAULT_USE_CASE
from website.command import get_commands_dict


class Invoker:
    def __init__(self):
        self._commands = {}

    def register(self, command_name, command):
        self._commands[command_name] = command

    def execute(self, attributes):
        try:
            if attributes is None:
                return bad_request_exception("attributes is None")

            if COMMAND_NAME not in attributes:
                return empty_field_exception(f"{COMMAND_NAME} not in attributes")

            if attributes[COMMAND_NAME] not in self._commands:
                return self._commands[DEFAULT_USE_CASE].execute(attributes)
            
            return self._commands[attributes[COMMAND_NAME]].execute(attributes)

        except Exception as e:
            return bad_request_exception(f"Invoker - execute(self, attributes): caught an exception: {e}")



