# sheet_utils.py

import gspread
import time
from datetime import datetime, date, timezone
from google.oauth2.service_account import Credentials
from models import PlayerELO
from config import GOOGLE

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

def find_player_by_bga_name(players, bga_name):
    for p in players:
        if p.bga_name == bga_name:
            return p
    return None

def open_spreadsheet():
    keyfile = GOOGLE['keyfile']
    spreadsheet_name = GOOGLE['spreadsheet_name']
    
    creds = Credentials.from_service_account_file(
        keyfile,
        scopes=SCOPES,
    )
    gc = gspread.authorize(creds)
    return gc.open(spreadsheet_name)

def read_players():
    sh = open_spreadsheet()

    # Players sheet
    ws = sh.worksheet("Players")
    rows = ws.get_all_values()
    
    if len(rows) < 2:
        return []

    header = [h.strip().lower() for h in rows[0]]

    def col_index(*names):
        for n in names:
            if n.lower() in header:
                return header.index(n.lower())
        return None

    i_name = col_index("név", "nev", "name")
    i_bga  = col_index("bga", "bga-név", "bga név", "bga_nev", "bga name")
    i_id   = col_index("id", "bga id", "bga_id", "player id")
    i_skip = col_index("skip")

    players: List[PlayerELO] = []
    for row in rows[1:]:
        if not any(row):
            continue

        if i_name is not None and i_name < len(row):
            name = row[i_name].strip()
        else:
            name = ""

        if i_bga is not None and i_bga < len(row):
            bga_name = row[i_bga].strip()
        else:
            bga_name = ""

        if i_id is not None and i_id < len(row):
            bga_id = row[i_id].strip()
        else:
            bga_id = ""

        if bga_name == "" and bga_id == "":
            continue

        if i_skip is not None and i_skip < len(row):
            skip = (row[i_skip].strip() == "1")
        else:
            skip = False

        players.append(PlayerELO(
            name = name,
            bga_name = bga_name,
            bga_id = bga_id,
            skip = skip
        ))

    # BGA-ELO sheet tartalmával kiegészítjük a játékosok adatait
    ws_elo = sh.worksheet("BGA-ELO")
    rows_elo = ws_elo.get_all_values()

    if len(rows_elo) < 2:
        return players

    header = [h.strip().lower() for h in rows_elo[0]]

    i_bga  = col_index("bga", "bga name", "name")
    i_id   = col_index("id", "bga id", "bga_id", "player id")
    i_current_elo = col_index("current elo","elo")
    i_last_table_date = col_index("date of last game","date of last table")
    i_last_table_id = col_index("table of last game","id of last game","id of last table")
    i_top_elo = col_index("top elo","max elo","highest elo")
    i_top_elo_date = col_index("date of top elo","date of max elo","date of highest elo")
    i_top_elo_table_id = col_index("table of top elo","table of max elo","table of highest elo")
    i_active = col_index("active")
    i_linkicon = col_index("link icon")
    i_profilepic = col_index("profile picture","avatar")

    for row in rows_elo[1:]:
        if not any(row):
            continue

        if i_bga is not None and i_bga < len(row):
            bga_name = row[i_bga].strip()
        else:
            bga_name = ""

        if i_id is not None and i_id < len(row):
            bga_id = row[i_id].strip()
        else:
            bga_id = ""

        if bga_name == "" and bga_id == "":
            continue

        player = find_player_by_bga_name(players, bga_name)
        if player is not None:

            if i_current_elo is not None and i_current_elo < len(row):
                player.current_elo = row[i_current_elo].strip()
            if i_last_table_date is not None and i_last_table_date < len(row):
                player.last_table_date = row[i_last_table_date].strip()
            if i_last_table_id is not None and i_last_table_id < len(row):
                player.last_table_id = row[i_last_table_id].strip()
            if i_top_elo is not None and i_top_elo < len(row):
                player.top_elo = row[i_top_elo].strip()
            if i_top_elo_date is not None and i_top_elo_date < len(row):
                player.top_elo_date = row[i_top_elo_date].strip()
            if i_top_elo_table_id is not None and i_top_elo_table_id < len(row):
                player.top_elo_table_id = row[i_top_elo_table_id].strip()
            if i_active is not None and i_active < len(row):
                player.active = (row[i_active].strip() == "1")
            if i_linkicon is not None and i_linkicon < len(row):
                player.linkicon = row[i_linkicon].strip()
            if i_profilepic is not None and i_profilepic < len(row):
                player.profilepic = row[i_profilepic].strip()

    players_copy = players.copy()
    for p in players_copy:
        if p.last_table_date is None and p.skip:
            print(p.bga_name + " skipped")
            players.remove(p)

    return players

def write_bga_elo(players: List[PlayerELO]):
    # Columns: Name | Id | Top ELO | Date of top ELO | Table of top ELO | Current ELO | Date of last game | ID of last game | Active | Link icon | Profile picture

    sh = open_spreadsheet()
    ws = sh.worksheet("BGA-ELO")

    header = [
        "Name",
        "Id",
        "Top ELO",
        "Date of top ELO",
        "Table of top ELO",
        "Current ELO",
        "Date of last game",
        "ID of last game",
        "Active",
        "Link icon",
        "Profile picture"
    ]

    rows = [header]

    for p in players:
        rows.append([
            p.bga_name if p.bga_name is not None else "",
            p.bga_id if p.bga_id is not None else "",
            p.top_elo if p.top_elo is not None else "",
            p.top_elo_date if p.top_elo_date is not None else "",
            p.top_elo_table_id if p.top_elo_table_id is not None else "",
            p.current_elo if p.current_elo is not None else "",
            p.last_table_date if p.last_table_date is not None else "",
            p.last_table_id if p.last_table_id is not None else "",
            "1" if p.active else "0",
            p.linkicon if p.linkicon is not None else "",
            p.profilepic if p.profilepic is not None else ""
        ])

    ws.clear()
    ws.update("A1", rows, value_input_option="USER_ENTERED")


def read_meta_value(key: str):
    sh = open_spreadsheet()
    ws = sh.worksheet("Meta")

    rows = ws.get_all_values()

    # Header: Key | Value
    for row in rows[1:]:
        if len(row) >= 2 and row[0] == key:
            return row[1]

    return None
    

def write_meta_last_run( success,
                         error = "" ):

    sh = open_spreadsheet()
    ws = sh.worksheet("Meta")

    # UTC timestamp
    now_utc = datetime.now(timezone.utc)
    unix_ts = int(now_utc.timestamp())

    # Local time
    now_local = datetime.now()
    display = now_local.strftime("%Y.%m.%d. %H:%M:%S")

    # For BGA filter
    date_str = now_local.strftime("%Y.%m.%d")

    rows = [
        ["last_run_tst", unix_ts],
        ["last_run_display", display],
        ["last_run_error", error],
    ]

    ws.update("A2:B4", rows, value_input_option="USER_ENTERED")

    if success == True:
        rows = [
            ["last_success_tst", unix_ts],
            ["last_success_display", display],
            ["last_success_date", date_str],
        ]

        ws.update("A5:B7", rows, value_input_option="USER_ENTERED")
        
