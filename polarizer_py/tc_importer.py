from polarizer_py.utils import launch
from polarizer_py.json_files import tcargs
import os
import shutil
import json
from pprint import pprint
import requests
import argparse


def git_compile(branch: str):
    git_cmd = "git checkout {}".format(branch)
    launch(git_cmd)
    launch("lein clean")
    launch("lein uberjar")


def create_tc_args(config, argpath: str):
    config["project"] = "RHEL6"
    config["testcase"]["enabled"] = os.environ["IMPORTER_ENABLED"]
    with open(argpath, 'w') as tc_args:
        tc = json.dumps(config, indent=2)
        print(tc)
        tc_args.write(tc)


def call_curl(tcargs_path: str, jarpath: str, mapping_path: str):
    cmd = '''curl -F tcargs=@{} \
    -F jar=@{} \
    -F mapping=@{} \
    http://rhsm-cimetrics2.usersys.redhat.com:9000/testcase/mapper | python -m json.tool'''\
        .format(tcargs_path, jarpath, mapping_path)
    print("Calling " + cmd)

    # The synchronous version
    return launch(cmd, shell=True)


def call_curl_req(tcargs_path, jarpath, mapping_path):
    files = {"tcargs": ('tcargs.json', open(tcargs_path, 'rb'), 'application/json'),
             "mapping": ('mapping.json', open(mapping_path, 'rb'), 'application/json'),
             "jar": ('sm-1.1.0-SNAPSHOT-standalone.jar', open(jarpath, 'rb'), 'application/java-archive')}
    r = requests.post('http://rhsm-cimetrics2.usersys.redhat.com:9000/testcase/mapper', files=files)
    return r


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Script to make testcase import")
    parser.add_argument("-m", "--new-mapping-path", help="Path to the new mapping.json file")
    parser.add_argument("-t", "--test", help="If true, clone rhsm-qe to /tmp", action="store_true", default=True)
    opts = parser.parse_args()

    if opts.test:
        if os.path.exists("/tmp/rhsm-qe"):
            shutil.rmtree("/tmp/rhsm-qe")
        os.chdir("/tmp")
        if not os.path.exists("/tmp/rhsm-qe"):
            launch("git clone https://github.com/rarebreed/rhsm-qe.git")
        os.chdir("/tmp/rhsm-qe")

    if 'WORKSPACE' not in os.environ:
        os.environ["WORKSPACE"] = "/tmp/rhsm-qe"
    if 'IMPORTER_ENABLED' not in os.environ:
        os.environ["IMPORTER_ENABLED"] = "false"
    if 'RHSMQE_BRANCH' not in os.environ:
        os.environ["RHSMQE_BRANCH"] = "master"
    if 'TC_IMPORT_CFG' not in os.environ:
        tc = json.dumps(tcargs, indent=2)
        print(tc)
        os.environ["TC_IMPORT_CFG"] = tc

    # Clean and compile
    git_compile(os.environ["RHSMQE_BRANCH"])

    JAR_NAME = launch("ls {}/target | grep standalone".format(os.getcwd()), shell=True)[0].strip()
    UBERJAR_PATH = "{}/target/{}".format(os.getcwd(), JAR_NAME)
    MAPPING_JSON_PATH = "{}/mapping.json".format(os.getcwd())
    TC_ARGS_PATH = "{}/tcargs.json".format(os.environ["WORKSPACE"])

    create_tc_args(tcargs, TC_ARGS_PATH)
    resp = call_curl_req(TC_ARGS_PATH, UBERJAR_PATH, MAPPING_JSON_PATH)

    jresp = json.loads(resp.text)
    mapping = jresp["mapping"]
    pprint(jresp, indent=2)

    with open(opts.new_mapping_path, "w") as new_map:
        new_map.write(json.dumps(mapping, indent=2, sort_keys=True))
