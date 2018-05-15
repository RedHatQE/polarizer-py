from pathlib import Path
import os
from modulefinder import ModuleFinder
from typing import Generator, Union, Sequence
from subprocess import Popen, PIPE, STDOUT
import time
import shutil

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


def launch(cmd: str, env=None, cwd=None, shell=False, timeout: int = 300):
    if env is None:
        env = os.environ
    if cwd is None:
        cwd = os.getcwd()
    if isinstance(cmd, str) and shell is False:
        cmd = cmd.split(" ")
        cmd = list(filter(lambda x: x != '', cmd))
    print("Executing command {}".format(cmd))

    proc = Popen(cmd, stdout=PIPE, stderr=STDOUT, env=env, cwd=cwd, shell=shell)
    out, err = proc.communicate()
    ret = proc.poll()
    if ret is not None and ret != 0:
        print("Command Failed. Return code = {}".format(ret))
    count = 0
    while ret is None and count < timeout:
        time.sleep(5)
        count += 5
        print("waiting for command '{}' to finish: {}".format(cmd, count))
    output = out.decode(encoding='utf-8')
    print(output)
    return output, proc.returncode


def remove(substr: str, replace: str,  file: str, tmp: str):
    print("in file {}".format(file))
    with open(file, "r") as java:
        with open(tmp, "w") as temp:
            for i, line in enumerate(java.readlines()):
                if substr in line:
                    newline = line.replace(substr, replace)
                    print("Removing {} from {}".format(substr, line))
                    print("line {} is now: {}".format(i, newline))
                    temp.write(newline)
                else:
                    temp.write(line)

    shutil.move(tmp, file)


if __name__ == "__main__":
    rhsm_qe = "/home/stoner/Projects/rhsm-qe/src/rhsm/cli/tests"
    from pathlib import Path
    ls = Path(rhsm_qe)
    java = [j for j in list(ls.glob("**/*.java")) if j.is_file()]
    for j in java:
        tmp = "/tmp/{}".format(j.name)
        remove('DefTypes.Role.VERIFIES', "DefTypes.Role.IS_VERIFIED_BY", str(j), tmp)

    if False:
        import argparse

        parser = argparse.ArgumentParser()
        parser.add_argument("-s", "--substr", help="Text to search for and replace")
        parser.add_argument("-r", "--replace", help="Text to replace if substr is found")
        parser.add_argument("-f", "--file", help="File to search")
        parser.add_argument("-t", "--temp", help="Temporary file")
        opts = parser.parse_args()

        remove(opts.substr, opts.replace, opts.file, opts.temp)

