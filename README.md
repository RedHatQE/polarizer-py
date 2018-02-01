# What is polarizer-py?

polarizer-py is a python library to collect metadata about your tests via decorators which wrap your test 
functions.  The decorators essentially do two things:

- Create or update a mapping.json file (which maps tests to a unique TestCase ID)
- Generates an XML testcase definition file useable by the Polarion TestCase importer

By generating the mapping.json file, as well as the XML test definition file, this allows a team to use the 
polarizer-vertx webservice to create or update TestCase definitions in Polarion


## The mapping.json file 

A simple mapping.json file looks like this:

```json
{
  "metatest.testmeta.test2": {
    "RHEL6": {
      "id": "RHEL6-12345",
      "params": [
        "name"
      ]
    }
  }
}
```

## The configuration file

polarizer-py uses a configuration that will be read in from ~/.polarizer/polarizer-testcase.yml|json.  It looks like this:

```yaml
---
project: RedHatEnterpriseLinux7
author: stoner
mapping: /home/stoner/dummy-map.json
new-testcase-xml: /home/stoner/testdefinitions.xml
servers:
  polarion:
    url: https://path.to.polarion.com
    user: myteam
    password: mypassword
testcase:
  endpoint: /import/testcases
  timeout: 300000
  enabled: false
  selector:
    name: rhsm_qe
    value: testcase_importer
  title:
    prefix: "RHSM-TC: "
    suffix: ""
```


## The metadata decorator 

Here's a simple example:

```python
from polarizer_py.metadata import metadata

@metadata(project="RedHatEnterpriseLinux7", 
          testcase_id="",
          importance="HIGH")
def test_some_feature(x):
    assert(x > 0)
```

This decorator will look up where the mapping.json file is from a json or yaml configuration file.  The decorator
will determine if the qualified name of the function (eg the package.module.function_name) is in the mapping.json file 
and then check what the "id" is for that project.

If mapping.json file is empty for the id (and the decorator testcase_id is an empty string also), then the decorator
knows it will need to make an import request to Polarion to create a new TestCase.  To do so, it will create an XML 
test definition file in the path indicated from the configuration's new-testcse-xml value.

## What polarizer-vertx does

A separate web service will take the XML testcase definition file and the mapping.json file, and return a new mapping.json
file with the new TestCase ID

```
curl -F tcargs=@/home/stoner/polarizer-testcase.json -F mapping=@/home/stoner/Projects/myproject/mapping.json -F tcxml=@/home/stoner/testdefinitions.xml http://localhost:9000/testcase/import

```
