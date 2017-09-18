import bf_controller, os, sqlite3
from database import stats, create_db
import logging, sys
import time
import datetime as dt
import bf_time as bft

USERS=["sprekk", "buttDecimator", "Chairman%20OSU", "BroNCHRIST", "Cyanider",
       "desertfox0231", "LurchMD", "HandMade45", "zarathustra007", "YutYutDblYut",
       "Custom3173", "Major%20Printers"]
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
            # stats.print_stat(cur_stat)
            latest_stat=stats.get_latest_stat_for_user(user, db)
            if not latest_stat:
                logging.info("No entry for user: " + user + ". Creating one now")
            if not latest_stat or (latest_stat.score != cur_stat.score):
                logging.info("Getting update for user: " + user)
                if latest_stat.rounds_played == cur_stat.rounds_played:
                    # remove the last entry from the database
                    stats.delete_from_db_by_date(latest_stat.date, db)
                # there's been an update
                stats.insert_stat_into_db(cur_stat, db)
                got_update = True
                if i != len(USERS)-1:
                    # put a 1 sec delay between website requests
                    time.sleep(1)
    if not got_update:
        logging.info("No new games played")

    # refresh the records
    bf_controller.calculate_all_weekly_records(db)
    #bf_controller.calculate_all_weekly_ace_squads(db)
    
    generate_webpage(db)

