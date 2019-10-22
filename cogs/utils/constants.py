cwl_league_names = ["bronze iii",
                    "bronze ii",
                    "bronze i",
                    "silver iii",
                    "silver ii",
                    "silver i",
                    "gold iii",
                    "gold ii",
                    "gold i",
                    "crystal iii",
                    "crystal ii",
                    "crystal i",
                    "master iii", "masters iii",
                    "master ii", "masters ii",
                    "master i", "masters i",
                    "champion iii", "champions iii", "champs iii",
                    "champion ii", "champions ii", "champs ii",
                    "champion i", "champions i", "champs i",
                    ]

cwl_league_order = ["Bronze III",
                    "Bronze II",
                    "Bronze I",
                    "Silver III",
                    "Silver II",
                    "Silver I",
                    "Gold III",
                    "Gold II",
                    "Gold I",
                    "Crystal III",
                    "Crystal II",
                    "Crystal I",
                    "Master III",
                    "Master II",
                    "Master I",
                    "Champion III",
                    "Champion II",
                    "Champion I",
                    ]

trophy_leagues = ["Bronze III",
                  "Bronze II",
                  "Bronze I",
                  "Silver III",
                  "Silver II",
                  "Silver I",
                  "Gold III",
                  "Gold II",
                  "Gold I",
                  "Crystal III",
                  "Crystal II",
                  "Crystal I",
                  "Master III",
                  "Master II",
                  "Master I",
                  "Champion III",
                  "Champion II",
                  "Champion I",
                  ]

answers = {
    1: "pumpkin bomb",
    4: "goblinstoppers",
    6: "[--rough--]",
    7: "heinz",
    9: "gdfechba",
    11: "16",
    13: "qvpgqluq",
    14: "72",
    15: "bgiloquv",
}

responses = {
    1: ("Well done!  That’s one challenge down, 14 to go!  Next step: head to Reddit Eclipse "
        "(https://discord.gg/FzUNupJ) for a few mysterious riddles.  Remember to look for the #trick-or-treat "
        "channel and type `++challenge`."),
    "2a": "That's right. The lions would have died from starvation and you can hang out in there as long as you like!",
    "2b": "You must be smart! Mail isn't delivered on Sundays!'",
    "2c": ("You are one sharp cookie!  Nicely done.  Your new mission is to zoom over to Reddit Zero (invite), "
           "find the #trick-or-treat channel, and post an image of your favorite Halloween treat or candy. "),
    3: ("I love candy and I love treats!  I also like pie!  And Reddit Pi!  Head over to their server "
        "(invite) and find a new challenge.  Just type `++challenge` in the #trick-or-treat channel for next steps."),
    4: ("I don’t know that pie and goblinstoppers go together, but you’ve got the right answer!  Your logic is "
        "flawless.  I hope you’re getting to know a few new RCS members during your trick or treating.  Now it’s "
        "time to get in the game!  Jump to 10% Beaver’s Discord (invite) and issue `++challenge` "
        "in #trick-or-treat to get your first, in-game challenge."),
    5: ("That one’s always a moving target but you got it!  For some more in-game fun, toodle on over to "
        "Reddit Tau (invite) and throw down `++challenge` in the #trick-or-treat channel."),
    6: ("Hopefully, that wasn’t too rough on you. Are you having fun yet?  I found a guy over in "
        "Reddit Argon (invite) who is still having fun and he’s dead!  Head over to their server "
        "and see what I mean.  Find #trick-or-treat and type `++challenge` to find out what I need from you "
        "to keep this adventure going!"),
    7: ("I thought maybe it was blood but maybe it is just ketchup.  Good work there super sleuth!  You’re sharp as a "
        "tack.  Or a dart.  Check out the Dartaholics server (invite) for your next challenge! "),
    8: ("And such a cute pumpkin you are!  Well done!  While you are hunting for treats, hit up "
        "Reddit Hunters (invite).  They have some popcorn and other goodies in store for RCS members "
        "who know their history!  Just type `++challenge` and see what you find!"),
    9: ("Hmm you are a smart one.  Well done.  I’m sure you didn’t have to use the wiki at all!  :wink:  "
        "Well put on a happy face and head over to Reddit Ace (invite) and see what `++challenge` "
        "awaits you there."),
    10: ("I am both pleased and frightened at the same time.  Well done… I think.  So I think it’s "
         "time you get a*round* to the Extremeillusion server (invite).  They have some cool "
         "stuff going on over there and we need to check your eyesight while you’re there."),
    11: ("How long did that take you? Not too bad.  But you’re right and that’s all that matters.  "
         "Now let’s see about those critters that can see… at night.  Reddit Night to be precise.  "
         "Jump to their server (invite) and have a little fun."),
    12: ("Nicely done bat person!  Person bat?  Per-bat?  I give up.  I’m getting dizzy.  Fortunately, "
         "there’s a cure for that.  Visit DIZZYS PLAYGRND (invite) for some more Halloween fun."),
    13: ("Spooky, isn’t it.  Someone put some real time into that one!  Good job hunting that one down.  "
         "Up for some pilfering?  Pirates love to count their loot and they need some help minding their Ps and Qs. "
         "Or was it Rs and Ps.  I don't remember.  Join Reddit Pirates (invite) and find out what we have in store."),
    14: ("Good job Pirate Hunter!  You are almost there.  One more quiz for you over at Reddit Zulu "
         "and you’ll be done!  Sneak into their server (invite) and find the #trick-or-treat channel!"),
}

wrong_answers_resp = [
    "That is not the answer you are looking for. Keep trying!",
    "Was that supposed to be an answer? Cause... uh... well, try again, champ!",
    "You're usually so good at these things, but that is not correct.",
    "Nope.  Guess again amigo!",
    "I know this one is tough. You can always `++skip` it if you want.",
    "I knew I would stump you on that one. Think about it and try again.",
    ("Congratulations!  You're the first person to get this one wrong! Just kidding, you are the first and you "
     "won't be the last."),
    "You know which challenge you're on, right? If not, try `++remind`.",
]