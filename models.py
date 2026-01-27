#models.py

from dataclasses import dataclass
from typing import Optional

@dataclass
class PlayerELO:
    # Players sheetről
    bga_name: str                  # BGA name
    name: Optional[str] = ""       # real name
    bga_id: Optional[str] = ""     # numeric ID
    active: Optional[bool] = None  # active player
    skip: Optional[bool] = None    # player to skip
    profilepic: Optional[str] = "" # profile picture url
    linkicon: Optional[str] = ""   # link icon url

    # Calculated data for the BGA-ELO sheet
    current_elo: Optional[str] = None
    last_table_date: Optional[str] = None
    last_table_id: Optional[str] = None
    top_elo: Optional[str] = None
    top_elo_date: Optional[str] = None
    top_elo_table_id: Optional[str] = None

    #Status info
    status: Optional[int] = 0 # 0: to process, 1: success, 2: error
    
