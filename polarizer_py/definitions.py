from typing import Sequence, Mapping

##############################################################################################
# Type definitions
# These are all read-only classes
##############################################################################################


class TypeDef:
    def set(self, value: str) -> str:
        if hasattr(self, value):
            return getattr(self, value)
        else:
            raise AttributeError("{} is not a valid value for {}".format(value, self.__class__))

    @staticmethod
    def getter(attr):
        def inner(self):
            return attr
        return inner

    @staticmethod
    def setter(attr):
        def inner(self, val):
            print("In TypeDef.setter. Trying to change to {}".format(val))
            raise AttributeError("{} is read only".format(self.__class__))
        return inner


class Roles(TypeDef):
    def __init__(self):
        pass

    @property
    def RELATES_TO(self):
        return "RELATES_TO"

    @RELATES_TO.setter
    def RELATES_TO(self, _):
        raise AttributeError("Can not change value of RELATES_TO")

    @property
    def HAS_PARENT(self):
        return "HAS_PARENT"

    @HAS_PARENT.setter
    def HAS_PARENT(self, _):
        raise AttributeError("Can not change value of HAS_PARENT")

    @property
    def DUPLICATES(self):
        return "DUPLICATES"

    @DUPLICATES.setter
    def DUPLICATES(self, _):
        raise AttributeError("Can not change value of DUPLICATES")

    @property
    def VERIFIES(self):
        return "VERIFIES"

    @VERIFIES.setter
    def VERIFIES(self, _):
        raise AttributeError("Can not change value of VERIFIES")

    @property
    def IS_RELEATED_TO(self):
        return "IS_RELATED_TO"

    @IS_RELEATED_TO.setter
    def IS_RELATED_TO(self, _):
        raise AttributeError("Can not change value of IS_RELATED_TO")

    @property
    def IS_PARENT_OF(self):
        return "IS_PARENT_OF"

    @IS_PARENT_OF.setter
    def IS_PARENT_OF(self, _):
        raise AttributeError("Can not change value of IS_PARENT_OF")

    @property
    def IS_DUPLICATED_BY(self):
        return "DUPLICATED_BY"

    @IS_DUPLICATED_BY.setter
    def IS_DUPLICATED_BY(self, _):
        raise AttributeError("Can not change value of DUPLICATED_BY")

    @property
    def TRIGGERS(self):
        return "TRIGGERS"

    @TRIGGERS.setter
    def TRIGGERS(self, _):
        raise AttributeError("Can not change value of TRIGGERS")


Role = Roles()


class TestType(TypeDef):
    err = "TestType is a read only value"

    @property
    def FUNCTIONAL(self):
        return "FUNCTIONAL"

    @FUNCTIONAL.setter
    def FUNCTIONAL(self, val):
        raise AttributeError(TestType.err)

    @property
    def NONFUNCTIONAL(self):
        return "FUNCTIONAL"

    @NONFUNCTIONAL.setter
    def NONFUNCTIONAL(self, val):
        raise AttributeError(TestType.err)

    @property
    def STRUCTURAL(self):
        return "FUNCTIONAL"

    @STRUCTURAL.setter
    def STRUCTURAL(self, val):
        raise AttributeError(TestType.err)


class Level(TypeDef):
    err = "Level is a read only data type"

    @property
    def COMPONENT(self):
        return "COMPONENT"

    @COMPONENT.setter
    def COMPONENT(self, val):
        raise AttributeError(Level.err)

    @property
    def INTEGRATION(self):
        return "INTEGRATION"

    @INTEGRATION.setter
    def INTEGRATION(self, val):
        raise AttributeError(Level.err)

    @property
    def SYSTEM(self):
        return "SYSTEM"

    @SYSTEM.setter
    def SYSTEM(self, val):
        raise AttributeError(Level.err)

    @property
    def ACCEPTANCE(self):
        return "ACCEPTANCE"

    @ACCEPTANCE.setter
    def ACCEPTANCE(self, val):
        raise AttributeError(Level.err)


class PosNegs(TypeDef):
    err = "PosNegs is read-only"

    @property
    def NEGATIVE(self):
        return "NEGATIVE"

    @NEGATIVE.setter
    def NEGATIVE(self, _):
        raise AttributeError(PosNegs.err)

    @property
    def POSITIVE(self):
        return "POSITIVE"

    @POSITIVE.setter
    def POSITIVE(self, _):
        raise AttributeError(PosNegs.err)


PosNeg = PosNegs()


class Importances(TypeDef):
    err = "Importances is read only"

    @property
    def CRITICAL(self):
        return "CRITICAL"

    @CRITICAL.setter
    def CRITICAL(self, _):
        raise AttributeError(Importances.err)

    @property
    def HIGH(self):
        return "HIGH"

    @HIGH.setter
    def HIGH(self, _):
        raise AttributeError(Importances.err)

    @property
    def MEDIUM(self):
        return "MEDIUM"

    @MEDIUM.setter
    def MEDIUM(self, _):
        raise AttributeError(Importances.err)

    @property
    def LOW(self):
        return "LOW"

    @LOW.setter
    def LOW(self, _):
        raise AttributeError(Importances.err)


