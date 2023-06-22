from tmdiscord import bot
from tmdiscord import config as bot_config
import tmdiscord.logging
from tmdiscord.logging import logger

import jsonargparse
from rich_argparse import RichHelpFormatter

import dataclasses
import json

UsageError = jsonargparse.ArgumentError


def parse_args() -> bot_config.TerraformingMarsDiscordBotConfig:
    return jsonargparse.CLI(
        bot_config.TerraformingMarsDiscordBotConfig,
        as_positional=False,
        exit_on_error=False,
        prog="tmdiscord",
        formatter_class=RichHelpFormatter,
    )


def run() -> None:
    parser = jsonargparse.capture_parser(parse_args)
    try:
        config = parse_args()
        logger.info(f"Configuration dump:\n{json.dumps(dataclasses.asdict(config), indent=4)}")
        tmdiscord.logging.configure_logger(config.logging_env, config.level, config.logging_file)
        bot.TerraformingMarsDiscordBot(config).run()
    except jsonargparse.ArgumentError as e:
        logger.error(e)
        print(parser.format_help())
        raise
