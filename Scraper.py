from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options 
from selenium.webdriver.support.select import Select
import json
import time


"""
This scrapes Leinster Rugbys historical players, it uses the Selenium Python library to mimic a web page, traverse
the page and locate the data we want
"""
def managePlayerListPage():
    time.sleep(2) #Give page time to load
    chrome_options = Options() #With Selenium you can set options
    chrome_options.add_argument("--start-maximized") #The table gets messed up if the window is not maximised
    #chrome_options.add_argument("--headless") #its faster when headless  
    driver = webdriver.Chrome(options= chrome_options)
    url = "https://www.leinsterrugby.ie/teams/historic-leinster-squads/"
    driver.get(url)
    players = []
    dropdown = Select(driver.find_element_by_class_name('user-split-by')) #selects dropdown menu
    temp =dropdown.options
    result = []
    for i in range(0, len(temp)): #This iterates through every year
        dropdown = Select(driver.find_element_by_class_name('user-split-by'))
        dropdown.select_by_index(i)
        dropdown = Select(driver.find_element_by_class_name('user-split-by')) #prevents stale element exception
        result, players = handlePlayerListPage(driver, players, result)
    toJson(result)

def handlePlayerListPage(driver, players, all_players):
    time.sleep(2)
    temp = driver.find_elements_by_xpath('//a[@href]')
    text = {}
    
    for item in temp:
        text[item.text] = item.get_attribute("href")
    for k, v in text.items():
        if k not in players and 'historic-players' in v.split('/'): #Keeps a list of players who have already been processed
            driver.get(v)
            all_players.append(managePlayerPage(driver, k))
            players.append(k)
            driver.back()
    return all_players, players

def managePlayerPage(driver, name):#This method manages the iteration over a player page
    player = {}
    try: #Some records are empty and do not have a drop down, this deals with this case
        dropdown = Select(driver.find_element_by_xpath('//*[@id="sotic_wp_widget-34-content"]/div/div[1]/select')) 
    except:
        print("Problem with page skipping " + name)
        return player
    temp =dropdown.options
    
    list_of_seasons = []
    for i in range(0, len(temp)):
        dropdown = Select(driver.find_element_by_xpath('//*[@id="sotic_wp_widget-34-content"]/div/div[1]/select')) 
        season = dropdown.options[i].text
        if season == '':
            season = "2019"
        dropdown.select_by_index(i)
        list_of_seasons.append(handlePlayerPage(driver, season)) #appends each season to a player
    player_details = get_player_details(driver)
    player['Season_Totals'] = get_total_season_details(driver)
    player['Player_Details'] = player_details
    player['Season_Details'] = list_of_seasons
    player['Player_Name'] = name
    print(name)
    return player

def get_player_details(driver):
    
    
    player_details = {}
    header_els = driver.find_elements_by_xpath('//*[@id="sotic_wp_widget-32-content"]')
    header_list = header_els[0].text.split('\n')
    if len(header_list) % 2 ==1:
        header_list.append('')
    for i in range(0, int(len(header_list)), 2):
        player_details[header_list[i]] = header_list[i+1]
    return player_details

def get_total_season_details(driver):
    all_seasons=[]
    button = driver.find_element_by_xpath('//*[@id="competition"]')
    button.click()
    table = driver.find_element_by_xpath('//*[@id="sotic_wp_widget-33-content"]/div/div/table')
    text = table.text
    text = text.split('\n')
    header = text[0].split(' ')
    body = text[1:]
    for item in body:
        season_details={}
        components = item.split(' ')
        if components[1].isnumeric():
            for i in range(0, len(components)):
                if i == 0:
                    season_details['Overall_Total'] = components[i]
                else:
                    season_details[header[i]] = components[i]
        else:
            components[0:2] = [' '.join(components[0:2])]
            if components[0][0].isnumeric():
                for i in range(0, len(components)):
                    season_details['Season'] = components[0]
                    if i == 0:
                        season_details['Season_Total'] = components[i]
                    else:
                        season_details[header[i]] = components[i]
            
        
            for i in range(0, len(components)):
                season_details[header[i]] = components[i]
        all_seasons.append(season_details)
    driver.back()
    return all_seasons

def handlePlayerPage(driver, season):
    time.sleep(2)
    season_details = {}
    test = driver.find_elements_by_tag_name('tr')

    body = []
    season_total = []

    
    for item in test:
        if item.text is not '':
            if item.text[0:5] != 'Total':
                body.append(item.text)
            else:
                season_total.append(item.text)
    headers = body[0]
    body.pop(0)
    player_details_by_season = {}
    games = []
    all_games = []
    ind_game = {}
    for item in body:   #The table is returned as a 1 line string that is not split. I split by space and
        components = item.split(' ') 
        if len(item.split(' ')) > 4:
            if item.split(' ')[4].isnumeric() == False:
                components[1:5] = [' '.join(components[1:5])]
            elif item.split(' ')[3].isnumeric() == False:
                if item.split(' ')[3] == '92':
                    components[1:5] = [' '.join(components[1:5])]
                else:
                    components[1:4] = [' '.join(components[1:4])]
            elif item.split(' ')[2].isnumeric() == False:
                if item.split(' ')[2] == '92':
                    components[1:4] = [' '.join(components[1:4])]
                else:
                    components[1:3] = [' '.join(components[1:3])]
        games.append(components)
    headers = headers.split()
    for item in games:
        if len(item)> len(headers):
            item.pop(len(item)-1)
        for i in range(0, len(item)):
            ind_game[headers[i]] = item[i]
        all_games.append(ind_game)
    season_details['Games'] = all_games
    season_details['Season'] = season
    return season_details

def toJson(results):
    with open('Leinster_result.json', 'w') as fp:
        json.dump(results, fp, ensure_ascii = False)
global players
players = {}
managePlayerListPage()
