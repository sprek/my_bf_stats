import unittest, tempfile, sqlite3
from database import stats, create_db

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
                flag_caps=         1469)
    ]

class TestStatsDatabase(unittest.TestCase):
    def setUp(self):
        self.db_file = tempfile.NamedTemporaryFile(delete=True)
        print ("CREATED DATABASE: " + self.db_file.name)
        create_db.create_db(self.db_file.name)
        self.db = sqlite3.connect(self.db_file.name,
                                  detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
    def initialize_db(self, db):
        stats.clear_table(db)
        for stat in TEST_STATS:
            stats.insert_stat_into_db(stat, db)

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

if __name__ == '__main__':
    unittest.main(verbosity=2)
