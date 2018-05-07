from typing import Mapping, Dict
from uuid import uuid4
from pathlib import Path
import asyncio
import websockets
import json
from pprint import pprint
import argparse
import os


def make_xunit_import_request(xunit: str, xargs: str = None):
    """
    Creates a WebSocket request to the Polarizer UMB verticle to do a Polarion /import/xunit import

    :param xunit: Path to the xunit xml file to submit
    :param xargs: Path to the json args file needed by polarizer
    :return:
    """
    op = "xunit-import-ws"
    tag = "xunit-import-{}".format(uuid4())
    ack = True
    data = {}
    with open(xunit, "r") as file:
        data["xunit"] = file.read()

    if xargs is None:
        # Look in default location
        home = Path.home()
        xargs = str(home)

    with open(xargs, "r") as file:
        data["xargs"] = file.read()

    data = json.dumps(data)

    return make_umb_request(op, tag=tag, ack=ack, data=data)


def make_testcase_import_request(testcase: str, mapping: str, tcargs: str = None):
    """
    Creates a WebSocket request  to the Polarizer UMB verticle to do a Polarion /import/testcase import

    :param testcase: path to the TestCase xml that will be imported to Polarion
    :param mapping: path to the mapping.json file
    :param tcargs:
    :return: a websocket JSON with an updated mapping.json file
    """
    op = "testcase-import-ws"
    tag = "testcase-import-{}".format(uuid4())
    ack = True
    data = {}

    with open(mapping, "r") as mapfile:
        body = mapfile.read()
        data["mapping"] = body

    with open(testcase, "r") as tcfile:
        data["testcase"] = tcfile.read()

    if tcargs is None:
        # Look in default location
        home = Path.home()
        tcargs = str(home)

    with open(tcargs, "r") as argfile:
        data["tcargs"] = argfile.read()

    data = json.dumps(data)

    return make_umb_request(op, tag=tag, ack=ack, data=data)


def ws_test():
    return {
        "op": "testing",
        "type": "string",
        "tag": "12345",
        "ack": False,
        "data": "This is just a test"
    }


def make_umb_request(op: str,
                     _type: str= "na",
                     tag=None,
                     ack: bool = False,
                     data: Mapping[str, str] = None):
    """
    Creates a python dict representing the JSON object to be sent over the websocket

    :param op:
    :param _type:
    :param tag:
    :param ack:
    :param data:
    :return:
    """
    if data is None:
        data = {}
    if tag is None:
        tag = uuid4()

    return {
        "op": op,
        "type": _type,
        "tag": tag,
        "ack": ack,
        "data": data
    }


async def serve(req: Dict,
                host: str = "rhsm-cimetrics.usersys.redhat.com",
                url: str = "/ws/xunit/import",
                port: int = 9000):
    wsurl = "ws://{}:{}{}".format(host, port, url)

    print("Sending request to {}".format(wsurl))

    async with websockets.connect(wsurl) as websocket:
        body = json.dumps(req)
        await websocket.send(body)

        count = 0
        while count < 30:
            if count % 5 == 0:
                print("Waited {} seconds".format(count * 2))
            try:
                # Have to use wait_for() here, otherwise websocket.recv will yield, effectively stopping the while loop
                # Yup, asyncio is tricky :)  Also, in python 3.5 can't use yield from in an async function
                response = await asyncio.wait_for(websocket.recv(), 2)
                print("<", end='')
                info = json.loads(response)
                pprint(info, indent=2, width=120)
                if 'info' in info and 'import-results' in info['info']:
                    break
            except asyncio.TimeoutError:
                count += 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="")
    parser.add_argument("-p", "--xml-path", help="Path to xml file which will be imported")
    parser.add_argument("-a", "--json-args", help="Path to the polarizer-xunit.json or polarizer-testcase.json")
    parser.add_argument("-m", "--mapping", help="Path to the mapping.json file (only required for testcase type")
    parser.add_argument("-t", "--type", choices=["xunit", "testcase", "test"], help="type of import to make [xunit|testcase]")
    parser.add_argument("-s", "--server", help="Hostname of polarizer", default="rhsm-cimetrics.usersys.redhat.com")
    parser.add_argument("--port", help="Port for the websocket server", default=9000, type=int)
    opts = parser.parse_args()

    try:
        print("xml_path is {}".format(opts.xml_path))
        print("{} exists is {}".format(opts.xml_path, os.path.exists(opts.xml_path)))
    except TypeError:
        pass

    xml = opts.xml_path
    args_path = opts.json_args
    choice = opts.type
    if not opts.xml_path and opts.type != 'test':
        raise Exception("Must provide path to xml file")
    if opts.type != 'test' and opts.xml_path and not os.path.exists(opts.xml_path):
        raise Exception("{} does not exist for --xml-path".format(opts.xml_path))
    if opts.type != 'test' and not opts.json_args:
        raise Exception("Must provide --type of xunit or testcase")
    if not choice:
        raise Exception("Must provide a choice of xunit or testcase for --type")

    req = None
    url_endpoint = None
    if choice == "xunit":
        req = make_xunit_import_request(xml, xargs=args_path)
        url_endpoint = "/ws/xunit/import"
    elif choice == "testcase":
        mapping = opts.mapping
        if not mapping:
            raise Exception("Must provide file to --mapping for testcase type")
        if mapping and not os.path.exists(mapping):
            raise Exception("{} not exist for --mapping")
        req = make_testcase_import_request(xml, mapping, tcargs=args_path)
        url_endpoint = "/ws/testcase/import"
    elif choice == "test":
        url_endpoint = "/ws"
        req = ws_test()
        opts.port = 4001
    else:
        raise Exception("Unknown choice for --type selected")

    loop = asyncio.get_event_loop()
    if req is not None and url_endpoint is not None:
        loop.run_until_complete(serve(req, host=opts.server, url=url_endpoint, port=opts.port))
