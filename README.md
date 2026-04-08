# BGA Scraping

This Python script provides methods to collect data from the website "Board Game Arena" website via web scraping.<br/>
Currently, it can be used for the following purposes:<br/>
- Analyzing changes in players' ELO ratings.<br/>
- Collecting the table IDs of Carcassonne tournaments.<br/>
- Collecting detailed data on Carcassonne games (into a relational database).<br/>

## Prerequisites

The script is designed to work with the Chrome browser. It is recommended to install **Chrome for Testing** to avoid issues caused by automatic browser updates.<br/>
Install the Selenium package for Python.<br/>
A WebDriver is required for web scraping; fortunately, recent versions of Selenium automatically download and manage the correct ChromeDriver at runtime.<br/>

Rename `conf_priv_example.yml` to `conf_priv.yml` and specify the path to your 'Chrome for Testing' installation. 
In `conf_priv.yml` you must also provide your BGA username and password so the script can access data on BGA.<br/>
You can also configure the default output directory and the log file directory here. 
If no log directory is specified, output will be written to the standard output.

## How it works

The script opens a browser session and logs into BGA using the credentials provided in `conf_priv.yml` file. Then it automatically navigates to the relevant URLs, fills in the required fields and interacts with the page to collect data.

## Usage

Run the script from the command line, specifying the desired function as a parameter.
Call the available functions as described below.<br/>
**Universal optional flags:**<br/>
- `--headless`: Runs Chrome in headless mode (without a visible window).<br/>
- `--no-sandbox`: Disables Chrome’s security sandbox, which may be required in restricted environments (e.g. certain Linux servers).<br/>

```
> python bga_scraping.py function_name [function specific arguments] [--headless] [--no-sandbox]
```

### elo_hist

The script processes the game history of the specified players for a given game, tracks the ELO rating after each game, and records the dates when players reached a new personal best.  
It can also calculate the average ELO rating over a given period.  
The results can optionally be saved to a file.

```
> python bga_scraping.py elo_hist [-g <game_id/game_name>] [-p <player_name>] [-mn <minimum_date>] [-mx <maximum_date>] [-o <file_name>] [--avg]
```

**Arguments:**<br/>
- `-g <game_id/game_name>`: ID or name of the game (must be listed in conf_pub.yml); default is Carcassonne.<br/>
- `-p <player_names>`: BGA usernames of the players, separated by commas; default is the username specified in `conf_priv.yml`.<br/>
- `-mn <minimum_date>`: Start of a period (YYYY-MM-DD format).<br/>
- `-mx <maximum_date>`: End of the period (YYYY-MM-DD format).<br/>
- `-o <file_name>`: Output file name. The default location is defined in `conf_priv.yml`. If `file_name` is a dot (`.`), a default filename will be used: `[player_name]__[game_name].elo`.<br/>
**Optional flags:**<br/>
- `--avg`: Calculate of the average ELO rating.<br/>

Example:
```
> python bga_scraping.py elo_hist -g 1 -p myplayer -f . -mn 2023-01-01 -mx 2023-12-31 --avg
```

### trn_tablecoll, trn_tablelistcoll

These functions collect the table IDs of games played in a BGA tournament (`trn_tablecoll`) or multiple tournaments (`trn_tablelistcoll`), and write them to a file.

```
> python bga_scraping.py trn_tablecoll -t [tournament_id] -o [outputfile_name] [-tg group_id] [-ts stage_seq]
> python bga_scraping.py trn_tablelistcoll -i [inputfile_name] [-o outputfile_name]
```

Arguments:<br/>
- `-t tournament_id`: ID of the BGA tournament (part of the tournament page URL).<br/>
- `-o outputfile_name`: Name of the output file. The default location is specified in `conf_priv.yml`. If the file name is a dot (.), a default filename will be used: tournament_[tournament_id].lst.<br/>
- `-i inputfile_name`: Name of the input file containing tournament IDs.<br/>
- `-tg group_id`: If the tournament has multiple groups, each group has its own URL containing the group ID.<br/>
- `-ts stage_seq`: If the tournament consists of multiple stages, each stage has its own URL containing the stage number.<br/>

Example:
```
> python bga_scraping.py trn_tablelistcoll -i trn_ids.lst -o table_ids.lst
```

### carc_tableproc, carc_tablelistproc

These functions collect detailed (turn-by-turn) data from a BGA Carcassonne table (`carc_tableproc`) or from multiple tables (`carc_tablelistproc`), and store th results in a file or an SQLite database.

```
> python bga_scraping.py carc_tableproc -b [table_id] [-od output_dir] [-tc tournament_code] [-tn tournament_name] [--winbyclock] [--skipreview] [--db]
> python bga_scraping.py carc_tablelistproc -i [inputfile_name] [-od output_dir] [--winbyclock] [--skipreview] [--db]
```

**Arguments:**<br/>
- `-b table_id`: ID or BGA table (part of the table page URL).<br/>
- `-i inputfile_name`: Name of the input file containing table IDs.<br/>
- `-od output_dir`: Name of the output subdirectory under the path defined in `conf_priv.yml`. If set to a dot (.), the input file name will be used.<br/>
- `-tc tournament_code`: Replace BGA's tournament code with a custom value.<br/>
- `-tn tournament_name`: Replace BGA's tournament name with a custom value.<br/>
**Optional flags:**<br/>
- `--winbyclock`: Counts a game as a loss if a player runs out of time, regardless of the final result shown on BGA.<br/>
- `--skipreview`: Skips the game review page (no turn-by-turn data will be collected).<br/>
- `--db`: Saves data into an SQLite database defined in `config_priv.yml` (`db_path`).<br/>

Example:
```
> python bga_scraping.py carc_tablelistproc -i table_ids.lst -od . --db
```