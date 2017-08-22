import bf_controller, os, sqlite3
from database import stats, create_db
import pandas as pd
import logging, sys
import time
import datetime as dt

USERS=['sprekk','buttDecimator', "Chairman%20OSU", "BroNCHRIST", "Cyanider",
       "desertfox0231", "LurchMD", "HandMade45", "zarathustra007","YutYutDblYut",
       "Custom3173","Major%20Printers"]
DATABASE=create_db.DATABASE
START_HTML="start_html.html"

OUT_HTML="../stats.html"

GENERATE_WITHOUT_SCRAPE=False

def get_usage():
    return "Usage: battlefield.py [-g]"

def get_help():
    msg = get_usage() + "\n"
    msg += """
Options:
   -g        Generates the battlefield web page without scraping
"""

def get_options():
    global GENERATE_WITHOUT_SCRAPE
    if len(sys.argv) > 1:
        # check that the only option is -g
        if any([x not in ['-g'] for x in sys.argv[1:]]):
            print(get_usage())
            sys.exit(1)
    if '-g' in sys.argv[1:]:
        GENERATE_WITHOUT_SCRAPE = True

def get_update(db):
    got_update=False
    if not GENERATE_WITHOUT_SCRAPE:
        for i,user in enumerate(USERS):
            cur_stat=bf_controller.get_stats(user, get_db())
            #stats.print_stat(cur_stat)
            latest_stat=stats.get_latest_stat_for_user(user, db)
            if not latest_stat:
                logging.info("No entry for user: " + user + ". Creating one now")
            if not latest_stat or (latest_stat.score != cur_stat.score):
                logging.info("Getting update for user: " + user)
                # there's been an update
                stats.insert_stat_into_db(cur_stat, db)
                got_update = True
                if i != len(USERS)-1:
                    # put a 1 sec delay between website requests
                    time.sleep(1)
    if not got_update:
        logging.info("No new games played")
    generate_webpage(db)

def check_highlight(cur_user, max_user):
    if cur_user == max_user:
        return " class=\"dt_highlight\""
    return ""
    
