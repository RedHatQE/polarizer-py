"""
This module contains some decorators and useful classes to hold metadata for your python based tests.

The idea is that all your tests will have a YAML based definition file, and the metadata decorator will point to that
file.
"""

from functools import wraps
import yaml
import os
import json
import types
from inspect import getfullargspec
from typing import Mapping, Callable, Sequence, Dict
from . logger import glob_logger as log
from pprint import pprint
from xml.etree import ElementTree as ET

# We can look for the configuration file in 2 places:
# - The default which is in ~/.polarizer/polarizer-testcase.json|yml
# - Look for environment variable POLARIZER_TESTCASE_CONFIG and use path defined there
POLARIZER_TESTCASE_CONFIG = "POLARIZER_TESTCASE_CONFIG"


def config():
    if POLARIZER_TESTCASE_CONFIG in os.environ:
        cfg_path = os.environ[POLARIZER_TESTCASE_CONFIG]
        fn = json.load if os.environ[POLARIZER_TESTCASE_CONFIG].endswith(".json") else yaml.load
        with open(cfg_path, "r") as cfg:
            return fn(cfg)

    polarizer_dir = os.path.join(os.path.expanduser("~"), ".polarizer")
    tups = zip(map(lambda x: os.path.join(polarizer_dir, x),
                   ["polarizer-testcase.json",  "polarizer-testcase.yaml", "polarizer-testcase.yml"]),
               (json.load, yaml.load, yaml.load))

    for p, fn in tups:
        if os.path.exists(p):
            with open(p, "r") as cfg:
                return fn(cfg)
    else:
        raise Exception("Could not find configuration file for polarizer")


def _validate_meta(meta):
    """
    Validates that the required fields are in the dictionary

    :param meta:
    :return:
    """
    return filter(lambda i: i not in meta, ["project", "id"])


def _set_custom_defaults(meta):
    """
    Give the metadata dictionary passed in from the decorator, if anything is either missing or falsey, set it to a
    default value

    :param meta:
    :return:
    """
    custom = meta["custom-fields"]

    def set_default(name, default):
        if name not in custom or not custom[name]:
            custom[name] = default

    defs = [("caseimportance", "medium"),
            ("caseautomation", "automated"),
            ("caselevel", "component"),
            ("caseposneg", "positive"),
            ("testtype", "functional"),
            ("subtype1", "-"),
            ("subtype2", "-")]
    map(lambda n, d: set_default(n, d), defs)


def _get_metadata_kwargs(kwargs: Mapping) -> Dict:
    """
    Retrieves the path to the test definition, and returns a dict

    :param meta_path:
    :return:
    """
    if kwargs["path"] is not None:
        meta_path = kwargs["path"]
        if not os.path.exists(meta_path):
            return {}
        with open(meta_path, "r") as cfg:
            return yaml.load(cfg)
    elif kwargs["definition"] is not None:
        return {"testcase": kwargs["definition"]}
    else:
        return {}


def get_mapping(map_path):
    if not os.path.exists(map_path):
        raise Exception("Could not find mapping.json file")

    with open(map_path, "r") as mapf:
        mapper = json.load(mapf)
    return mapper


def qual_name(obj) -> str:
    if isinstance(obj, types.ModuleType):
        return "{}.{}".format(obj.__package__, obj.__name__)
    else:
        return "{}.{}".format(obj.__module__, obj.__name__)


def meta_to_tc_xml(name: str, meta: Mapping) -> ET.Element:
    """
    Given the metadata from the dict, create a <testcase> element

    :param name:
    :param meta:
    :param project:
    :return:
    """
    pprint(meta)
    root = ET.Element("testcase", attrib={"id": meta["id"]})
    title = ET.Element("title", text=name)
    description = ET.Element("description", text=meta["description"])
    test_steps = ET.Element("test-steps")

    root.append(title)
    root.append(description)

    test_step_cols = ET.Element("test-step-columns", attrib={"id": "step"})
    for ts in meta["test-steps"]:
        test_step = ET.Element("test-step")
        for param in ts["test-step"]["test-step-column"]:
            p = param["parameter"]
            if p["name"] == "self":
                continue
            param_elm = ET.Element("parameter", attrib={"name": p["name"], "scope": p["scope"]})
            test_step_cols.append(param_elm)
        test_step.append(test_step_cols)
        test_steps.append(test_step)
    root.append(test_steps)
    return root


def _get_test_steps(fn: Callable) -> Sequence:
    """
    Inspects the function object, and returns a sequence of the test steps

    :param fn:
    :return:
    """
    spec = getfullargspec(fn)
    test_step_column = []
    for arg in spec.args:
        parameter = {
            "parameter": {
                "name": arg,
                "scope": "local"
            }
        }
        test_step_column.append(parameter)
    test_step = [{
        "test-step": {
            "test-step-column": test_step_column
        }
    }]
    return test_step


def metadata(cfg=config(), path=None, definition=None):
    """
    The decorator which specifies where the test definition yaml file lives.

    Unlike the java version which uses an annotation to generate the definition, the python version just uses a yaml
    file which is then converted into the XML needed by Polarion.  The decorator simply takes a path to where this
    definition lives.  The advantage to this is that:

    - If the testcase_id is a keyword, it initially starts as "", but what happens when you get a new ID?
    - If you want to update the definitions, if you have a keyword like update=True, how do you tell it to revert back?

    These are problems with the java version that will be fixed by doing something similar here.  Since we can edit a
    plain text file in code (but we can not edit source code as in python decorators or java annotations), we can
    automatically fill in the ID for the testcase, or turn off the update key in the file.

    :param cfg: a dictionary containing configuration options
    :param path: Path to where the yaml definition file is
    :param definition: An optional configuration dictionary
    :return: decorator
    """
    tc = _get_metadata_kwargs({"path": path, "definition": definition})
    meta = tc["testcase"]

    # Set up the defaults
    test_case_id = meta["id"]
    update = meta["update"] if "update" in meta else False
    project = meta["project"]

    def outer(fn):
        """Code here gets executed at decoration not invocation time"""
        # get the mapping file, and see if the name from the metadata exists in it.
        mapping = get_mapping(cfg["mapping"])
        qname = qual_name(fn)

        # Insert information about the function via reflection
        meta["description"] = fn.__docstring__ if hasattr(fn, "__docstring__") else "No docstring for {}".format(qname)
        meta["test-steps"] = _get_test_steps(fn)
        _set_custom_defaults(meta)

        def set_fn_in_mapping(imap: Mapping) -> Mapping:
            imap[project] = {
                "id": test_case_id,
                "params": list(fn.__code__.co_varnames)
            }
            with open(cfg["mapping"], "w") as j:
                json.dump(mapping, j, sort_keys=True, indent=2)
            return mapping

        # If the qualified name is not in the mapping file, add it.
        # If it is in mapping.json, check if the testcase_id is set for the project
        if qname not in mapping:
            mapping[qname] = {}
            set_fn_in_mapping(mapping[qname])
        elif project not in mapping[qname]:
                set_fn_in_mapping(mapping[qname])
        else:
            log.debug("{} already in map file for project {}".format(qname, project))

        # Write out the dictionary to XML if id is "" or update is true.  These will be collected per project
        entry_by_name = mapping[qname][project]
        if entry_by_name["id"] == "" or update:
            log.info("TODO: Test method {} will be added to TestCase import request".format(qname))
            root = meta_to_tc_xml(qname, meta)
            ET.dump(root)

        @wraps(fn)
        def inner(*args, **kwds):
            """This gets called only when decorated method is invoked"""
            return fn(*args, **kwds)
        return inner
    return outer
