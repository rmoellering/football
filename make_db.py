
# 1 me
# 2 trevor
# 3 david
# 4 scott
# 5 catherine
# 6 chris
# 7 vince
# 8 tony
# 9 jambach
# 10 gannon

import psycopg2
import requests
import sys

from bs4 import BeautifulSoup
import re
import sqlite3

from utils import get_logger, get_human_time_diff

log = get_logger(__name__)
host = '127.0.0.1'
port = 5000
app_id = None

def get_conn():
	return psycopg2.connect(
		host='localhost',
		dbname='football',
		user='robmo',
		password=''
	)

	# return sqlite3.connect('database.db')

def startup():

	# TODO: find a way to wrap this and similar methods in something that opens, provides, and closes the connection and cursor for it

	conn = get_conn()
	c = conn.cursor()

	# delete tables if they exist
	log.info('Deleting old tables...')
	tables = ['ff_teams', 'ff_players', 'ff_games', 'ff_player_games']
	for table in tables:
		try:
			c.execute("DROP TABLE {};".format(table))
		except sqlite3.OperationalError:
			print('{} cannot be dropped'.format(table))
			pass
		except psycopg2.ProgrammingError:
			print('{} cannot be dropped'.format(table))
			c.execute("END;")
			pass
	conn.commit()

	# create tables
	log.info('Creating tables...')
	# TODO: status instead of is_active, mebbe both tho
	c.execute("CREATE TABLE ff_teams (id INT, name TEXT, owner TEXT)")
	c.execute("CREATE TABLE ff_players (id INT, name TEXT, yahoo_id INT, team TEXT, position TEXT)")
	c.execute("CREATE TABLE ff_games (id INT, week INT, self INT, opponent INT, score DECIMAL(5, 2), projected DECIMAL(5, 2))")
	c.execute("CREATE TABLE ff_player_games (game INT, player INT, position TEXT, score DECIMAL(5, 2), projected DECIMAL(5, 2), notes TEXT)")
	conn.commit()

	dat = [
		(1, 'A Bag of Six', 'Rob'),
		(2, 'Orange Crush', 'Trevor'),
		(3, "David''s Destroyers", 'David'),
		(4, 'Kriztastic', 'Scott'),
		(5, 'Moo Cat', 'Catherine'),
		(6, 'Rabid Weasels', 'Chris'),
		(7, "Vince''s Team", 'Vince'),
		(8, 'Cat-tastic', 'Tony'),
		(9, 'Squad Jambach', 'James'),
		(10, 'G Money', 'Gannon')
	]


	# initialize teams
	for tpl in dat:
		c.execute("INSERT INTO ff_teams (id, name, owner) VALUES ({}, '{}', '{}')".format(tpl[0], tpl[1], tpl[2]))
	conn.commit()

	c.close()
	conn.close()
	log.info('Startup successful')

def clean(raw):
	cleaned = raw.replace("\n", "")
	cleaned = cleaned.rstrip(" ")
	cleaned = cleaned.lstrip(" ")
	return cleaned

# TODO: yahoo_id
def get_or_create_player(player):
	c.execute("SELECT MAX(id) from ff_players WHERE name = '{}' AND team = '{}';".format(player['name'], player['team']))
	id = c.fetchone()[0]
	if not id:
		c.execute("SELECT MAX(id) from ff_players;")
		id = c.fetchone()[0]
		if not id:
			id = 0
		id += 1
		c.execute("INSERT INTO ff_players (id, name, yahoo_id, team, position) VALUES ({}, '{}', 0, '{}', '{}')". \
			format(id, player['name'], player['team'], player['position']))
	return id

startup()

team_to_id = {
	'A Bag of Six': 1,
	'Orange Crush': 2,
	"David's Destroyers": 3,
	'Kriztastic': 4,
	'Moo Cat': 5,
	'Rabid Weasels': 6,
	"Vince's Team": 7,
	'Cat-tastic': 8,
	'Squad Jambach': 9,
	'G Money': 10
}

