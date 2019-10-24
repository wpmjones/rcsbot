import discord
import asyncio
import random

from cogs.utils.constants import responses
from cogs.utils.db import Sql


def challenge_1():
    challenge = ("Clash of clans offered a one time limited edition Halloween trap that was added to the game "
                 "the same Day the Reddit Clan System was born! (October 27, 2012 was the day Flammy posted "
                 "the original post that later became our wiki and announced we were open for business).\n\n"
                 "The limited edition trap is shown in this picture.  What was it called?")
    image = discord.File("images/1.jpg")
    return challenge, image


def challenge_2a():
    challenge = ("You are given the choice of walking through three doors. One is filled with deadly assassins "
                 "who are instructed to kill you, one is filled with fire, one is full of lions who haven’t "
                 "eaten in years, and one is filled with poisonous gas.  You have no protective equipment and "
                 "must survive for one hour.  Which door do you choose?")
    return challenge


def challenge_2b():
    challenge = ("In Boston, a man is found dead on a Sunday morning in his study. His wife calls the police "
                 "immediately. The police question the wife and staff about what they were doing at 7am when "
                 "they believe the man was murdered. The wife (W) said she thinks she was asleep but can’t "
                 "recall when the dog woke her up.  The cook (C) said he was making breakfast for everyone. "
                 "The butler (B) said that he was cleaning the upstairs closet. The maid (M) said that she "
                 "was getting the mail just like she had the day before.  The gardener (G) said he was "
                 "picking vegetables for lunch. Who do the police arrest?")
    return challenge


def challenge_2c():
    challenge = ("A man shoots his wife three times in the park but she is still alive. Then he asks her if "
                 "she’s ready to go to dinner and she agrees as if nothing has happened.  What explains this?")
    return challenge


def challenge_3():
    challenge = ("Share a pic of your favorite (or favourite) Halloween treat or candy in the "
                 "#trick-or-treat channel.")
    return challenge


def challenge_4():
    challenge = ("Members of Reddit Pis leadership each like a different clash candy.\n\n"
                 "Using the following clues, Which Candy does Roville like?\n\n"
                 "(It helps if you use a drawing app or a piece of paper to make the grid above.  If you see "
                 "someone cannot like a particular candy, put an X in the square for that candy in that person's "
                 "row.  When you know what candy they do like, put an O.  Every person likes one of the 5 candies "
                 "best, no two people have the same favorite. So you can use process of elimination "
                 "to find out who has which as their favorite!)")
    image = discord.File("images/4.png")
    return challenge, image


def challenge_5():
    challenge = ("No one really knows for sure how much wood would a woodchuck chuck if a woodchuck could chuck "
                 "wood.  But you can answer this one.  How many beavers in the clan are currently "
                 "chewing on over 5000 trophies?")
    return challenge


def challenge_6():
    challenge = ("Check out the Tau co-leaders! Which co-leader has TWO of the very first Halloween "
                 "obstacle offered in the game?\n\n"
                 "Options: Evil-Panda, Caped Crusader, [--rough--], Jason, drewski1019, RM3")
    return challenge


def challenge_7():
    challenge = ("Find the spooky pic of a severely malnourished (you could say...skeletal) man playing clash "
                 "in the #trick-or-treat channel.  What's the brand name on the bottle he keeps close at hand?")
    return challenge


def challenge_8():
    challenge = ("Change your pfp/avatar to something including a pumpkin! Once you have, ask someone else "
                 "in the Dartaholics to enter the command `++pumpkin @your_name`")
    return challenge


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
    return challenge


def challenge_10():
    challenge = ("Find your favorite spooky picture and @ the leader (SAQ) with that image.  Who knows?  "
                 "Maybe it will end up as his profile picture!")
    return challenge


def challenge_11():
    challenge = "How many circles are in this picture?"
    image = discord.File("images/11.jpg")
    return challenge, image


def challenge_12():
    challenge = "Edit your nickname here to include one or more of this emoji: :bat: !"
    return challenge


def challenge_13():
    challenge = ("Time to play hide and seek!  A player in DIZZYS PLAYGRND is using this base!  Please view the "
                 "clan in game and respond with the player tag as soon as you find it!")
    image = discord.File("images/13.jpg")
    return challenge, image


def challenge_14():
    challenge = ("Those sneaky Pirates have hidden their bounty where they think you'll never find it. "
                 "But we have faith!\n\n"
                 "Look at the picture below?  How many 'R's and 'P's are hidden in the Deep B Sea?\n\n"
                 "Enter yout answer in the format of `##` where the first digit is the number of 'R's "
                 "and the second digit is the number of 'P's.")
    image = discord.File("images/14.jpg")
    return challenge, image


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
    return challenge


