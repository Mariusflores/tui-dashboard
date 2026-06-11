from pathlib import Path
import tomllib

from textual.app import ComposeResult
from textual.containers import VerticalGroup
from textual.widgets import Static


from datetime import datetime


class Greeting(VerticalGroup):
    """ Greeting Widget """

    def compose(self) -> ComposeResult:
        yield Static("", id="greeting")

    def on_mount(self) -> None:
        self.update_greeting()
        self.set_interval(10000, self.update_greeting)


    def update_greeting(self):
        PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent

        CONFIG_PATH = PROJECT_ROOT / "config.toml"
        with CONFIG_PATH.open("rb") as f:
            config = tomllib.load(f)

        name = config["name"]
        greeting = ""

        hour = datetime.now().hour

        if 5 <= hour < 12:
            greeting = f"Good Morning, {name}!"

        elif 12 <= hour < 17:
            greeting = f"Good Afternoon, {name}!"
        
        elif 17 <= hour < 22:
            greeting = f"Good Evening, {name}!"

        else:
            greeting = f"Hi {name}, working late?"
    

    
        self.query_one(Static).update(greeting)