from __future__ import print_function

# http://www.espn.com/nfl/schedule

import logging
import urllib2
from bs4 import BeautifulSoup
import re
from lxml import etree
import pandas as pd

from stand_proc import simpconvert_to_str, NFL_Schedule_Error
from collections import defaultdict
import pandas as pd
import datetime
import re


HOME_PAGE = 'www.espn.com'

season_types = {'postseason': 3,
 'regular_season': 2,
 'preseason': 1}
POSTSEASON_WEEKS = range(1,6)
REGULAR_SEASON_WEEKS = range(1,18) # 17 weeks
PRESEASON_WEEKS = range(2,6) # weeks 2-5 (don't include HOF weekend)
#http://www.espn.com/nfl/schedule/_/seasontype/{season_type}/year/{year}/week/{week}


logging.basicConfig(filename='./nfl_schedule_{}.log'.format(datetime.datetime.strftime(datetime.datetime.now(),'%Y%m%d')),level=logging.DEBUG)
def get_schedule_soup(year, week, season_type = 2):

    geturl = 'http://www.espn.com/nfl/schedule/_/seasontype/{season_type}/year/{year}/week/{week}'.format(**{'year':year,'week':week,'season_type':season_type})
    try:
        r = urllib2.urlopen(geturl).read()
    except urllib2.HTTPError:
        logging.warning("Could not find the URL -- HTP Error 404 Not Found {}".format(geturl))
        raise NFL_Schedule_Error("Could not find the URL")

    soup = BeautifulSoup(r, 'html.parser')

    # Grabs the schedule container
    schedule_container = soup.find('div',id='sched-container')

    # Finds all the scheduled games
    date_containers = schedule_container.find_all('div', class_='responsive-table-wrap')
    games_data = []
    for date_container in date_containers:
        if date_container.find('th') is None:
            continue

        if date_container.find('th').text.lower() == 'bye':
            # add the bye weeks to a list
            all_team_abbrv =[i.text for i in date_container.find_all('abbr')]
            print(week, all_team_abbrv)


        elif date_container.find('th').text.lower() == 'matchup':
            dateOfGame = date_container.find_previous('h2').text

            d = defaultdict(lambda: len(d))
            for i in [t.text for t in date_container.find('thead').find_all('th')]: d[i]


            all_schedule_games = date_container.find('tbody').find_all('tr')
            for matchup in all_schedule_games:
                all_cols = matchup.find_all('td')

                team_1 = all_cols[0].find('abbr').text
                home_text = matchup.find('td', class_='home')['data-home-text']
                team_2 = all_cols[1].find('abbr').text

                score = all_cols[2].find('a').text
                try:
                    team_1_score = int( re.search(team_1+' ([0-9]+)', all_cols[2].find('a').text).group(1))
                    team_2_score = int(re.search(team_2+' ([0-9]+)', all_cols[2].find('a').text).group(1))

                except AttributeError:
                    # No score was found:
                    logging.warning('Could not find the score in this link.  Please add it manually.: {}'.format(str(all_cols)))
                    continue
                finally:
                    if '(ot)' in all_cols[2].find('a').text.lower():
                        OT = 1
                    else:
                        OT = 0



                game_link = HOME_PAGE + all_cols[2].find('a')['href']
                game_id =  int(re.search('gameId=([0-9]*)',game_link,re.IGNORECASE).group(1))

                # Change St. Louis
                if team_1 == 'STL':
                    team_1 = 'LA'
                elif team_2 == 'STL':
                    team_2 = 'LA'

                #
                games_data.append((int(year), int(season_type), int(week), dateOfGame, int(game_id), team_1, int(team_1_score) , home_text, team_2, int(team_2_score), int(OT)))
        else:
            print(date_container.__str__())

    print(week,len(games_data))
    return games_data
import pymysql
def execute_sql(games_data):
    if games_data is None or len(games_data) ==0:
        return
    global creds
    with open('./mysqlaccess') as f:
        acc = f.read()
        acc = acc.strip()
        creds = dict([a.split('=') for a in acc.split('\n')])

    cxn = pymysql.connect(host=creds['host'], user=creds['user'],
                        password=creds['pw'], db='fantasysports')
    c = cxn.cursor()
    tempstatement = """
    CREATE TEMPORARY TABLE IF NOT EXISTS insert_game_table LIKE fantasysports.Game;
    ALTER TABLE insert_game_table CHANGE COLUMN `homeTeam` `homeTeam` VARCHAR(20) NOT NULL ;
    ALTER TABLE insert_game_table CHANGE COLUMN `awayTeam` `awayTeam` VARCHAR(20) NOT NULL ;


    INSERT INTO fantasysports.insert_game_table (year,season_type, week, gameDate, gameID, awayTeam, awayScore,at_or_vs, homeTeam,homeScore, OT)
    VALUES                                      (%s,    %s,       %s,    %s,      %s,      %s,       %s,       %s,      %s          , %s    ,%s);

    """
    print(c.executemany(tempstatement, games_data))
    print(games_data)
    statement="""
    REPLACE INTO fantasysports.Game (year,season_type, week, gameDate, gameID, homeTeam,homeScore,at_or_vs, awayTeam, awayScore, OT)
    SELECT year,season_type, week, gameDate, gameID, h.teamID,homeScore,at_or_vs, a.teamID, awayScore, OT
    FROM insert_game_table
    left join fantasysports.Team h
        on h.teamshort = homeTeam
    left join fantasysports.Team a
        on a.teamshort = awayTeam;

    DROP TABLE IF EXISTS insert_game_table
    """
    c.execute(statement)




for y in range(2016,2017):
    for rs in REGULAR_SEASON_WEEKS:
        try:
            d = get_schedule_soup(y, rs, season_types['regular_season'])
        except NFL_Schedule_Error:
            continue
        #print(d)
        print("Moving to sql")
        execute_sql(d)
    for pos in POSTSEASON_WEEKS:
        try:
            d = get_schedule_soup(y, pos, season_types['postseason'])
        except NFL_Schedule_Error:
            continue
        #print(d)
        execute_sql(d)
    for prs in PRESEASON_WEEKS:
        try:
            d = get_schedule_soup(y, prs, season_types['preseason'])
        except NFL_Schedule_Error:
            continue
        #print(d)
        execute_sql(d)


# print(team_1,home_text,team_2)




