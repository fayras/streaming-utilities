import os
import importlib
import inspect

from typing import Type

from commands.base_command import BaseCommand


def get_classes_dict() -> dict[str, Type[BaseCommand]]:
    # Get the directory of the current module
    current_dir = os.path.dirname(__file__)

    # Dictionary to store discovered classes
    classes_dict = {}

    # Iterate through all .py files in the current directory
    for filename in os.listdir(current_dir):
        # Skip __init__.py and any non-python files
        if (filename == "base_command.py"
                or filename.startswith('__')
                or not filename.endswith('.py')
        ):
            continue

        # Remove .py extension
        module_name = filename[:-3]

        try:
            # Dynamically import the module
            module = importlib.import_module(f'.{module_name}',
                                             package=__package__)

            # Iterate through all attributes in the module
            for name, obj in inspect.getmembers(module):
                # Check if the attribute is a class (but not built-in)
                if inspect.isclass(obj) and obj.__module__ == module.__name__:
                    # Check if the class has a 'name' attribute
                    if hasattr(obj, 'name'):
                        classes_dict[obj.name] = obj

        except ImportError:
            # Handle any import errors gracefully
            print(f"Could not import module {module_name}")

    return classes_dict


# Create the dictionary of classes
CLASSES = get_classes_dict()


def parse(chat_str: str) -> BaseCommand | None:
    if not chat_str.startswith("!"):
        return None

    chat_str_without_exclamation_mark = chat_str[1:]
    tokens = chat_str_without_exclamation_mark.split()
    if not tokens[0] in CLASSES:
        return None

    command = CLASSES[tokens[0]]()
    # TODO: Ggf. Fehler werfen, wenn nicht geparsed werden kann und Nachricht
    #       im Twitch Chat schreiben, mit einer "man page"
    return command.parse(tokens[1:])


def parse_from_json(json: dict) -> BaseCommand | None:
    if "command" in json:
        command = CLASSES[json["command"]]()
        command.set_params_from_json(json["params"])

        return command


# Optional: expose the dictionary for import
__all__ = ['CLASSES', 'parse', 'parse_from_json']
