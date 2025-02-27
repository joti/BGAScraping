# BGA_Scraping.py
# Python program to get data from BGA

import time
import sys
import yaml
import re
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

def login24():
    # Deprecated login method
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

def login():
    global loggedIn
    global lang
    
    if loggedIn == True :
        return        

    login_link = bga_data['urls']['login']
    print(login_link);
    driver.get(login_link)

    username = bga_login['user']
    pw = bga_login['password']

    wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="account-module"]/div[3]/div[3]/div/div[2]/div/div[2]/div[1]/div/div[2]/form/div[2]/div/input')))
    it_username = driver.find_element(By.XPATH, '//*[@id="account-module"]/div[3]/div[3]/div/div[2]/div/div[2]/div[1]/div/div[2]/form/div[2]/div/input')

    it_username.send_keys(username)
    time.sleep(2)

    wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="account-module"]/div[3]/div[3]/div/div[2]/div/div[2]/div[1]/div/div[2]/form/div[3]/div/a')))
    driver.find_element(By.XPATH, '//*[@id="account-module"]/div[3]/div[3]/div/div[2]/div/div[2]/div[1]/div/div[2]/form/div[3]/div/a').click()
    time.sleep(1)

    wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="account-module"]/div[3]/div[3]/div/div[2]/div/div[2]/div[2]/div/form/div[1]/div[2]/div/input')))
    it_password = driver.find_element(By.XPATH, '//*[@id="account-module"]/div[3]/div[3]/div/div[2]/div/div[2]/div[2]/div/form/div[1]/div[2]/div/input')
    it_password.send_keys(pw)
    time.sleep(2)

    wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="account-module"]/div[3]/div[3]/div/div[2]/div/div[2]/div[2]/div/form/div[2]/div/div/a')))
    driver.find_element(By.XPATH, '//*[@id="account-module"]/div[3]/div[3]/div/div[2]/div/div[2]/div[2]/div/form/div[2]/div/div/a').click()

    time.sleep(1)

    wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="account-module"]/div[3]/div[3]/div/div[2]/div/div[2]/div[3]/div[2]/div[3]/div[3]/div/div/a')))
    driver.find_element(By.XPATH, '//*[@id="account-module"]/div[3]/div[3]/div/div[2]/div/div[2]/div[3]/div[2]/div[3]/div[3]/div/div/a').click()
    time.sleep(1)
    loggedIn = True
    print("login successful")

    forumlink = driver.find_element(By.XPATH, "//a[contains(@href, 'forum')]")
    print(forumlink.text)
    if forumlink.text.upper() == 'FORUMS' :
        lang = "en"
    print(lang)
    


def elo_hist( game_def,     # id or name of the game,
              player_names, # the players' BGA name separated by comma
              min_date,     # start of the period to check (no limit if empty)
              max_date,     # end of the period to check (no limit if empty)
              file_name,    # name of file to export data
              subfunc_set   # subfunctions to execute
            ):

    global lang

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
        else :
            player_file = ""
            
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
            continue

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

        match lang :
            case "hu":
                dateFormat = "%Y.%m.%d"
            case _ :    
                dateFormat = "%m/%d/%Y"
        
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
                        endDate = (datetime.today() - timedelta(days=1)).strftime(dateFormat)
                    case _ :    
                        if len(endDate) < 3 or endDate[0].isalpha() :
                            # "20 minutes ago" / "today"
                            endDate = datetime.today().strftime(dateFormat)

                #print(endDate + " " + endTime)                

                if "avg" in subfunc_set :
                    endDateTime = datetime(int(endDate[0:4]), int(endDate[5:7]), int(endDate[8:10]), int(endTime[0:2]), int(endTime[3:5]))
                    endTst = datetime.timestamp(endDateTime)
                    #print(str(endDateTime) + " -> " + str(int(endTst)))
                
                endDateDT = datetime.strptime(endDate, dateFormat)
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
                current_date = current_date + timedelta(days=1)


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

def trn_tablecoll( trn_id,   # id of the tournament
                  file_name # name of file to export data
                ):

    trn_file = ""
    if file_name == ".":
        trn_file = ("tournament_" + trn_id + ".games")
    elif file_name != "":
        trn_file = file_name
    else :
        trn_file = ""
        
    if trn_file != "" and output_path != "" :
        if os.path.isdir(output_path):
            trn_file = output_path + trn_file
        else :
            print(output_path + " does not exist")
    if trn_file != "" :
        print("Output file: " + trn_file)

    close_popup()

    # to get game stats we need to log in
    login()

    start_millisec = int(time.time() * 1000)
    
    trn_url = (bga_data['urls']['tournament'].
                             replace('{p1}', trn_id))
    print(trn_url)

# div containing all games of the tournament:

# Swiss system:
# XPath:       //*[@id="stage_display"]/div/div/div[2]
# Full XPath:  /html/body/div[2]/div[5]/div[1]/div/div/div[4]/div/div/div/div/div[2]

