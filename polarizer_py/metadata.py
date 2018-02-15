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
from xml.dom import minidom
import tempfile

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
                   ["polarizer-testcase.json", "polarizer-testcase.yaml", "polarizer-testcase.yml"]),
               (json.load, yaml.load, yaml.load))

    for p, fn in tups:
        if os.path.exists(p):
            with open(p, "r") as cfg:
                return fn(cfg)
    else:
        #raise Exception("Could not find configuration file for polarizer")
        log.error("Could not find config")


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


def _fltr_definitions_by_name(name: str):
    def inner(yaml: Dict):
        tc = yaml["testcase"]
        return tc["name"] == name or name in tc["title"]

    return inner


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
    title = ET.SubElement(root, "title")
    title.text = name
    description = ET.SubElement(root, "description")
    description.text = meta["description"]
    test_steps = ET.SubElement(root, "test-steps")

    test_step_cols = ET.SubElement(test_steps, "test-step-columns", attrib={"id": "step"})
    for ts in meta["test-steps"]:
        test_step = ET.SubElement(test_step_cols, "test-step")
        for param in ts["test-step"]["test-step-column"]:
            p = param["parameter"]
            if p["name"] == "self":
                continue
            param_elm = ET.SubElement(test_step, "parameter", attrib={"name": p["name"], "scope": p["scope"]})
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


def write_xml(path, node):
    with open(path, "w+b") as x:
        x.write(str.encode(node))


def testcase_xml_node(tid, qname, meta, update=False):
    if tid == "" or update:
        log.info("TODO: Test method {} will be added to TestCase import request".format(qname))
        root = meta_to_tc_xml(qname, meta)
        parsed = ET.tostring(root)
        pretty = minidom.parseString(parsed)
        node = pretty.toprettyxml(indent="\t")
        # For some reason, using the NamedTemporaryFile in a with context didn't work
        tf = tempfile.NamedTemporaryFile(suffix=".xml", prefix="polarion-testcase-", dir="/tmp")
        log.info("Created xml definition file in {}".format(tf.name))
        tf.close()
        return tf.name, root
    return "", None


def generate_import_xml(import_list: Dict, cfg=config()):
    s_name = cfg["testcase"]["selector"]["name"]
    s_val = cfg["testcase"]["selector"]["value"]
    nodes = {}
    for project, tcs in import_list.items():
        parent = ET.Element("testcases", attrib={"project-id": project})
        response_props = ET.SubElement(parent, "response-properties")
        response_prop = ET.SubElement(response_props, "response-property", attrib={"name": s_name, "value": s_val})
        for item in tcs:
            qname = item["name"]
            log.info("TODO: Test method {} will be added to TestCase import request".format(qname))
            root = meta_to_tc_xml(qname, item)
            parent.append(root)

        parsed = ET.tostring(parent)
        pretty = minidom.parseString(parsed)
        node = pretty.toprettyxml(indent="  ")
        # For some reason, using the NamedTemporaryFile in a with context didn't work
        tf = tempfile.NamedTemporaryFile(suffix=".xml", prefix="polarion-testcase-", dir="/tmp")
        log.info("Created xml definition file in {}".format(tf.name))
        tf.close()
        write_xml(tf.name, node)
        nodes[project] = tf.name
    return nodes


def calc(kw, mtype=0):
    mtype |= 0 if kw["path"] is None else 1 << 1
    mtype |= 0 if kw["definition"] is None else 1 << 0
    return mtype


def _get_metadata_kwargs(kwargs: Mapping, name: str) -> Dict:
    """
    :param meta_path:
    :return:
    """
    if kwargs["path"] is not None:
        meta_path = kwargs["path"]
        if not os.path.exists(meta_path):
            return {}
        with open(meta_path, "r") as cfg:
            defs = yaml.load(cfg)
        if defs is not None:
            fltr = _fltr_definitions_by_name(name)
            definition = list(filter(fltr, defs))
            if len(definition) > 1:
                tc_def = definition[0]
                log.error("Found multiple entries with {} in {} file. Using {}".format(name, meta_path, tc_def))
                return tc_def
            if len(definition) == 0:
                err = "No definition found for {} in file."
                log.error(err)
                raise Exception(err)
    elif kwargs["definition"] is not None:
        return {"testcase": kwargs["definition"]}
    else:
        return {}


