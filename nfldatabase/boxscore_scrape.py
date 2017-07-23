"""

All the box score data is taken from a specific website www.footballdb.com.

Be gentle when pinging

"""

from urllib.request import urlopen, urljoin
from bs4 import BeautifulSoup
from lxml import etree
import re
from dateutil.parser import parse

DOMAIN_SOURCE = "http://www.footballdb.com/"


def getGameUrls(year: int, week: int, season_type: str):
    url2go = "http://www.footballdb.com/scores/index.html?lg=NFL&yr={year}&type={season_type}&wk={week}".format(
        year=year, season_type=season_type, week=week)

    r = urlopen(url2go)
    if r.status != 200:
        raise ConnectionError("Url link {} was not valid".format(url2go))

    else:
        game_links = []
        soup = BeautifulSoup(r.read(), 'lxml')
        for found_a in soup.find_all('a', text='Boxscore'):
            try:
                game_links = urljoin(DOMAIN_SOURCE, found_a.attrs['href'])
            except (KeyError, AttributeError):
                continue  # No link seemed attached to it

        return game_links


class Boxscore():
    def __init__(self, gameurl):
        self.gameurl = gameurl
        r = urlopen(gameurl)
        if r.status != 200:
            raise ConnectionError("Url link {} was not valid".format(url2go))
        self.soup = BeautifulSoup(r.read(), 'lxml')
        self.root = etree.fromstring(self.soup.prettify())
        if isinstance(self.root, etree._ElementTree):
            self.root = self.root.getroot()
        assert (isinstance(self.root, etree._Element))

        self.date = ''  # datetime
        self.location = ''  # str
        self.attendance = -1  # str
        self.homeRecord = ""
        self.awayRecord = ""
        self.homeTeam_link = ''
        self.awayTeam_link = ''
        self.homeTeam = ''  # str
        self.awayTeam = ''  # str
        self.quarterScores = {}

        self.home_score = -1
        self.away_score = -1

    def parseHead(self):
        try:
            header_ = self.root.xpath('//div[@id="breadcrumbs"]/following-sibling::center/div/text()')
        except IndexError:
            raise IndexError("Could not find the header in {}".format(gameurl))

        lines = [x.strip() for x in header_ if x.strip() != '']
        self.date = parse(lines[0].split('-')[0])  # the date
        self.location = lines[0].split('-')[1].strip()  # The stadium and location
        self.attendance = int(lines[1].strip().split('Attendance:')[1].replace(',', '').strip())

        print(self.date, self.location, self.attendance)

    def parseBoxscore(self):
        table_box = self.soup.find('table', attrs={'class': 'statistics'})

        table_box.find_all('tr')[0].find_all('td')[-2].text     # Last is the total, second to last is the last quarter

        for header_row, away_row, home_row in zip(table_box.find_all('tr')[0].find_all('td'),
                                                  table_box.find_all('tr')[1].find_all('td'),
                                                  table_box.find_all('tr')[2].find_all('td')):
            if header_row.text.strip() == '':

                away_search = re.search("(.*) (\([0-9]{1,2}-[0-9]{1,2}\)$)",
                                           away_row.text.strip())
                self.awayTeam = away_search.group(1)
                self.awayRecord = away_search.group(2)
                self.awayTeam_link = urljoin(DOMAIN_SOURCE, away_row.find('a').attrs['href'])

                home_search = re.search("(.*) (\([0-9]{1,2}-[0-9]{1,2}\)$)",
                                        home_row.text.strip())
                self.homeTeam = home_search.group(1)
                self.homeRecord = home_search.group(2)
                self.homeTeam_link = urljoin(DOMAIN_SOURCE, home_row.find('a').attrs['href'])

            elif header_row.text.strip() == 'Total':
                self.away_score = int(away_row.text.strip())
                self.home_score = int(home_row.text.strip())

            else:
                self.quarterScores[header_row.text.strip()] = {}
                self.quarterScores[header_row.text.strip()]['away'] = int(home_row.text.strip())
                self.quarterScores[header_row.text.strip()]['home'] = int(home_row.text.strip())




