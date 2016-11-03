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

"""
This will be prepared for SQL
 BUT **will also be translated into an unstractured text file dataset**

"""

def clear_doublespaces(text):
    while "  " in text:
        text = text.replace('  ',' ')

    return text


# play by play url
#http://www.espn.com/nfl/playbyplay?gameId=301107001
def get_gameplay_soup(gameid):
    geturl = 'http://www.espn.com/nfl/playbyplay?gameId={}'.format(gameid)
    try:
        r = urllib2.urlopen(geturl).read()
    except urllib2.HTTPError:
        logging.warning("Could not find the URL -- HTP Error 404 Not Found {}".format(geturl))
        raise NFL_Schedule_Error("Could not find the URL")

    soup = BeautifulSoup(r, 'html.parser')

    all_drives = soup.find_all('li', class_='accordion-item')

    for drive in all_drives:
        # Get the  outcome,current score, drive summary, team-posession


        drive_left = drive.find('div', class_='left')
        if drive_left is None:
            # Could not find a logo, hence onto the next row
            continue
        playindex = 0

        #team in posession
        try:
            img = drive_left.find('span',class_='home-logo')
            img_link = img.find('img')['src']
        except AttributeError:
            # Could not find a logo, hence onto the next row
            continue


        try:
            team_posession = re.search('.*teamlogos\/nfl\/500\/([a-z]{2,3})\..*',img_link,re.IGNORECASE).group(1)
        except:
            print("could not find team in link: {}".format(img_link))
            team_posession = 'UNK'

        # outcome
        outcome = drive_left.find('span', class_='headline').text

        # drive summary
        summary = drive_left.find('span', class_='drive-details').text

        drive_right = drive.find('div', class_='right')
        # current score
        curr_home_score = drive_right.find('span',class_='home')
        curr_home_score = curr_home_score.find('span',class_='team-score').text
        curr_away_score = drive_right.find('span', class_='away')
        curr_away_score = curr_away_score.find('span',class_='team-score').text

        playcontent = drive.find('div',class_='content')

        print(team_posession, curr_home_score,curr_away_score, outcome)
        all_plays = []
        for drive_play in playcontent.find_all('li', class_=''):

            current_down = drive_play.find('h3').text
            play = drive_play.find('p').text
            play = play.strip()
            play = play.replace('\n', ' ')
            play = play.replace('\t', ' ')
            play = clear_doublespaces(play)
            play = play.strip()
            all_plays.append([current_down, play])

        print(all_plays)















