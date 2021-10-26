# This program scrapes all the games from OSSCA's soccer schedules for Ohio high school soccer.
# It covers all the games played from the 2003 season onward, including all reported scores.
# The site's design is fairly old and there are some weird issues (like and HTML closing tag 
# in the middle of the page), so there are a few bandaids put in place to address these issues.
# The program takes a LONG time to run mainly because OSSCA's site takes ages to deliver the 
# content for each request, so a way to get multiple requests in one would be really nice.

from bs4 import BeautifulSoup
import requests
import json
import time

#Optimization tracking
start_time = time.time()

#The data that will be written to the json file at the end
data = []

year = 2021
#The first season logged in the OSSCA schedules is 2003 and the curernt schedule is 2020

#Mapping object to sort months of the year
monthMap = {'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11}

#For each year, create a table with the year set as the year being recorded and a blank array for the schedules to be added
#Used as a kind of visual progress tracker since this program takes ages to run
print('\n ID' + str(year) + '\n')
print("--- %s seconds ---" % (time.time() - start_time))
print('\n')

#Create table for each year with the year and an array to hold all the schedules from all schools for that year
yearData = {'year': year, 'schoolSchedules': []}

for x in range(1, 2960):
    #The highest ID in the OSSCA list is 2959 and the lowest is 1

    #Another visual progress tracker
    print(x)

    #Create a table for each school with their id, name, and an array to hold their games
    schoolData = {'id': x, 'name': '', 'schedule': []}

    #OSSCA link to pull web pages holding schedules, get data, and parse with BeautifulSoup
    url = "http://ossca.org/schedules.asp?qtype=teamschedule&season=" + str(year) + "&B_G=B&team=" + str(x)
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    #Get all the tables. The school's name is located in the second table and the games are located in the third table
    table = soup.find("div", {"id": "mainNormal2"}).find_all('table')
    schoolData['name'] = table[1].tr.td.b.text
    #You have to identify the games by grabbing table rows with a bgcolor attribute because terrible site design :(
    games = table[2].find_all('tr', {'bgcolor': 'e1dec2'})

    if "(Boys)" in table[1].tr.td.text:
        print(schoolData['name'] + " Boys")
        schoolData['gender'] = "Boys"
    elif "(Girls)" in table[1].tr.td.text:
        print(schoolData['name'] + " Girls")
        schoolData['gender'] = "Girls"

    #Make sure the team actually had games that season. Some schools have teams fold and form and have blank seasons.
    if (len(games) != 0):
        for x in range(0, len(games)):
            #The date is in the first table data. Have to trim off the &nbsp;
            month = games[x].find_all('td')[0].text[2:5]
            day = games[x].find_all('td')[0].text[6:8]
            #The opponent's name is in the second table data, the other game data is in the fourth table data
            opponent = games[x].find_all('td')[1].text
            gameData = games[x].find_all('td')[3].table.tr.find_all('td')[1]
            #Make sure all relevant data for the game is reported
            if (len(gameData) == 3):
                gameData = gameData.table.tr.find_all
                result = gameData('td')[0].text
                pointsFor = gameData('td')[2].text
                #For some reason the opponent score adds the - before the number to create a scoreline (e.g. 3-2)
                #so that part has to be taken off the string
                pointsAgainst = gameData('td')[3].text[1:]
            schoolData['schedule'].append({'month': monthMap[month], 'day': int(day), 'opponent': opponent, 'result': result, 'pointsFor': pointsFor, 'pointsAgainst': pointsAgainst})
            #print(opponent, result, score, oppScore)
        yearData['schoolSchedules'].append(schoolData)
data.append(yearData)

#Total time it took the program to run
print("--- %s seconds ---" % (time.time() - start_time))

#Write the program to scrapeData.json with some extra arguments to prettify it
with open('./2021Data.json', 'w') as f:
    json.dump(data, f, ensure_ascii=False, indent=4)