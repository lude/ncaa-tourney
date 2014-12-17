#!/usr/bin/python3

from bs4 import BeautifulSoup
from pprint import pprint
from dateutil.parser import parse
import requests
import re
import pymongo
import datetime

from pymongo import MongoClient
client = MongoClient('localhost', 27017)
db = client.ncaa_tourney

#r = requests.get('http://espn.go.com/college-football/story/_/id/11419086/2014-15-college-football-bowl-schedule')
#r = requests.get('http://www.fbschedules.com/ncaa/college-football-bowl-schedule.php')
with open ("web_page.html", "r") as myfile:
    data=myfile.read()
soup = BeautifulSoup(data)

def hasNumbers(inputString):
    return any(char.isdigit() for char in inputString)

for x in soup.find_all('tr'):
    game = {}
    if x.td.get('class'):
        if "bowl1g" in x.td.get('class') or "bowl1" in x.td.get('class'):
            for y in x.find_all('td'):
                if y.strong:
                    game['name'] = y.strong.string
                    game['teams'] = y.br.next_sibling.lstrip('\n\r\t ')
                elif not y.br:
                    game['network'] = y.string
                else:
                    if hasNumbers(y.br.previous_sibling):
                        game['date'] = y.br.previous_sibling
                        game['time'] = y.br.next_sibling.lstrip('\n\r\t ')
                    elif "." not in y.br.previous_sibling and "," in y.br.previous_sibling:
                        game['location'] = y.br.previous_sibling
                        game['stadium'] = y.br.next_sibling.lstrip('\n\r\t ')
            teams = game['teams'].split(" vs. ")
            pprint(game)
            game['team0'] = {}
            game['team1'] = {}
            if game['time'] == "Noon ET":
                game['time'] = "12:00 p.m ET"
            if "Jan" in game['date']:
                parseable = "%s, 2015 %s" % (game['date'], game['time'])
            else:
                parseable = "%s %s" % (game['date'], game['time'])
            game['datetime'] = parse(parseable)
            if "(" in teams[0]:
                p = re.compile(r'\((\d+)\) ([\w\s]+)')
                m = p.match(teams[0])
                game['team0']['rank'] = m.group(1)
                game['team0']['name'] = m.group(2)
            else:
                game['team0']['name'] = teams[0]
            if "(" in teams[1]:
                p = re.compile(r'\((\d+)\) ([\w\s]+)')
                m = p.match(teams[1])
                game['team1']['rank'] = m.group(1)
                game['team1']['name'] = m.group(2)
            else: 
                game['team1']['name'] = teams[1]
            pprint(game)
            if not game.get('stadium'):
                game['location'] = 'St. Petersburg, FL'
                game['stadium'] = 'Tropicana Field'
            if game['datetime'] > datetime.datetime(2014, 12, 26, 0, 0):
                db.games.insert(game)
            else:
                print("Not inserting %s because datetime: %s" % (game['name'], game['datetime']))
