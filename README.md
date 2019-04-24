# rcs-bot

rcs-bot is a Discord bot designed for the Reddit Clan System (RCS).  Data from the Clash of Clans API is stored in a SQL database and information is pulled based on commands provided by the user on Discord.

# Basic commands

## ++attacks
**++attacks <clan name or tag>**

Lists the number of attack wins per player for the current season
  
## ++defenses
**++defenses <clan name or tag>**

Lists the number of defense wins per player for the current season
  
## ++donations
**++donations <clan name or tag>**

Lists the number of donations per player
Note: Due to how Supercell tracks this information, the donation count will reset if you leave and rejoin your clan
  
## ++trophies
**++trophies <clan name or tag>**

Lists the number of trophies per player
  
## ++besttrophies
**++besttrophies <clan name or tag>**

Lists the highest trophy count per player (all time)
  
## ++townhalls
**++townhalls <clan name or tag>**

Lists the town hall level of each player in the clan
  
## ++builderhalls
**++builderhalls <clan name or tag>**

Lists the builder hall level of each player in the clan
  
## ++warstars
**++warstars <clan name or tag>**

Lists the number of war stars accumulated by each player in the clan
  
## ++top
**++top <category>**

Lists the top ten players across the RCS for the category specified
  
## ++games
Because the API does not expose Clan Games scores, this category is calculated mathematically using the Games Champion achievement (cumulative Clan Games scores).  The achievement score is stored in the database before the games start and this is subtracted from the current achievement score from the API to determine current points.

**++games all**

Lists all RCS clans ranked by Clan Games total

**++games average**

Lists the average score for each clan in the RCS

**++games <clan name or tag>**

Lists the player scores for all players in the specified clan

## ++push
Only active if a trophy push is occurring (twice a year)

**++push all**

Lists all RCS clans ranked by their current Trophy Push score (scoring system [found here](https://www.reddit.com/r/RedditClanSystem/comments/8fj1zx/the_super_spring_showdown_trophy_push_2018_may/))

**++push TH#**

Lists all players of the specified town hall level and their scores

**++push top**

Lists the top ten players and scores for each town hall level

**++push <clan name or tag>**

Lists all players and scores for the specified clan
  
## ++reddit
**++reddit <clan name or tag>**

Responds with the subreddit link for the specified clan (if it exists)
  
# Hidden/Reserved Commands
There are other commands that are restricted to leadership or are Easter eggs.  I'll try and document these soon.

# Contact me
Obviously, you can submit issues here. I am active in the [Real Python](https://realpython.com/) Slack community.  You can also find me on Discord @TubaKid (Reddit Oak)#8822.