def check_highlight(cur_user, max_user):
    if str(cur_user) in list(map(lambda x: str(x).strip(), str(max_user).split(','))):
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
    weekly_records_df = bf_controller.get_weekly_record_stats(db)
    ace_squads_df = bf_controller.get_ace_squads(db)
    max_weekly_records=bf_controller.get_maximum_records(weekly_records_df)
    all_records_df = bf_controller.get_all_records_from_db(db)
    all_records_maximums_df = bf_controller.get_max_all_records(all_records_df)
    
    webpage += """
<script>
$(document).ready(function() {

$('#apg').click(function() {
  $('#body').addClass('apg');
  $("#animate").removeClass('invis');
  $("#animate").addClass('vis');
  });

$('#bf_table_all_weekly_records').DataTable({
             "order" : [[0,"desc"]],
             paging: false,
             bFilter: false,
             bInfo: false
         });

$('#bf_table_ace').DataTable({
             "order" : [[0,"desc"]],
             paging: false,
             bFilter: false,
             bInfo: false
         });
$('#bf_table_weekly_records').DataTable({
             "order" : [[1,"desc"]],
             paging: false,
             bFilter: false,
             bInfo: false

         });
$('#bf_table').DataTable({
             "order" : [[6,"desc"]],
             "scrollX": true,
             paging: false,
             fixedColumns: true,
             bFilter: false,
             bInfo: false
         });
$('#bf_table2').DataTable({
             "scrollX": true,
             paging: false,
             fixedColumns: true,
             bFilter: false,
             bInfo: false
         });
});
</script>
"""
    webpage += """
<body id="body">
<div class="container">
<h2><a href="#" id="apg">Stats</a></h2>
<div id="animate" class="invis"><img src="static/pat_moar.jpg"></div>
"""
    webpage += """
<h3>Best Squad <small>(at least 3 people in game)</small></h3>
<table id="bf_table_ace" class="display text-right" cellspace="0">
<thead>
<tr>
"""
    display_fields=["#", "Week", "5 Top Contributors", "Total Top Squads", "Total Games"]
    webpage += '\n'.join(["<th>" + x + "</th>" for x in display_fields])
    webpage += "</tr>\n"
    webpage += "</thead>\n"
    webpage += "<tfoot>\n"
    webpage += '\n'.join(["<th>" + x + "</th>" for x in display_fields])
    webpage += "</tr>\n"
    webpage += "</tfoot>\n"
    webpage += "<tbody>\n"
    for i, row in enumerate(ace_squads_df.itertuples()):
        cur_date=bft.get_date_from_date_int(row.date)
        webpage += "<tr>\n"
        webpage += "<td>" + str(i) + "</td>\n"
        webpage += "<td>" + cur_date.strftime("%B %d") + "</td>\n"
        webpage += "<td>" + row.top_contributors + "</td>\n"
        webpage += "<td"+check_highlight(row.total_top, bf_controller.get_max_squads_total_top(ace_squads_df)) +">" + str(row.total_top) + "</td>\n"
        webpage += "<td>" + str(row.total_games) + "</td>\n"
        webpage += "</tr>\n"
    webpage += "</tbody>\n</table>\n"
        
    webpage += """
<h3>Scoreboard <small>(best in a single game)</small></h3>
<table id="bf_table_all_weekly_records" class="display text-right" cellspace="0" width="600px" style="margin: 0px">
<thead>
<tr>
"""
    display_fields=["#", "Week", "Score Winner", "Score", "Kills Winner", "Kills", "Flag Caps Winner", "Flag Caps"]
    webpage += '\n'.join(["<th>" + x + "</th>" for x in display_fields])
    webpage += "</tr>\n"
    webpage += "</thead>\n"
    webpage += "<tfoot>\n"
    webpage += "<tr>\n"
    webpage += '\n'.join(["<th>" + x + "</th>" for x in display_fields])
    webpage += "</tr>\n"
    webpage += "</tfoot>\n</thead>\n<tbody>\n"
    for i,row in enumerate(all_records_df.itertuples()):
        cur_date=bft.get_date_from_date_int(row.date)
        webpage += "<tr>\n"
        webpage += "<td>" + str(i) + "</td>\n"
        webpage += "<td>" + cur_date.strftime("%B %d") + "</td>\n"
        webpage += "<td>" + row.score_user + "</td>\n"
        webpage += "<td"+check_highlight(row.score, all_records_maximums_df.score)+">" + str(row.score) + "</td>\n"
        webpage += "<td>" + row.kills_user + "</td>\n"
        webpage += "<td"+check_highlight(row.kills, all_records_maximums_df.kills)+">" + str(row.kills) + "</td>\n"
        webpage += "<td>" + row.flag_caps_user + "</td>\n"
        webpage += "<td"+check_highlight(row.flag_caps, all_records_maximums_df.flag_caps)+">" + str(row.flag_caps) + "</td>\n"
        webpage += "</tr>\n"
    webpage += "</tbody>\n</table>\n"
    webpage += """
<h3>Weekly Records <small>(best in a single game)</small></h3>
<table id="bf_table_weekly_records" class="display text-right" cellspace="0" width="400px" style="margin: 0px">
<thead>
<tr>
"""
    display_fields=["User", "Score", "Kills", "Flag Caps"]
    webpage += '\n'.join(["<th>" + x + "</th>" for x in display_fields])
    webpage += "</tr>\n"
    webpage += "</thead>\n"
    webpage += "<tfoot>\n"
    webpage += "<tr>\n"
    webpage += '\n'.join(["<th>" + x + "</th>" for x in display_fields])
    webpage += "</tr>\n"
    webpage += "</tfoot>\n</thead>\n<tbody>\n"
    if weekly_records_df is not None and not weekly_records_df.empty and len(weekly_records_df) != 0:
        for row in weekly_records_df.itertuples():
            webpage += "<tr>\n"
            webpage += "<td>" + str(row.user) + "</td>\n"
            webpage += "<td"+check_highlight(row.user, max_weekly_records.score)+">" + str(row.score) + "</td>\n"
            webpage += "<td"+check_highlight(row.user, max_weekly_records.kills)+">" + str(row.kills) + "</td>\n"
            webpage += "<td"+check_highlight(row.user, max_weekly_records.flag_caps)+">" + str(row.flag_caps) + "</td>\n"
            webpage += "</tr>\n"
    webpage += "</tbody>\n</table>\n"
    webpage += """
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
    