def _get_definitions_from_path(def_path: str) -> Dict:
    with open(def_path, "r") as definitions:
        defs = yaml.load(definitions)
    return defs


def _get_metadata_definitions(def_path: str) -> Dict:
    defs = _get_definitions_from_path(def_path)
    if not defs:
        return {}

    # Return a dictionary instead of a list, keyed by name.  This means names must be unique
    testcases = {}
    for d in defs:
        tc = d["testcase"]
        name = tc["name"]
        project = tc["project"]
        if name not in testcases:
            testcases[name] = {}
            if isinstance(project, str):
                testcases[name][project] = tc
            else:
                for p in project:
                    testcases[name][p] = tc
    return testcases


def get_meta_from_dict(definitions: Mapping, qname: str, project: str) -> Dict:
    if qname not in definitions:
        return {}
    if project not in definitions[qname]:
        return {}
    return definitions[qname][project]


class MetaData:
    """
    Container class so that every function wrapped with @metadata can store information here
    """
    cfg = config()
    mapping = get_mapping(cfg["mapping"])
    definitions = _get_metadata_definitions(cfg["definitions-path"])
    import_list = {}
    import_by = set()

    @classmethod
    def update_definition(cls, qname: str, project: str, map_id: str):
        """Edits the map_id in the id field of the definition file"""
        meta = cls.definitions[qname][project]
        meta["id"] = map_id

    @classmethod
    def update_mapping(cls, qname: str, project: str, meta_id: str):
        """
        Edits the mapping.json file id key with the meta_id value

        :param qname:
        :param project:
        :param meta_id:
        :return:
        """
        meta = get_meta_from_dict(cls.definitions["testcase"], qname, project)
        if qname not in cls.mapping:
            log.error("Could not find {} in mapping.json".format(qname))
            cls.mapping[qname] = {project: {}}
        if project not in cls.mapping[qname]:
            cls.mapping[qname][project] = {}
        cls.mapping[qname][project]["id"] = meta_id

    @classmethod
    def compare_map_to_meta(cls, qname: str, project: str, map_id: str, meta_id: str, update=False):
        """
        There are 4 possibilities.

        | map.id  | meta.id |
        |---------|---------|------------------------------
        | 0       | 0       | 0: neither are empty strings. Check equality, and warn if mismatch but do nothing
        | 0       | 1       | 1: meta is empty. update meta with map_id
        | 1       | 0       | 2: map is empty. update map with meta.id
        | 1       | 1       | 4: both are empty. add to import testcase list

        :param qname:
        :param project:
        :param map_id:
        :param meta_id:
        :param update:
        :return:
        """

        def check(choice=0):
            choice |= 1 << 1 if map_id == "" else 0
            choice |= 1 << 0 if meta_id == "" else 0
            return choice

        comparison = check()
        if comparison == 0:
            if map_id != meta_id: log.error("{} in map and {} in meta do not match".format(map_id, meta_id))
        elif comparison == 1:
            cls.update_definition(qname, project, map_id)
        elif comparison == 2:
            cls.update_mapping(qname, project, meta_id)
        elif comparison == 3 or update:
            if project not in cls.import_list:
                cls.import_list[project] = []
            metas = cls.import_list[project]
            meta = get_meta_from_dict(cls.definitions, qname, project)
            if not meta:
                raise Exception("No metadata for {} in {}.  Can not create XML definition".format(qname, project))
            metas.append(meta)

    @classmethod
    def _get_metadata(cls, kwargs: Dict, name: str):
        """
        The @metadata decorator can have 4 possibilities:

        +------+------------+------------------------------------------------------------------------------------
        | path | definition | Action
        +======+============+====================================================================================
        | 0    | 0          | 0: Uses the path from config()["definitions-path"] for default definition file
        +------+------------+------------------------------------------------------------------------------------
        | 0    | 1          | 1: Compares the dict with the matching default definition file, editing as needed
        +------+------------+------------------------------------------------------------------------------------
        | 1    | 0          | 2: Uses a custom definition file
        +------+------------+------------------------------------------------------------------------------------
        | 1    | 1          | 3: Compared the dict with custom definition file, editing as needed
        +------+------------+------------------------------------------------------------------------------------


        :param kwargs:
        :param name:
        :return:
        """
        mtype = calc(kwargs)

        def type1():
            meta_tc = kwargs["definition"]
            meta_tc["name"] = name
            def_tc = cls.definitions[name] if name in cls.definitions else {}

            if not def_tc:
                final = meta_tc
            else:
                for k, v in meta_tc.items():
                    if k == "update":
                        continue
                    def_tc[k] = v
                final = def_tc
            final["title"] = name
            if name not in cls.definitions:
                cls.definitions[name] = {}
            if isinstance(final["project"], str):
                cls.definitions[name][final["project"]] = final
            else:
                for prj in final["project"]:
                    cls.definitions[name][prj] = final
            return cls.definitions[name]

        def type2():
            meta_path = kwargs["path"]
            if not os.path.exists(meta_path):
                return {}
            defs = _get_metadata_definitions(meta_path)
            if defs is not None:
                if name in defs:
                    return defs[name]
                else:
                    err = "No definition found for {} in file {}.".format(name, meta_path)
                    log.error(err)
                    raise Exception(err)

        if mtype == 0:
            return cls.definitions[name] if name in cls.definitions else {"testcase": {}}
        elif mtype == 1:
            return type1()
        elif mtype == 2:
            return type2()
        else:
            def_tc = type1()
            path_tc = type2()
            for k, v in path_tc.items():
                def_tc[k] = v
            return def_tc

    @classmethod
    def metadata(cls, cfg=config(), path=None, definition=None):
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

        def outer(fn):
            """Code here gets executed at decoration not invocation time"""
            qname = qual_name(fn)
            tcs = cls._get_metadata({"path": path, "definition": definition}, qname)

            for project in tcs:
                meta = tcs[project]
                # Set up the defaults
                test_case_id = meta["id"]
                update = meta["update"] if "update" in meta else False
                mapping = cls.mapping

                # Insert information about the function via reflection
                is_doc = hasattr(fn, "__docstring__")
                meta["description"] = fn.__docstring__ if is_doc else "No docstring for {}".format(qname)
                meta["test-steps"] = _get_test_steps(fn)
                _set_custom_defaults(meta)
                cls.definitions[qname][project] = meta

                def set_fn_in_mapping(imap: Dict) -> Dict:
                    """
                    Writes the inner map conaining the id and params to the mapping json file

                    :param imap:
                    :return:
                    """
                    imap[project] = {
                        "id": test_case_id,
                        "params": list(fn.__code__.co_varnames)
                    }
                    with open(cfg["mapping"], "w") as j:
                        json.dump(mapping, j, sort_keys=True, indent=2)
                    return mapping

                # Set up the mapping.json appropriately. If the qualified name is not in the mapping file, add it.
                # If it is in mapping.json, check if the testcase_id is set for the project
                if qname not in mapping:
                    mapping[qname] = {}
                    set_fn_in_mapping(mapping[qname])
                elif project not in mapping[qname]:
                    set_fn_in_mapping(mapping[qname])
                else:
                    log.debug("{} already in map file for project {}".format(qname, project))

                # Compare the meta defintion with the mapping definition and do what is needed.  This will add functions
                # to the cls.import_list as needed
                map_id = mapping[qname][project]["id"]
                cls.compare_map_to_meta(qname, project, map_id, test_case_id, update=update)

            @wraps(fn)
            def inner(*args, **kwds):
                """This gets called only when decorated method is invoked"""
                return fn(*args, **kwds)
            return inner
        return outer

    @classmethod
    def make_testcase_xml(cls):
        return generate_import_xml(cls.import_list, cfg=cls.cfg)

    @classmethod
    def testcase_import(cls):
        """
        Makes a call to polarizer

        :return:
        """
        pass


metadata = MetaData.metadata
