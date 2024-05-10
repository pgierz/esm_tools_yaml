class EsmToolsError(Exception):
    """Base class for EsmTools exceptions"""


class EsmToolsParserError(EsmToolsError):
    """Base class for EsmToolsParser exceptions"""


class EsmToolsConstructorError(EsmToolsParserError):
    """Base class for EsmToolsConstructor exceptions"""


class EsmToolsConstructorFencePlaceholderError(EsmToolsConstructorError):
    """Raise this when a fence placeholder is already defined"""


class EsmToolsConstructorFenceTypeError(EsmToolsConstructorError):
    """Raise this when a fence type is not recognized"""


class EsmToolsConstructorEnvironmentVariableError(EsmToolsConstructorError):
    """Raise this when an environment variable is not set"""
