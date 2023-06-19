from dataclasses import dataclass
import jsonargparse

jsonargparse.set_docstring_parse_options(attribute_docstrings=True)


@dataclass
class TerraformingMarsDiscordBotConfig:
    """Discord bot for Terraforming Mars Open-Source."""

    webhook_url: str
    """Discord webhook url."""
