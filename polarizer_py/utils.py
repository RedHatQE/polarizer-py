from pathlib import Path


def get_file_dir(fd):
    p = Path(fd)
    return Path(*p.parts[:-1])
