from polarizer_py.metadata import metadata
from polarizer_py.utils import get_file_dir
from pathlib import Path

this_dir = get_file_dir(__file__)
test_dir = Path(this_dir, "definitions")

"""
@metadata(path=str(Path(test_dir, "polarizer_py.tests.testmeta.yaml")))
def test2(name: str) -> str:
    print("you passed in {}".format(name))
    return name + ": got it"
"""


class MyTest:
    def __init__(self, x):
        self.x = x

    @metadata(definition={
        "project": "RedHatEnterpriseLinux7",
        "id": "",
        "custom-fields": {
            "importance": "",
            "automation": "",
            "caselevel": "",
            "caseposneg": "",
            "casecomponent": "",
            "testtype": "functional",
            "subtype1": "",
            "subtype2": "",
            "tags": "comma,separated,values"
        }
    })
    def test3(self, y, bar=""):
        print("Just seeing how it works as a method")
        return y + bar
