import unittest, tempfile, sqlite3
from database import stats, create_db, records
import bf_controller
from unittest.mock import patch
import datetime as dt
from freezegun import freeze_time

TEST_RECORDS = [
    records.Records (date=20170806000000,
                     score = 100,
                     score_user = "sprekk",
                     kills = 20,
                     kills_user = "LurchMD",
                     flag_caps = 20,
                     flag_caps_user = "buttDecimator"),
    records.Records (date=20170813000000,
                     score = 120,
                     score_user = "LurchMD",
                     kills = 25,
                     kills_user = "sprekk",
                     flag_caps = 16,
                     flag_caps_user = "buttDecimator"),
    records.Records (date=20170820000000,
                     score = 150,
                     score_user = "buttDecimator",
                     kills = 12,
                     kills_user = "LurchMD",
                     flag_caps = 20,
                     flag_caps_user = "sprekk, HandMade45")]

TEST_STATS = [
    stats.Stats(date=20170817121110,
                user="sprekk",
                score=            12234300,
                general_score=    2559200,
                wins=             293,
                losses=           286,
                rounds_played=    579,
                kills=            9659,
                deaths=           8190,
                time_played=      2474131,
                mvp=              14,
                ace_squad=        149,
                longest_headshot= 231,
                kill_streak=      29,
                flag_caps=        2187),
    stats.Stats(date=20170817122110,
                user="sprekk",
                score=            12235300,
                general_score=    2559300,
                wins=             294,
                losses=           286,
                rounds_played=    580,
                kills=            9666,
                deaths=           8194,
                time_played=      2475131,
                mvp=              15,
                ace_squad=        150,
                longest_headshot= 235,
                kill_streak=      29,
                flag_caps=        2189),
    stats.Stats(date=20170817122110,
                user="buttDecimator",
                score=            8524290,
                general_score=    1663320,
                wins=             223,
                losses=           219,
                rounds_played=    442,
                kills=            7098,
                deaths=           5310,
                time_played=      1942035,
                mvp=              7,
                ace_squad=        64,
                longest_headshot= 362,
                kill_streak=      30,
                flag_caps=         1469)]

class TestStatsDatabase(unittest.TestCase):
    def setUp(self):
        self.db_file = tempfile.NamedTemporaryFile(delete=True)
        print ("CREATED DATABASE: " + self.db_file.name)
        create_db.create_db(self.db_file.name)
        self.db = sqlite3.connect(self.db_file.name,
                                  detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
        
    def initialize_db(self, db):
        stats.clear_table(db)
        for stat in TEST_STATS:
            stats.insert_stat_into_db(stat, db)
        for record in TEST_RECORDS:
            records.insert_record_into_db(record, db)

    def test_stats_db(self):
        self.initialize_db(self.db)
        stats_ = stats.get_stats_from_db(self.db)
        self.assertEqual(stats_, TEST_STATS)

    def test_latest_stats(self):
        self.initialize_db(self.db)
        tmp_stat=TEST_STATS[0]
        tmp_stat.date=21170817121110
        stats.insert_stat_into_db(tmp_stat, self.db)
        stats_ = stats.get_latest_stat_for_user('sprekk', self.db)
        self.assertEqual(stats_, tmp_stat)
        stats_ = stats.get_stats_for_user_starting_from_date('sprekk',21000817121110, self.db)
        self.assertEqual(len(stats_), 1)
        self.assertEqual(stats_[0], tmp_stat)
        stats_ = stats.get_last_stat_before_date('sprekk', 21000817121110, self.db)
        self.assertEqual(stats_.date, 20170817122110)
    
    def test_records(self):
        self.initialize_db(self.db)
        recs = records.get_records_from_db(self.db)
        self.assertEqual(recs[0].date, TEST_RECORDS[0].date)

    def test_get_date_from_date_int(self):
        date_int=20170806000000
        date_obj=dt.datetime(year=2017, month=8, day=6, hour=0, minute=0, second=0)
        self.assertEqual(bf_controller.get_date_from_date_int(date_int), date_obj)

    @freeze_time('2017-08-28')
    def test_check_reset_week(self):
        self.initialize_db(self.db)
        self.assertTrue(bf_controller.check_reset_week(self.db))
        
    #@patch('bf_controller.check_reset_week')
    #def test_update_record(self, mock_check_reset_week):
    #    self.initialize_db(self.db)
    #    #print ("NOW: " + str(dt.datetime.now()))
    #    #witch patch('
    #    mock_check_reset_week.return_value = True
    #    bf_controller.update_records(self.db)
    #    #mock_now.return_value = dt.datetime(year=2017, month=8, day=27, hour=1)
    #    #self.assertTrue(bf_controller.check_reset_week(self.db))
    #    #tmp_rec=TEST_RECORDS[0]

    def test_subtract_time(self):
        time1=1222043
        time2=1212036
        print("TIME: " + str(bf_controller.subtract_times(time1, time2)))
        

if __name__ == '__main__':
    unittest.main(verbosity=2)
