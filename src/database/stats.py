from database import data_model

class Stats:
    def __init__(self, date=0, user="", score=0, general_score=0, wins=0, losses=0, rounds_played=0, kills=0, deaths=0, time_played=0, mvp=0, ace_squad=0, longest_headshot=0, kill_streak=0, flag_caps=0):
        self.date             = date
        self.user             = user
        self.score            = score
        self.general_score    = general_score
        self.wins             = wins
        self.losses           = losses
        self.rounds_played    = rounds_played
        self.kills            = kills
        self.deaths           = deaths
        self.time_played      = time_played
        self.mvp              = mvp
        self.ace_squad        = ace_squad
        self.longest_headshot = longest_headshot
        self.kill_streak      = kill_streak
        self.flag_caps        = flag_caps

    def __eq__(self,other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        return False

    def __hash__(self):
        return hash(tuple([(self.__dict__[x]) for x in sorted(self.__dict__)]))
    
    def get_info(self):
        print ([str(self.__dict__[x]) for x in sorted(self.__dict__)])

def get_stats_from_db(db):
    return data_model.get_objects_from_db (Stats, db)

def get_latest_stat_for_user(user, db):
    results=data_model.get_objects_from_db_by_key_sorted(Stats, "user", user, "date", db)
    if results:
        return results[-1]
    return None

def get_stats_for_user_starting_from_date(user,date,db):
    results=data_model.get_objects_from_db_by_key_and_col_condition(Stats, "user", user, "date", date, ">=", db)
    if results:
        return results
    return None

def get_stats_for_user_in_date_range(user,start_date,end_date,db):
    results=data_model.get_objects_from_db_by_key_and_two_col_condition(Stats, "user", user, "date", start_date, ">=", "date", end_date, "<=", db)
    if results:
        return results
    return None

def get_last_stat_before_date(user, date, db):
    results=data_model.get_objects_from_db_by_key_and_col_condition(Stats, "user", user, "date", date, "<", db)
    if results:
        return results[-1]
    return None

def get_stats_from_db_sorted(db):
    return data_model.get_objects_from_db_sorted(Stats, db, "date")

def insert_stat_into_db(stats, db):
    data_model.insert_object_into_db(stats, db)

def check_for_date(date, db):
    result = data_model.get_object_from_db_by_key(Stats, 'date', date, db)
    if result:
        return True
    return False

def get_single_stats_from_db(date, user, db):
    #return data_model.get_object_from_db_by_key(Stats, 'date', date, db)
    return data_model.get_object_from_db_by_2key(Stats, 'date', date, 'user', user, db)

def clear_table(db):
    data_model.clear_table(Stats, db)

def update_stats(stats, db):
    data_model.update_object_in_db_by_2key(stats, "date", stats.date, "label", stats.label, db)

def delete_from_db_by_date(date, db):
    data_model.delete_by_key(Stats, "date", date, db)

def get_printable_time(date_int):
    str_date=str(date_int)
    return str_date[:4] + '-' + str_date[4:6] + '-' + str_date[6:]
#    return date_time.strftime("%Y-%m-%d %H:%M:%S")

def get_dates(db):
    return data_model.get_distinct(Stats, "date", db)

def get_latest_date(db):
    return sorted(get_dates(db))[-1]

def get_earliest_date(db):
    return sorted(get_dates(db))[0]

def get_users(db):
    return sorted(data_model.get_distinct(Stats, "user", db))

def print_stat(stat):
    print ("date              : " + str(stat.date))
    print ("user              : " + str(stat.user))
    print ("score             : " + str(stat.score))
    print ("general_score     : " + str(stat.general_score))
    print ("wins              : " + str(stat.wins))
    print ("losses            : " + str(stat.losses))
    print ("rounds_played     : " + str(stat.rounds_played))
    print ("kills             : " + str(stat.kills))
    print ("deaths            : " + str(stat.deaths))
    print ("time_played       : " + str(stat.time_played))
    print ("mvp               : " + str(stat.mvp))
    print ("ace_squad         : " + str(stat.ace_squad))
    print ("longest_headshot  : " + str(stat.longest_headshot))
    print ("kill_streak       : " + str(stat.kill_streak))
    print ("flag_caps         : " + str(stat.flag_caps))
