from bs4 import BeautifulSoup
import urllib2
import re
from datetime import  datetime
position_abbrvs = {
    'Quarterback': 'QB',
    'Running Back': 'RB',
    'Fullback': 'FB',
    'Wide Receiver': 'WR',
    'Tight End': 'TE',
    'Offensive Lineman': 'OL',
    'Center': 'C',
    'Guard': 'G',
    'Left Guard': 'LG',
    'Right Guard': 'RG',
    'Tackle': 'T',
    'Left Tackle': 'LT',
    'Right Tackle': 'RT',
    'Kicker': 'K',
    'Kick Returner': 'KR',
    'Defensive Lineman': 'DL',
    'Defensive End': 'DE',
    'Defensive Tackle': 'DT',
    'Nose Tackle': 'NT',
    'Linebacker': 'LB',
    'Inside Linebacker': 'ILB',
    'Outside Linebacker': 'OLB',
    'Middle Linebacker': 'MLB',
    'Defensive Back': 'DB',
    'Cornerback': 'CB',
    'Free Safety': 'FS',
    'Strong Safety': 'SS',
    'Safety': 'S',
    'Punter': 'P',
    'Punt Returner': 'PR',

}


class Player(object):
    def __init__(self):
        self.name = ''
        self.playerID = ''
        self.status = ''
        self.position = ''
        self.height = ''
        self.weight = ''
        self.experience_int = ''

        self.Born = ''
        self.Drafted = 'Undrafted'
        self.Experience = ''
        self.College = ''

    def get_height_weight(self, height_val):
        height_re = re.compile('(\d{1,2})\'.(\d{0,2})\"?, (\d{2,3}) lbs')

        matches = height_re.match(height_val)
        if matches:
            height = int(matches.group(1)) + round(int(matches.group(2)) / 12.0, 2)
            weight = int(matches.group(3))

            return height, weight

    def scrapeID_fromURL(self, url):
        matcher = re.compile('.*player/.*_/id/(\d{,9})/.*')
        return matcher.match(url).group(1)


    def scrapePlayerInfo(self, player_url):

        self.playerURL = player_url
        soup = BeautifulSoup(urllib2.urlopen(player_url).read(), 'html.parser')

        self.playerID = self.scrapeID_fromURL(player_url)

        main_content = soup.find('div', class_='mod-content')
        self.name = main_content.find('h1').text

        general_info = main_content.find('ul', class_='general-info')

        #need to iterate over metadata if the picture is missing or is split in floats
        metadata = main_content.find_all('ul', class_=re.compile('player-metadata.*'))

        # Player is retired if the first list in the bio is only 1 (i.e the position spelled out "Running Back"
        if len(general_info.find_all('li')) == 1:
            self.status = "Retired"
            self.position = general_info.find('li').text.encode('ascii', 'ignore')

        else:
            # Format is #11 WR|5' 8", 176 lbs|Los Angeles Rams
            self.status = "Active"
            # '#11 WR'

            self.position = general_info.find_all('li')[0].text.split(' ')[1]
            # '5' 8", 176 lbs'
            self.height, self.weight = self.get_height_weight(general_info.find_all('li')[1].text)

        for meta in main_content.find_all('span'):
            if meta.text == 'Born':
                r = re.compile('[(A-z][a-z][a-z] \d{1,2}, \d{4}).*')
                try:
                    str_date = r.match(meta.next_sibling).group(1)
                    self.Born = datetime.strptime(str_date, '%b %d, %Y').date()
                except:
                    pass
            elif meta.text == 'Drafted':
                r = re.compile('\d{4}. \d{1,2}[a-z]{2} Rnd, \d{1,3} by [A-Z]{3}')
                try:
                    str_draftdate = r.match(meta.next_sibling).group(0)
                    self.Drafted = str_draftdate
                except:
                    pass

            elif meta.text == 'Experience':
                r = re.compile('(\d{1,2}).*')
                self.Experience = int(r.match(meta.next_sibling).group(1))

            elif meta.text == 'College':
                self.College = meta.next_sibling








    def get_attributes(self):
        return vars(self)

