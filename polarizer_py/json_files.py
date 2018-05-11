tcargs = {
  "project": "${PROJECT_ID}",
  "author": "stoner",
  "packages": [
    "rhsm.cli.tests",
    "rhsm.gui.tests"
  ],
  "servers": {
    "polarion": {
      "url": "https://polarion.engineering.redhat.com/polarion",
      "user": "platformqe_machine",
      "domain": ".engineering.redhat.com",
      "password": "polarion"
    }
  },
  "testcase": {
    "endpoint": "/import/testcase",
    "timeout": 300000,
    "enabled": "${IMPORTER_ENABLED}",
    "selector": {
      "name": "rhsm_qe",
      "value": "testcase_importer"
    },
    "title": {
      "prefix": "",
      "suffix": ""
    }
  }
}
