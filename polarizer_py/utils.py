from pathlib import Path
import os
from modulefinder import ModuleFinder

def get_file_dir(fd):
    p = Path(fd)
    return Path(*p.parts[:-1])


def recurse(start="."):
    """
    Helper function to return all files from a given start directory
    :param start:
    :return:
    """
    if start == ".": start = os.getcwd()
    p = Path(start)
    for i in p.iterdir():
        if i.is_file():
            yield i
        if i.is_dir():
            yield i
            yield from recurse(start=str(i))


def find_all_py_files(start):
    return [p for p in recurse(start=start) if str(p).endswith(".py")]


def imports_metadata(path):
    mf = ModuleFinder()
    mf.run_script(path)
    modules = list(mod for name, mod in mf.modules.items() if "metadata" in name)
    if modules:
        return True
    else:
        return False

