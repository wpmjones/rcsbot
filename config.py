import yaml

with open("config.yaml", "r") as f:
    settings = yaml.load(f, Loader=yaml.CLoader)

with open("emoji.yaml", "r") as f:
    emojis = yaml.load(f, Loader=yaml.CLoader)


def color_pick(r, g, b):
    return int.from_bytes([r, g, b], byteorder='big')
