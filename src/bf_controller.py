import requests, sqlite3
from bs4 import BeautifulSoup
from database import stats, create_db
import datetime as dt
from collections import namedtuple
import pandas as pd

HOURS=10000
MINUTES=100

def remove_commas(comma_int):
    return int(comma_int.replace(',',''))

def convert_time_to_int(time_str):
    time=0
    time_split=time_str.split(":")
    if len(time_str) >=3:
        time += int(time_split[0]) * HOURS
        time += int(time_split[1]) * MINUTES
        time += int(time_split[2])
    elif len(time_split) <= 2:
        time += int(time_split[1]) * MINUTES
        time += int(time_split[2])
    else:
        time = int(time_split[2])
    return time

def get_current_time():
    now = dt.datetime.now()
    return ''.join(map(lambda x: '{0:02d}'.format(x),[now.year, now.month, now.day, now.hour, now.minute, now.second]))

def get_stats(user, db):
    page = requests.get("http://bf1stats.com/xone/" + user)
    soup = BeautifulSoup(page.content, 'html.parser')
    #with open (user+".html","w") as f:
    #    f.write(page.content.decode('utf-8'))

    #with open(user+'.html','r') as f:
    #    page = f.read()
    #soup = BeautifulSoup(page, 'html.parser')

    score=remove_commas(soup.find_all(attrs={"data-stat" : "stats.scores.rank|nf"})[0].get_text())
    general_score=remove_commas(soup.find_all(attrs={"data-stat" : "stats.scores.general|nf"})[0].get_text())
    wins=remove_commas(soup.find_all(attrs={"data-stat" : "stats.numWins|nf"})[0].get_text())
    losses=remove_commas(soup.find_all(attrs={"data-stat" : "stats.numLosses|nf"})[0].get_text())
    rounds_played=remove_commas(soup.find_all(attrs={"data-stat" : "stats.numRounds|nf"})[0].get_text())
    kills=remove_commas(soup.find_all(attrs={"data-stat" : "stats.kills|nf"})[0].get_text())
    deaths=remove_commas(soup.find_all(attrs={"data-stat" : "stats.deaths|nf"})[0].get_text())
    time_played=convert_time_to_int(soup.find_all(attrs={"data-stat" : "stats.timePlayedAll|time"})[0].get_text())
    mvp=remove_commas(soup.find_all(attrs={"data-stat" : "stats.flagDefend|nf"})[0].get_text())
    ace_squad=remove_commas(soup.find_all(attrs={"data-stat" : "stats.aceSquad|nf"})[0].get_text())
    longest_headshot=remove_commas(soup.find_all(attrs={"data-stat" : "stats.longestHeadshot|nf"})[0].get_text())
    kill_streak=remove_commas(soup.find_all(attrs={"data-stat" : "stats.killStreak|nf"})[0].get_text())
    flag_caps=remove_commas(soup.find_all(attrs={"data-stat" : "gameModes.conquest.stat.flagCaptures|nf"})[0].get_text())

    return stats.Stats(date             = get_current_time(),
                       user             = user,
                       score            = score,
                       general_score    = general_score,
                       wins             = wins,
                       losses           = losses,
                       rounds_played    = rounds_played,
                       kills            = kills,
                       deaths           = deaths,
                       time_played      = time_played,
                       mvp              = mvp,
                       ace_squad        = ace_squad,
                       longest_headshot = longest_headshot,
                       kill_streak      = kill_streak,
                       flag_caps        = flag_caps)

#def initialize_stats_dic():
#    StatsDic = namedtuple("StatsDic", "users scores general_scores wins losses rounds_played kills deaths time_played mvp ace_squad longest_headshot kill_streak flag_caps")
#    return StatsDic(user=[], score=[], general_score=[], wins=[], losses=[],
#                    rounds_played=[], kills=[], deaths=[], time_played=[],
#                    mvp=[], ace_squad=[], longest_headshot=[], kill_streak=[],
#                    flag_caps=[])

