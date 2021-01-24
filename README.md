# writer-cm

`writer-cm` is a context manager allowing you to atomically write files given a
file path.

## Features

- Cross-platform atomic file writes powered by
  [python-atomicwrites](https://github.com/untitaker/python-atomicwrites).
- Interface using a file path instead of a file handle, for more compatibility
  with external libraries (e.g. `pandas.to_pickle`).
- Automatically create missing directories and set their permissions.
- Automatically set the file permissions.

## How?

```python
from writer_cm import writer_cm

with writer_cm("file.txt") as temp:
    with open(temp, mode="w") as fh:
        fh.write("foo")

with open("file.txt") as fh:
    assert fh.read() == "foo"

# Specify overwrite=True

with writer_cm("file.txt", overwrite=True) as temp:
    with open(temp, mode="w") as fh:
        fh.write("bar")

with open("file.txt") as fh:
    assert fh.read() == "bar"
```
