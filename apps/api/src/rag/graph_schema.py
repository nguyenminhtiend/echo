from enum import Enum


class EntityType(Enum):
    MODULE = "Module"
    CLASS = "Class"
    FUNCTION = "Function"
    FILE = "File"
    CONFIG = "Config"
    TEST = "Test"
    CONCEPT = "Concept"


class RelationType(Enum):
    IMPORTS = "IMPORTS"
    CALLS = "CALLS"
    INHERITS = "INHERITS"
    DEFINES = "DEFINES"
    TESTS = "TESTS"
    DEPENDS_ON = "DEPENDS_ON"
    DOCUMENTS = "DOCUMENTS"
