from loguru import logger
from ruamel.yaml.comments import CommentedMap


class EsmToolsSimulationConfig(CommentedMap):
    pass


class EsmToolsSimulationConfigMap(CommentedMap):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        logger.debug("You are using a custom EsmToolsSimulationConfigMap class")
        logger.debug("args:", args)
        logger.debug("kwargs:", kwargs)
