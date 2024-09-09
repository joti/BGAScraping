# BGA_Scraping.py
# Python program to get data from BGA

import time
import sys
import yaml

from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.common.exceptions import TimeoutException

# terminology:
# game = the type of board game
# table = one particular match of a given game
class tableClass :
    def __init__(self,seq,tableId,endDate,newELO,unranked,newRecord,newRecByDay):
        self.seq=seq
        self.tableId=tableId
        self.endDate=endDate
        self.newELO=newELO
        self.unranked=unranked
        self.newRecord = newRecord
        self.newRecByDay = newRecByDay

def exit_program():
    print("Exiting...")
    sys.exit(0)

def login():

    login_link = bga_data['urls']['login']
    print(login_link);
    driver.get(login_link)

    username = bga_login['user']
    pw = bga_login['password']
        
    wait.until(EC.visibility_of_element_located((By.ID, "username_input")))
    it_username = driver.find_element(By.ID, "username_input")
    it_username.send_keys(username)

    wait.until(EC.visibility_of_element_located((By.ID, "password_input")))
    password = driver.find_element(By.ID, "password_input")
    password.send_keys(pw)

    wait.until(EC.visibility_of_element_located((By.ID, "submit_login_button")))
    driver.find_element(By.ID, "submit_login_button").click()

