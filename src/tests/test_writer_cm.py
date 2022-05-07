from pathlib import Path
from stat import S_IRUSR
from stat import S_IRWXG
from stat import S_IRWXO
from stat import S_IRWXU
from stat import S_IWUSR
from stat import S_IXUSR
from sys import platform
from typing import Union

from pytest import mark
from pytest import param
from pytest import raises

from writer_cm import writer_cm


@mark.parametrize(
    "is_binary, contents",
    [
        param(False, "contents", id="text"),
        param(True, b"contents", id="binary"),
    ],
)
def test_basic_usage(
    tmp_path: Path, is_binary: bool, contents: Union[str, bytes]
) -> None:
    path = tmp_path.joinpath("file.txt")
    with writer_cm(path) as temp, open(
        temp, mode="wb" if is_binary else "w"
    ) as fh1:
        _ = fh1.write(contents)
    with open(str(path), mode="rb" if is_binary else "r") as fh2:
        assert fh2.read() == contents


def test_dir_perms(tmp_path: Path) -> None:
    path = tmp_path.joinpath("dir1/dir2/dir3/file.txt")
    with writer_cm(path, dir_perms=S_IRWXU) as temp, open(temp, mode="w") as fh:
        _ = fh.write("contents")
    parts = path.relative_to(tmp_path).parent.parts
    for idx, _ in enumerate(parts):
        path_parent = tmp_path.joinpath(*parts[: (idx + 1)])
        assert path_parent.is_dir()
        assert path_parent.stat().st_mode & S_IRWXU & (~S_IRWXG) & (~S_IRWXO)


@mark.skipif(
    platform == "win32", reason=r"re.error: incomplete escape \U at position 2"
)
def test_file_exists_error(tmp_path: Path) -> None:
    path = tmp_path.joinpath("file.txt")
    with writer_cm(path) as temp1, open(temp1, mode="w") as fh1:
        _ = fh1.write("contents")
    with raises(FileExistsError, match=str(path)), writer_cm(
        path
    ) as temp2, open(temp2, mode="w") as fh2:
        _ = fh2.write("new contents")


def test_file_perms(tmp_path: Path) -> None:
    path = tmp_path.joinpath("file.txt")
    with writer_cm(path, file_perms=S_IRUSR) as temp, open(
        temp, mode="w"
    ) as fh:
        _ = fh.write("contents")
    assert (
        path.stat().st_mode
        & S_IRUSR
        & (~S_IWUSR)
        & (~S_IXUSR)
        & (~S_IRWXG)
        & (~S_IRWXO)
    )


def test_overwrite(tmp_path: Path) -> None:
    path = tmp_path.joinpath("file.txt")
    with writer_cm(path) as temp1, open(temp1, mode="w") as fh1:
        _ = fh1.write("contents")
    with writer_cm(path, overwrite=True) as temp2, open(temp2, mode="w") as fh2:
        _ = fh2.write("new contents")
    with open(str(path)) as fh3:
        assert fh3.read() == "new contents"
