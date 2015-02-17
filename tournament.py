#!/usr/bin/env python
#
# tournament.py -- implementation of a Swiss-system tournament
#

import bleach
import datetime
import psycopg2

def connect():
    """Connect to the PostgreSQL database.  Returns a database connection."""
    return psycopg2.connect("dbname=tournament")

def createTournament(name="Tournament One",
                    start_date="2015-12-10",
                    end_date="2015-12-27",
                    details="A Swiss style tournament!!"
                    ):
    """
    This method creates one tournament; because you need to do so in order to register players, have matches, etc

    Args:
      name: the tournament name
      start_date: the date of the start of the tournament
      end_date: the date of the end of the tournament
      details: other information about the tournament
      ==> all these args have defaults that can be overriden
    """
    DB = connect()
    c = DB.cursor()
    c.execute("INSERT INTO tournaments (name, start_date, end_date, details) VALUES (%s,%s,%s,%s)",
              ( bleach.clean(name),
                bleach.clean(start_date),
                bleach.clean(end_date),
                bleach.clean(details)
            ))
    DB.commit()
    DB.close()

def deleteMatches(tournament_id=None):
    """
        Remove all the match records from the database.
        Args:
          tournament_id: the id of a particular tournament, if not defined then delete matches from all tournaments
    """
    DB = connect()
    c = DB.cursor()
    if tournament_id:
        c.execute("DELETE FROM tournament_matches WHERE tournament_id = %s", (tournament_id,))
    else:
        c.execute("DELETE FROM tournament_matches")
    DB.commit()
    DB.close()

def deletePlayers():
    """
        Remove all the player records from the database.
    """
    deleteTournamentPlayers(tournament_id=None)
    DB = connect()
    c = DB.cursor()
    c.execute("DELETE FROM players")
    DB.commit()
    DB.close()

def deleteTournamentPlayers(tournament_id=None):
    """
        Remove all the player records from the database.
        Args:
          tournament_id: the id of a particular tournament, if not defined then delete players from all tournaments
    """
    DB = connect()
    c = DB.cursor()
    if tournament_id:
        c.execute("DELETE FROM tournament_players WHERE tournament_id = %s", (tournament_id,))
    else:
        c.execute("DELETE FROM tournament_players")
    DB.commit()
    DB.close()

def countPlayers(tournament_id=1):
    """
        Returns the number of players currently registered.
        Args:
          tournament_id: the id of a particular tournament, if defined, just count players signed up tp a specific tournament
    """
    DB = connect()
    c = DB.cursor()
    if not tournament_id:
        #returns total number of players
        c.execute("SELECT COUNT(id) FROM players")
        result = c.fetchone()
    else:
        #returns total number of players in a particular tournament
        c.execute("SELECT COUNT(player_id) FROM tournament_players WHERE tournament_id = %s", (tournament_id,))
        result = c.fetchone()
    DB.close()
    return result[0]

def registerPlayer(name,tournament_id=1,registration_date=None):
    """Adds a player to the tournament database.

    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)

    Args:
      name: the player's full name (need not be unique).
      tournament_id: the id of the tournament in which to register the player
      registration_date: the date player was registered for tournament

    NOTE: This method creates a new player AND registers him from a tournament
          To register an existing player for a tournament, then use registerExistingPlayer() method
    """
    #if not registration_date then use today
    if not registration_date:
        registration_date = datetime.datetime.now().strftime("%Y-%m-%d")

    DB = connect()
    c = DB.cursor()
    #insert player into players Table and then get his ID to use to register for tournament
    c.execute("INSERT INTO players (name) VALUES (%s) RETURNING id",
              (bleach.clean(name),))
    id_of_new_player = c.fetchone()[0]
    #register player for tournament
    c.execute("INSERT INTO tournament_players(tournament_id, player_id, registration_date) VALUES (%s,%s,%s)",
              ( tournament_id,
                id_of_new_player,
                bleach.clean(registration_date)
            ))
    DB.commit()
    DB.close()

def registerExistingPlayer(player_id,tournament_id=1,registration_date=None):
    """Registers an exisiting player for a tournament

    Args:
      player_id: the player_id of the player in question
      tournament_id: the id of the tournament in which to register the player
      registration_date: the date player was registered for tournament

    NOTE: This method takes an existing player AND registers him from a tournament
          To create a new player and register for a tournament, then use registerPlayer() method
    """
    #if not registration_date then use today
    if not registration_date:
        registration_date = datetime.datetime.now().strftime("%Y-%m-%d")

    DB = connect()
    c = DB.cursor()
    c.execute("INSERT INTO tournament_players(tournament_id, player_id, registration_date) VALUES (%s,%s,%s)",
              ( tournament_id,
                player_id,
                bleach.clean(registration_date)
            ))
    DB.commit()
    DB.close()

def playerStandings(tournament_id=1):
    """Returns a list of the players and their win records, sorted by wins.

    The first entry in the list should be the player in first place, or a player
    tied for first place if there is currently a tie.

    Args:
      tournament_id: the tournament whose standings we want

    Returns:
      A list of tuples, each of which contains (id, name, wins, matches):
        id: the player's unique id (assigned by the database)
        name: the player's full name (as registered)
        wins: the number of matches the player has won
        matches: the number of matches the player has played
    """
    DB = connect()
    c = DB.cursor()
    #get players and no of wins
    c.execute("""SELECT players.id, players.name, COUNT(tournament_matches.id) AS wins FROM players LEFT JOIN tournament_matches
                ON players.id = tournament_matches.winning_player_id GROUP BY players.id ORDER BY wins DESC
            """)
    wins_record = c.fetchall()
    #get players and no of matches
    c.execute("""SELECT players.id, players.name, COUNT(tournament_matches.id) AS matches FROM players LEFT JOIN tournament_matches
                ON players.id = tournament_matches.player_1_id OR players.id = tournament_matches.player_2_id GROUP BY players.id
                ORDER BY players.id
            """)
    matches_records = c.fetchall()
    DB.close()
    #get a final list of tuples that merges players wins and matches played
    result = []
    for item in wins_record:
        for row in matches_records:
            if item[0] == row[0]:
                result.append((
                    item[0],
                    item[1],
                    item[2],
                    row[2]
                ))
    return result