async def send_challenge(ctx, cur_challenge, challenge, image):
    if cur_challenge in (1, 3, 5, 6, 7, 8, 9, 10, 12, 15):
        await ctx.author.send(challenge)
    if cur_challenge in (4, 11, 13, 14):
        await ctx.author.send(challenge)
        await ctx.author.send(file=image)
    if cur_challenge == 2:
        reactions_1 = ("🔥", "🕵", "🦁")
        reactions_2 = ("🇼", "🇨", "🇧", "🇲", "🇬")
        reactions_3 = ("🐾", "💤", "👯", "💼", "🐦", "📞", "🗑", "🌡", "🐍", "🌳", "🗞", "📸", "💳", "🗡", "🔋", "🖊",
                       "🔫", "📎", "⏱", "🏀")

        def check_1(reaction, user):
            return user == ctx.message.author and str(reaction.emoji) in reactions_1

        def check_2(reaction, user):
            return user == ctx.message.author and str(reaction.emoji) in reactions_2

        def check_3(reaction, user):
            return user == ctx.message.author and str(reaction.emoji) in reactions_3

        msg = await ctx.author.send(challenge_2a())
        for r in reactions_1:
            await msg.add_reaction(r)

        for i in range(4):
            try:
                reaction, user = await ctx.bot.wait_for("reaction_add", timeout=60, check=check_1)
            except asyncio.TimeoutError:
                await msg.clear_reactions()
                await msg.edit("You have run out of time. When you're ready, just type `++challenge`.")
                return

            if str(reaction.emoji) != reactions_1[2]:
                await ctx.author.send(random.choice[
                                          "I'm afraid that was the wrong door.  You're dead.  But a magical "
                                          "fairy has come and brought you back to life.  Try again!",
                                          "Do you have a death wish?! You're lucky that you have 9 lives! Try again.",
                                          "Are you nuts? There was practically a sign on that door that said 'Die "
                                          "here' and you went and opened it!  Fortunately, the Healer was nearby "
                                          "and you live to try another door.  One more time..."
                                      ])
            else:
                break
        else:
            await msg.clear_reactions()
            await msg.edit("You have run out of time. When you're ready, just type `++challenge`.")
            return

        await ctx.author.send("That's right!  Wise choice.  Those lions all died of starvation and you are safe!")

        # 2a complete, start 2b
        msg = await ctx.author.send(challenge_2b())
        for r in reactions_2:
            await msg.add_reaction(r)

        for i in range(5):
            try:
                reaction, user = await ctx.bot.wait_for("reaction_add", timeout=60, check=check_2)
            except asyncio.TimeoutError:
                await msg.clear_reactions()
                await msg.edit("You have run out of time. When you're ready, just type `++challenge`.")
                return

            if str(reaction.emoji) != reactions_2[3]:
                await ctx.author.send(random.choice[
                                          "False arrest. They did nothing wrong! Try again!",
                                          "Innocent, I say! Innocent! Try again!",
                                          "There is no way you can prove that! Pick someone else!",
                                          "And you would be wrong. Check the clues and guess again!",
                                          "They didn't do it. Try one more time!"
                                      ])
            else:
                break
        else:
            await msg.clear_reactions()
            await msg.edit("You have run out of time. When you're ready, just type `++challenge`.")
            return

        await ctx.author.send("The maid lied about getting the mail. There is no mail delivery on Sunday!")

        # 2b complete, start 2c
        msg = await ctx.author.send(challenge_2c())
        for r in reactions_3:
            await msg.add_reaction(r)

        for i in range(12):
            try:
                reaction, user = await ctx.bot.wait_for("reaction_add", timeout=90, check=check_3)
            except asyncio.TimeoutError:
                await msg.clear_reactions()
                await msg.edit("You have run out of time. When you're ready, just type `++challenge`.")
                return

            if str(reaction.emoji) != reactions_2[11]:
                await ctx.author.send("That's an interesting choice.  Also wrong.  Please try again.")
            else:
                break
        else:
            await msg.clear_reactions()
            await msg.edit("You have run out of time. When you're ready, just type `++challenge`.")
            return

        await ctx.author.send("He's a photographer of course!  Well done!")
        await ctx.author.send(responses[2])
        with Sql() as cursor:
            sql = "UPDATE rcs_halloween_players SET last_completed = %d WHERE discord_id = %d"
            cursor.execute(sql, (cur_challenge, ctx.author.id))