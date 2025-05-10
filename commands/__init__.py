import os
import importlib
import inspect

from typing import Type
from commands.base_command import BaseCommand


def get_all_commands() -> dict[str, Type[BaseCommand]]:
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
                if (inspect.isclass(obj) and
                        inspect.isabstract(obj) == False and
                        inspect.isbuiltin(obj) == False
                ):
                    # Check if the class has a 'name' attribute
                    if hasattr(obj, 'name'):
                        classes_dict[obj.name] = obj

                    if hasattr(obj, 'aliases'):
                        for alias in obj.aliases:
                            classes_dict[alias] = obj

        except ImportError:
            # Handle any import errors gracefully
            print(f"Could not import module {module_name}")

    return classes_dict
