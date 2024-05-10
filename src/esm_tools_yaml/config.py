from loguru import logger
from ruamel.yaml.comments import CommentedMap


class EsmToolsSingletonError(Exception):
    """Exception raised for errors in the esm_tools_singleton module."""


class EsmToolsConfigSingleton:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(EsmToolsConfigSingleton, cls).__new__(cls)
            cls._instance.config = CommentedMap()
            cls._instance.config["simulation"] = EsmToolsSimulationConfig()
            cls._instance.config["simulation"]["name"] = "default"
            cls._instance.config["simulation"]["description"] = "Default simulation"
            cls._instance.config["simulation"]["version"] = "0.1"
            cls._instance.config["simulation"]["author"] = "John Doe"
            cls._instance.config["simulation"]["email"] = "john.doe@awi.de"
            cls._instance.config["postprocess_tasks"] = CommentedMap()
            cls._instance.config["postprocess_tasks"]["fences"] = CommentedMap()
            return cls._instance
        else:
            logger.critical(
                "EsmToolsConfigSingleton is a singleton class. Use EsmToolsConfigSingleton.get_instance() to get the instance."
            )
            raise EsmToolsSingletonError(
                "EsmToolsConfigSingleton is a singleton class."
            )

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            return cls()
        return cls._instance


class EsmToolsSimulationConfig(CommentedMap):
    pass


class EsmToolsSimulationConfigMap(CommentedMap):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        logger.debug("You are using a custom EsmToolsSimulationConfigMap class")
        logger.debug("args:", args)
        logger.debug("kwargs:", kwargs)
