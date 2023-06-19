import time

import requests

from tmdiscord import config as bot_config


MESSAGE_TEMPLATE = "<@{user_id}> It's yo turn, {name} [{url}]"
PLAYER_URL_TEMPLATE = "https://terraforming-mars.herokuapp.com/player?id={player_id}"

DISCORD_MAPPING = {
    "david": 448538894695268352,
    "alex": 527350406238568478,
    "kai": 735572794871513088,
    "charles": 1115485549541732363,
    "jessica": 735554088866939091,
}


class TerraformingMarsDiscordBot:
    def __init__(self, config: bot_config.TerraformingMarsDiscordBotConfig):
        self.config = config
        print(f"webhook url: {self.config.webhook_url}")
        print(f"game url: {self.config.game_url}")

    def run(self):
        previous_current_player_name = None
        while True:
            time.sleep(self.config.poll_interval)
            r = requests.get(self.config.game_url)
            r.raise_for_status()
            tm_res = r.json()
            current_color = tm_res["activePlayer"]
            players = tm_res["players"]
            current_player = next(player for player in players if player["color"] == current_color)
            current_player_name = current_player["name"]
            if current_player_name == previous_current_player_name:
                if self.config.verbose:
                    print(f"Current player is still {current_player_name}.")
                continue
            previous_current_player_name = current_player_name
            current_player_id = DISCORD_MAPPING[current_player_name.lower()]
            current_player_url = PLAYER_URL_TEMPLATE.format(player_id=current_player["id"])
            message = MESSAGE_TEMPLATE.format(
                user_id=current_player_id, name=current_player_name, url=current_player_url
            )
            if self.config.debug:
                print(message)
            else:
                r = requests.post(
                    self.config.webhook_url,
                    json={"content": message},
                )
                r.raise_for_status()
