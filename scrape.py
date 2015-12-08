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
db = client.cfb_bowl_games

#r = requests.get('http://espn.go.com/college-football/story/_/id/11419086/2014-15-college-football-bowl-schedule')
#r = requests.get('http://www.fbschedules.com/ncaa/college-football-bowl-schedule.php')
with open ("web_page.html", "r") as myfile:
    data=myfile.read()
soup = BeautifulSoup(data, "html.parser")

def hasNumbers(inputString):
    return any(char.isdigit() for char in inputString)

for x in soup.find_all('h3'):
    datestring = x.string

    for y in x.next_siblings:
        game = {}
        game['team0'] = {}
        game['team1'] = {}

        try:
            lines = y.get_text().replace(";", "").split("\n")
        except AttributeError:
            lines = []


        if len(lines) == 4:
            if "Jan. 11" in lines[0]:
                continue
            for idx, val in enumerate(lines):
                if idx == 0:
                    game['name'] = val
                if idx == 1:
                    game['teams'] = val
                    teams = game['teams'].split(" vs. ")
                    if "No." in teams[0]:
                        p = re.compile(r'No. (\d+) ([\w\s]+)')
                        m = p.match(teams[0])
                        game['team0']['rank'] = m.group(1)
                        game['team0']['name'] = m.group(2)
                    else:
                        game['team0']['name'] = teams[0]
                    if "No." in teams[1]:
                        p = re.compile(r'No. (\d+) ([\w\s]+)')
                        m = p.match(teams[1])
                        game['team1']['rank'] = m.group(1)
                        game['team1']['name'] = m.group(2)
                    else:
                        game['team1']['name'] = teams[1]
                if idx == 2:
                    info = val.split("|")
                    game['location'] = info[0]
                    game['venue'] = info[1]
                if idx == 3:
                    info = val.split(" on ")
                    if info[0] == "Noon":
                        game['time'] = "12 p.m."
                    else:
                        game['time'] = info[0]
                    game['network'] = info[1]
            if "Jan" in datestring:
                parseable = "%s, 2016 %s" % (datestring, game['time'])
            else:
                parseable = "%s, 2015 %s" % (datestring, game['time'])
                game['datetime'] = parse(parseable)

        else:
            continue

        print(game)
        db.games.insert(game)


    """
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
            if game['datetime'] > datetime.datetime(2014, 12, 19, 0, 0):
                db.games.insert(game)
            else:
                print("Not inserting %s because datetime: %s" % (game['name'], game['datetime']))
    """
