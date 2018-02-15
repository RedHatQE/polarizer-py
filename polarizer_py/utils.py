from pathlib import Path
import os
from modulefinder import ModuleFinder
from typing import Generator, Union, Sequence


def get_file_dir(fd: str, up: int=1) -> Path:
    p = Path(fd)
    return Path(*p.parts[:-up])


def recurse(start: Path=None, get_dirs=False, excludes: Sequence[str]=None) -> Generator[Path, None, None]:
    """
    Helper function to return all files from a given start directory

    :param excludes:
    :param get_dirs:
    :param start:
    :return:
    """
    if excludes is None:
        excludes = []
    if start is None: start = Path(os.getcwd())
    for i in start.iterdir():
        if i.is_file():
            yield i
        if i.is_dir():
            if get_dirs:
                yield i
            if i.name not in excludes:
                yield from recurse(start=i)


def find_all_py_files(start: str, excludes=None) -> Generator[Path, None, None]:
    return (p for p in recurse(start=Path(start), excludes=excludes) if str(p).endswith(".py"))


def imports_metadata(path: Union[str, Path]) -> bool:
    mf = ModuleFinder()
    if isinstance(path, Path):
        path = str(path)
    mf.run_script(path)
    modules = list(mod for name, mod in mf.modules.items() if "metadata" in name)
    if modules:
        return True
    else:
        return False


def run(project: str):
    modules = filter(imports_metadata, find_all_py_files(project, excludes=["venv"]))
    for i in modules:
        print(i)
    return modules


if __name__ == "__main__":
    import sys
    args = sys.argv
    run(args[1])

