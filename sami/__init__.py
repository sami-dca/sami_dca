from pathlib import Path as _Path

# from .controller import Controller

__version__ = (_Path(__file__).parent / "VERSION.txt").read_text().strip()
