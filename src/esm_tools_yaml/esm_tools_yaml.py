# from .config import EsmToolsSimulationConfig
from constructor import EsmToolsConstructor
from loguru import logger
from ruamel.yaml import YAML

# from .constructor import EsmToolsConstructor


class EsmToolsYaml(YAML):
    """
    A custom YAML subclass to contain the special logic for the ESM Tools YAML files.

    Parameters
    ----------
    add_provenance : bool
        Whether or not to add provenance comments to the YAML file when using this
        object to dump the finished config back to disk. Default is ``False``.
    *args
        Any other arguments typically passed to the YAML class.
        See https://tinyurl.com/mu98x55s
    **kwargs
        Any other keyword arguments typically passed to the YAML class.
        See https://tinyurl.com/mu98x55s
    """

    def __init__(self, *args, **kwargs):
        logger.debug(f"You are using a custom YAML class {self.__class__.__name__}")
        logger.debug("This class was created with the following arguments:")
        for arg in args:
            logger.debug(f"{arg=}")
        logger.debug("This class was created with the following keyword arguments:")
        for kwarg_key, kwarg_value in kwargs.items():
            logger.debug(f"{kwarg_key=}, {kwarg_value=}")
        self.add_provenance = kwargs.pop("add_provenance", False)
        super().__init__(*args, **kwargs)
        self.Constructor = EsmToolsConstructor
        # self.Resolver = ...
        # self.Representer: ...
        # self.Scanner: ...
        # self.Serializer: ...
        # self.Emitter: ...
        # self.Representer: ...
        # self.Parser: ...
        # self.Composer: ...
        # self.Constructor: ...


# NOTE(PG): This could be folded into the EsmToolsYaml class, but I'm keeping it
# separate for now to make it easier to understand the different parts of the code.
#
# Also be aware, this **cannot** be part of the Constructor class, because the
# inheritant logic requires all of the data to be already available. I don't like
# it either, I know....
class EsmToolsYamlPostprocessor:
    """
    Runs various postprocessing steps on the YAML file to fix lists, add provenance,
    etc.
    """

    def __call__(self, data):
        logger.debug(f"Running postprocessor on {data=}")
        data = self.recursive_run_method(data, self.substitute_variables)
        data = self.recursive_run_metho(data, self.do_math)
        data = self.recursive_run_method(data, self.run_chooses)
        return data

    def recursive_run_method(self, data, method):
        """
        Recursively run a method on the YAML data.

        Parameters
        ----------
        data : dict
            The YAML data to process.
        method : method
            The method to run on the YAML data.

        Returns
        -------
        dict
            The processed YAML data.
        """
        if isinstance(data, dict):
            for key, value in data.items():
                data[key] = self.recursive_run_method(value, method)
        elif isinstance(data, list):
            for index, item in enumerate(data):
                data[index] = self.recursive_run_method(item, method)
        else:
            data = method(data)
        return data

    def substitute_variables(self, data):
        """
        Substitute variables in the YAML file.

        Parameters
        ----------
        data : dict
            The YAML data to process.

        Returns
        -------
        dict
            The processed YAML data.
        """
        return data

    def do_math(self, data):
        """
        Perform math operations on the YAML file.

        Parameters
        ----------
        data : dict
            The YAML data to process.

        Returns
        -------
        dict
            The processed YAML data.
        """
        return data

    def run_chooses(self, data):
        """
        Run the "choose" logic in the YAML file.

        Parameters
        ----------
        data : dict
            The YAML data to process.

        Returns
        -------
        dict
            The processed YAML data.
        """
        return data


def main():
    config_file_handler = EsmToolsYaml(add_provenance=True)
    postprocessor = EsmToolsYamlPostprocessor()
    with open("test.yaml", "r") as user_config:
        loaded_config = config_file_handler.load(user_config)
    logger.debug(loaded_config)
    logger.debug(f"{type(loaded_config)=}")
    logger.debug(f"{config_file_handler.add_provenance=}")
    finalized_config = postprocessor(loaded_config)
    logger.debug(finalized_config)


if __name__ == "__main__":
    main()
