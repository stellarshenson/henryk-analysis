"""
Logging utilities for the henryk analysis project.

Provides colored console output, progress bars, and notebook cell control.
"""
import sys

from colorama import Back, Fore, Style
from loguru import logger


# Configure loguru with tqdm-compatible output
logger.remove()
try:
    from tqdm import tqdm
    logger.add(lambda msg: tqdm.write(msg, end="", file=sys.stdout), colorize=True)
except ModuleNotFoundError:
    logger.add(sys.stdout, colorize=True)


def progress_bar(
    iteration: int,
    total: int,
    prefix: str = "",
    suffix: str = "",
    decimals: int = 1,
    length: int = 50,
    fill: str = "\u2588",
    print_end: str = "\r",
) -> None:
    """
    Call in a loop to create terminal progress bar.

    Parameters
    ----------
    iteration : int
        Current iteration
    total : int
        Total iterations
    prefix : str
        Prefix string
    suffix : str
        Suffix string
    decimals : int
        Positive number of decimals in percent complete
    length : int
        Character length of bar
    fill : str
        Bar fill character
    print_end : str
        End character (e.g. "\\r", "\\r\\n")
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filled_length = int(length * iteration // total)
    bar = fill * filled_length + "-" * (length - filled_length)
    print(f"\r{prefix} |{bar}| {percent}% {suffix}", end=print_end)
    if iteration == total:
        print()


# Alias for backwards compatibility
progressBar = progress_bar


def coloured_text(
    text: str,
    colour: str = "white",
    bg_colour: str = "normal",
    style: str = "normal",
) -> str:
    """
    Returns coloured text using Colorama.

    Parameters
    ----------
    text : str
        The text to be coloured
    colour : str
        The text colour (default: white)
    bg_colour : str
        The background colour (default: normal)
    style : str
        The text style (default: normal)

    Returns
    -------
    str
        Coloured text string
    """
    colour_mapping = {
        "black": Fore.BLACK,
        "red": Fore.RED,
        "green": Fore.GREEN,
        "yellow": Fore.YELLOW,
        "blue": Fore.BLUE,
        "magenta": Fore.MAGENTA,
        "cyan": Fore.CYAN,
        "white": Fore.WHITE,
        "lightgreen": Fore.LIGHTGREEN_EX,
        "lightred": Fore.LIGHTRED_EX,
        "lightblue": Fore.LIGHTBLUE_EX,
    }
    bg_colour_mapping = {
        "black": Back.BLACK,
        "red": Back.RED,
        "green": Back.GREEN,
        "yellow": Back.YELLOW,
        "blue": Back.BLUE,
        "magenta": Back.MAGENTA,
        "cyan": Back.CYAN,
        "white": Back.WHITE,
        "normal": Back.RESET,
    }
    style_mapping = {
        "normal": Style.NORMAL,
        "bright": Style.BRIGHT,
        "dim": Style.DIM,
    }

    selected_colour = colour_mapping.get(colour.lower(), Fore.WHITE)
    selected_bg_colour = bg_colour_mapping.get(bg_colour.lower(), Back.RESET)
    selected_style = style_mapping.get(style.lower(), Style.NORMAL)

    return f"{selected_style}{selected_bg_colour}{selected_colour}{text}{Style.RESET_ALL}"


def coloured_print(
    text: str,
    colour: str = "white",
    bg_colour: str = "normal",
    style: str = "normal",
) -> None:
    """Wrapper function for print that prints coloured text using Colorama."""
    print(coloured_text(text, colour, bg_colour, style))


class StopExecution(Exception):
    """
    Raise this exception to quietly stop notebook processing.

    Example
    -------
    >>> raise StopExecution
    """

    def _render_traceback_(self):
        return []


def exit_cell():
    """Exit the current notebook cell."""
    raise StopExecution("stopped")


# EOF
