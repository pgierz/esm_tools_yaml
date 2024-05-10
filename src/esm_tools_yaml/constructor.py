"""
This provides implementation for the ``Constructor`` of the ``esm-tools`` YAML parser. Several
rules are handled directly by the constructor. See the documentation of ``EsmToolsConstructor``
for more specific information.

In general, the Constructor is the part of the parser that is responsible for turning the text
represented in the YAML into corresponding Python objects. It is important to note that this does
**not** handle variable expansion, choose blocks, and the like. This only takes care of special
tags which might be defined in the configuration file, such as getting variables from the environment,
shell expressions, and marking particular blocks for post-processing, such as fence expansions.
"""

# NOTE(PG): This module might also cover parsing and transforming dates, I am not sure about that yet.

import os
from functools import wraps

from loguru import logger
from ruamel.yaml.constructor import RoundTripConstructor

from .config import EsmToolsConfigSingleton
from .exceptions import (EsmToolsConstructorEnvironmentVariableError,
                         EsmToolsConstructorFenceTypeError)

LIST_FENCE_START = "[["
"""str : start of a list fence"""
LIST_FENCE_END = "]]"
"""str : end of a list fence"""

DICT_FENCE_START = "{{"
"""str : start of a dict fence"""
DICT_FENCE_END = "}}"
"""str : end of a dict fence"""


class FencedValue:
    # FIXME(PG): I don't really like the names here. Could be more elegant...
    """
    This class defines a fenced value, either as a list or as a dictionary
    to be expanded during post-processing of the config

    Properties
    ----------
    value : Any
        The actual value (un-expanded)
    fence_type : type
        Either dict or list
    fence_placeholder : str
    fence_values_to_expand : list
    """

    def __init__(
        self,
        value,
        fence_type=None,
        fence_placeholder=None,
        fence_values_to_expand=None,
    ):
        self.value = value
        self.fence_type = fence_type
        self.fence_placeholder = fence_placeholder
        self.fence_values_to_expand = fence_values_to_expand

    def __str__(self):
        return self.value

    def __repr__(self):
        return self.value


def tag_debugger(method):
    """
    You can use this decorator to enable a debug statement when loading specific nodes
    that have been tagged.
    """

    @wraps(method)
    def wrapper(loader, node):
        logger.debug(f"Using customized tag loader {method.__name__} for {node.tag}")
        return method(loader, node)

    return wrapper


def tag_replacer(start_str, end_str):
    """
    This decorator will remove ``start_str`` and ``end_str`` from a specific node **before**
    it is parsed by whatever method is decorated

    Parameters
    ----------
    start_str : str
        The beginning string to purge
    end_str : str
        The ending string to purge
    """

    def _tag_replacer(method):
        @wraps(method)
        def wrapper(loader, node):
            if node.value.startswith(start_str):
                node.value = node.value[len(start_str) :]
            if node.value.endswith(end_str):
                node.value = node.value[: -len(end_str)]
            return method(loader, node)

        return wrapper

    return _tag_replacer


@tag_debugger
@tag_replacer("${", "}")
def env_var_constructor(loader, node):
    """
    If a particular node has been tagged with ``!ENV``, the value of that
    shell environment variable is returned.

    Parameters
    ----------
    loader : ~FIXME_LOADER
        The instantiated ``Constructor`` object used to load
        this node

    node : Any
        The actual value that is being loaded. Normally something like
        ``list``, ``bool``, ``dict``, ``str`` or similar. Custom objects
        can also be loaded, but this is rarely (if ever) the case.

    Returns
    -------
    str :
        The string of the value that has been tagged as it is found in the
        current shell environment.

    Raises
    ------
    EsmToolsConstructorEnvironmentVariableError :
        Raised when the requested variable is not found in the shell.

    Example
    -------
    Given the following shell environment:
    ..code ::

        $ export MY_VARIABLE="hello"
        $ cat config.yaml
            foo: !ENV ${MY_VARIABLE}

    After parsing in Python, you would get the following when enabling the
    ``!ENV`` tag with this rule::

        >>> config["MY_VARIABLE"]
        'hello'
    """
    env_var_to_return = loader.construct_scalar(node)
    logger.debug(f"{env_var_to_return=}")
    value = os.environ.get(env_var_to_return)
    if value is None:
        for key, value in os.environ.items():
            logger.debug(f"{key}={value}")
        raise EsmToolsConstructorEnvironmentVariableError(
            f"Environment variable {env_var_to_return} is not set."
        )
    return value