conn = get_conn()
c = conn.cursor()

for week in range(17):
	if week == 0:
		continue
	top = 6 if week < 15 else 5

	for player in range(top):
		if player == 0:
			continue

		log.info('')
		log.info('WEEK {} PLAYER {}'.format(week, player))
		log.info('')

		fh = open("./pages/week_{}_{}.html".format(week, player))
		page = fh.read()
		fh.close()
		soup = BeautifulSoup(page, 'html.parser')

		# TEAM NAMES

		# <div class='Hd No-m No-p No-bdr'>
		section = soup.find('div', class_='Hd No-m No-p No-bdr')
		#<div class='Fz-xxl Ell'><a class="F-link" href="/f1/756505/1">A Bag of Six</a></div>
		teams = section.find_all('div', 'Fz-xxl Ell')
		if len(teams) != 2:
			log.error('Found {} teams, expecting 2'.format(len(teams)))
			exit()
		team1 = teams[0].text
		team1_id = team_to_id[team1]
		team2 = teams[1].text
		team2_id = team_to_id[team2]

		# TEAM SCORES

		table = section.find('table', 'M-a')
		tds = section.find_all('td',)
		if len(tds) != 4:
			log.error('Found {} tds, expecting 2'.format(len(tds)))
			exit()
		team1_score = tds[0].text
		team2_score = tds[1].text
		team1_projected = tds[2].text
		team2_projected = tds[3].text


		c.execute("SELECT MAX(id) from ff_games;")
		team1_game_id = c.fetchone()[0]
		if team1_game_id:
			team1_game_id += 1
		else:
			team1_game_id = 1
		sql = "INSERT INTO ff_games (id, week, self, opponent, score, projected) VALUES ({}, {}, {}, {}, {}, {})". \
			format(team1_game_id, week, team1_id, team2_id, team1_score, team1_projected)
		c.execute(sql)

		c.execute("SELECT MAX(id) from ff_games;")
		team2_game_id = c.fetchone()[0] + 1
		sql = "INSERT INTO ff_games (id, week, self, opponent, score, projected) VALUES ({}, {}, {}, {}, {}, {})". \
			format(team2_game_id, week, team2_id, team1_id, team2_score, team2_projected)
		c.execute(sql)

		log.info('Team 1 - {} - {} - {} - {}'.format(team1, team1_id, team1_score, team1_projected))
		log.info('Team 2 - {} - {} - {} - {}'.format(team2, team2_id, team2_score, team2_projected))

		# PLAYER SCORES

		player = []
		player.append({})
		player.append({})
		player.append({})

		log.info('PLAYERS')

		tbl = soup.find("div", id="matchups").find('table')
		first = True
		for tr in tbl.find_all('tr'):
			if first:
				first = False
				continue

			tds = tr.find_all('td')

			if tds[0].find('a'):
				player[1]['notes'] = clean(tds[0].find('a').text)
			else:
				player[1]['notes'] = ''
			player[1]['name'] = clean(tds[1].find('a', class_="Nowrap").text)
			team_pos = tds[1].find('span', class_="Fz-xxs").text
			player[1]['team'], player[1]['position'] = clean(team_pos).split(' - ')
			player[1]['id'] = get_or_create_player(player[1])
			player[1]['projected'] = clean(tds[2].text)
			score = clean(tds[3].text)
			player[1]['score'] = '0.00' if len(score) == 1 else score

			fantasy_position = clean(tds[5].text)

			sql = "INSERT INTO ff_player_games (game, player, position, score, projected, notes) VALUES ({}, '{}', '{}', {}, {}, '{}')". \
				format(team1_game_id, player[1]['id'], fantasy_position, player[1]['score'], player[1]['projected'], player[1]['notes'])
			log.info(sql)
			c.execute(sql)

			score = clean(tds[7].text)
			player[2]['score'] = '0.00' if len(score) == 1 else score
			player[2]['projected'] = clean(tds[8].text)
			player[2]['name'] = clean(tds[9].find('a', class_="Nowrap").text)
			team_pos = tds[9].find('span', class_="Fz-xxs").text
			player[2]['team'], player[2]['position'] = clean(team_pos).split(' - ')
			player[2]['id'] = get_or_create_player(player[2])
			if tds[10].find('a'):
				player[2]['notes'] = clean(tds[10].find('a').text)
			else:
				player[2]['notes'] = ''

			sql = "INSERT INTO ff_player_games (game, player, position, score, projected, notes) VALUES ({}, '{}', '{}', {}, {}, '{}')". \
				format(team1_game_id, player[2]['id'], fantasy_position, player[2]['score'], player[2]['projected'], player[2]['notes'])
			c.execute(sql)

			log.info(fantasy_position)
			log.info(player)

			if player[2]['position'] == 'DEF':
				break
			player[1] = {}
			player[2] = {}
		conn.commit()

		log.info('BENCH')
		tbl = soup.find("div", id="matchupcontent2").find('table')
		first = True
		count = 0
		for tr in tbl.find_all('tr'):
			if first:
				first = False
				continue

			tds = tr.find_all('td')

			if tds[0].find('a'):
				player[1]['notes'] = clean(tds[0].find('a').text)
			else:
				player[1]['notes'] = ''

			pname = tds[1].find('a', class_="Nowrap")
			if pname and type(pname) != str and pname.text:
				player[1]['name'] = clean(pname.text)
				team_pos = tds[1].find('span', class_="Fz-xxs").text
				player[1]['team'], player[1]['position'] = clean(team_pos).split(' - ')
				player[1]['id'] = get_or_create_player(player[1])
				player[1]['projected'] = clean(tds[2].text)

				score = clean(tds[3].text)
				player[1]['score'] = '0.00' if len(score) == 1 else score

				fantasy_position = clean(tds[5].text)

				sql = "INSERT INTO ff_player_games (game, player, position, score, projected, notes) VALUES ({}, '{}', '{}', {}, {}, '{}')". \
					format(team1_game_id, player[1]['id'], fantasy_position, player[1]['score'], player[1]['projected'], player[1]['notes'])
				c.execute(sql)
			else:
				log.warn('Empty player for Team 1 Bench')

			pname = tds[9].find('a', class_="Nowrap")
			if pname and pname.text:
				player[2]['name'] = clean(pname.text)

				score = clean(tds[7].text)
				# weird chr(8211)
				player[2]['score'] = '0.00' if len(score) == 1 else score
				# log.info(score == '-')
				# if len(score) == 1:
				# 	log.info(ord(score))
				# 	log.info(ord('-'))
				# log.info('-' == '-')
				#log.info(player[2]['score'])

				player[2]['projected'] = clean(tds[8].text)
				player[2]['name'] = clean(tds[9].find('a', class_="Nowrap").text)
				team_pos = tds[9].find('span', class_="Fz-xxs").text
				player[2]['team'], player[2]['position'] = clean(team_pos).split(' - ')
				player[2]['id'] = get_or_create_player(player[2])
				if tds[10].find('a'):
					player[2]['notes'] = clean(tds[10].find('a').text)
				else:
					player[2]['notes'] = ''

				sql = "INSERT INTO ff_player_games (game, player, position, score, projected, notes) VALUES ({}, '{}', '{}', {}, {}, '{}')". \
					format(team1_game_id, player[2]['id'], fantasy_position, player[2]['score'], player[2]['projected'], player[2]['notes'])
				#log.info(sql)
				c.execute(sql)
			else:
				log.warn('Empty player for Team 2 Bench')

			log.info(fantasy_position)
			log.info(player)

			count += 1
			if count == 6:
				break
			player[1] = {}
			player[2] = {}
		conn.commit()

		tables = ['ff_teams', 'ff_players', 'ff_games', 'ff_player_games']
		for table in tables:
			c.execute("SELECT COUNT(*) from {};".format(table))
			log.info("{} {}".format(table, c.fetchone()[0]))


c.close()
conn.close()

exit()
