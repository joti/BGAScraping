# BGA Scraping

This python script provides methods to collect data from the website "Board Game Arena" by web scraping.<br/>
Currently, it can be used for the following purposes:<br/>
- Analyzing changes in players' ELO ratings.<br/>
- Collecting the table IDs of a Carcassonne tournament.<br/>
- Collecting data on Carcassonne games (into a relational database).<br/>

## Prerequisites

The script is prepared for use with the Chrome browser. Install 'Chrome for Testing' to avoid problems with automatic updates of the browser.<br/>
Install the Selenium package for python.
To do web scraping, we need a webdriver. Fortunately, the current version of Selenium gets the correct Chromedriver for us at runtime.<br/>

Rename conf_priv_example.yml to conf_priv.yml and specify the path where your 'Chrome for Testing' is located. 
In conf_priv.yml you also need to set your BGA username and password so that the script can access the data on BGA.
You can set the default output directory and the logfile directory here as well.

## How it works

The script opens up a browser window, and logs you in to BGA with the username and password you provided in conf_priv.yml file. Then it automatically opens the appropriate urls, fills the necessary fields and clicks on buttons to collect data.

## Usage

Run the script from the command line. Set the name of the desired function in parameter.
Call the available functions as described below.

```
> python bga_scraping.py function_name [other parameters]
```

### elo_hist

The script runs through the game history of the given players for a specified game, checks the ELO rating after each game, and collects the dates when the players broke their personal best. 
The script can also calculate the average ELO rating of one or more players within a given period.
The result can also be saved to a file.

```
> python bga_scraping.py elo_hist -g [game_id/game_name] -p [player_name] [-mn minimum_date] [-mx maximum_date] [-f file_name] [--avg]
```

Arguments:<br/>
-g game_id/game_name: id or name of the game (should be listed in conf_pub.yml); default is Carcassonne.<br/>
-p player_names: BGA name of the players, separated by comma; default is the username provided in conf_priv.yml.<br/>
-mn minimum_date: start of a period in YYYY-MM-DD format.<br/>
-mx maximum_date: end of the period in YYYY-MM-DD format.<br/>
-f file_name: save the results in a file; default location is the path given in conf_priv.yml; if file_name is a dot (.) then a default filename will be: [player_name]__[game_name].elo<br/>
Optional flags:<br/>
--avg: run calculation of the average ELO rating<br/>

Example:
```
> python bga_scraping.py elo_hist -g 1 -p myplayer -f . -mn 2023-01-01 -mx 2023-12-31 --avg
```

### trn_tablecoll, trn_tablelistcoll

The script collects the table ids of the games played in a BGA tournament (trn_tablecoll) or in several tournaments (trn_tablelistcoll), and writes them into a file.

```
> python bga_scraping.py trn_tablecoll -t [tournament_id] -f [file_name] [-tg group_id] [-ts stage_seq]
> python bga_scraping.py trn_tablelistcoll -if [inputfile_name] [-f outputfile_name]
```

Arguments:<br/>
-t tournament_id: id or BGA tournament (part of the URL of the tournament page).<br/>
-f file_name: name of the output file; default location is the path given in conf_priv.yml; if file_name is a dot (.) then a default filename will be: tournament_[tournament_id].lst<br/>
-if inputfile_name: name of the input file containing tournament ids.<br/>
-tg group_id: if the tournament has multiple groups, each group has its own URL, which includes the id of the group.<br/>
-ts stage_seq: if the tournament consists of multiple stages, each stage has its own URL, which includes the stage number.<br/>

Example:
```
> python bga_scraping.py trn_tablelistcoll -if wtcoc_r4.txt -f wtcoc_r4_tables.lst
```