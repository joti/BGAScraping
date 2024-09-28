# BGA_Scraping.py
# Python program to get data from BGA

import time
import sys
import yaml
import os.path

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
    def __init__(self,seq,tableId,endDate,endTst,newELO,unranked,newRecord,newRecByDay,fake):
        self.seq = seq
        self.tableId = tableId
        self.endDate = endDate
        self.endTst = endTst
        self.newELO = newELO
        self.unranked = unranked
        self.newRecord = newRecord
        self.newRecByDay = newRecByDay
        self.fake = fake

def exit_program():
    print("Exiting...")
    sys.exit(0)

def close_popup():
    # We open the main page just to dismiss popups if there's any
    mainpage_link = bga_data['urls']['main']
    driver.get(mainpage_link)
    try:
        popup = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'cc-window')]//a[contains(@class, 'cc-btn')]")))
        popup.click()
        print("Popup closed")
    except TimeoutException:
        print("No clickable popup found")    

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

def elo_hist( game_def,     # id or name of the game,
              player_names, # the players' BGA name separated by comma
              min_date,     # start of the period to check (no limit if empty)
              max_date,     # end of the period to check (no limit if empty)
              file_name,    # name of file to export data
              subfunc_set   # subfunctions to execute
            ):

    ROW_LIMIT = 200

    maxDateStr = ""
    minDateStr = ""
    maxDateDT = datetime.max
    minDateDT = datetime.min
    
    maxTst = None
    minTst = None

    if max_date != "":
        maxDateStr = max_date.replace("-", ".")
        try:
            maxDateDT = datetime.strptime(maxDateStr, '%Y.%m.%d')
        except ValueError as e:
            print("End of period is not a proper date value (YYYY-MM-DD)")
            exit_program()
        #time.mktime(maxDateTime.timetuple())
    else :
        if "avg" in subfunc_set :
            maxDateStr = datetime.today().strftime('%Y.%m.%d')
    if maxDateStr != "" :
        maxTstDT = datetime(int(maxDateStr[0:4]), int(maxDateStr[5:7]), int(maxDateStr[8:10]), 12, 0)
        maxTst = datetime.timestamp(maxTstDT)

    print("maxDate = " + maxDateStr + "    maxTst = " + str(maxTst))        

    if min_date != "":
        minDateStr = min_date.replace("-", ".")
        try:
            minDateDT = datetime.strptime(minDateStr, '%Y.%m.%d')
        except ValueError as e:
            print("Start of period is not a proper date value (YYYY-MM-DD)")
            exit_program()
            
        minTstDT = datetime(int(minDateStr[0:4]), int(minDateStr[5:7]), int(minDateStr[8:10]), 0, 0)
        minTst = datetime.timestamp(minTstDT)
        #time.mktime(minDateTime.timetuple())

    print("minDate = " + minDateStr + "    minTst = " + str(minTst))        

    game_name = 'unknown'
    game_id = '0'
    if game_def != "" :
        for k, v in bga_data['gameids'].items():
            if game_def.upper().replace(" ", "").replace("_", "") == k.upper().replace(" ", "").replace("_", "") or game_def == str(v) :
                game_id = str(v)
                game_name = k
    else :
        game_id = '1'
        game_name = 'Carcassonne'

    if game_id == '0' :
        print("Unknown game")
        exit_program()
        
    print(game_id + " - " + game_name)
        
    if player_names == "" :
        player_names = bga_login['user']
    
    if minDateDT != datetime.min :
        print('Start date: %s' % (minDateStr))
    if maxDateDT != datetime.max :
        print('End date: %s' % (maxDateStr))

    close_popup()

    # we need the player's id in BGA
    # to get the community page we need to log in
    login()
    time.sleep(1)

    start_millisec = int(time.time() * 1000)

    for player_name in player_names.split(","):
        player_name = player_name.strip()
        print('ELO progress of %s in the game %s:' % (player_name, game_name))

        if file_name == ".":
            player_file = (player_name + "__" + game_name).lower().replace(" ", "_") + ".elo"
        elif file_name != "":
            player_file = file_name
            
        if player_file != "" and output_path != "" :
            if os.path.isdir(output_path):
                player_file = output_path + player_file
            else :
                print(output_path + " does not exist")
        if player_file != "" :
            print("Output file: " + player_file)
        print()

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
        print("The current url is: " + str(player_url))

        player_id = player_url[(player_url.find('='))+1:]
        print("Player id is: " + player_id)    

        startDT = datetime.now()

        if maxDateDT != datetime.max :
            current_date = maxDateDT + timedelta(days=1)
        else :   
            current_date = startDT + timedelta(days=1)

        needSearch = True
        tableSeq = 0
        tableNum = 0
        tableIdSet = {}
        tableList = []
        gameStatsLoadTotalTime = 0
        gameStatsProcTotalTime = 0
        endTst = None
        
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
                    trycount += 1
                    if trycount == 4 and trycause == "Click":
                        print("Cannot click 'More tables' button.")
                        exit_program()            

                    trycause = "Click"
                    time.sleep(trycount * 0.2)
                    continue

                time.sleep(0.05)

                wait.until(EC.visibility_of_element_located((By.XPATH, "//table[@id='gamelist_inner']")))
                rownum=len(driver.find_elements(by=By.XPATH, value="//table[@id='gamelist_inner']/tr"))

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
            
            rownum=len(driver.find_elements(by=By.XPATH, value="//table[@id='gamelist_inner']/tr"))
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

                # 1st column, 2nd 'a': table id (class: bga_link)
                #tableId = gamerow.find_element(by=By.XPATH, value =".//td[1]/a[2]").text.lstrip('#')
                tableId = gamerow.find_element(by=By.CLASS_NAME, value ="bga-link").text.lstrip('#')
                tableIdSet.add(tableId)

                if skipTable and tableId in prevTableIdSet:
                    print(tableId + " skipped")
                    continue

                skipTable = False
                
                # 2nd column, 1st div: end time
                gameEnd = gamerow.find_element(by=By.XPATH, value =".//td[2]/div[1]").text

                # 4th column, 2nd div, 1st div, 2nd span: nem ELO value (class: gamerank_value)
                try:
                    #newELOStr = gamerow.find_element(by=By.XPATH, value=".//td[4]/div[2]/div[1]/span[@class='gamerank_value ']").text
                    newELOStr = gamerow.find_element(by=By.CLASS_NAME, value="gamerank_value ").text
                except NoSuchElementException:
                    newELOStr = ""
                if newELOStr == "" :
                    newELO = 0    
                else:
                    newELO = int(newELOStr)

                # examples of game end values:
                # 2024-09-24 at 22:51           2024.09.24 22:51
                # yesterday at 14:51            tegnap 14:51-kor
                # today at 13:00                ma 13:00-kor
                # 2 hours ago                   2 órája
                # one hour ago                  egy órával ezelőtt
                # 41 minutes ago                41 perce
                endDate = gameEnd.split()[0]
                endDate = endDate.replace("-", ".")

                if "avg" in subfunc_set :
                    timePos = gameEnd.find(':')
                    if timePos == -1 :
                        # For today, we consider all games as having finished at noon
                        endTime = "12:00"
                    else :
                        timePos -= 2
                        endTime = gameEnd[timePos:timePos+5]
                
                match endDate :
                    case "tegnap" | "yesterday":
                        endDate = (datetime.today() - timedelta(days=1)).strftime('%Y.%m.%d')
                    case _ :    
                        if len(endDate) < 3 or endDate[0].isalpha() :
                            # "20 minutes ago" / "today"
                            endDate = datetime.today().strftime('%Y.%m.%d')

                #print(endDate + " " + endTime)                

                if "avg" in subfunc_set :
                    endDateTime = datetime(int(endDate[0:4]), int(endDate[5:7]), int(endDate[8:10]), int(endTime[0:2]), int(endTime[3:5]))
                    endTst = datetime.timestamp(endDateTime)
                    #print(str(endDateTime) + " -> " + str(int(endTst)))
                
                endDateDT = datetime.strptime(endDate, '%Y.%m.%d')
                if endDateDT < current_date :
                    current_date = endDateDT
                else :
                    pass

                if endDateDT > maxDateDT:
                    print(tableId + " skipped (out of period)")
                    continue
                
                if newELO == 0:
                    unranked = True
                    newELO = prevELO
                else:
                    unranked = False

                # if this is the first game in the table then we add an extra item to help the calculation of the average ELO rating
                if len(tableList) == 0 and "avg" in subfunc_set:
                    tableSeq += 1
                    tableObj = tableClass(1000000 - tableSeq, tableId + "0", maxDateStr, maxTst, newELO, False, False, False, True)
                    tableList.append(tableObj)

                if endDateDT < minDateDT:
                    tableSeq += 1
                    tableObj = tableClass(1000000 - tableSeq, "1", minDateStr, minTst, newELO, False, False, False, True)
                    tableList.append(tableObj)
                    needSearch = False
                    
                    print(tableId + " and older games skipped (out of period)")
                    break

                tableSeq += 1
                tableNum += 1
                tableObj = tableClass(1000000 - tableSeq, tableId, endDate, endTst, newELO, unranked, False, False, False)
                tableList.append(tableObj)


            print(str(tableNum) + " games total")
            millisec2 = int(time.time() * 1000)
            gameStatsProcTotalTime += (millisec2 - millisec1)

        tableList.sort(key=lambda x: x.seq, reverse=False)

        maxELO = 0
        maxELODate = ""
        dayRecSeq = 0
        dayRecSeqs = set()
        prevDate = ""
        rankedNum = 0

        for tableObj in tableList:
            if tableObj.endDate != prevDate :
                if dayRecSeq > 0 :
                    dayRecSeqs.add(dayRecSeq)
                    dayRecSeq = 0

            if not tableObj.unranked :
                if not tableObj.fake :
                    rankedNum += 1
                    
                #print(str(tableObj.newELO) + ": " + tableObj.endDate + ", " + str(tableObj.endTst) + ", " + str(tableObj.fake))
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

        if "avg" in subfunc_set :
            firstObj = True
            avgSum = 0
            prevELO = 0
            for tableObj in tableList:
                if not tableObj.unranked :
                    if firstObj :
                        firstObj = False
                        firstTst = tableObj.endTst
                    else :
                        avgSum += prevELO * ( tableObj.endTst - prevTst )
                    prevTst = tableObj.endTst
                    prevELO = tableObj.newELO
            print("avgSum   = " + str(avgSum))
            print("firstTst = " + str(firstTst))
            print("lastTst  = " + str(tableObj.endTst))
            if tableObj.endTst - firstTst > 1 :
                avgELO = avgSum / (tableObj.endTst - firstTst)


        file_opened = False
        if player_file != "":
            f = open(player_file, "w")
            file_opened = True

            f.write("Player: " + player_name + "\n")
            f.write("Game: " + game_name + "\n")
            if minDateDT != datetime.min :
                f.write("Start date of examination: " + minDateStr + "\n")
            if maxDateDT != datetime.max :
                f.write("End date of examination: " + maxDateStr + "\n")
            f.write("Examination started at " + startDT.strftime("%Y.%m.%d %H:%M:%S") + "\n")
            f.write("\n")

        print()
        if maxDateDT != datetime.max or minDateDT != datetime.min :
            print("Number of ranked games within the period: " + str(rankedNum))
            print("Personal ELO record of " + player_name + " within the period:")
        else :    
            print("Number of ranked games: " + str(rankedNum))
            print("Personal ELO record of " + player_name + ":")
        print(maxELODate + ": " + str(maxELO))
        if "avg" in subfunc_set :
            print("Average ELO: " + str('{0:.2f}'.format(avgELO)))

        if file_opened :
            f.write("Number of ranked games: " + str(rankedNum) + "\n")
            if "avg" in subfunc_set :
                f.write("Average ELO: " + str('{0:.2f}'.format(avgELO)) + "\n")
            f.write("Highest ELO: " + str(maxELO) + " (" + maxELODate + ")\n")
            f.write("\n")

        print()
        print("Days when " + player_name + " reached new personal ELO record:")

        if file_opened :
            f.write("ELO progress:\n")
            f.write("\n")
        
        for tableObj in tableList:
            if tableObj.newRecByDay :
                endMark = " *" if tableObj.fake else ""
                    
                print(tableObj.endDate + ": " + str(tableObj.newELO) + endMark)
                if file_opened:
                    f.write(tableObj.endDate + ": " + str(tableObj.newELO) + endMark + "\n")

        if file_opened:
            f.close()
        print()

    end_millisec = int(time.time() * 1000)
    print("Average load time per game:    " + str('{0:.2f}'.format(gameStatsLoadTotalTime / tableSeq)) + " ms")
    print("Average process time per game: " + str('{0:.2f}'.format(gameStatsProcTotalTime / tableSeq)) + " ms")
    print("Complete runtime: " + str(end_millisec - start_millisec) + " ms")
    
    time.sleep(1)


PRIVCONFIG_FILE = r'conf_priv.yml'
with open(PRIVCONFIG_FILE, 'r') as f:
    config = yaml.safe_load(f)
    bga_login = config['bga_login']
    chrome = config['chrome']
    output_path = config['output_path']

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

game_def = ""
player_names = ""
file_name = ""
min_date = ""
max_date = ""
subfunc_set = set()

if argnum > 2 :
    for argpos in range(2, argnum):
        if argpos == argnum - 1 and sys.argv[argpos][:2] != '--':
            break
            
        match sys.argv[argpos]:
            case "-g":
                game_def = sys.argv[argpos + 1]
            case "-p":
                player_names = sys.argv[argpos + 1]
            case "-f":
                file_name = sys.argv[argpos + 1]
            case "-mn":
                min_date = sys.argv[argpos + 1]
            case "-mx":
                max_date = sys.argv[argpos + 1]
            case "--avg":
                subfunc_set.add("avg")

print("game: " + game_def + ", player: " + player_names + ", file: " + file_name)            

match func :
    case "elo_hist":
        elo_hist(game_def, player_names, min_date, max_date, file_name, subfunc_set)
    case "login":    
        login()
    case _:
        print("unknown function")
    
 
