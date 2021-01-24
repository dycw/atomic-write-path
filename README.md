# writer-cm

![GitHub](https://github.com/dycw/writer-cm/workflows/push/badge.svg)
[![PyPI version](https://badge.fury.io/py/writer-cm.svg)](https://badge.fury.io/py/writer-cm)

## Overview

`writer-cm` is a context manager allowing you to atomically write files given a
file path.

## Features

- Cross-platform atomic file writes powered by
  [python-atomicwrites](https://github.com/untitaker/python-atomicwrites).
- Interface using a file path instead of a file handle, for more compatibility
  with external libraries (e.g. `pandas.to_pickle`).
- Automatically create missing directories and set their permissions.
- Automatically set the file permissions.

## Installation

```bash
pip install writer-cm
```

## Usage

Import and invoke `writer_cm` as a context manager to obtain a `pathlib.Path`
object to which you can atomically write to:

```python
from writer_cm import writer_cm

with writer_cm("file.txt") as temp:
    # `temp` is a `pathlib.Path` object

    with open(temp, mode="w") as fh:
        fh.write("foo")

# file.txt is atomically written to upon leaving the context manager

with open("file.txt") as fh:
    assert fh.read() == "foo"
```

`writer_cm` can also automatically create missing directories and set their
permissions (which is done carefully as opposed to relying on
[`Path.mkdir`](https://docs.python.org/3/library/pathlib.html#pathlib.Path.mkdir),
which itself notes that "\[parents\] are created with the default permissions
without taking _mode_ into account"). Analogously, `writer_cm` can also set the
file permissions too.

```python
from stat import S_IRWXU, S_IRWXG, S_IRUSR, S_IWUSR

with writer_cm("dir1/dir2/dir3/file.txt",
               dir_perms=S_IRWXU | S_IRWXG,   # the default
               file_perms=S_IRUSR | S_IWUSR,  # the default
               ) as temp:
    with open(temp, mode="w") as fh:
        fh.write("foo")

# now `dir1/dir2/dir3`          has been created with u=rwx,g=rwx permissions
#     `dir1/dir2/dir3.file.txt` has been created with u=rw        permissions
```

For more info on `stat`, see the
[official docs](https://docs.python.org/3/library/stat.html).

Finally, pass `overwrite=True` to overwrite an already existing file; an error
is thrown otherwise:

```python
with writer_cm("file.txt", overwrite=True) as temp:
    with open(temp, mode="w") as fh:
        fh.write("bar")

with open("file.txt") as fh:
    assert fh.read() == "bar"
```
