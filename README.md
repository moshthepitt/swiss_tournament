# swiss_tournament
PostgreSQL Swiss Style Tournament match pairings - essentially a Python module that uses the PostgreSQL database to keep track of players and matches in a game tournament.

The game tournament uses the Swiss system for pairing up players in each round: players are not eliminated, and each player should be paired with another player with the same number of wins, or as close as possible.

# Features

* Create and manage as many tournaments as you want
* Add new players to the database
* Register players for any tournament in the database
* Count total players, or just players registered to a certain tournament
* Delete all players, or just players from a certain tournament
* Generate swiis-style pairings for the next round of matches
* Tournaments with an odd number of players means one player will get a BYE in each round.  No one player can get a BYE more than once in the same tournament
* Report matches. Supports matches that result in a draw
* Delete matches
* View player standings, showing all the players, matches played and matches won

# Requirements

* Ubuntu operating system
* PostgreSQL
* Python 2.7

# How to run

This assumes the above "Requirements" are installed

1. Navigate to the project folder
2. Use psql to create a database table called "tournament"
3. Use the command \i tournament.sql to import tournament.sql into psql.  This should create all the tables needed
4. In your command line, run python tournament_test.py to ascertain that everything works as it should
5. ???
6. Profit


