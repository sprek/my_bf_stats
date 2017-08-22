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
    """ --------------------------------------------------
    Converts a string in format H:MM:SS to an integer in 
    the format: HMMSS
    """
    return int(str(time_str).replace(':',''))

    #if str(time_str).strip() == '0':
    #    return 0
    #time=0
    #time_split=time_str.split(":")
    #if len(time_split) ==3:
    #    time += int(time_split[0]) * HOURS
    #    time += int(time_split[1]) * MINUTES
    #    time += int(time_split[2])
    #elif len(time_split) == 2:
    #    time += int(time_split[0]) * MINUTES
    #    time += int(time_split[1])
    #else:
    #    time = int(time_str)
    #return time

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
    time_played=convert_time_to_int(soup.find_all(attrs={"data-stat" : "stats.timePlayed|time"})[0].get_text())
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
        tmp_list.append(unescape_spaces(last_stat.user))
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
    """ --------------------------------------------------
    Converts a time integer in the format HMMSS to a float
    equal to the number of minutes
    """
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
    """ --------------------------------------------------
    Converts a time integer in the format HMMSS to a string
    in the format: H:MM:SS
    """
    new_str=''
    time_str=str(time_int)
    if len(time_str) >= 1:
        new_str = time_str[-2:]
    if len(time_str) >= 3:
        new_str = time_str[-4:-2] + ':' + new_str
    if len(time_str) >= 5:
        new_str = time_str[0:-4] + ':' + new_str
    return new_str

def get_timedelta_from_time_str(time_str):
    """ --------------------------------------------------
    Converts a time string in the format H:MM:SS to a 
    timedelta object
    """
    #print ("TIME STR: " + time_str)
    td=dt.timedelta(minutes=get_minutes_in_time(convert_time_to_int(time_str)))
    #print ("TD: " + str(td))
    return td

def get_time_str_from_timedelta(td):
    hours, remainder = divmod(td.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return_time=""
    if seconds > 0:
        return_time='{0:02d}'.format(seconds)
    if minutes > 0:
        return_time='{0:02d}'.format(minutes) + ":" + return_time
    if hours > 0:
        return_time=str(hours) + ":" + return_time
    return return_time

def subtract_times(time_int_a, time_int_b):
    diff_time=get_timedelta_from_time_str(get_time_str_from_int(time_int_a)) - \
               get_timedelta_from_time_str(get_time_str_from_int(time_int_b))
    return get_time_str_from_timedelta (diff_time)

def unescape_spaces(word):
    return word.replace("%20"," ")

def calculate_stats(db):
    users = sorted(stats.get_users(db))
    last_sun = get_last_sunday()
    data=[]
    NUM_ENTRIES=14
    for user in users:
        all_stats=stats.get_stats_for_user_starting_from_date(user, last_sun, db)
        last_stat=stats.get_last_stat_before_date(user, last_sun, db)
        tmp_list=[]
        tmp_list.append(unescape_spaces(user))
        
        if not all_stats:
            # don't have an entry for this player this week
            #logging.info("Don't have entry for " + user + " this week")
            tmp_list += [0]*(NUM_ENTRIES-1)
            data.append(tmp_list)
            continue
        if not last_stat:
            if len(all_stats)==1:
                # only have a single entry and no entry from last week
                # just set everything to 0
                tmp_list += [0]*(NUM_ENTRIES-1)
                data.append(tmp_list)
                continue
            # don't have an entry for last week
            # use the first stat of this week
            last_stat=all_stats[0]
        
        rounds=all_stats[-1].rounds_played - last_stat.rounds_played
        time_played = subtract_times(all_stats[-1].time_played, last_stat.time_played)
        score=all_stats[-1].score - last_stat.score
        general_score=all_stats[-1].general_score - last_stat.general_score
        wins=all_stats[-1].wins - last_stat.wins
        losses=all_stats[-1].losses - last_stat.losses
        kills=all_stats[-1].kills - last_stat.kills
        deaths=all_stats[-1].deaths - last_stat.deaths
        mvp=all_stats[-1].mvp - last_stat.mvp
        ace=all_stats[-1].ace_squad - last_stat.ace_squad
        flags=all_stats[-1].flag_caps - last_stat.flag_caps
        time_min=get_minutes_in_time(convert_time_to_int(time_played))
        score_per_min=score / float(time_min)
        general_score_per_min=general_score / float(time_min)
        kills_per_min=kills / float(time_min)
        flags_capped_per_min=flags / float(time_min)
        kills_per_round=kills/float(max(rounds,1))
        win_loss=wins / float(max(losses,1))
        kill_death=kills / float(max(deaths,1))
        
        tmp_list.append(rounds)
        tmp_list.append(time_played)
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
        if len(tmp_list) != NUM_ENTRIES:
            logging.error("Invalid number of entries in calculate_stats")
        data.append(tmp_list)
    calc_stats_df = pd.DataFrame(data)
    calc_stats_df.columns=["user", "rounds", "time_played", "score", "general_score", "score_per_min", "general_score_per_min", "win_loss", "kill_death", "kills_per_min", "kills_per_round", "mvp", "ace", "flags_capped_per_min"]
    return calc_stats_df

def get_maximums(stats_df):
    field_list=["score", "general_score", "wins", "losses", "rounds_played", "kills", "deaths", "time_played", "mvp", "ace_squad", "longest_headshot", "kill_streak", "flag_caps"]
    MaxUsers=namedtuple("MaxUsers",field_list)
    tmp_df=stats_df.copy()
    tmp_df['time_played']=tmp_df['time_played'].map(convert_time_to_int)
    field_vals=[]
    for i,field in enumerate(field_list):
        if len(tmp_df[field_list[i]].unique()) == 1:
            field_vals.append('')
        else:
            field_vals.append(tmp_df.iloc[tmp_df[field].argmax].user)
    max_users=MaxUsers(*field_vals)
    return max_users

def get_maximums_calc(calc_stats_df):
    field_list=["rounds", "time_played", "score", "general_score", "score_per_min", "general_score_per_min", "win_loss", "kill_death", "kills_per_min", "kills_per_round", "mvp", "ace", "flags_capped_per_min"]
    MaxUsersCalc=namedtuple("MaxUsersCalc",field_list)
    
    tmp_df=calc_stats_df.copy()
    tmp_df['time_played']=tmp_df['time_played'].map(convert_time_to_int)
    field_vals=[]
    for i,field in enumerate(field_list):
        if len(tmp_df[field_list[i]].unique()) == 1:
            field_vals.append('')
        else:
            field_vals.append(tmp_df.iloc[tmp_df[field].argmax].user)
        
    max_users=MaxUsersCalc(*field_vals)
    return max_users
