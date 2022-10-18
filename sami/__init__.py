from pathlib import Path as _Path

__version__ = (_Path(__file__).parent / "VERSION.txt").read_text().strip()

# from .controller import Controller
from .network import Networks  # noqa
