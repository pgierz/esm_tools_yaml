import os
from functools import wraps

from loguru import logger
from ruamel.yaml.constructor import RoundTripConstructor


def tag_debugger(method):
    @wraps(method)
    def wrapper(self, loader, node):
        logger.debug(f"Using customized tag loader {method.__name__} for {node.tag}")
        return method(self, loader, node)

    return wrapper


def tag_replacer(start_str, end_str):
    def _tag_replacer(method):
        @wraps(method)
        def wrapper(self, loader, node):
            if node.value.startswith(start_str):
                node.value = node.value[len(start_str) :]
            if node.value.endswith(end_str):
                node.value = node.value[: -len(end_str)]
            return method(self, loader, node)

        return wrapper

    return _tag_replacer


class EsmToolsConstructor(RoundTripConstructor):
    """
    Turns a dictionary into a EsmToolsSimulationConfig object
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_constructor("!ENV", self.env_var_constructor)
        self.add_constructor("!SHELL", self.shell_expression_constructor)

    def construct_mapping(self, *args, **kwargs):
        value = super().construct_mapping(*args, **kwargs)
        # breakpoint()
        # value = EsmToolsSimulationConfigMap(value)
        return value

    # NOTE(PG): I would rather have these outside of the class definition
    @tag_debugger
    @tag_replacer("${", "}")
    def env_var_constructor(self, loader, node):
        env_var_to_return = loader.construct_scalar(node)
        logger.debug(f"{env_var_to_return=}")
        value = os.environ.get(env_var_to_return)
        if value is None:
            for key, value in os.environ.items():
                logger.debug(f"{key}={value}")
            raise ValueError(f"Environment variable {env_var_to_return} is not set.")
        return value

    @tag_debugger
    @tag_replacer("$(", ")")
    def shell_expression_constructor(self, loader, node):
        value = loader.construct_scalar(node)
        expression_to_run = node.value
        logger.debug(f"{expression_to_run=}")
        value = os.popen(expression_to_run).read().strip()
        return value
