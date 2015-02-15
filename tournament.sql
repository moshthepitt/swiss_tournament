-- Table definitions for the tournament project.
--
-- Put your SQL 'create table' statements in this file; also 'create view'
-- statements if you choose to use it.
--
-- You can write comments in this file by starting them with two dashes, like
-- these lines here.

-- this table stores information about a tournament
-- the "created_on" field helps us to track when a particular record was inserted into the database
-- the name, start_date, end_date and details fields store information about a tournament
CREATE TABLE tournaments(
	id SERIAL PRIMARY KEY,
	created_on TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	name VARCHAR(255) NOT NULL,
	start_date DATE,
	end_date DATE,
	details TEXT
);

-- this table stores information about players
-- the "created_on" field helps us to track when a particular record was inserted into the database
CREATE TABLE players(
	id SERIAL PRIMARY KEY,
	created_on TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	name VARCHAR(255) NOT NULL
);

-- this table stores information about which players are enrolled to any particular tournament
-- the "created_on" field helps us to track when a particular record was inserted into the database
-- A restriction exists to prevent tournaments that have players enrolled from being deleted
-- A restriction exists to prevent playerss that ares enrolled in a tournament from being deleted
-- Tournament_id and player_id are together used as a primary key.  Also helps prevent one player enrolled in a tournament more than once
CREATE TABLE tournament_players(
	tournament_id INTEGER REFERENCES tournaments(id) ON DELETE RESTRICT NOT NULL,
	player_id INTEGER REFERENCES players(id) ON DELETE RESTRICT NOT NULL,
	created_on TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	registration_date DATE,
	PRIMARY KEY(tournament_id, player_id)
);

-- this table stores information about the matches between players in a tournament
-- the "created_on" field helps us to track when a particular record was inserted into the database
-- A restriction exists to prevent players that have matches from being deleted
-- One tournament cannot have two players play each other more than once
-- If player_2_id is NULL then this means that player_1_id was given a BYE in this match
-- The winning player ID records which of the two players won the match, if it is NULL it means that there was a draw
CREATE TABLE tournament_matches(
	id SERIAL PRIMARY KEY,
	created_on TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	match_date DATE NOT NULL,
	tournament_id INTEGER REFERENCES tournaments(id) ON DELETE RESTRICT NOT NULL,
	player_1_id INTEGER REFERENCES players(id) ON DELETE RESTRICT NOT NULL,
	player_2_id INTEGER REFERENCES players(id) ON DELETE RESTRICT,
	winning_player_id INTEGER REFERENCES players(id) ON DELETE RESTRICT DEFAULT NULL,
	CONSTRAINT u_constraint UNIQUE (tournament_id, player_1_id, player_2_id)
);