import discord

color = discord.Color.dark_orange()


def challenge_1():
    challenge = ("Clash of clans offered a one time limited edition Halloween trap that was added to the game "
                 "the same Day the Reddit Clan System was born! (October 27, 2012 was the day Flammy posted "
                 "the original post that later became our wiki and announced we were open for business).\n\n"
                 "The limited edition trap is shown in this picture.  What was it called?\n\n"
                 "`NOTE: Unless the bot specifically tells you to do so, don't use ++ when providing answers.`")
    title = "Reddit Electrum Challenge #1:"
    image_url = "http://www.mayodev.com/images/1.jpg"
    return challenge, title, image_url


def challenge_2a():
    challenge = ("You are given the choice of walking through three doors. One is filled with deadly assassins "
                 "who are instructed to kill you, one is filled with fire, one is full of lions who haven’t "
                 "eaten in years, and one is filled with poisonous gas.  You have no protective equipment and "
                 "must survive for one hour.  Which door do you choose?")
    title = "Reddit Eclipse Challenge #2a:"
    embed = discord.Embed(title=title, description=challenge, color=color)
    return embed


def challenge_2b():
    challenge = ("In Boston, a man is found dead on a Sunday morning in his study. His wife calls the police "
                 "immediately. The police question the wife and staff about what they were doing at 7am when "
                 "they believe the man was murdered. The wife (W) said she thinks she was asleep but can’t "
                 "recall when the dog woke her up.  The cook (C) said he was making breakfast for everyone. "
                 "The butler (B) said that he was cleaning the upstairs closet. The maid (M) said that she "
                 "was getting the mail just like she had the day before.  The gardener (G) said he was "
                 "picking vegetables for lunch. Who do the police arrest?")
    title = "Reddit Elclipse Challenge #2b:"
    embed = discord.Embed(title=title, description=challenge, color=color)
    return embed


def challenge_2c():
    challenge = ("A man shoots his wife three times in the park but she is still alive. Then he asks her if "
                 "she’s ready to go to dinner and she agrees as if nothing has happened.  What explains this?")
    title = "Reddit Eclipse Challenge #2c:"
    embed = discord.Embed(title=title, description=challenge, color=color)
    return embed


def challenge_3():
    challenge = ("Share a pic of your favorite (or favourite) Halloween treat or candy in the "
                 "#trick-or-treat channel.")
    title = "Reddit Zero Challenge #3:"
    image_url = False
    return challenge, title, image_url


def challenge_4():
    challenge = ("Members of Reddit Pis leadership each like a different clash candy.\n\n"
                 "Using the following clues, Which Candy does Roville like?\n\n"
                 "(It helps if you use a drawing app or a piece of paper to make the grid above.  If you see "
                 "someone cannot like a particular candy, put an X in the square for that candy in that person's "
                 "row.  When you know what candy they do like, put an O.  Every person likes one of the 5 candies "
                 "best, no two people have the same favorite. So you can use process of elimination "
                 "to find out who has which as their favorite!)\n\n"
                 "```1. cary'd and Maren don't like candies named after troops who are blue\n"
                 "2. Roville and Dan don't care for candies that have names that are more than one word\n" 
                 "3. Maren's favorite is named after a female troop\n"
                 "4. Dan has sworn off all things goblin after having his DE stolen one too many times!```")
    title = "Reddit Pi Challenge #4:"
    image_url = "http://www.mayodev.com/images/4.png"
    return challenge, title, image_url


def challenge_5():
    challenge = ("**10% Beaver Challenge:**\n"
                 "No one really knows for sure how much wood would a woodchuck chuck if a woodchuck could chuck "
                 "wood.  But you can answer this one.  How many beavers in the clan are currently "
                 "chewing on 5000 or more trophies?")
    title = "10% Beaver Challenge #5:"
    image_url = False
    return challenge, title, image_url


def challenge_6():
    challenge = ("Check out the Tau co-leaders! Which co-leader has TWO of the very first Halloween "
                 "obstacle offered in the game?\n\n"
                 "Options: Evil-Panda, Caped Crusader, [--rough--], Jason, drewski1019, RM3")
    title = "Reddit Tau Challenge #6:"
    image_url = False
    return challenge, title, image_url


