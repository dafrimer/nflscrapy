import pandas as pd
from players_gather import read_all_stats





stat = ['passing','rushing','receiving','scoring','returning','kicking','punting','defense']

players = []
for s in stat:
    for y in range(2011,2017):
        players += read_all_stats(s,y)

pd.DataFrame(players).to_csv('./playersdata.csv')



