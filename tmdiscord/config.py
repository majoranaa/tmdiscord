import tmdiscord.logging

from dataclasses import dataclass
import jsonargparse
from typing import List

jsonargparse.set_docstring_parse_options(attribute_docstrings=True)


@dataclass
class TerraformingMarsDiscordBotConfig:
    """Discord bot for Terraforming Mars Open-Source."""

    logging_env: tmdiscord.logging.LoggingEnvironment
    """Configure logging behavior."""

    webhook_url: str
    """Discord webhook url."""

    game_ids: List[str]
    """Terraforming Mars game ids."""

    poll_interval: int = 30
    """How many seconds in between Terraforming Mars polls."""

    dry_run: bool = True
    """Whether to fake sending messages to Discord."""

    level: tmdiscord.logging.LoggingLevel = tmdiscord.logging.LoggingLevel.INFO
    """Configure log level."""

    logging_file: str = "tmdiscord.log"
    """Only relevant for CLOUD logging_env. Specify the file that JSON logs are saved to."""
