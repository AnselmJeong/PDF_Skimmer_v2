import tomli

with open("config.toml", "rb") as f:
    CONFIG = tomli.load(f)
