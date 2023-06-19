from dataclasses import dataclass
import jsonargparse

jsonargparse.set_docstring_parse_options(attribute_docstrings=True)


@dataclass
class TerraformingMarsDiscordBotConfig:
    """Discord bot for Terraforming Mars Open-Source."""

    delay_length: int = 60
    """Delay in minutes."""
