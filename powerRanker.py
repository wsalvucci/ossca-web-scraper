import json
import math
from os import name

teamData = {}

rankingAnalysis = {
    'gamesPredicted': 0,
    'pointsOff': 0,
    'pointsOffNoBlowouts': 0,
    'winnerPredicted': 0,
    '1ptGames': 0,
    '1ptGamesPredicted': 0,
    '2ptGames': 0,
    '2ptGamesPredicted': 0,
    '3ptGames': 0,
    '3ptGamesPredicted': 0,
    '4ptGames': 0,
    '4ptGamesPredicted': 0,
    '5ptGames': 0,
    '5ptGamesPredicted': 0,
    'blowoutGames': 0,
    'blowoutGamesPredicted': 0
}

teamAccuracy = {}

confidence = []

allMatches = []

#Cutoff to prevent incomplete data affecting analysis
#The first year will obviously be bad since all teams are ranked the same
analysisYearCutoff = 2005

#Cutoff for when to start tracking team data. Useful if needed to get x-year history
statsYearCutoff = 2016

startYear = 2003
endYear = 2022

#Modifier to tweak expected points per game appropriately
expectedPointsConstant = 50

#Modifier to tweak starting expected points against. Shouldn't change much
startingExpectedPointsAgainst = 1.5

#How severe should departures from expected scores be punished/rewarded
graphCompression = 1.5

def expectedPoints(rating1, rating2, pointsAvg):
    return (((rating1 - rating2)/1500) * expectedPointsConstant) + pointsAvg

#Use for offensive results
def calculateEloResult(shift, result):
    return math.pow(math.e/graphCompression,result-shift) / (math.pow(math.e/graphCompression, result-shift) + 1)

#Use for defensive results
def calculateInvertedEloResult(shift, result):
    return math.pow(math.e/graphCompression,-(result-shift)) / (math.pow(math.e/graphCompression, -(result-shift)) + 1)

def calculateNewElo(current, kFactor, expected, actual):
    return current + (kFactor * (actual - expected))

def calculateExpectedElo(rating1, rating2):
    return 1 / (1 + math.pow(10,(rating2-rating1)/400))
    

