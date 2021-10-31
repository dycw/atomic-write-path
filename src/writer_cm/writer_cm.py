from __future__ import annotations

from contextlib import contextmanager
from contextlib import suppress
from pathlib import Path
from shutil import chown
from stat import S_IRGRP
from stat import S_IRUSR
from stat import S_IWUSR
from stat import S_IXGRP
from stat import S_IXUSR
from tempfile import TemporaryDirectory
from typing import Iterator

from atomicwrites import move_atomic
from atomicwrites import replace_atomic


@contextmanager
def writer_cm(
    destination: Path | str,
    *,
    overwrite: bool = False,
    dir_perms: int = S_IRUSR | S_IWUSR | S_IXUSR | S_IRGRP | S_IXGRP,
    file_perms: int = S_IRUSR | S_IWUSR,
    user: str | None = None,
    group: str | None = None,
) -> Iterator[Path]:
    """Context manager allowing you to atomically write files given a target
    path.

    Parameters:
      - `destination` (`pathlib.Path` or `str`):
          the target path to write the file to.
      - `overwrite` (bool, default=False):
          whether to overwrite the target file if it already exists.
      - `dir_perms` (int, default=`u=rwx,g=rx,o=`):
          the permissions of any parent directories to be created. A
          recommended way to provide this integer value is to use the flags
          from the built-in `stat` module.
      - `file_perms` (int, default=`u=rwx,g=rx,o=`):
          the permissions of the target file to be created
      - `user` (str or None, default=None):
          the user owner of the parent directories to be created and the target
          file.
      - `group` (str or None, default=None):
          the group owner of the parent directories to be created and the
          target file.

    Returns: context manager
    """

    destination = Path(destination).expanduser().resolve()
    parent = destination.parent
    parts = parent.parts
    for idx, _ in enumerate(parts):
        path_parent = Path(*parts[: (idx + 1)])
        with suppress(FileExistsError, IsADirectoryError, PermissionError):
            path_parent.mkdir()
            _set_properties(
                path_parent, permissions=dir_perms, user=user, group=group
            )
    name = destination.name
    with TemporaryDirectory(suffix=".tmp", prefix=name, dir=parent) as temp_dir:
        source = Path(temp_dir).joinpath(name)
        yield source
        if overwrite:
            replace_atomic(str(source), str(destination))
        else:
            move_atomic(str(source), str(destination))
        _set_properties(
            destination, permissions=file_perms, user=user, group=group
        )


def _set_properties(
    path: Path, permissions: int, user: str | None, group: str | None
) -> None:
    """Set the permissions and/or ownership of a file."""

    path.chmod(permissions)
    if (user is not None) or (group is not None):
        chown(path, user=user, group=group)
