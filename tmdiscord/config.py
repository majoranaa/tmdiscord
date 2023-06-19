from dataclasses import dataclass
import jsonargparse

jsonargparse.set_docstring_parse_options(attribute_docstrings=True)


@dataclass
class TerraformingMarsDiscordBotConfig:
    """Discord bot for Terraforming Mars Open-Source."""

    webhook_url: str
    """Discord webhook url."""

    game_url: str
    """Terraforming Mars game url."""

    debug: bool = False
    """Only print messages to stdout. Don't send to Discord API."""

    poll_interval: int = 5
    """How many seconds in between Terraforming Mars polls."""

    verbose: bool = False
    """More debug output."""