def challenge_7():
    challenge = ("Find the spooky pic of a severely malnourished (you could say...skeletal) man playing clash "
                 "in the #trick-or-treat channel.  What's the brand name on the bottle he keeps close at hand?")
    title = "Reddit Argon Challenge #7:"
    image_url = False
    return challenge, title, image_url


def challenge_8():
    challenge = ("Change your pfp/avatar to something including a pumpkin! Once you have, ask someone else "
                 "in the Dartaholics to enter the command `++pumpkin @your_name`")
    title = "Dartaholics Challenge #8:"
    image_url = False
    return challenge, title, image_url


def challenge_9():
    challenge = ("The following passwords have all been used in the RCS in the past:\n\n"
                 "(A) ramen\n"
                 "(B) popcorn\n"
                 "(C) pretzels\n"
                 "(D) bacon\n"
                 "(E) galaxy\n"
                 "(F) shadow\n"
                 "(G) kittens\n"
                 "(H) adventure\n\n"
                 "Can you put them in the correct chronological order?  (Using the letter names `ABCDEFGH`)")
    title = "Reddit Hunters Challenge #9:"
    image_url = False
    return challenge, title, image_url


def challenge_10():
    challenge = ("Find your favorite spooky picture and @ the leader (SAQ) with that image.  Who knows?  "
                 "Maybe it will end up as his profile picture!")
    title = "Reddit Ace Challenge #10:"
    image_url = False
    return challenge, title, image_url


def challenge_11():
    challenge = "How many circles are in this picture?"
    title = "Extremeillusion Challenge #11:"
    image_url = "http://www.mayodev.com/images/11.jpg"
    return challenge, title, image_url


def challenge_12():
    challenge = "Edit your nickname here to include one or more 🦇 emoji!"
    title = "Reddit Night Challenge #12:"
    image_url = False
    return challenge, title, image_url


def challenge_13():
    challenge = ("Time to play hide and seek!  A player in DIZZYS PLAYGRND is using this base!  Please view the "
                 "clan in game and respond with the player tag as soon as you find it!")
    title = "DIZZYS PLAYGRND Challenge #13:"
    image_url = "http://www.mayodev.com/images/13.jpg"
    return challenge, title, image_url


def challenge_14():
    challenge = ("Those sneaky Pirates have hidden their bounty where they think you'll never find it. "
                 "But we have faith!\n\n"
                 "Look at the picture below?  How many 'R's and 'P's are hidden in the Deep B Sea?\n\n"
                 "Enter yout answer in the format of `##` where the first digit is the number of 'R's "
                 "and the second digit is the number of 'P's.")
    title = "Reddit Pirates Challenge #14:"
    image_url = "http://www.mayodev.com/images/14.jpg"
    return challenge, title, image_url


def challenge_15():
    challenge = ("Today, there are MANY more and many with diverse clan names that don't include the word 'Reddit', "
                 "but initially, our founder Flammy wanted to name the 26 original Reddit clans that followed "
                 "Reddit after the  NATO alphabet. There were a few exceptions as they didn't want place names, "
                 "some were legitimate mistakes, and some of the original crew liked another name better.\n\n"
                 "These are the original 26 clans that followed Reddit:\n"
                 "Alpha\n"
                 "Beta\n"
                 "Charlie\n"
                 "Delta\n"
                 "Echo\n"
                 "Foxtrot\n"
                 "Gold\n"
                 "Hotel\n"
                 "Indy\n"
                 "Juliet\n"
                 "Kilo\n"
                 "Light\n"
                 "Mike\n"
                 "November\n"
                 "Oak\n"
                 "Papa\n"
                 "Quandary\n"
                 "Romeo\n"
                 "Sierra\n"
                 "Tango\n"
                 "United\n"
                 "Veteran\n"
                 "Whiskey\n"
                 "X-Ray\n"
                 "Yankee\n"
                 "Zulu\n\n"
                 "Of these, which did not follow the official NATO alphabet?  (Use the first letter like `ABCD`)")
    title = "Reddit Zulu Challenge #15:"
    image_url = False
    return challenge, title, image_url
