import os
from typing import List, Optional, Tuple

from loguru import logger
from omegaconf import DictConfig
from transformers.integrations import NeptuneCallback


def get_neptune_token_and_project_set() -> Tuple[Optional[str], Optional[str]]:
    """
    Loads neptune token and project from environment variables.

    Returns:
        Neptune token and project values.
    """

    neptune_token = os.getenv("NEPTUNE_API_TOKEN")
    neptune_project_name = os.getenv("NEPTUNE_PROJECT")

    if neptune_token is None:
        logger.info("neptune token not found")

    if neptune_project_name is None:
        logger.info("neptune project name not found")

    return neptune_token, neptune_project_name


def create_neptune_callback(config: DictConfig, tags: Optional[List[str]] = None) -> Optional[NeptuneCallback]:
    """
    Args:
        config: DictConfig with experiment configuration.
        tags: Optional tags to be stored in experiments metadata.

    Returns:
        Neptune Callback.
    """

    neptune_token, neptune_project_name = get_neptune_token_and_project_set()

    if neptune_token is not None and neptune_project_name is not None:
        neptune_callback = NeptuneCallback(project=neptune_project_name, api_token=neptune_token, tags=tags)
        neptune_callback.config = config
        return neptune_callback
    logger.warning("Neptune environment variables not set properly. Neptune won't be used for this experiment.")
    return None
