import yaml
from datetime import datetime

with open("/home/tuba/config.yaml", "r") as f:
    settings = yaml.load(f, Loader=yaml.CLoader)

with open("/home/tuba/emoji.yaml", "r") as f:
    emojis = yaml.load(f, Loader=yaml.CLoader)


def color_pick(r, g, b):
    return int.from_bytes([r, g, b], byteorder='big')


def bot_log(command, request, author, guild, err_flag=0):
    msg = f"{str(datetime.now())[:16]} - "
    if err_flag == 0:
        msg += f"Printing {command} for {request}. Requested by {author} for {guild}."
    else:
        msg += (f"ERROR: User provided an incorrect argument for {command}. "
                f"Argument provided: {request}. Requested by {author} for {guild}.")
    print(msg)