@tag_debugger
@tag_replacer("$(", ")")
def shell_expression_constructor(loader, node):
    """
    If a node has been tagged with ``!SHELL``, the value of the shell
    expression is returned.

    Parameters
    ----------
    loader : ~FIXME_LOADER
        The instantiated ``Constructor`` object used to load
        this node

    node : Any
        The actual value that is being loaded. Normally something like
        ``list``, ``bool``, ``dict``, ``str`` or similar. Custom objects
        can also be loaded, but this is rarely (if ever) the case.

    Returns
    -------
    str :
        The result of the shell expression that has been run.
    """
    value = loader.construct_scalar(node)
    expression_to_run = node.value
    logger.debug(f"{expression_to_run=}")
    try:
        value = os.popen(expression_to_run).read().strip()
        return value
    except Exception as e:
        logger.error(f"Error running shell expression {expression_to_run}: {e}")
        raise e


@tag_debugger
def fence_expand_constructor(loader, node):
    value = loader.construct_scalar(node)
    logger.debug(f"{value=}")
    if LIST_FENCE_START in value and LIST_FENCE_END in value:
        fence_type = list
        fence_value = (
            value.partition(LIST_FENCE_START)[2].rpartition(LIST_FENCE_END)[0].strip()
        )
    elif DICT_FENCE_START in value and DICT_FENCE_END in value:
        fence_type = dict
        fence_value = (
            value.partition(DICT_FENCE_START)[2].rpartition(DICT_FENCE_END)[0].strip()
        )
    else:
        raise EsmToolsConstructorFenceTypeError(f"Unknown fence type for {value=}")
    logger.debug(f"{fence_type=}")
    fence_placeholder = fence_value.split("-->")[0].strip()
    fence_values_to_expand = fence_value.split("-->")[1].strip()
    logger.debug(f"{fence_placeholder=}")
    logger.debug(f"{fence_values_to_expand=}")
    global_config = EsmToolsConfigSingleton.get_instance().config
    fences = global_config["postprocess_tasks"]["fences"]
    rvalue = FencedValue(
        value,
        fence_type=fence_type,
        fence_placeholder=fence_placeholder,
        fence_values_to_expand=fence_values_to_expand,
    )
    breakpoint()
    fences[id(rvalue)] = rvalue
    return rvalue


class EsmToolsConstructor(RoundTripConstructor):
    """
    A ``ruamel.yaml`` constructor that is aware of ``esm-tools`` rules.

    You can use this constructor with a ``YAML`` object as documented in
    the ``ruamel.yaml`` handbook (URL). It is aware of the following
    special rules:

        * ``!ENV``    : This tag can be used to get an environment variable.
        * ``!SHELL``  : This tag can be used to run a shell expression.
        * ``!EXPAND`` : This contains the previous "fence" logic to
                        expand lists and dictionaries based upon other
                        values in the configuration.

    Note that ``choose`` blocks and variable interpolation is **not**
    done here, rather, that is the job of the postprocessor. Here we
    only define rules that are of relevance for dealing with special
    ``yaml`` tags which need to be dealt with when loading the raw
    configuration file. This will also keep a list of post-processing
    tasks to be completed later on, which is stored in the config
    ``EsmToolsConfigSingleton``, and later accessed by the ``PostProcessor``
    object.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fences_to_expand = {}
        self.add_constructor("!ENV", env_var_constructor)
        self.add_constructor("!SHELL", shell_expression_constructor)
        self.add_constructor("!EXPAND", fence_expand_constructor)

    # NOTE(PG): The next few methods are placeholders in case we
    #           need to override the basic constructors.
    def construct_mapping(self, *args, **kwargs):
        return super().construct_mapping(*args, **kwargs)

    def construct_list(self, *args, **kwargs):
        return super().construct_list(*args, **kwargs)

    def construct_scalar(self, node):
        return super().construct_scalar(node)
