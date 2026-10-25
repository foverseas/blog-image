"""The two failures a user can cause, and the only two the CLI catches.

Both carry a message written for whoever wrote the spec file rather than
for whoever wrote the code: `main` prints it and exits 2, with no
traceback. They live outside `schema` because an exception is not a type
the renderer passes around.
"""

from __future__ import annotations


class SpecError(ValueError):
    """The spec file is unusable; the message is meant for the user, not a trace."""


class FontError(RuntimeError):
    """No usable font was found; the message is meant for the user."""
