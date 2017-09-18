from database import data_model

class Squad:
    def __init__(self, date=0, top_contributors="", total_top=0, total_games=0):
        self.date = date
        self.top_contributors = top_contributors
        self.total_top = total_top
        self.total_games = total_games

    def __eq__(self,other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        return False

    def __hash__(self):
        return hash(tuple([(self.__dict__[x]) for x in sorted(self.__dict__)]))

    def get_info(self):
        print ([str(self.__dict__[x]) for x in sorted(self.__dict__)])

def get_squad_from_db(db):
    return data_model.get_objects_from_db_sorted (Squad, db, "date")

def insert_squad_into_db(squad, db):
    data_model.insert_object_into_db(squad, db)

def clear_table(db):
    data_model.clear_table(Squad, db)

def check_for_date(date, db):
    result = data_model.get_object_from_db_by_key(Squad, 'date', date, db)
    if result:
        return True
    return False

def get_dates(db):
    return data_model.get_distinct(Squad, "date", db)

def get_earliest_date(db):
    dates = get_dates(db)
    if not dates:
        return 0
    return sorted(dates)[0]

def get_latest_date(db):
    dates = get_dates(db)
    if not dates:
        return 0
    return sorted(dates)[-1]

def print_squad (squad):
    print ("date             : " + str(squad.date            ))
    print ("top_contributors : " + str(squad.top_contributors))
    print ("total_top        : " + str(squad.total_top       ))
    print ("total_games      : " + str(squad.total_games     ))
