from contextlib import contextmanager
from contextlib import suppress
from pathlib import Path
from stat import S_IRUSR
from stat import S_IRWXG
from stat import S_IRWXU
from stat import S_IWUSR
from tempfile import TemporaryDirectory
from typing import Generator
from typing import Union

from atomicwrites import move_atomic
from atomicwrites import replace_atomic


@contextmanager
def writer_cm(
    destination: Union[Path, str],
    *,
    overwrite: bool = False,
    dir_perms: int = S_IRWXU | S_IRWXG,
    file_perms: int = S_IRUSR | S_IWUSR,
) -> Generator[Path, None, None]:
    destination = Path(destination).expanduser().resolve()
    parent = destination.parent
    parts = parent.parts
    for idx, _ in enumerate(parts):
        path_parent = Path(*parts[: (idx + 1)])
        with suppress(FileExistsError, IsADirectoryError, PermissionError):
            path_parent.mkdir(mode=dir_perms)
    name = destination.name
    with TemporaryDirectory(suffix=".tmp", prefix=name, dir=parent) as temp_dir:
        source = Path(temp_dir).joinpath(name)
        yield source
        if overwrite:
            replace_atomic(str(source), str(destination))
        else:
            move_atomic(str(source), str(destination))
        destination.chmod(file_perms)