# Round-robin (1 stage)
# XPath:       //*[@id="stage_display"]/div/div/div[2]
# Full XPath:  /html/body/div[2]/div[5]/div[1]/div/div/div[4]/div/div/div/div/div[2]

# Round-robin (2 stage):
# XPath:       //*[@id="stage_display"]/div/div/div/div[2]/div[3]/div[2]
# Full XPath:  /html/body/div[2]/div[5]/div[1]/div/div/div[4]/div/div/div/div/div/div[2]/div[3]/div[2]

# class of div containing all games:          v2tournament__encounters
# class of emelents containing link to games: v2tournament__encounter-title

    trycount = 0
    success = False
    while not success:
        try:
            if trycount == 0:
                driver.get(trn_url)
            else:    
                driver.refresh()
                print("refresh")
            elements = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "v2tournament__encounter-title")))
            
            success = True
        except TimeoutException:
            time.sleep(1)
            trycount += 1
            if trycount == 3:
                print("Cannot load tournament page.")
                exit_program()            

    print("Tournament page loaded.")
    print("Number of games:" + str(len(elements)))

    table_ids = []

    for elem in elements:
        href = elem.get_attribute("href")
        if href:
            match = re.search(r"table=(\d+)", href)
            if match:
                table_ids.append(match.group(1))

    file_opened = False
    if trn_file != "":
        try:
            f = open(trn_file, "w")
            file_opened = True

            for table_id in table_ids:
                f.write(table_id + "\n")
        except:
            print("Cannot write file " + trn_file)
        finally:    
            if file_opened:
                f.close()


    end_millisec = int(time.time() * 1000)

    print("Complete runtime: " + str(end_millisec - start_millisec) + " ms")
                  
    time.sleep(1)