def analyseMatch(team1, team2, score1, score2, year):
    if team1['name'] in teamAccuracy:
        teamAccuracy[team1['name']]['gamesPlayed'] = teamAccuracy[team1['name']]['gamesPlayed'] + 1
    else:
        teamAccuracy[team1['name']] = {"name": team1['name'], "gamesPlayed": 1, "gamesPredicted": 0}
    if team2['name'] in teamAccuracy:
        teamAccuracy[team2['name']]['gamesPlayed'] = teamAccuracy[team2['name']]['gamesPlayed'] + 1
    else:
        teamAccuracy[team2['name']] = {"name": team2['name'], "gamesPlayed": 1, "gamesPredicted": 0}

    #print('Analysing ' + team1['name'] + '(' + str(team1['offRank']) + ', ' + str(team1['defRank']) + ') vs ' + team2['name'] + '(' + str(team2['offRank']) + ', ' + str(team2['defRank']) + ')')
    expected1OffElo = calculateExpectedElo(team1['offRank'], team2['defRank'])
    expected1DefElo = calculateExpectedElo(team1['defRank'], team2['offRank'])

    expected2OffElo = calculateExpectedElo(team2['offRank'], team1['defRank'])
    expected2DefElo = calculateExpectedElo(team2['defRank'], team1['offRank'])

    if team2['gamesPlayed'] != 0 and team1['gamesPlayed'] != 0:
        expected1Score = expectedPoints(team1['offRank'], team2['defRank'], ((team2['pointsAgainst'] / team2['gamesPlayed']) + (team1['pointsFor'] / team1['gamesPlayed'])) / 2)
    else:
        expected1Score = startingExpectedPointsAgainst
    
    if team2['gamesPlayed'] != 0 and team1['gamesPlayed'] != 0:
        expected2Score = expectedPoints(team2['offRank'], team1['defRank'], ((team1['pointsAgainst'] / team1['gamesPlayed']) + (team2['pointsFor'] / team2['gamesPlayed'])) / 2)
    else:
        expected2Score = startingExpectedPointsAgainst

    print('(' + str(team1['offRank']) + ', ' + str(team1['defRank']) + ') vs (' + str(team2['offRank']) + ', ' + str(team2['defRank']) + ')')
    print('Expected Score: ' + str(expected1Score) + ' - ' + str(expected2Score))
    print('Score: ' + str(score1) + ' - ' + str(score2))

    actual1OffElo = calculateEloResult(expected1Score, score1)
    actual2OffElo = calculateEloResult(expected2Score, score2)
    actual1DefElo = 1 - actual2OffElo
    actual2DefElo = 1 - actual1OffElo

    print('Performance:' + team1['name'] + ' (' + str(actual1OffElo) + ', ' + str(actual1DefElo) + ') | ' + team2['name'] + ' (' + str(actual2OffElo) + ', ' + str(actual2DefElo) +')')

    team1kFactor = 32
    team2kFactor = 32
    if team2['name'] in team1['kFactors']:
        team1kFactor = team1['kFactors'][team2['name']]
    else:
        team1['kFactors'][team2['name']] = 32
    
    if team1['name'] in team2['kFactors']:
        team2kFactor = team2['kFactors'][team1['name']]
    else:
        team2['kFactors'][team1['name']] = 32
    
    team1['offRank'] = calculateNewElo(team1['offRank'], team1kFactor, expected1OffElo, actual1OffElo)
    team1['defRank'] = calculateNewElo(team1['defRank'], team1kFactor, expected1DefElo, actual1DefElo)
    team2['offRank'] = calculateNewElo(team2['offRank'], team2kFactor, expected2OffElo, actual2OffElo)
    team2['defRank'] = calculateNewElo(team2['defRank'], team2kFactor, expected2DefElo, actual2DefElo)

    print("Kfactors: ", team1kFactor, " ", team2kFactor)

    if team1['kFactors'][team2['name']] > 16:
        team1['kFactors'][team2['name']] = team1['kFactors'][team2['name']] - 8
    if team2['kFactors'][team1['name']] > 16:
        team2['kFactors'][team1['name']] = team2['kFactors'][team1['name']] - 8

    if year >= statsYearCutoff:
        team1['5yearGamesPlayed'] = team1['5yearGamesPlayed'] + 1
        team2['5yearGamesPlayed'] = team2['5yearGamesPlayed'] + 1
        team1['5yearPointsFor'] = team1['5yearPointsFor'] + score1
        team2['5yearPointsFor'] = team2['5yearPointsFor'] + score2
        team1['5yearPointsAgainst'] = team1['5yearPointsAgainst'] + score2
        team2['5yearPointsAgainst'] = team2['5yearPointsAgainst'] + score1
        if score1 > score2:
            team1['5yearWins'] = team1['5yearWins'] + 1
            team2['5yearLosses'] = team2['5yearLosses'] + 1
        elif score1 < score2:
            team1['5yearLosses'] = team1['5yearLosses'] + 1
            team2['5yearWins'] = team2['5yearWins'] + 1
        else:
            team1['5yearTies'] = team1['5yearTies'] + 1
            team2['5yearTies'] = team2['5yearTies'] + 1
        team1['5yearPointDifferential'] = team1['5yearPointDifferential'] + abs(score1 + score2)
        team2['5yearPointDifferential'] = team2['5yearPointDifferential'] + abs(score1 + score2)
    
    #Update team stats
    team1['gamesPlayed'] = team1['gamesPlayed'] + 1
    team2['gamesPlayed'] = team2['gamesPlayed'] + 1
    team1['pointsFor'] = team1['pointsFor'] + score1
    team2['pointsFor'] = team2['pointsFor'] + score2
    team1['pointsAgainst'] = team1['pointsAgainst'] + score2
    team2['pointsAgainst'] = team2['pointsAgainst'] + score1
    team1['pointDifferential'] = team1['pointDifferential'] + abs(score1 + score2)
    team2['pointDifferential'] = team2['pointDifferential'] + abs(score1 + score2)
    
    if score1 > score2:
        team1['wins'] = team1['wins'] + 1
        team2['losses'] = team2['losses'] + 1
    elif score1 < score2:
        team1['losses'] = team1['losses'] + 1
        team2['wins'] = team2['wins'] + 1
    else:
        team1['ties'] = team1['ties'] + 1
        team2['ties'] = team2['ties'] + 1

    #Modify K Factors
    team1['kFactor'] = team1['kFactor'] - 0.75
    team2['kFactor'] = team2['kFactor'] - 0.75
    
    if year >= analysisYearCutoff:
        #Ranking Analysis
        rankingAnalysis['gamesPredicted'] = rankingAnalysis['gamesPredicted'] + 1
        if round(expected1Score) == round(expected2Score) and score1 == score2:
            print('Tie predicted!')
            rankingAnalysis['winnerPredicted'] = rankingAnalysis['winnerPredicted'] + 1
            teamAccuracy[team1['name']]['gamesPredicted'] = teamAccuracy[team1['name']]['gamesPredicted'] + 1
            teamAccuracy[team2['name']]['gamesPredicted'] = teamAccuracy[team2['name']]['gamesPredicted'] + 1
        if expected1Score > expected2Score and score1 > score2:
            print('Winner predicted!')
            rankingAnalysis['winnerPredicted'] = rankingAnalysis['winnerPredicted'] + 1
            teamAccuracy[team1['name']]['gamesPredicted'] = teamAccuracy[team1['name']]['gamesPredicted'] + 1
            teamAccuracy[team2['name']]['gamesPredicted'] = teamAccuracy[team2['name']]['gamesPredicted'] + 1
        elif expected1Score < expected2Score and score1 < score2:
            print('Winner predicted!')
            rankingAnalysis['winnerPredicted'] = rankingAnalysis['winnerPredicted'] + 1
            teamAccuracy[team1['name']]['gamesPredicted'] = teamAccuracy[team1['name']]['gamesPredicted'] + 1
            teamAccuracy[team2['name']]['gamesPredicted'] = teamAccuracy[team2['name']]['gamesPredicted'] + 1
        else:
            print('Prediction missed.')
        
        if score1 == score2:
            confidence.append({"score1": round(expected1Score,1), "score2": round(expected2Score,1), "result": "tie"})
        elif score1 > score2:
            confidence.append({"score1": round(expected1Score,1), "score2": round(expected2Score,1), "result": "win"})
        else:
            confidence.append({"score1": round(expected1Score,1), "score2": round(expected2Score,1), "result": "loss"})
        
        #Seperate metric for tracking games without blowouts
        if abs(expected1Score - expected2Score) < 5:
            rankingAnalysis['pointsOffNoBlowouts'] = rankingAnalysis['pointsOffNoBlowouts'] + abs(expected1Score - score1) + abs(expected2Score - score2)
        
        #Another prediction tracker for tight games, rather than picking easy blowouts
        if abs(expected1Score - expected2Score) <= 1.5:
            rankingAnalysis['1ptGames'] = rankingAnalysis['1ptGames'] + 1
            if expected1Score - expected2Score < 0.75 and score1 == score2:
                rankingAnalysis['1ptGamesPredicted'] = rankingAnalysis['1ptGamesPredicted'] + 1
            if expected1Score > expected2Score and score1 > score2:
                rankingAnalysis['1ptGamesPredicted'] = rankingAnalysis['1ptGamesPredicted'] + 1
            elif expected1Score < expected2Score and score1 < score2:
                rankingAnalysis['1ptGamesPredicted'] = rankingAnalysis['1ptGamesPredicted'] + 1
        elif abs(expected1Score - expected2Score) <= 2.5:
            rankingAnalysis['2ptGames'] = rankingAnalysis['2ptGames'] + 1
            if expected1Score > expected2Score and score1 > score2:
                rankingAnalysis['2ptGamesPredicted'] = rankingAnalysis['2ptGamesPredicted'] + 1
            elif expected1Score < expected2Score and score1 < score2:
                rankingAnalysis['2ptGamesPredicted'] = rankingAnalysis['2ptGamesPredicted'] + 1
        elif abs(expected1Score - expected2Score) <= 3.5:
            rankingAnalysis['3ptGames'] = rankingAnalysis['3ptGames'] + 1
            if expected1Score > expected2Score and score1 > score2:
                rankingAnalysis['3ptGamesPredicted'] = rankingAnalysis['3ptGamesPredicted'] + 1
            elif expected1Score < expected2Score and score1 < score2:
                rankingAnalysis['3ptGamesPredicted'] = rankingAnalysis['3ptGamesPredicted'] + 1
        elif abs(expected1Score - expected2Score) <= 4.5:
            rankingAnalysis['4ptGames'] = rankingAnalysis['4ptGames'] + 1
            if expected1Score > expected2Score and score1 > score2:
                rankingAnalysis['4ptGamesPredicted'] = rankingAnalysis['4ptGamesPredicted'] + 1
            elif expected1Score < expected2Score and score1 < score2:
                rankingAnalysis['4ptGamesPredicted'] = rankingAnalysis['4ptGamesPredicted'] + 1
        elif abs(expected1Score - expected2Score) <= 5.5:
            rankingAnalysis['5ptGames'] = rankingAnalysis['5ptGames'] + 1
            if expected1Score > expected2Score and score1 > score2:
                rankingAnalysis['5ptGamesPredicted'] = rankingAnalysis['5ptGamesPredicted'] + 1
            elif expected1Score < expected2Score and score1 < score2:
                rankingAnalysis['5ptGamesPredicted'] = rankingAnalysis['5ptGamesPredicted'] + 1
        else:
            rankingAnalysis['blowoutGames'] = rankingAnalysis['blowoutGames'] + 1
            if expected1Score > expected2Score and score1 > score2:
                rankingAnalysis['blowoutGamesPredicted'] = rankingAnalysis['blowoutGamesPredicted'] + 1
            elif expected1Score < expected2Score and score1 < score2:
                rankingAnalysis['blowoutGamesPredicted'] = rankingAnalysis['blowoutGamesPredicted'] + 1
        
        rankingAnalysis['pointsOff'] = rankingAnalysis['pointsOff'] + abs(expected1Score - score1) + abs(expected2Score - score2)

        allMatches.append({
            "year": year,
            "team1": team1['name'],
            "team2": team2['name'],
            "team1Score": score1,
            "team2Score": score2,
            "expected1Score": expected1Score,
            "expected2Score": expected2Score,
            "team1ExpOff": expected1OffElo,
            "team1ExpDef": expected1DefElo,
            "team2ExpOff": expected2OffElo,
            "team2ExpDef": expected2DefElo,
            "team1ActOff": actual1OffElo,
            "team1ActDef": actual1DefElo,
            "team2ActOff": actual2OffElo,
            "team2ActDef": actual2DefElo
        })

