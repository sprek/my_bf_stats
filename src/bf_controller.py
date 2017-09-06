import requests
from bs4 import BeautifulSoup
from database import stats, records
import datetime as dt
from collections import namedtuple
import pandas as pd
import logging
import bf_time as bft

HOURS=10000
MINUTES=100

def remove_commas(comma_int):
    return int(comma_int.replace(',',''))

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
    time_played=bft.convert_time_to_int(soup.find_all(attrs={"data-stat" : "stats.timePlayed|time"})[0].get_text())
    mvp=remove_commas(soup.find_all(attrs={"data-stat" : "stats.flagDefend|nf"})[0].get_text())
    ace_squad=remove_commas(soup.find_all(attrs={"data-stat" : "stats.aceSquad|nf"})[0].get_text())
    longest_headshot=remove_commas(soup.find_all(attrs={"data-stat" : "stats.longestHeadshot|nf"})[0].get_text())
    kill_streak=remove_commas(soup.find_all(attrs={"data-stat" : "stats.killStreak|nf"})[0].get_text())
    flag_caps=remove_commas(soup.find_all(attrs={"data-stat" : "gameModes.conquest.stat.flagCaptures|nf"})[0].get_text())
    return stats.Stats(date             = bft.get_current_time(),
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
        tmp_list.append(bft.get_time_str_from_int(last_stat.time_played))
        tmp_list.append(last_stat.mvp)
        tmp_list.append(last_stat.ace_squad)
        tmp_list.append(last_stat.longest_headshot)
        tmp_list.append(last_stat.kill_streak)
        tmp_list.append(last_stat.flag_caps)
        data.append(tmp_list)
    stats_df=pd.DataFrame(data)
    stats_df.columns=["user", "score", "general_score", "wins", "losses", "rounds_played", "kills", "deaths", "time_played", "mvp", "ace_squad", "longest_headshot", "kill_streak", "flag_caps"]
    return stats_df

def unescape_spaces(word):
    return word.replace("%20"," ")

def update_max_vals(max_vals, cur_user, cur_stats):
    """ --------------------------------------------------
    max_vals - a dictionary containing the following items:
        "score"      : tuple containing: (integer of the max score, string of username)
        "kills"      : tuple containing: (integer of the max num of kills, string of username)
        "flag_caps"       : tuple contianing: (integer of max flag caps, string of username)
    cur_user - the current user to evaluate
    cur_stats - a dictionary of ["score":int, "kills":int, "flag_caps":int]

    if cur_stats[cur_stat] == max_vals[cur_stat], the user will be added to the comma separated list
    if cur_stats[cur_stat] > max_vals[cur_stat], the user will replace the comma separated list

    returns an updated max_vals dict
    """
    for key in max_vals:
        if cur_stats[key] == max_vals[key][0] and cur_stats[key] > 0:
            if cur_user not in max_vals[key][1].split(', '):
                max_vals[key][1] += ", " + cur_user
        elif cur_stats[key] > max_vals[key]:
            max_vals[key][0] = cur_stats[key]
            max_vals[key][1] = cur_user
    return max_vals

#def check_reset_week(db):
#    """ --------------------------------------------------
#    Returns True if the last entry in the records table is more than one week older than current date
#    """
#    recs = records.get_records_from_db(db)
#    if len(recs) <= 0:
#        latest_db_date = stats.get_latest_date(db)
#    else:
#        latest_db_date = bft.get_date_from_date_int(recs[-1].date)
#    if (dt.datetime.now() - latest_db_date).days > 7:
#        return True
#    return False

#def update_records(db):
#    if (check_reset_week(db)):
#        recs_df = get_weekly_record_stats(db)
#        max_recs=get_maximum_records(recs_df)
#        new_rec=records.Records(date=bft.get_last_sunday(),
#                                score_user=max_recs.score,
#                                score=max_recs[max_recs.user==max_recs.score].score.values[0],
#                                kills_user=max_recs.kills,
#                                kills=max_recs[max_recs.kills].kills.values[0],
#                                flag_caps_user=max_recs.flag_caps,
#                                flag_caps=max_recs[max_recs.flag_caps].flag_caps.values[0])
#        #records.print_record(new_rec)
#        records.insert_record_into_db(new_rec)

def get_weekly_record_stats(db):
    last_sun = bft.get_last_sunday()
    user_stats_dict={}
    for user in sorted(stats.get_users(db)):
        all_stats=stats.get_stats_for_user_starting_from_date(user, last_sun, db)
        if not all_stats or len(all_stats) == 0:
            continue
        last_stat=stats.get_last_stat_before_date(user, last_sun, db)
        if not last_stat:
            if len(all_stats)==0:
                continue
            last_stat=all_stats[0]
        tmp_list=[last_stat, *all_stats]
        user_stats_dict[user]=tmp_list
    return get_record_stats(user_stats_dict)

def stats_to_dataframe(stats_):
    """ --------------------------------------------------
    Converts a list of stats objects into a dataframe
    """
    tmp_list=[]
    for stat in stats_:
        tmp_list.append([stat.date, stat.user, stat.score, stat.general_score, stat.wins, stat.losses, stat.rounds_played, stat.kills, stat.deaths, stat.time_played, stat.mvp, stat.ace_squad, stat.longest_headshot, stat.kill_streak, stat.flag_caps])
    tmp_df = pd.DataFrame(tmp_list)
    tmp_df.columns=["date", "user", "score", "general_score", "wins", "losses", "rounds_played", "kills", "deaths", "time_played", "mvp", "ace_squad", "longest_headshot", "kill_streak", "flag_caps"]
    return tmp_df

def records_to_dataframe(records_):
    """ --------------------------------------------------
    Converts a list of records objects into a dataframe
    """
    tmp_list=[]
    for record in records_:
        tmp_list.append([record.date, record.score, record.score_user, record.kills, record.kills_user, record.flag_caps, record.flag_caps_user])
    tmp_df = pd.DataFrame(tmp_list)
    tmp_df.columns=["date", "score", "score_user", "kills", "kills_user", "flag_caps", "flag_caps_user"]
    return tmp_df

def calculate_all_weekly_records(db):
    """ --------------------------------------------------
    Calculates all the weekly records, and inserts them into the database if a
    record entry for that week doesn't exist
    """
    #all_stats=stats.get_stats_from_db_sorted(db)
    # just get the YYYMMDD
    start_date_int=int(str(stats.get_earliest_date(db))[:8]+"000000")
    last_date_int=int(str(stats.get_latest_date(db))[:8]+"000000")
    users = stats.get_users(db)

    while start_date_int <= last_date_int:
        if start_date_int >= bft.get_last_sunday():
            break
        start_date=bft.get_date_from_date_int(start_date_int)
        days_til_end_week = 7 - start_date.weekday()
        end_date=start_date + dt.timedelta(days=days_til_end_week) - dt.timedelta(seconds=1)

        if not records.check_for_date(start_date_int, db):
            user_stats_dict = {}
            for user in users:
                tmp_stats = stats.get_stats_for_user_in_date_range (user, bft.datetime_to_int(start_date),
                                                                    bft.datetime_to_int(end_date), db)
                user_stats_dict[user]=tmp_stats
            
            if len(user_stats_dict) == 0:
                continue
            record_stats=get_record_stats(user_stats_dict)
            max_recs=get_maximum_records_and_vals(record_stats)
            new_rec=records.Records(date=start_date_int, score=max_recs.score_val, score_user=max_recs.score,
                                    kills=max_recs.kills_val, kills_user=max_recs.kills,
                                    flag_caps=max_recs.flag_caps_val, flag_caps_user=max_recs.flag_caps)
            records.insert_record_into_db(new_rec, db)
        start_date_int=bft.datetime_to_int(start_date + dt.timedelta(days=days_til_end_week))

def get_all_records_from_db(db):
    """ --------------------------------------------------
    Returns a dataframe containing all of the records in the database
    """
    return records_to_dataframe(records.get_records_from_db(db))
    
        
def get_record_stats(user_stats_dict):
    #users = sorted(stats.get_users(db))
    data=[]
    NUM_ENTRIES=4
    for user in user_stats_dict.keys():
        tmp_list=[]
        tmp_list.append(unescape_spaces(user))
        
        if not user_stats_dict[user] or len(user_stats_dict[user]) <= 1:
            continue
        last_stat=user_stats_dict[user][0]
        all_stats=user_stats_dict[user][1:]
        
        max_score=0
        max_kills=0
        max_caps=0
        for i in range(len(all_stats)-1, -1, -1):
            if i == 0:
                if last_stat == all_stats[0]:
                    continue
                num_rounds=all_stats[i].rounds_played - last_stat.rounds_played
                score=(all_stats[i].general_score - last_stat.general_score) / float(num_rounds)
                num_kills=(all_stats[i].kills - last_stat.kills) / float(num_rounds)
                flag_caps=(all_stats[i].flag_caps - last_stat.flag_caps) / float(num_rounds)
            else:
                num_rounds=all_stats[i].rounds_played - all_stats[i-1].rounds_played
                score=(all_stats[i].general_score - all_stats[i-1].general_score) / float(num_rounds)
                num_kills=(all_stats[i].kills - all_stats[i-1].kills) / float(num_rounds)
                flag_caps=(all_stats[i].flag_caps - all_stats[i-1].flag_caps) / float(num_rounds)
            
            max_score=max(max_score, score)
            max_kills=max(max_kills,num_kills)
            max_caps=max(max_caps,flag_caps)
            
        tmp_list.append(max_score)
        tmp_list.append(max_kills)
        tmp_list.append(max_caps)
        
        if len(tmp_list) != NUM_ENTRIES:
            logging.error("Invalid number of entries in get_weekly_record_stats")
        data.append(tmp_list)
    if len(data) == 0:
        return None
    max_vals_df = pd.DataFrame(data)
    max_vals_df.columns=["user", "score", "kills", "flag_caps"]
    return max_vals_df

def calculate_stats(db):
    users = sorted(stats.get_users(db))
    last_sun = bft.get_last_sunday()
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
        time_played = bft.subtract_times(all_stats[-1].time_played, last_stat.time_played)
        score=all_stats[-1].score - last_stat.score
        general_score=all_stats[-1].general_score - last_stat.general_score
        wins=all_stats[-1].wins - last_stat.wins
        losses=all_stats[-1].losses - last_stat.losses
        kills=all_stats[-1].kills - last_stat.kills
        deaths=all_stats[-1].deaths - last_stat.deaths
        mvp=all_stats[-1].mvp - last_stat.mvp
        ace=all_stats[-1].ace_squad - last_stat.ace_squad
        flags=all_stats[-1].flag_caps - last_stat.flag_caps
        time_min=bft.get_minutes_in_time(bft.convert_time_to_int(time_played))
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
    tmp_df['time_played']=tmp_df['time_played'].map(bft.convert_time_to_int)
    field_vals=[]
    for i,field in enumerate(field_list):
        if len(tmp_df[field_list[i]].unique()) == 1:
            field_vals.append('')
        else:
            max_val=tmp_df[field].max(axis=0)
            all_users=tmp_df[tmp_df[field] == max_val].user.tolist()
            field_vals.append(','.join(all_users))
    max_users=MaxUsers(*field_vals)
    return max_users

def get_maximums_calc(calc_stats_df):
    field_list=["rounds", "time_played", "score", "general_score", "score_per_min", "general_score_per_min", "win_loss", "kill_death", "kills_per_min", "kills_per_round", "mvp", "ace", "flags_capped_per_min"]
    MaxUsersCalc=namedtuple("MaxUsersCalc",field_list)
    
    tmp_df=calc_stats_df.copy()
    tmp_df['time_played']=tmp_df['time_played'].map(bft.convert_time_to_int)
    field_vals=[]
    for i,field in enumerate(field_list):
        if len(tmp_df[field_list[i]].unique()) == 1:
            field_vals.append('')
        else:
            max_val=tmp_df[field].max(axis=0)
            all_users=tmp_df[tmp_df[field] == max_val].user.tolist()
            field_vals.append(','.join(all_users))
        
    max_users=MaxUsersCalc(*field_vals)
    return max_users

def get_maximum_records(records_df):
    field_list=["score", "kills", "flag_caps"]
    MaxUsersRecords=namedtuple("MaxUsersRecords",field_list)
    
    field_vals=[]
    if records_df.empty:
        return MaxUsersRecords("","","")
    for i,field in enumerate(field_list):
        if len(records_df[field_list[i]].unique()) == 1:
            field_vals.append('')
        else:
            max_val=records_df[field].max(axis=0)
            all_users=records_df[records_df[field] == max_val].user.tolist()
            field_vals.append(','.join(all_users))
    max_users=MaxUsersRecords(*field_vals)
    return max_users

def get_maximum_records_and_vals(records_df):
    field_list=["score", "kills", "flag_caps", "score_val", "kills_val", "flag_caps_val"]
    MaxUsersRecords=namedtuple("MaxUsersRecords",field_list)
    
    field_users=[]
    field_vals=[]
    for i,field in enumerate(field_list[:3]):
        if len(records_df[field_list[i]].unique()) == 1:
            field_users.append('')
        else:
            max_val=records_df[field].max(axis=0)
            all_users=records_df[records_df[field] == max_val].user.tolist()
            field_users.append(', '.join(all_users))
            field_vals.append(max_val)
    max_users=MaxUsersRecords(*field_users, *field_vals)
    return max_users

def get_max_all_records(all_records_df):
    field_list=["score", "kills", "flag_caps"]
    MaxUsersRecords=namedtuple("MaxUsersRecords",field_list)
    return MaxUsersRecords (score = all_records_df.score.max(axis=0),
                            kills = all_records_df.kills.max(axis=0),
                            flag_caps = all_records_df.flag_caps.max(axis=0))
    

