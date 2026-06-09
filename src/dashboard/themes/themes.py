from textual.theme import Theme

norwegian_forest = Theme(
    name="norwegian-forest",
    primary="#6B8E5A",
    secondary="#4A7C59",
    accent="#C9A961",
    foreground="#D7CFA8",
    background="#0F1611",
    success="#7FB069",
    warning="#D4A574",
    error="#B8634E",
    surface="#16201A",
    panel="#1B2620",
    dark=True,
    variables={
        "boost": "#243029",
        "foreground-muted": "#8B9080",
        "border": "#3A4A3F",
    },
)

graphite = Theme(
    name="graphite",
    primary="#79C0FF",
    secondary="#58A6FF",
    accent="#FFA657",
    foreground="#E6EDF3",
    background="#0D1117",
    success="#7EE787",
    warning="#F0883E",
    error="#FF7B72",
    surface="#161B22",
    panel="#1C2128",
    dark=True,
    variables={
        "boost": "#21262D",
        "foreground-muted": "#7D8590",
        "border": "#30363D",
    },
)

hearth = Theme(
    name="hearth",
    primary="#D4A574",
    secondary="#B08755",
    accent="#E8A87C",
    foreground="#E8D9B8",
    background="#1F1812",
    success="#A8B85E",
    warning="#E8B86E",
    error="#C97064",
    surface="#26201A",
    panel="#2D2620",
    dark=True,
    variables={
        "boost": "#332B23",
        "foreground-muted": "#9B8B6F",
        "border": "#4A3F33",
    },
)

ALL_THEMES = [norwegian_forest, graphite, hearth]