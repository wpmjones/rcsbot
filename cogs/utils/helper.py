import re


def correct_tag(tag, prefix='#'):
    """Attempts to correct malformed Clash of Clans tags
    to match how they are formatted in game

    Example
    ---------
        ' 123aBc O' -> '#123ABC0'
    """
    return prefix + re.sub(r'[^A-Z0-9]+', '', tag.upper()).replace('O', '0')