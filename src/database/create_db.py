import sqlite3

DATABASE = 'bfstats.db'

def create_db(filename=DATABASE):
    con = sqlite3.connect(filename)
    with con:
        cur = con.cursor()
        cur.execute("DROP TABLE IF EXISTS stats")
        cur.execute("CREATE TABLE stats (date INT, user TEXT, score INT, general_score INT, wins INT, losses INT, rounds_played INT, kills INT, deaths INT, time_played INT, mvp INT, ace_squad INT, longest_headshot INT, kill_streak INT, flag_caps INT )")
        cur.execute("DROP TABLE IF EXISTS records")
        cur.execute("CREATE TABLE records (date INT, score INT, score_user TEXT, kills INT, kills_user TEXT, flag_caps INT, flag_caps_user TEXT)")
        cur.execute("DROP TABLE IF EXISTS squad")
        cur.execute("CREATE TABLE squad (date INT, top_contributors TEXT, total_top INT, total_games INT)")
    con.close()

    
if __name__ == '__main__':
    create_db()
