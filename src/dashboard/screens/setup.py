from textual import work
from textual.app import ComposeResult
from textual.containers import Horizontal, VerticalScroll
from textual.markup import escape
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Input, Label, Select, Static

from dashboard.calendar.client import test_source
from dashboard.config import AppConfig, ConfigError, WeatherConfig, parse_config


class SetupScreen(Screen[AppConfig]):          # [AppConfig] = the type dismiss() returns
    CSS = """
    #setup { width: 70; max-width: 100%; height: auto; margin: 1 2; padding: 1 2;
             border: round $primary; }
    #setup Label { margin-top: 1; color: $text-muted; }
    #setup .row { height: auto; }
    #setup .row Input { width: 1fr; }
    #title { text-style: bold; color: $accent; }
    #buttons { margin-top: 1; height: auto; }
    """
    BINDINGS = [("escape", "app.quit", "Quit")]

    def __init__(self, themes: list[str]) -> None:
        super().__init__()
        self.themes = themes

    # ---- layout ----------------------------------------------------------
    def compose(self) -> ComposeResult:
        defaults = WeatherConfig()
        yield Header()
        with VerticalScroll(id="setup"):       # `with` = children go inside this container
            yield Static("Welcome! Let's set up your dashboard.", id="title")

            yield Label("Your name")
            yield Input(placeholder="Name", id="name")

            yield Label("Theme")
            yield Select([(t, t) for t in self.themes], value=self.themes[0],
                         allow_blank=False, id="theme")

            yield Label("Location (latitude, longitude)")
            with Horizontal(classes="row"):
                yield Input(str(defaults.lat), type="number", id="lat")
                yield Input(str(defaults.lon), type="number", id="lon")

            yield Label("Calendar ICS link (optional)")
            with Horizontal(classes="row"):
                yield Input(placeholder="https://…/calendar.ics", id="cal-url")
                yield Button("Test", id="test")
            yield Static("", id="test-result")

            yield Static("", id="error")
            with Horizontal(id="buttons"):
                yield Button("Save", variant="primary", id="save")
                yield Button("Quit", id="quit")
        yield Footer()

    # ---- events: Textual calls on_<widget>_<event> automatically -----------
    def on_select_changed(self, event: Select.Changed) -> None:
        if event.select.id == "theme":
            self.app.theme = event.value       # live preview

    def on_button_pressed(self, event: Button.Pressed) -> None:
        match event.button.id:
            case "save": self.save()
            case "test": self.test_calendar()
            case "quit": self.app.exit()

    # ---- form -> dict -> AppConfig (reusing config.py validation) ---------
    def _value(self, widget_id: str) -> str:
        return self.query_one(f"#{widget_id}", Input).value.strip()

    def _number(self, widget_id: str) -> float | str:
        try:
            return float(self._value(widget_id))
        except ValueError:
            return self._value(widget_id)      # let parse_config report it

    def _form_to_dict(self) -> dict:
        raw = {
            "theme": self.query_one("#theme", Select).value,
            "weather": {"lat": self._number("lat"), "lon": self._number("lon")},
        }
        if name := self._value("name"):
            raw["name"] = name
        if url := self._value("cal-url"):
            raw["calendar"] = {"sources": [{"name": "Calendar", "url": url}]}
        return raw

    def save(self) -> None:
        try:
            config = parse_config(self._form_to_dict())
        except ConfigError as e:
            self.query_one("#error", Static).update(f"[$error]{escape(str(e))}[/]")
            return
        self.dismiss(config)                   # closes the screen, hands config to the callback

    # ---- runs in the background so the UI doesn't freeze -------------------
    @work(exclusive=True)
    async def test_calendar(self) -> None:
        result = self.query_one("#test-result", Static)
        try:
            source = parse_config(self._form_to_dict()).calendar.sources[0]
        except ConfigError as e:
            result.update(f"[$error]✗ {escape(str(e))}[/]")
            return
        except IndexError:
            result.update("[$error]✗ Enter a link first[/]")
            return

        result.update("Testing…")
        try:
            count = await test_source(source)
        except Exception as e:
            result.update(f"[$error]✗ {escape(f'{type(e).__name__}: {e}')}[/]")
        else:
            result.update(f"[$success]✓ {count} events in the next 7 days[/]")