def get_stats_from_db(db):
    users=sorted(stats.get_users(db))
    data=[]
    for user in users:
        last_stat=stats.get_latest_stat_for_user(user, db)
        tmp_list=[]
        tmp_list.append(last_stat.user)
        tmp_list.append(last_stat.score)
        tmp_list.append(last_stat.general_score)
        tmp_list.append(last_stat.wins)
        tmp_list.append(last_stat.losses)
        tmp_list.append(last_stat.rounds_played)
        tmp_list.append(last_stat.kills)
        tmp_list.append(last_stat.deaths)
        tmp_list.append(get_time_str_from_int(last_stat.time_played))
        tmp_list.append(last_stat.mvp)
        tmp_list.append(last_stat.ace_squad)
        tmp_list.append(last_stat.longest_headshot)
        tmp_list.append(last_stat.kill_streak)
        tmp_list.append(last_stat.flag_caps)
        data.append(tmp_list)
    stats_df=pd.DataFrame(data)
    stats_df.columns=["user", "score", "general_score", "wins", "losses", "rounds_played", "kills", "deaths", "time_played", "mvp", "ace_squad", "longest_headshot", "kill_streak", "flag_caps"]
    return stats_df

def get_last_sunday():
    today=dt.date.today()
    last_sun = today - dt.timedelta(days=((today.weekday()+1)%7))
    last_sun=int(''.join(map(lambda x: '{0:02d}'.format(x),[last_sun.year, last_sun.month, last_sun.day, 0, 0, 0])))
    return last_sun

def get_minutes_in_time(time_int):
    total=0
    time_str=str(time_int)
    if len(time_str) >= 1:
        total += int(time_str[-2:]) / 60.0
    if len(time_str) >= 3:
        total += int(time_str[-4:-2])
    if len(time_str) >= 5:
        total += int(time_str[0:-4]) * 60
    return total

def get_time_str_from_int(time_int):
    new_str=''
    time_str=str(time_int)
    if len(time_str) >= 1:
        new_str = time_str[-2:]
    if len(time_str) >= 3:
        new_str = time_str[-4:-2] + ':' + new_str
    if len(time_str) >= 5:
        new_str = time_str[0:-4] + ':' + new_str
    return new_str

def calculate_stats(db):
    users = sorted(stats.get_users(db))
    last_sun = get_last_sunday()
    data=[]
    for user in users:
        all_stats=stats.get_stats_for_user_starting_from_date(user, last_sun, db)
        last_stat=stats.get_last_stat_before_date(user, last_sun, db)
        if not all_stats:
            # don't have an entry for this player this week
            tmp_list += [0]*13
            data.append(tmp_list)
            continue
        if not last_stat:
            # initialize to all 0's
            #last_stat=stats.Stats(user=user)
            last_stat=all_stats[0]
        tmp_list=[]
        tmp_list.append(user)
        
        rounds=all_stats[-1].rounds_played - last_stat.rounds_played
        time_played = all_stats[-1].time_played - last_stat.time_played
        score=all_stats[-1].score - last_stat.score
        general_score=all_stats[-1].general_score - last_stat.general_score
        wins=all_stats[-1].wins - last_stat.wins
        losses=all_stats[-1].losses - last_stat.losses
        kills=all_stats[-1].kills - last_stat.kills
        deaths=all_stats[-1].deaths - last_stat.deaths
        mvp=all_stats[-1].mvp - last_stat.mvp
        ace=all_stats[-1].ace_squad - last_stat.ace_squad
        flags=all_stats[-1].flag_caps - last_stat.flag_caps
        time_min=get_minutes_in_time(time_played)
        if time_min == 0:
            score_per_min=0
            general_score_per_min=0
            kills_per_min=0
            flags_capped_per_min=0
        else:
            score_per_min=score / float(time_min)
            general_score_per_min=general_score / float(time_min)
            kills_per_min=kills / float(time_min)
            flags_capped_per_min=flags / float(time_min)
        if rounds==0:
            kills_per_round=0
        else:
            kills_per_round=kills/float(rounds)
        if losses==0:
            win_loss=0
        else:
            win_loss=wins / float(losses)
        if deaths==0:
            kill_death=0
        else:
            kill_death=kills / float(deaths)
        
        tmp_list.append(rounds)
        tmp_list.append(get_time_str_from_int(time_played))
        tmp_list.append(score)
        tmp_list.append(general_score)
        tmp_list.append(score_per_min)
        tmp_list.append(general_score_per_min)
        tmp_list.append(win_loss)
        tmp_list.append(kill_death)
        tmp_list.append(kills_per_min)
        tmp_list.append(kills_per_round)
        tmp_list.append(mvp)
        tmp_list.append(ace)
        tmp_list.append(flags_capped_per_min)
        data.append(tmp_list)
    calc_stats_df = pd.DataFrame(data)
    calc_stats_df.columns=["user", "rounds", "time_played", "score", "general_score", "score_per_min", "general_score_per_min", "win_loss", "kill_death", "kills_per_min", "kills_per_round", "mvp", "ace", "flags_capped_per_min"]
    return calc_stats_df
