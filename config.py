import yaml
import typing
from datetime import datetime, timedelta

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


def logger(ctx,
           log_type: str = "INFO",
           cog: str = "main",
           args_dict: typing.Dict[str, str] = {},
           message: str = ""):
    """Custom logging for bot"""
    log_level = 10
    log_types = {"CRITICAL": 50,
                 "ERROR": 40,
                 "WARNING": 30,
                 "INFO": 20,
                 "DEBUG": 10,
                 "NOTSET": 0}
    if log_type in log_types:
        log_type_num = log_types[log_type]
    else:
        log_type_num = 20
    if log_type_num >= log_level:
        date_fmt = "%Y-%m-%d %H:%M:%S"
        msg = f"\n{(datetime.now() - timedelta(hours=6)).strftime(date_fmt)} | {log_type} | "
        msg += f"{ctx.command} invoked by {ctx.author}"
        msg += f"\n- Channel: {ctx.channel}"
        if len(args_dict) != 0:
            args = "\n- Arguments:"
            for key, value in args_dict.items():
                args += f"\n  - {key}: {value}"
            msg += args
        if message != "":
            msg += f"\nMessage: {message}"
        with open(f"{cog}.log", "a") as f:
            f.write(msg)