def elo_hist():

    ROW_LIMIT = 200

    #2nd param : id or name of the game
    #3rd param : player name
    #4th param : name of file to export data
    game_name = 'unknown'
    game_id = '0'
    if argnum > 2 :
        gamearg = sys.argv[2]

        for k, v in bga_data['gameids'].items():
            if gamearg.upper() == k.upper() or gamearg == str(v) :
                game_id = str(v)
                game_name = k
    else :
        game_id = '1'
        game_name = 'Carcassonne'
    print(game_id + " - " + game_name)
        
    if argnum > 3 :
        player_name = sys.argv[3]
    else :
        player_name = bga_login['user']
    print('ELO progress of %s in the game %s:' % (player_name, game_name))

    if argnum > 4 :
        file_name = sys.argv[4]
        if file_name == "-":
            file_name = (player_name + "__" + game_name).lower().replace(" ", "_") + ".elo"
    else :
        file_name = ""

    # we need the player's id in BGA
    login()
    time.sleep(1)

    start_millisec = int(time.time() * 1000)

    community_link = bga_data['urls']['community']
    driver.get(community_link)
    time.sleep(1)

    wait.until(EC.visibility_of_element_located((By.ID, "findplayer")))
    it_findplayer = driver.find_element(By.ID, "findplayer")
    it_findplayer.send_keys(player_name)
    it_findplayer.send_keys(Keys.ENTER)

    try:
        wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="elo_game_' + game_id + '"]')))
    except TimeoutException:
        print("Player %s has not played the game %s yet." % (player_name, game_name))
        exit_program()

    player_url = driver.current_url
    print("The current url is: "+str(player_url))

    player_id = player_url[(player_url.find('='))+1:]
    print("Player id is: "+player_id)    

    # game history of the player can be found here:
    # https://boardgamearena.com/gamestats?player=88033752&game_id=1
    # with further parameters (filtering by opponent and end date)
    # https://boardgamearena.com/gamestats?player=85374022&opponent_id=0&game_id=1&end_date=1719784800&finished=1

    current_date = datetime.now() + timedelta(days=1)

    needSearch = True
    tableSeq = 0
    tableIdSet = {}
    tableList = []
    gameStatsLoadTotalTime = 0
    gameStatsProcTotalTime = 0
    
    while needSearch :
        # convert date to lixux timestamp
        unix_timestamp = datetime.timestamp(current_date)
        end_timestamp = str(int(unix_timestamp))

        gamestats_url = (bga_data['urls']['gamestatsfull'].
                         replace('{p1}', player_id).
                         replace('{p2}', game_id).
                         replace('{p3}', '0').
                         replace('{p4}', end_timestamp))
        print(gamestats_url)

        millisec1 = int(time.time() * 1000)
        
        trycount = 0
        needSearch = False
        success = False
        while not success:
            try:
                if trycount == 0:
                    driver.get(gamestats_url)
                else:    
                    driver.refresh()
                    print("refresh")
                wait.until(EC.visibility_of_element_located((By.XPATH, "//table[@id='gamelist_inner']")))
                success = True
            except TimeoutException:
                time.sleep(1)
                trycount += 1
                if trycount == 3:
                    print("Cannot load gamestat page.")
                    exit_program()            

        #print("Gamestats page loaded.")

        rownum = len(driver.find_elements(by=By.XPATH, value="//table[@id='gamelist_inner']/tr"))
        time.sleep(0.5)

        trycount = 0
        trycause = ""

        # pressing "more tables" until the number of games doesn't increase any more or the number of rows reaches 100
        while trycount < 4:
            prev_rownum = rownum

            footer = driver.find_element(By.ID, "overall-footer")
            location = footer.location_once_scrolled_into_view
            ##footer.sendKeys(Keys.END);

            wait.until(EC.visibility_of_element_located((By.XPATH, '//a[@class="bga-link"][@id="see_more_tables"]')))
            wait.until(EC.element_to_be_clickable((By.XPATH, '//a[@class="bga-link"][@id="see_more_tables"]')))
            
            link = driver.find_element(By.XPATH, '//a[@class="bga-link"][@id="see_more_tables"]')

            #success = False
            #while not success:
            try:
                link.click()
                #success = True
                if trycount > 0 and trycause == "Click":
                    trycount = 0
            except ElementClickInterceptedException:
                print("ElementClickInterceptedException. Trycount=" + str(trycount))
                trycause = "Click"
                trycount += 1
                if trycount == 4:
                    print("Cannot click 'More tables' button.")
                    exit_program()            

                time.sleep(trycount * 0.2)
                continue

            time.sleep(0.05)

            wait.until(EC.visibility_of_element_located((By.XPATH, "//table[@id='gamelist_inner']")))
            rownum=len(driver.find_elements(by=By.XPATH, value="//table[@id='gamelist_inner']/tr"))
            #print("No. of games: "+str(rownum))

            if prev_rownum == rownum:
                trycount += 1
                trycause = "EqRow"
                time.sleep(trycount * 0.2)
                continue

            if trycount > 0 and trycause == "EqRow":
                trycount = 0

            if rownum >= ROW_LIMIT :
                needSearch = True
                break
        
        print(str(rownum) + " games found")
        millisec2 = int(time.time() * 1000)
        gameStatsLoadTotalTime += (millisec2 - millisec1)

        gametable = driver.find_element(by=By.XPATH, value="//table[@id='gamelist_inner']")

        prevTableIdSet = tableIdSet
        tableIdSet = set()
        rowcount = 0
        newELO = 0
        skipTable = True
        millisec1 = int(time.time() * 1000)
        
        for gamerow in gametable.find_elements(by=By.XPATH, value =".//tr"):
            
            rowcount += 1
            colcount = 0
            prevELO = newELO

            # unfortunately it takes 15-20 ms to find an element...

            # az 1. oszlopban a 2. 'a' tartalmazza a sorszámot
            #tableId = gamerow.find_element(by=By.XPATH, value =".//td[1]/a[2]").text.lstrip('#')
            tableId = gamerow.find_element(by=By.CLASS_NAME, value ="bga-link").text.lstrip('#')
            tableIdSet.add(tableId)

            if skipTable and tableId in prevTableIdSet:
                print(tableId + " skipped")
                continue

            skipTable = False
            
            # a 2. oszlopban az 1. div tartalmazza az időbélyeget
            gameEnd = gamerow.find_element(by=By.XPATH, value =".//td[2]/div[1]").text

            # a 4. oszlopban a 2.divben az 1. divben a 2. span tartalmazza az új ÉLŐ pontot (class: gamerank_value)
            try:
                #newELOStr = gamerow.find_element(by=By.XPATH, value=".//td[4]/div[2]/div[1]/span[@class='gamerank_value ']").text
                newELOStr = gamerow.find_element(by=By.CLASS_NAME, value="gamerank_value ").text
            except NoSuchElementException:
                newELOStr = ""
            if newELOStr == "" :
                newELO = 0    
            else:
                newELO = int(newELOStr)

            endDate = gameEnd.split()[0]
            
            match endDate :
                case "tegnap" | "yesterday":
                    endDate = (datetime.today() - timedelta(days=1)).strftime('%Y.%m.%d')
                case _ :    
                    if len(endDate) < 3 or endDate[0].isalpha() :
                        # "20 minutes ago" / "today"
                        endDate = datetime.today().strftime('%Y.%m.%d')
            
            endDateDT = datetime.strptime(endDate, '%Y.%m.%d')
            if endDateDT < current_date :
                current_date = endDateDT
                #print(tableId + ": " + endDate + " (new)")
            else :
                #print(tableId + ": " + endDate)
                pass
            
            if newELO == 0:
                unranked = True
                newELO = prevELO
            else:
                unranked = False

            tableSeq += 1
            tableObj = tableClass(1000000 - tableSeq, tableId, endDate, newELO, unranked, False, False)
            tableList.append(tableObj)

        print(str(tableSeq) + " games total")
        millisec2 = int(time.time() * 1000)
        gameStatsProcTotalTime += (millisec2 - millisec1)

    tableList.sort(key=lambda x: x.seq, reverse=False)

    maxELO = 0
    maxELODate = ""
    dayRecSeq = 0
    dayRecSeqs = set()
    prevDate = ""

    for tableObj in tableList:
        if tableObj.endDate != prevDate :
            if dayRecSeq > 0 :
                dayRecSeqs.add(dayRecSeq)
                dayRecSeq = 0

        if not tableObj.unranked :
            #print(str(tableObj.newELO) + ": " + tableObj.endDate)
            if tableObj.newELO > maxELO :
                tableObj.newRecord = True
                maxELO = tableObj.newELO
                maxELODate = tableObj.endDate
                dayRecSeq = tableObj.seq
        prevDate = tableObj.endDate                

    if dayRecSeq > 0 :
        dayRecSeqs.add(dayRecSeq)

    for tableObj in tableList:
        if tableObj.seq in dayRecSeqs:
            tableObj.newRecByDay = True

    print()
    print("Personal ELO record of " + player_name + ":")
    print(maxELODate + ": " + str(maxELO))

    print()
    print("Days when " + player_name + " reached new personal ELO record:")

    file_opened = False
    if file_name != "":
        f = open(file_name, "w")
        file_opened = True
    
    for tableObj in tableList:
        if tableObj.newRecByDay :
            print(tableObj.endDate + ": " + str(tableObj.newELO))
            if file_opened:
                f.write(tableObj.endDate + ": " + str(tableObj.newELO) + "\n")

    if file_opened:
        f.close()        

    end_millisec = int(time.time() * 1000)
    print()
    print("Average load time per game:    " + str('{0:.2f}'.format(gameStatsLoadTotalTime / tableSeq)) + " ms")
    print("Average process time per game: " + str('{0:.2f}'.format(gameStatsProcTotalTime / tableSeq)) + " ms")
    print("Complete runtime: " + str(end_millisec - start_millisec) + " ms")
    
    time.sleep(1)


PRIVCONFIG_FILE = r'conf_priv.yml'
with open(PRIVCONFIG_FILE, 'r') as f:
    config = yaml.safe_load(f)
    bga_login = config['bga_login']
    chrome = config['chrome']

PUBCONFIG_FILE = r'conf_pub.yml'
with open(PUBCONFIG_FILE, 'r') as f:
    config = yaml.safe_load(f)
    bga_data = config['bga_data']

chrome_path = chrome['chrome_path']
chromedriver_path = chrome['chromedriver_path']

service = Service(executable_path=chromedriver_path)
options = webdriver.ChromeOptions()
options.binary_location = chrome_path
options.add_argument("--log-level=1")
driver = webdriver.Chrome(service=service, options=options)
wait = WebDriverWait(driver, 15)

# 1st param.: function to call
argnum = len(sys.argv)

if argnum > 1 :
    func = sys.argv[1]
else :
    func = 'elo_hist'

match func :
    case "elo_hist":
        elo_hist()
    case "login":    
        login()
    case _:
        print("unknown function")
    
 
