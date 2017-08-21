import bf_controller, os, sqlite3
from database import stats, create_db
import pandas as pd
import logging, sys
import time

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
    if not GENERATE_WITHOUT_SCRAPE:
        for i,user in enumerate(USERS):
            cur_stat=bf_controller.get_stats(user, get_db())
            #stats.print_stat(cur_stat)
            latest_stat=stats.get_latest_stat_for_user(user, db)
            if not latest_stat:
                logging.info("No entry for user: " + user + ". Creating one now")
            else:
                print ("SCORES: " + str(cur_stat.score) + " , " + str(latest_stat.score))
            if not latest_stat or (latest_stat.score != cur_stat.score):
                logging.info("Getting update for user: " + user)
                # there's been an update
                stats.insert_stat_into_db(cur_stat, db)
                got_update = True
                if i != len(USERS)-1:
                    # put a 1 sec delay between website requests
                    time.sleep(1)
    generate_webpage(db)

def generate_webpage(db):
    webpage=""
    with open (START_HTML,'r') as f:
        webpage += f.read()
    stats_df=bf_controller.get_stats_from_db(db)
    calc_stats_df=bf_controller.calculate_stats(db)
    webpage += """
<script>
$(document).ready(function() {
$('#example').DataTable({
             "scrollX": true,
             paging: false,
             fixedColumns: true
         });
$('#example2').DataTable({
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
<table id="example" class="display text-right" cellspace="0" width="100%">
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
        webpage += "<td>" + str(row.rounds) + "</td>\n"
        webpage += "<td>" + str(row.time_played) + "</td>\n"
        webpage += "<td>" + str(row.score) + "</td>\n"
        webpage += "<td>" + str(row.general_score) + "</td>\n"
        webpage += "<td>" + str(round(row.score_per_min,2)) + "</td>\n"
        webpage += "<td>" + str(round(row.general_score_per_min,2)) + "</td>\n"
        webpage += "<td>" + str(round(row.win_loss,2)) + "</td>\n"
        webpage += "<td>" + str(round(row.kill_death,2)) + "</td>\n"
        webpage += "<td>" + str(round(row.kills_per_min,2)) + "</td>\n"
        webpage += "<td>" + str(round(row.kills_per_round,2)) + "</td>\n"
        webpage += "<td>" + str(row.mvp) + "</td>\n"
        webpage += "<td>" + str(row.ace) + "</td>\n"
        webpage += "<td>" + str(round(row.flags_capped_per_min,2)) + "</td>\n"
        webpage += "</tr>\n"
    webpage += "</tbody>\n</table>\n"
    webpage += """
<h3>Overall</h3>
<table id="example2" class="display text-right" cellspace="0" width="100%">
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
        webpage += "<td>" + str(row.score) + "</td>\n"
        webpage += "<td>" + str(row.general_score) + "</td>\n"
        webpage += "<td>" + str(row.wins) + "</td>\n"
        webpage += "<td>" + str(row.losses) + "</td>\n"
        webpage += "<td>" + str(row.rounds_played) + "</td>\n"
        webpage += "<td>" + str(row.kills) + "</td>\n"
        webpage += "<td>" + str(row.deaths) + "</td>\n"
        webpage += "<td>" + str(row.time_played) + "</td>\n"
        webpage += "<td>" + str(row.mvp) + "</td>\n"
        webpage += "<td>" + str(row.ace_squad) + "</td>\n"
        webpage += "<td>" + str(row.longest_headshot) + "</td>\n"
        webpage += "<td>" + str(row.kill_streak) + "</td>\n"
        webpage += "<td>" + str(row.flag_caps) + "</td>\n"
        webpage += "</tr>\n"
    webpage += "</tbody>\n</table>\n"
    
    webpage += "</div>"
    webpage += """
    <link rel="stylesheet" type="text/css" href="js/DataTables/datatables.min.css"/>
    <script type="text/javascript" src="js/DataTables/datatables.js"></script>
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
    
