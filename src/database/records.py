from database import data_model

class Records:
    def __init__(self, date=0, score=0, score_user="", kills=0, kills_user="", flag_caps=0, flag_caps_user=""):
        self.date = date
        self.score = score
        self.score_user = score_user
        self.kills = kills
        self.kills_user = kills_user
        self.flag_caps = flag_caps
        self.flag_caps_user = flag_caps_user

    def __eq__(self,other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        return False

    def __hash__(self):
        return hash(tuple([(self.__dict__[x]) for x in sorted(self.__dict__)]))

    def get_info(self):
        print ([str(self.__dict__[x]) for x in sorted(self.__dict__)])

def get_records_from_db(db):
    return data_model.get_objects_from_db_sorted (Records, db, "date")

def insert_record_into_db(record, db):
    data_model.insert_object_into_db(record, db)

def clear_table(db):
    data_model.clear_table(Records, db)

def check_for_date(date, db):
    result = data_model.get_object_from_db_by_key(Records, 'date', date, db)
    if result:
        return True
    return False

def print_record (record):
    print ("date           : " + str(record.date))
    print ("score          : " + str(record.score))
    print ("score_user     : " + str(record.score_user))
    print ("kills          : " + str(record.kills))
    print ("kills_user     : " + str(record.kills_user))
    print ("flag_caps      : " + str(record.flag_caps))
    print ("flag_caps_user : " + str(record.flag_caps_user))
