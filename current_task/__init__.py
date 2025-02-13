import rich.markup
from rich.console import Console
from rich.theme import Theme
from rich.live import Live
from rich.text import Text

import asyncio

from prompt_toolkit import PromptSession
from prompt_toolkit.input import create_input
from prompt_toolkit.keys import Keys
from enum import Enum


class Type(Enum):
    TITLE = 1
    SUBTASK = 2


async def new_task(session: PromptSession):
    title = await session.prompt_async("Neuer Titel> ")
    subtasks = []
    while True:
        new_subtask = await session.prompt_async("Neue Aufgabe> ")
        if new_subtask == "":
            break

        subtasks.append(new_subtask)

    return title, subtasks


async def new_subtask(session: PromptSession):
    return await session.prompt_async("Neuer Aufgabe> ")


async def prompt_new(type: Type, console: Console, session: PromptSession):
    console.clear()

    if type == Type.TITLE:
        return_value = await new_task(session)

    if type == Type.SUBTASK:
        return_value = await new_subtask(session)

    console.clear()
    console.show_cursor(False)
    console.print("[green]❯[/green] [blue]./stream[/blue] [cyan]--current-task[/cyan]")
    return return_value


async def run_live_view_async() -> None:
    console = Console(theme=Theme({"repr.number": "default"}))
    console.set_window_title("☒☐☒☐")
    console.show_cursor(False)
    console.clear()
    console.print("[green]❯[/green] [blue]./stream[/blue] [cyan]--current-task[/cyan]")

    done = asyncio.Event()
    key_pressed = asyncio.Event()
    new_title_requested = asyncio.Event()
    new_subtasks_requested = asyncio.Event()
    input = create_input()
    session = PromptSession()

    with open(".task") as file:
        lines = [line.rstrip() for line in file]

    title = lines.pop(0)
    done_refix = "x "
    marked_task = None

    def keys_ready():
        nonlocal title
        nonlocal marked_task

        for key_press in input.read_keys():
            if key_press.key == Keys.ControlC:
                done.set()

            if key_press.key.isnumeric() and not key_press.key == 0:
                marked_task = int(key_press.key)

            if key_press.key == 'x' and marked_task:
                line = lines[marked_task - 1]
                if line.startswith(done_refix):
                    lines[marked_task - 1] = line[len(done_refix):]
                else:
                    lines[marked_task - 1] = "x " + line

                marked_task = None

            if key_press.key == 'd' and marked_task:
                del lines[marked_task - 1]

            if key_press.key == 'a' and not marked_task:
                new_subtasks_requested.set()

            if key_press.key == 'c' and not marked_task:
                new_title_requested.set()

            with open(".task", "w") as file:
                file.write(title + "\n" + "\n".join(lines))

            key_pressed.set()

    with input.raw_mode():
        with input.attach(keys_ready):
            with Live(Text(), auto_refresh=False, console=console) as live:
                while True:
                    key_pressed.clear()
                    if done.is_set():
                        break

                    if new_title_requested.is_set():
                        title, lines = await prompt_new(Type.TITLE, console, session)
                        new_title_requested.clear()

                    if new_subtasks_requested.is_set():
                        subtask = await prompt_new(Type.SUBTASK, console, session)
                        lines.append(subtask)
                        new_subtasks_requested.clear()

                    parsed_lines = map(
                        lambda l: f"[x] {l[len(done_refix):]}" if l.startswith(done_refix) else f"[ ] {l}", lines)
                    tasks = rich.markup.escape("\n".join(parsed_lines))
                    display_string = f"""[bold]{title}[/bold][default]\n{tasks}[/default]"""
                    live.update(display_string)
                    live.refresh()
                    await key_pressed.wait()


def show_current_task():
    asyncio.run(run_live_view_async())