for x in range(startYear, endYear):
    #Each year, reset kFactors
    for team in teamData:
        for opp in teamData[team]['kFactors']:
            if teamData[team]['kFactors'][opp] + 2 <= 32:
                teamData[team]['kFactors'][opp] = teamData[team]['kFactors'][opp] + 4
    with open('./CombinedSchedules/' + str(x) + '.json') as f:
        data = list(json.load(f))
        for match in data:
            #print(match)
            team1 = {
                'name': match['team1'],
                'offRank': 1500,
                'defRank': 1500,
                'gamesPlayed': 0,
                'wins': 0,
                'losses': 0,
                'ties': 0,
                'pointsFor': 0,
                'pointsAgainst': 0,
                'kFactor': 32,
                'kFactors': {},
                'pointDifferential': 0,

                '5yearGamesPlayed': 0,
                '5yearPointsFor': 0,
                '5yearPointsAgainst': 0,
                '5yearWins': 0,
                '5yearLosses': 0,
                '5yearTies': 0,
                '5yearPointDifferential': 0,
            }
            team2 = {
                'name': match['team2'],
                'offRank': 1500,
                'defRank': 1500,
                'gamesPlayed': 0,
                'wins': 0,
                'losses': 0,
                'ties': 0,
                'pointsFor': 0,
                'pointsAgainst': 0,
                'kFactor': 32,
                'kFactors': {},
                'pointDifferential': 0,

                '5yearGamesPlayed': 0,
                '5yearPointsFor': 0,
                '5yearPointsAgainst': 0,
                '5yearWins': 0,
                '5yearLosses': 0,
                '5yearTies': 0,
                '5yearPointDifferential': 0,
            }
            if match['team1'] in teamData:
                team1 = teamData[match['team1']]
            else:
                teamData[match['team1']] = team1
            if match['team2'] in teamData:
                team2 = teamData[match['team2']]
            else:
                teamData[match['team2']] = team2
            analyseMatch(team1, team2, match['team1Score'], match['team2Score'], x)

#Clear kFactors to clean up output
for team in teamData:
    teamData[team]['kFactors'] = 0

formattedTeamData = []
for team in teamData:
    formattedTeamData.append(teamData[team])

with open('./FinalRatings.json', 'w') as f:
    json.dump(formattedTeamData, f, ensure_ascii=False, indent=4)

with open('./RankingAnalysis.json', 'w') as f:
    json.dump(rankingAnalysis, f, ensure_ascii=False, indent=4)

formattedAcuracyData = []
for team in teamAccuracy:
    formattedAcuracyData.append(teamAccuracy[team])

with open('./TeamAccuracy.json', 'w') as f:
    json.dump(formattedAcuracyData, f, ensure_ascii=False, indent=4)

with open('./Confidence.json', 'w') as f:
    json.dump(confidence, f, ensure_ascii=False, indent=4)

with open('./AllMatches.json', 'w') as f:
    json.dump(allMatches, f, ensure_ascii=False, indent=4)
            