def tableproc( table_id, # id of the table
               file_name # name of file to save data
             ):

    if len(table_id) < 8 :
        print("Wrong table id: " + table_id)
        return

    table_file = ""
    if file_name == ".":
        table_file = ("review_" + table_id + ".html")
    elif file_name != "":
        table_file = file_name
    else :
        table_file = ""
        
    if table_file != "" and output_path != "" :
        if os.path.isdir(output_path):
            table_file = output_path + table_file
        else :
            print(output_path + " does not exist")
    if table_file != "" :
        print("Output file: " + table_file)

    close_popup()

    # to get game stats we need to log in
    login()

    start_millisec = int(time.time() * 1000)

    # requests are not suitable for collecting table data - the responses don't contain the relevant components
    # thus we have to use Selenium for this purpose as well
    
    table_url = (bga_data['urls']['table'].replace('{p1}', table_id))
    #table_url = (bga_data['urls']['gamereview'].replace('{p1}', table_id))
    print(table_url)

    trycount = 0
    success = False
    while not success:
        try:
            if trycount == 0:
                driver.get(table_url)
            else:    
                driver.refresh()
                print("refresh")
            #wait.until(EC.visibility_of_element_located((By.ID, "gametable_box")))
            wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "score")))
            success = True
        except TimeoutException:
            time.sleep(1)
            trycount += 1
            if trycount == 3:
                print("Cannot load table page.")
                exit_program()            

    # relevant ids:
    # - div id = gameoptions: game settings
    # - div id = game_result: player names and result of the game
    # - div id = statistics_content:
    #   - div id = table_stats
    #   - table id = player_stats_table

    print("oldal betöltve")
    result_div = driver.find_element(By.XPATH, "//div[@id='game_result']")
    print("result_div OK")
    player_divs = result_div.find_elements(By.XPATH, "./div")
    print(len(player_divs))

    for player_div in player_divs:

        player_elem = player_div.find_element(By.XPATH, ".//a[@class='playername']")

        player_name = player_elem.text
        print(f"Játékos név: {player_name}")

        href_value = player_elem.get_attribute("href")
        match = re.search(r"id=(\d+)", href_value)
        if match:
            player_id = match.group(1)
        else:
            player_id = "N/A"
        print(f"Játékos id: {player_id}")

        score_div = player_div.find_element(By.XPATH, ".//div[@class='score']")
        player_score = score_div.text.split()[0]        
        print(f"Játékos pontszáma: {player_score}")

        newrank_span = player_div.find_element(By.XPATH, ".//span[@class='gamerank_value ']")
        player_newrank = newrank_span.text.split()[0]        
        print(f"Játékos új Élője: {player_newrank}")

        winpt_span = player_div.find_element(By.XPATH, ".//span[starts-with(@id, 'winpoints_value')]")
        player_winpt = winpt_span.text.split()[0]        
        print(f"Játékos Élő változása: {player_winpt}")

    stat_div = driver.find_element(By.XPATH, "//div[@id='statistics_content']")
    print("stat_div OK")
    tablestat_div = stat_div.find_element(By.XPATH, ".//div[@id='table_stats']")
    print("tablestat_div OK")
    tablestatrow_divs = tablestat_div.find_elements(By.XPATH, "./div[@class='row-data']")
    print(len(player_divs))

    table_duration = "" 
    table_width = "" 
    table_height = "" 
    table_ccities = "" 
    for tablestatrow_div in tablestatrow_divs:
        tablestatrow_label = tablestatrow_div.find_element(By.XPATH, "./div[@class='row-label']")
        tablestatrow_value = tablestatrow_div.find_element(By.XPATH, "./div[@class='row-value']")
        match tablestatrow_label.text :
            case "Játékhossz" | "Game duration":
                table_duration = tablestatrow_value.text.strip()
            case "Tábla szélessége" | "Board width" :                
                table_width = tablestatrow_value.text.strip()
            case "Tábla magassága" | "Board height" :                
                table_height = tablestatrow_value.text.strip()
            case "Befejezett városok" | "Completed cities" :                
                table_ccities = tablestatrow_value.text.strip()

    print(f"Tábla szélessége: {table_width}")
    print(f"Tábla magassága: {table_height}")
    print(f"Játékhossz: {table_duration}")
    print(f"Befejezett városok: {table_ccities}")

    playerstattable = stat_div.find_element(By.XPATH, ".//table[@id='player_stats_table']")
    print("playerstat_table OK")

    player1_time = ""
    player2_time = ""
    player1_roadpt = ""
    player2_roadpt = ""
    player1_citypt = ""
    player2_citypt = ""
    player1_monasterypt = ""
    player2_monasterypt = ""
    player1_fieldpt = ""
    player2_fieldpt = ""
    player1_meeples = ""
    player2_meeples = ""

    for playerstatrow in playerstattable.find_elements(by=By.XPATH, value =".//tr"):
        playerstatrow_head = playerstatrow.find_element(By.XPATH, "./th")
        playerstatrow_cols = playerstatrow.find_elements(By.TAG_NAME, "td")
        if playerstatrow_cols :
        
            #playerstatrow_col1 = playerstatrow.find_element(By.XPATH, ".//td[1]")
            #playerstatrow_col2 = playerstatrow.find_element(By.XPATH, ".//td[2]")

            match playerstatrow_head.text :
                case "Gondolkodási idő" | "Thinking time":
                    player1_time = playerstatrow_cols[0].text.strip()
                    player2_time = playerstatrow_cols[1].text.strip()
                case "Utakért kapott pontok" | "Points from roads" :                
                    player1_roadpt = playerstatrow_cols[0].text.strip()
                    player2_roadpt = playerstatrow_cols[1].text.strip()
                case "Városokért kapott pontok" | "Points from cities" :                
                    player1_citypt = playerstatrow_cols[0].text.strip()
                    player2_citypt = playerstatrow_cols[1].text.strip()
                case "Kolostorokért kapott pontok" | "Points from monasteries" :                
                    player1_monasterypt = playerstatrow_cols[0].text.strip()
                    player2_monasterypt = playerstatrow_cols[1].text.strip()
                case "Mezőkért kapott pontok" | "Points from fields" :                
                    player1_fieldpt = playerstatrow_cols[0].text.strip()
                    player2_fieldpt = playerstatrow_cols[1].text.strip()
                case "Kijátszott alattvalók" | "Meeples placed" :                
                    player1_meeples = playerstatrow_cols[0].text.strip()
                    player2_meeples = playerstatrow_cols[1].text.strip()

    print(f"Gondolkodási idők: {player1_time} - {player2_time}")
    print(f"Utakért kapott pontok: {player1_roadpt} - {player2_roadpt}")
    print(f"Városokért kapott pontok: {player1_citypt} - {player2_citypt}")
    print(f"Kolostorokért kapott pontok: {player1_monasterypt} - {player2_monasterypt}")
    print(f"Mezőkért kapott pontok: {player1_fieldpt} - {player2_fieldpt}")
    print(f"Kijátszott alattvalók: {player1_meeples} - {player2_meeples}")


    end_millisec = int(time.time() * 1000)

    print("Complete runtime: " + str(end_millisec - start_millisec) + " ms")



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

service = Service()
options = webdriver.ChromeOptions()
options.binary_location = chrome_path
options.add_argument("--log-level=1")
driver = webdriver.Chrome(service=service, options=options)
wait = WebDriverWait(driver, 15)
loggedIn = False
lang = "hu"

# 1st param.: function to call
argnum = len(sys.argv)

if argnum > 1 :
    func = sys.argv[1]
else :
    func = 'elo_hist'

table_id = ""
trn_id = ""
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
            case "-t":
                trn_id = sys.argv[argpos + 1]
            case "-b":
                table_id = sys.argv[argpos + 1]
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
    case "trn_tablecoll":
        trn_tablecoll(trn_id, file_name)
    case "tableproc":
        tableproc(table_id, file_name)
    case _:
        print("unknown function")
    
 
