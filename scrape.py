#!/usr/bin/python3

from bs4 import BeautifulSoup
from pprint import pprint
import requests
import re

r = requests.get('http://espn.go.com/college-football/story/_/id/11419086/2014-15-college-football-bowl-schedule')
soup = BeautifulSoup(r.text)

def hasNumbers(inputString):
    return any(char.isdigit() for char in inputString)

bowl_games = []

for x in soup.find_all('tr', attrs={'class':'last'}):
    game = {}
    for y in x.find_all('td'):
        if y.strong:
            game['name'] = y.strong.string
            game['teams'] = y.br.next_sibling.lstrip('\n')
        elif not y.br:
            game['network'] = y.string
        else:
            if hasNumbers(y.br.previous_sibling):
                game['date'] = y.br.previous_sibling
                game['time'] = y.br.next_sibling.lstrip('\n')
            else: 
                game['stadium'] = y.br.previous_sibling
                game['location'] = y.br.next_sibling.lstrip('\n')
    teams = game['teams'].split(" vs. ")
    game['team0'] = {}
    game['team1'] = {}
    if "No. " in teams[0]:
        p = re.compile(r'No. (\d+) (\w+)')
        m = p.match(teams[0])
        game['team0']['rank'] = m.group(1)
        game['team0']['name'] = m.group(2)
        m = p.match(teams[1])
        game['team1']['rank'] = m.group(1)
        game['team1']['name'] = m.group(2)
    else:
        game['team0']['name'] = teams[0]
        game['team1']['name'] = teams[1]
    bowl_games.append(game)
    if "Florida Citrus Bowl" in game['location']:
        break

pprint(bowl_games)
