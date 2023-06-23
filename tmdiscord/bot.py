from __future__ import annotations
from tmdiscord import config as bot_config
from tmdiscord.logging import logger

import requests

import time
from types import TracebackType
from typing import Type


GAME_URL_TEMPLATE = "https://terraforming-mars.herokuapp.com/api/game?id={game_id}"
PLAYER_URL_TEMPLATE = "https://terraforming-mars.herokuapp.com/api/player?id={player_id}"

DISCORD_MAPPING = {
    "david": 448538894695268352,
    "alex": 527350406238568478,
    "kai": 735572794871513088,
    "charles": 1115485549541732363,
    "jessica": 735554088866939091,
}

ACTION_TEMPLATE = "<@{discord_id}> It's yo turn now, {name}. [{url}]"
RESEARCH_TEMPLATE = "<@{discord_id}> It's time to research, {name}. [{url}]"
ACTION_REMINDER_TEMPLATE = (
    "<@{discord_id}> It's yo turn now, {name}! It's been {elapsed} hours. [{url}]"
)
RESEARCH_REMINDER_TEMPLATE = (
    "<@{discord_id}> It's time to research, {name}! It's been {elapsed} hours. [{url}]"
)


class Game:
    def __init__(self, game_id: str, config: bot_config.TerraformingMarsDiscordBotConfig):
        self.game_id = game_id
        self.config = config
        self.logger = logger.bind(game=game_id)

        # Initialize state variables.
        self.current_phase: str | None = None
        self.active_player_colors: set[str] = set()
        # Epoch time when last message(s) was sent.
        self.time_last_sent: float | None = None
        # Total elapsed time in minutes when player's turn started.
        self.elapsed_time: int | None = None

        # Get arbitrary player url.
        game_url = GAME_URL_TEMPLATE.format(game_id=game_id)
        res = requests.get(game_url)
        res.raise_for_status()
        tm_res = res.json()
        players = tm_res["players"]
        arbitrary_player_id = players[0]["id"]
        self.arbitrary_player_url = PLAYER_URL_TEMPLATE.format(player_id=arbitrary_player_id)
        self.logger.debug("Arbitrary player url: {}", self.arbitrary_player_url)
        self.player_mapping = {
            player["color"]: {"name": player["name"], "id": player["id"]} for player in players
        }

    def process(self) -> None:
        self.logger.debug("Processing game.")
        res = requests.get(self.arbitrary_player_url)
        res.raise_for_status()
        tm_res = res.json()
        game = tm_res["game"]
        players = tm_res["players"]
        active_player_color: str
        if game["phase"] == "research":
            active_player_colors = [
                player["color"] for player in players if player["needsToResearch"]
            ]
            # TODO: should also check the generation
            if self.current_phase == "research":
                # Send reminders
                for active_player_color in active_player_colors:
                    self.logger.debug(
                        "{} is still researching.", self.get_player_name(active_player_color)
                    )
            else:
                # Send first messages
                self.current_phase = "research"
                self.active_player_colors = set(active_player_colors)
                for active_player_color in active_player_colors:
                    self.send_message(active_player_color, RESEARCH_TEMPLATE)

        elif game["phase"] == "action":
            # Determine current player
            active_player_color = next(player for player in players if player["isActive"])["color"]
            if self.current_phase == "action" and active_player_color in self.active_player_colors:
                self.logger.debug(
                    "Current player is still {}.", self.get_player_name(active_player_color)
                )
            else:
                # Send first message
                self.current_phase = "action"
                self.active_player_colors = {active_player_color}
                self.send_message(active_player_color, ACTION_TEMPLATE)

    def send_message(self, active_player_color: str, template: str) -> None:
        player = self.player_mapping[active_player_color]
        player_url = PLAYER_URL_TEMPLATE.format(player_id=player["id"])
        player_name = player["name"]
        discord_id = DISCORD_MAPPING[player_name.lower()]
        message = template.format(discord_id=discord_id, name=player_name, url=player_url)
        if self.config.dry_run:
            self.logger.info("(Dry run) Would send: {}", message)
        else:
            self.logger.info("Sending: {}", message)
            res = requests.post(self.config.webhook_url, json={"content": message})
            res.raise_for_status()

    def get_player_name(self, color: str) -> str:
        return self.player_mapping[color]["name"]


class TerraformingMarsDiscordBot:
    def __init__(self, config: bot_config.TerraformingMarsDiscordBotConfig):
        self.config = config

    def __enter__(self) -> TerraformingMarsDiscordBot:
        # TODO: load state from GCS
        return self

    def __exit__(
        self,
        exc_type: Type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        # TODO: save state to GCS
        pass

    def run(self) -> None:
        if self.config.dry_run:
            logger.info("Conducting dry run (Not actually sending to Discord).")

        logger.info("Setting up games.")
        games = [Game(game_id, self.config) for game_id in self.config.game_ids]

        while True:
            time.sleep(self.config.poll_interval)

            logger.debug("Passing through games.")
            for game in games:
                game.process()
