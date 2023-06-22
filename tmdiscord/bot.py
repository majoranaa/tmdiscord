from tmdiscord import config as bot_config
from tmdiscord.logging import logger

import requests

import time
from typing import List


MESSAGE_TEMPLATE = "<@{user_id}> It's yo turn now, {name}. [{url}]"
REMINDER_TEMPLATE = "<@{user_id}> It's yo turn now, {name}! It's been {elapsed} hours. [{url}]"
PLAYER_URL_TEMPLATE = "https://terraforming-mars.herokuapp.com/player?id={player_id}"

DISCORD_MAPPING = {
    "david": 448538894695268352,
    "alex": 527350406238568478,
    "kai": 735572794871513088,
    "charles": 1115485549541732363,
    "jessica": 735554088866939091,
}


class Game:
    def __init__(self, game_url: str):
        self.game_url = game_url
        self.current_player_name: str | None = None
        # Epoch time when last message was sent
        self.time_last_sent: float | None = None
        # Total elapsed time in minutes when player's turn started
        self.elapsed_time: int | None = None


class TerraformingMarsDiscordBot:
    def __init__(self, config: bot_config.TerraformingMarsDiscordBotConfig):
        self.config = config

    def run(self) -> None:
        if self.config.dry_run:
            logger.info("Conducting dry run (Not actually sending to Discord).")

        while True:
            time.sleep(self.config.poll_interval)

            logger.info("Setting up games.")
            games: List[Game] = []
            for game_url in self.config.game_urls:
                games.append(Game(game_url))
            games = [Game(game_url) for game_url in self.config.game_urls]

            logger.debug("Passing through games.")
            for game in games:
                logger.bind(game=game.game_url).info("Processing game.")

                # Make HTTP request
                r = requests.get(game.game_url)
                r.raise_for_status()
                tm_res = r.json()

                # Determine current player
                current_color: str = tm_res["activePlayer"]
                players = tm_res["players"]
                current_player = next(
                    player for player in players if player["color"] == current_color
                )
                current_player_name: str = current_player["name"]

                if current_player_name == game.current_player_name:
                    # The current player hasn't changed. Determine if reminder needs to be sent.
                    logger.debug("Current player is still {}.", current_player_name)
                    continue

                # Current player is different. Send a message.
                game.current_player_name = current_player_name
                current_player_id = DISCORD_MAPPING[current_player_name.lower()]
                current_player_url = PLAYER_URL_TEMPLATE.format(player_id=current_player["id"])
                message = MESSAGE_TEMPLATE.format(
                    user_id=current_player_id, name=current_player_name, url=current_player_url
                )
                if self.config.dry_run:
                    logger.info("(Dry run) Would send: {}", message)
                else:
                    logger.info("Sending: {}", message)
                    r = requests.post(
                        self.config.webhook_url,
                        json={"content": message},
                    )
                    r.raise_for_status()
                game.time_last_sent = time.time()