def generate_webpage(db):
    webpage=""
    with open (START_HTML,'r') as f:
        webpage += f.read()
    stats_df=bf_controller.get_stats_from_db(db)
    calc_stats_df=bf_controller.calculate_stats(db)
    max_users_calc=bf_controller.get_maximums_calc(calc_stats_df)
    max_users=bf_controller.get_maximums(stats_df)
    webpage += """
<script>
$(document).ready(function() {
$('#bf_table').DataTable({
             "scrollX": true,
             paging: false,
             fixedColumns: true
         });
$('#bf_table2').DataTable({
             "scrollX": true,
             paging: false,
             fixedColumns: true
         });
});
</script>
"""
    webpage += """
<body>
<div class="container">
<h2>Stats</h2>
<h3>Weekly</h3>
<table id="bf_table" class="display text-right" cellspace="0" width="100%">
<thead>
<tr>
"""
    display_fields=["User", "Rounds", "Time Played", "Score", "General Score", "Score/Min", "General Score/Min", "Win/Loss", "Kill/Death", "Kills/Min", "Kills/Round", "MVP", "Ace Squad", "Flags Capped/Minute"]
    webpage += '\n'.join(["<th>" + x + "</th>" for x in display_fields])
    webpage += "</tr>\n"
    webpage += "</thead>\n"
    webpage += "<tfoot>\n"
    webpage += '\n'.join(["<th>" + x + "</th>" for x in display_fields])
    webpage += "</tr>\n"
    webpage += "</tfoot>\n"
    webpage += "<tbody>\n"
    for row in calc_stats_df.itertuples():
        webpage += "<tr>\n"
        webpage += "<td>" + str(row.user) + "</td>\n"
        webpage += "<td"+check_highlight(row.user, max_users_calc.rounds)+">" + str(row.rounds) + "</td>\n"
        webpage += "<td"+check_highlight(row.user, max_users_calc.time_played)+">" + str(row.time_played) + "</td>\n"
        webpage += "<td"+check_highlight(row.user, max_users_calc.score)+">" + str(row.score) + "</td>\n"
        webpage += "<td"+check_highlight(row.user, max_users_calc.general_score)+">" + str(row.general_score) + "</td>\n"
        webpage += "<td"+check_highlight(row.user, max_users_calc.score_per_min)+">" + str(round(row.score_per_min,2)) + "</td>\n"
        webpage += "<td"+check_highlight(row.user, max_users_calc.general_score_per_min)+">" + str(round(row.general_score_per_min,2)) + "</td>\n"
        webpage += "<td"+check_highlight(row.user, max_users_calc.win_loss)+">" + str(round(row.win_loss,2)) + "</td>\n"
        webpage += "<td"+check_highlight(row.user, max_users_calc.kill_death)+">" + str(round(row.kill_death,2)) + "</td>\n"
        webpage += "<td"+check_highlight(row.user, max_users_calc.kills_per_min)+">" + str(round(row.kills_per_min,2)) + "</td>\n"
        webpage += "<td"+check_highlight(row.user, max_users_calc.kills_per_round)+">" + str(round(row.kills_per_round,2)) + "</td>\n"
        webpage += "<td"+check_highlight(row.user, max_users_calc.mvp)+">" + str(row.mvp) + "</td>\n"
        webpage += "<td"+check_highlight(row.user, max_users_calc.ace)+">" + str(row.ace) + "</td>\n"
        webpage += "<td"+check_highlight(row.user, max_users_calc.flags_capped_per_min)+">" + str(round(row.flags_capped_per_min,2)) + "</td>\n"
        webpage += "</tr>\n"
    webpage += "</tbody>\n</table>\n"
    webpage += """
<h3>Overall</h3>
<table id="bf_table2" class="display text-right" cellspace="0" width="100%">
<thead>
<tr>
"""
    display_fields=["User", "Score", "General Score", "Wins", "Losses", "Rounds Played", "Kills",
                    "Deaths", "Time Played", "MVP", "Ace Squad", "Longest Headshot",
                    "Kill Streak", "Flags Capped"]
    webpage += '\n'.join(["<th>" + x + "</th>" for x in display_fields])
    webpage += "</tr>\n"
    webpage += "</thead>\n"
    webpage += "<tfoot>\n"
    webpage += '\n'.join(["<th>" + x + "</th>" for x in display_fields])
    webpage += "</tr>\n"
    webpage += "</tfoot>\n"
    webpage += "<tbody>\n"
    for row in stats_df.itertuples():
        webpage += "<tr>\n"
        webpage += "<td>" + str(row.user) + "</td>\n"
        webpage += "<td"+check_highlight(row.user, max_users.score           )+">" + str(row.score) + "</td>\n"
        webpage += "<td"+check_highlight(row.user, max_users.general_score   )+">" + str(row.general_score) + "</td>\n"
        webpage += "<td"+check_highlight(row.user, max_users.wins            )+">" + str(row.wins) + "</td>\n"
        webpage += "<td"+check_highlight(row.user, max_users.losses          )+">" + str(row.losses) + "</td>\n"
        webpage += "<td"+check_highlight(row.user, max_users.rounds_played   )+">" + str(row.rounds_played) + "</td>\n"
        webpage += "<td"+check_highlight(row.user, max_users.kills           )+">" + str(row.kills) + "</td>\n"
        webpage += "<td"+check_highlight(row.user, max_users.deaths          )+">" + str(row.deaths) + "</td>\n"
        webpage += "<td"+check_highlight(row.user, max_users.time_played     )+">" + str(row.time_played) + "</td>\n"
        webpage += "<td"+check_highlight(row.user, max_users.mvp             )+">" + str(row.mvp) + "</td>\n"
        webpage += "<td"+check_highlight(row.user, max_users.ace_squad       )+">" + str(row.ace_squad) + "</td>\n"
        webpage += "<td"+check_highlight(row.user, max_users.longest_headshot)+">" + str(row.longest_headshot) + "</td>\n"
        webpage += "<td"+check_highlight(row.user, max_users.kill_streak     )+">" + str(row.kill_streak) + "</td>\n"
        webpage += "<td"+check_highlight(row.user, max_users.flag_caps       )+">" + str(row.flag_caps) + "</td>\n"
        webpage += "</tr>\n"
    webpage += "</tbody>\n</table>\n"
    webpage += "<div class=\"row\">\n<hr>\n"
    
    cur_time=(dt.datetime.utcnow() - dt.timedelta(minutes=60*4)).strftime("%Y-%m-%d %H:%M")
    webpage += "<p class=\"text-right\">Updated: " + cur_time + "</p>\n"
    webpage += "</div>"
    webpage += """

</div>

    <link rel="stylesheet" type="text/css" href="static/js/DataTables/datatables.min.css"/>
    <script type="text/javascript" src="static/js/DataTables/datatables.js"></script>
"""
    with open (OUT_HTML, "w") as f:
        f.write(webpage)
    
        #for col in row:
        #    webpage += row['score']

def setup_logging():
    log_format='%(asctime)s [%(levelname)-5.5s] %(message)s'
    date_format='%Y-%m-%d %H:%M:%S'
    logging.basicConfig(filename='bfstats.log',
                        format=log_format,
                        datefmt=date_format,
                        level=logging.INFO)

    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(logging.Formatter(log_format))
    logging.getLogger().addHandler(ch)

def get_db():
    if not os.path.isfile(DATABASE):
        create_db.create_db()
        #print ("Database not found")
        #sys.exit(1)
    db = sqlite3.connect(DATABASE, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
    return db

if __name__ == "__main__":
    setup_logging()
    get_options()
    get_update(get_db())
    