def reportMatch(player_one, player_two=None, tournament_id=1, match_date=None, draw=False):
    """Records the outcome of a single match between two players.

    Args:
      player_one:  the id number of one the players. If match is not a draw this is the winning player
      player_two:  the id number of one the players. If not defined then player_one is given a BYE
      tournament_id: the tournament in questions
      match_date: the date on which the match took place
      draw: if True then the match was a draw
    """
    #return error if player_one = player_two
    if player_one == player_two:
        return "ERROR: A player cannot play against himself!"
    #if not registration_date then use today
    if not match_date:
        match_date = datetime.datetime.now().strftime("%Y-%m-%d")
    #set winner to NULL if match was drawn.  A draw can only happen if the match is not a BYE
    if draw and player_two:
        winner = None
    else:
        winner = player_one
    #insert into DB
    DB = connect()
    c = DB.cursor()
    #prevent one player from receiving more than one BYE
    if not player_two:
        c.execute("SELECT COUNT(id) FROM tournament_matches WHERE tournament_id = %s AND player_1_id = %s AND player_2_id IS %s", (tournament_id, player_one, None))
        result = c.fetchone()
        if result[0] > 0:
            DB.close()
            return "EROR: One player cannot get more than one BYE in the same tournament!"
    #insert this record into DB
    try:
        c.execute("INSERT INTO tournament_matches(match_date, tournament_id, player_1_id, player_2_id, winning_player_id) VALUES (%s,%s,%s,%s,%s)",
              ( bleach.clean(match_date),
                tournament_id,
                player_one,
                player_two,
                winner
            ))
        DB.commit()
    except psycopg2.IntegrityError:
        return "EROR: Two players cannot face each other twice in the same tournament!"
    DB.close()

def can_this_guy_get_a_bye(player,tournament_id=1):
    """
    Check this player can get a BYE.  No player can get a BYE twice in the same tournament
    """
    DB = connect()
    c = DB.cursor()
    #the first case is where player_1_id and player_2_id are in order
    c.execute("SELECT COUNT(id) FROM tournament_matches WHERE player_1_id = %s AND player_2_id IS NULL and tournament_id = %s", (player,tournament_id))
    r = c.fetchone()
    return r[0] < 1

def can_this_guy_play_this_guy(player_one,player_two,tournament_id=1):
    """
    Check if two players can play against one another
    No two players should play against each other more than once in the same tournament
    """
    if player_one == player_two:
        return False
    DB = connect()
    c = DB.cursor()
    #the first case is where player_1_id and player_2_id are in order
    c.execute("SELECT COUNT(id) FROM tournament_matches WHERE player_1_id = %s AND player_2_id = %s and tournament_id = %s", (player_one,player_two,tournament_id))
    r1 = c.fetchone()
    #the second case is where player_1_id and player_2_id are in reverse order
    c.execute("SELECT COUNT(id) FROM tournament_matches WHERE player_2_id = %s AND player_1_id = %s and tournament_id = %s", (player_one,player_two,tournament_id))
    r2 = c.fetchone()
    DB.close()

    #if EIHER count  is > 0 then return false
    if r1[0] > 0 or r2[0] > 0:
        return False
    return True

def swissPairings(tournament_id=1):
    """Returns a list of pairs of players for the next round of a match.

    Each player appears exactly once in the pairings.
    Each player is paired with another player with an equal or nearly-equal win record, that is, a player adjacent
    to him or her in the standings.

    If the number of players is not Even then one player will get a BYE in the pairings.
    Each player can only get one BYE in any one tournament.

    Args:
      tournament_id: the tournament whose pairings we want to get

    Returns:
      A list of tuples, each of which contains (id1, name1, id2, name2)
        id1: the first player's unique id
        name1: the first player's name
        id2: the second player's unique id
        name2: the second player's name
    """
    #determine if one player will get a BYE
    no_of_players = countPlayers(tournament_id)
    give_bye = False
    has_bye_been_given = False
    if no_of_players % 2 != 0:
        give_bye = True

    #this variable holds a list of players who already have been placed into a match
    already_matched = []
    #this variable holds matches
    matches = []
    #get a list of player stnadings
    standings = playerStandings(tournament_id)
    #go through the standings list and create matches
    for row in standings:
        #for convenience, name the player
        this_player = row[0]

        #check if this player should get a BYE this round
        if give_bye and not has_bye_been_given:
            if can_this_guy_get_a_bye(this_player,tournament_id):
                has_bye_been_given = True
                matches.append((
                        this_player,
                        row[1],
                        None,
                        None
                    ))
                already_matched.append(this_player)

        #only proceed if this player has not been put in a match
        if this_player not in already_matched:
            #go through all the players and find a match for this_player
            for other_row in standings:
                #for convenience, name the OTHER player
                other_player = other_row[0]
                #check if this_player and other_player can be matched together
                if can_this_guy_play_this_guy(this_player,other_player,tournament_id) and other_player not in already_matched:
                    matches.append((
                        this_player,
                        row[1],
                        other_player,
                        other_row[1]
                    ))
                    already_matched.append(this_player)
                    already_matched.append(other_player)
                    break
    return matches