Importance = Importances()


class AutoTypes(TypeDef):
    err = "AutoTypes is read-only"

    @property
    def AUTOMATED(self):
        return "AUTOMATED"

    @AUTOMATED.setter
    def AUTOMATED(self, _):
        raise AttributeError(AutoTypes.err)

    @property
    def NOTAUTOMATED(self):
        return "NOTAUTOMATED"

    @NOTAUTOMATED.setter
    def NOTAUTOMATED(self, _):
        raise AttributeError(AutoTypes.err)

    @property
    def MANUALONLY(self):
        return "MANUALONLY"

    @MANUALONLY.setter
    def MANUALONLY(self, _):
        raise AttributeError(AutoTypes.err)


Automation = AutoTypes()


class SubTypes(TypeDef):
    err = "SubTypes is read-only"

    @property
    def EMPTY(self):
        return "EMPTY"

    @EMPTY.setter
    def EMPTY(self, _):
        raise AttributeError(SubTypes.err)

    @property
    def COMPLIANCE(self):
        return "COMPLIANCE"

    @COMPLIANCE.setter
    def COMPLIANCE(self, _):
        raise AttributeError(SubTypes.err)

    @property
    def DOCUMENTATION(self):
        return "DOCUMENTATION"

    @DOCUMENTATION.setter
    def DOCUMENTATION(self, _):
        raise AttributeError(SubTypes.err)

    @property
    def I18NL10N(self):
        return "I18NL10N"

    @I18NL10N.setter
    def I18NL10N(self, _):
        raise AttributeError(SubTypes.err)

    @property
    def INSTALLABILITY(self):
        return

    @INSTALLABILITY.setter
    def INSTALLABILITY(self, _):
        raise AttributeError(SubTypes.err)

    @property
    def INTEROPERABILITY(self):
        return "INTEROPERABILITY"

    @INTEROPERABILITY.setter
    def INTEROPERABILITY(self, _):
        raise AttributeError(SubTypes.err)

    @property
    def PERFORMANCE(self):
        return "PERFORMANCE"

    @PERFORMANCE.setter
    def PERFORMANCE(self, _):
        raise AttributeError(SubTypes.err)

    @property
    def RELIABILITY(self):
        return "RELIABILITY"

    @RELIABILITY.setter
    def RELIABILITY(self, _):
        raise AttributeError(SubTypes.err)

    @property
    def SCALABILITY(self):
        return "SCALABILITY"

    @SCALABILITY.setter
    def SCALABILITY(self, _):
        raise AttributeError(SubTypes.err)

    @property
    def SECURITY(self):
        return "SECURITY"

    @SECURITY.setter
    def SECURITY(self, _):
        raise AttributeError(SubTypes.err)

    @property
    def USABILITY(self):
        return "USASBILITY"

    @USABILITY.setter
    def USABILITY(self, _):
        raise AttributeError(SubTypes.err)

    @property
    def RECOVERYFAILOVER(self):
        return "RECOVERYFAILOVER"

    @RECOVERYFAILOVER.setter
    def RECOVERYFAILOVER(self, _):
        raise AttributeError(SubTypes.err)

##############################################################################################
# Classes to (de)serialize from a json.load/dump
##############################################################################################


class LinkedWorkItem:
    def __init__(self, wid, role, project, revision, suspect=False):
        self.workitemId = wid
        self.suspect = suspect
        self.role = role
        self.project = project
        self.revision = revision


class Parameter:
    def __init__(self, name: str, scope: str = "local"):
        self.name = name
        self.scope = scope


class TestStepColumn:
    def __init__(self, params: Sequence[Parameter] = None):
        if params is None:
            self.parameters = []
        else:
            self.parameters = params


class TestStep:
    def __init__(self, id: str = "step", cols: Sequence[TestStepColumn] = None):
        if cols is None:
            self.columns = []
        else:
            self.columns = cols
        self.id = id


class Custom:
    def __init__(self, fields: Sequence[Mapping[str, str]] = None):
        if fields is None:
            self.fields = []
        else:
            self.fields = fields

    @staticmethod
    def default_custom():
        ids = ""


class TestCase:
    def __init__(self, title="", description="", steps=None, custom=None):
        self.title = title
        self.description = description
        if steps is None:
            self.test_steps = [TestStep()]
        else:
            self.test_steps = steps
        if custom is None:
            self.custom = []


example_meta = {
    "project": "RedHatEnterpriseLinux7",
    "description": "Just a test",
    # Normally, this is not necessary, since we can determine this via introspection
    "test-steps": [
        {"test-step": [  # test_step has an array of columns, however, usually only one
            {"test-step-column": [  # columns have an array of parameter
                {"parameter": {
                    "name": "bugzilla", "scope": "local"
                }},
                {"parameter": {
                    "name": "bashCommand", "scope": "local",
                }},
                {"parameter": {
                    "name": "", "scope": "local"
                }}
            ]}
        ]}
    ],
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
}