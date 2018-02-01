"""
This module contains some decorators and useful classes to hold metadata for your python based tests.

The idea is that all your tests will be decorated by the metadata decorator, which in turn will
"""

from functools import wraps
import yaml
import os
import json
import types
from typing import Mapping, Callable, Union
from pathlib import Path
from xml.etree import ElementTree

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
    polarizer_json = os.path.join(polarizer_dir, "polarizer-testcase.json")
    polarizer_yaml = os.path.join(polarizer_dir, "polarizer-testcase.yaml")
    polarizer_yml = os.path.join(polarizer_dir, "polarizer-testcase.yml")

    for p, fn in [(polarizer_json, json.load), (polarizer_yaml, yaml.load), (polarizer_yml, yaml.load)]:
        if os.path.exists(p):
            with open(p, "r") as cfg:
                return fn(cfg)
    else:
        raise Exception("Could not find configuration file for polarizer")


def _get_metadata_kwargs(kwargs):
    meta = {}
    meta["project"] = kwargs.get("project", "")
    meta["test_case_id"] = kwargs.get("test_case_id", "")
    meta["importance"] = kwargs.get("importance", "MEDIUM")
    meta["posneg"] = kwargs.get("posneg", "POSITIVE")
    meta["level"] = kwargs.get("level", "SYSTEM")
    meta["linked_work_items"] = kwargs.get("linked_work_items")
    meta["testtype"] = kwargs.get("testtype")
    meta["setup"] = kwargs.get("setup", "")
    meta["teardown"] = kwargs.get("teardown", "")
    meta["tags"] = kwargs.get("tags")
    meta["update"] = kwargs.get("update", False)
    meta["automation"] = kwargs.get("automation")

    return meta


def get_mapping(map_path):
    if not os.path.exists(map_path):
        raise Exception("Could not find mapping.json file")

    with open(map_path, "r") as mapf:
        mapper = json.load(mapf)
    return mapper


def fltr_id(tid):
    def inner(item):
        _, inner_map = item
        for proj, params in inner_map.items():
            if params["id"] == tid:
                return True
        else:
            return False

    return inner


def fltr_name(name: str) -> Mapping:
    def inner(item):
        fn_name, inner_map = item
        if fn_name == name:
            return True
        else:
            return False

    return inner


def qual_name(obj) -> str:
    if isinstance(obj, types.ModuleType):
        return "{}.{}".format(obj.__package__, obj.__name__)
    else:
        return "{}.{}".format(obj.__module__, obj.__name__)


def meta_to_tc_xml(meta: Mapping) -> Path:
    """

    :param meta:
    :return:
    """
    pass


def metadata(cfg=config(), **kwargs):
    """
    Decorator to wrap any test methods with.  This method
    """
    meta = _get_metadata_kwargs(kwargs)

    # Set up the defaults
    test_case_id = meta["test_case_id"]
    update = meta["update"]
    project = meta["project"]

    def outer(fn):
        """Code here gets executed at decoration not invocation time"""
        # get the mapping file, and see if the name from the metadata exists in it.
        mapping = get_mapping(cfg["mapping"])
        qname = qual_name(fn)

        def set_fn_in_mapping(imap: Mapping) -> Mapping:
            imap[project] = {
                "id": test_case_id,
                "params": list(fn.__code__.co_varnames)
            }
            with open(cfg["mapping"], "w") as j:
                json.dump(mapping, j, sort_keys=True, indent=2)
            return mapping

        # If the qualified name is not in the mapping file, add it.  Otherwise if it is in mapping.json, check if the
        # testcase_id is set in
        if qname not in mapping:
            mapping[qname] = {}
            set_fn_in_mapping(mapping[qname])
        else:
            if project not in mapping[qname]:
                set_fn_in_mapping(mapping[qname])

        entry_by_name = mapping[qname][project]
        if entry_by_name["id"] == "":
            print("TODO: Test method {} will be added to TestCase import request".format(qname))

        @wraps(fn)
        def inner(*args, **kwds):
            """This gets called only when decorated method is invoked"""
            return fn(*args, **kwds)

        return inner

    return outer
