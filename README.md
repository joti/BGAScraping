# BGA Scraping

This python script provides methods to collect data from the website "Board Game Arena" by web scraping.<br/>
Currently it can be used to analyze ELO rating progression of players.

## Prerequisites

Install the Selenium package for python.
To do web scraping, you need to download a webdriver. If you use Chrome, you need to download the compatible browser that matches the webdriver.
Rename conf_priv_example.yml to conf_priv.yml and specify the path where your Chrome and your Chromedriver is located. 
In conf_priv.yml you also need to set your BGA username and password so that the script can access the data on BGA.
You can set the default output directory here as well.

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