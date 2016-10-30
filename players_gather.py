


import urllib2
from bs4 import BeautifulSoup
import re
from lxml import etree
import pandas as pd
import nfl_classes


stat = 'passing','rushing','receiving','scoring','returning','kicking','punting','defense'
START_YEAR = 2015
STATISTIC = stat[0]

MAIN_STAT_PAGE = "http://www.espn.com/nfl/statistics/player/_/stat/{statistic}/year/{year}/".format(statistic=STATISTIC,year=START_YEAR)
r = urllib2.urlopen(MAIN_STAT_PAGE).read()

main_soup = BeautifulSoup(r,'html.parser')
current_soup = main_soup


def simpconvert_to_str(val):
    try:
        return str(val)
    except UnicodeEncodeError:
        return e.text.encode('ascii', 'ignore')

def get_tag_attribute(tagval,attrb):
    att_val = tagval.attrs[attrb]

    if isinstance(att_val,list):
        result = ''
        for each_val in att_val:
            result = result + ' ' + each_val
        result = result.strip()

        return result
    elif isinstance(att_val, (str,unicode)):
        return simpconvert_to_str(att_val)

    else:
        return






def format_col_headers(first_header, second_header=None, abbrv=False):
    column_list = []

    if second_header is not None and get_tag_attribute(second_header,'class') =='colhead':
        second_header_iter = second_header.children
        #combine both rows into same header
        column_start = 0
        columns = 0
        for td in first_header.children:
            if td.attrs.has_key('colspan'):
                assert td.attrs['colspan'].isnumeric()
                columns += int(td.attrs['colspan'])

                primary_header = simpconvert_to_str(td.text)

                #only use  the column span of primary header to insert before secondary header
                for col in range(column_start,columns):
                    sub_td = second_header_iter.next()
                    if abbrv:

                        result_column = simpconvert_to_str(sub_td.text)

                        if len(primary_header) > 0:
                            result_column = primary_header + ' - ' + result_column
                        else:
                            result_column = result_column

                        column_list.append(result_column)

                    else:
                        result_column = ''
                        try:

                            result_column = simpconvert_to_str(get_tag_attribute(sub_td.find('a'), 'title'))

                        except KeyError:
                            result_column = simpconvert_to_str(sub_td.text)

                        except AttributeError:
                            result_column = simpconvert_to_str(sub_td.text)

                        finally:
                            if len(primary_header) > 0:
                                result_column = primary_header + ' - ' + result_column
                            else:
                                result_column = result_column

                            column_list.append(result_column)

                column_start = columns
        return column_list

    else:
        #just use the first row
        for td in first_header.children:
            primary_header = simpconvert_to_str(td.text)

            column_list.append(primary_header)

        return column_list



def get_player_data(player_row):
    pass




def read_all_stats(STATISTIC, START_YEAR):
    MAIN_STAT_PAGE = "http://www.espn.com/nfl/statistics/player/_/stat/{statistic}/year/{year}/".format(\
        statistic=STATISTIC, year=START_YEAR)
    r = urllib2.urlopen(MAIN_STAT_PAGE).read()

    soup = BeautifulSoup(r, 'html.parser')
    current_soup = soup


    player_data_rows = soup.find_all('tr', class_=re.compile('.*player-28-.*'))

    first_header = player_data_rows[0].parent.find('tr',class_='colhead')
    second_header = first_header.next_sibling
    all_columns = format_col_headers(first_header,second_header)



    #ONCE ROWS HAVE BEEN READ.  YOU NEED TO GO TO THE NEXT PAGE


    table_rows = []
    while 1==1:
        r = re.compile('(\d{1,3}) of (\d{1,3})')
        matches = r.match(\
            current_soup.find('div', class_='jcarousel-next').parent.parent.find('div', class_='page-numbers').text)


        player_data_rows = current_soup.find_all('tr', class_=re.compile("(even|odd)row.*"))
        for player_row in player_data_rows:
            player_col = player_row.find_all('td')[all_columns.index('PLAYER')]
            p = nfl_classes.Player()
            p.scrapePlayerInfo(player_col.find('a').attrs['href'])
            print vars(p)



        next_link = current_soup.find('div', class_='jcarousel-next').parent.attrs["href"]
        print matches.group(0)
        #####THE CHECK FOR THE END##########
        if matches.group(1) == matches.group(2):
            break


        try:
            next_link = current_soup.find('div', class_='jcarousel-next').parent.attrs["href"]
            if 'http:' in next_link:
                current_soup = BeautifulSoup(urllib2.urlopen(next_link).read())
            else:
                current_soup = BeautifulSoup(urllib2.urlopen('http:' + next_link).read(),'html.parser')
        except KeyError:
            break



def read_player_page(player_link_url):
    soup = BeautifulSoup(player_link_url)





read_all_stats('passing','2015')








#GET THE SEASON STATS FOR EACH PLAYER FOR EACH SEASON



#GET THE GAME STATS FOR EACH PLAYER FOR EACH SEASON
