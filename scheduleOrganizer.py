import json

#Final data that holds rankings
allGames = []

#Start with the first year of data
startYear = 2003
#End year needs to be 1 year after the current year of data
endYear = 2022

#Mapping object to sort months of the year
monthMap = {'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11}

def sortingFun(game):
    return (game['month'] * 100) + game['day']

for x in range(startYear, endYear):
    #Keep track of schools that have already had schedules entered
    schoolsCompleted = []
    #Schedule for that particular year
    yearData = []
    with open(str(x) + 'Data.json') as f:
        data = list(json.load(f))
        for school in data[0]['schoolSchedules']:
            for opp in school['schedule']:
                #If that school's schedule has already been added to the list, ignore it
                if not opp['opponent'] in schoolsCompleted:
                    winner = ''
                    if (opp['result'] == 'W'):
                        winner = school['name']
                    if (opp['result'] == 'L'):
                        winner = opp['opponent']
                    yearData.append({
                        'month': opp['month'],
                        'day': opp['day'],
                        'gender': school['gender'],
                        'team1': school['name'],
                        "team1Id:": school['id'],
                        'team2': opp['opponent'],
                        "team2Id:": opp['id'],
                        'winner': winner,
                        'team1Score': int(opp['pointsFor']),
                        'team2Score': int(opp['pointsAgainst'])
                    })
                else:
                    print('Already completed ' + opp['opponent'] + ' for ' + str(x))
            #Add the school to the list of schools added to the full schedule already
            schoolsCompleted.append(school['name'])
        #Sort the games in the combined list
        yearData = sorted(yearData, key=sortingFun)
    
    with open('./CombinedSchedules/' + str(x) + '.json', 'w') as f:
        json.dump(yearData, f, ensure_ascii=False, indent=4)