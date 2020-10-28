import json
from pprint import pprint


teamStyles = []

with open('./FinalRatings.json') as f:
    data = list(json.load(f))
    for team in data:
        if team['5yearGamesPlayed'] >= 50:
            style = {
                'name': team['name'],
                'style': ""
            }

            ovrRank = (team['offRank'] + team['defRank']) / 2
            wltRatio = (team['5yearWins'] + team['5yearTies']*0.5) / (team['5yearGamesPlayed'])
            shootoutIndex = team['5yearPointDifferential'] / team['5yearGamesPlayed']
            closenessIndex = (team['5yearPointsFor'] / team['5yearGamesPlayed']) - (team['5yearPointsAgainst'] / team['5yearGamesPlayed'])

            if ovrRank >= 1545.31:
                if wltRatio > 0.65:
                    if team['offRank'] > 1557.36:
                        if team['defRank'] > 1544.96:
                            style['style'] = 'Powerhouse'
                        else:
                            style['style'] = 'Offensive Powerhouse'
                    else:
                        if team['defRank'] > 1544.96:
                            style['style'] = 'Defensive Powerhouse'
                else:
                    style['style'] = 'Superhot'
            else:
                if ovrRank > 1505.19:
                    if wltRatio >= 0.75:
                        style['style'] = 'Consistent Dominance'
                    elif wltRatio < 0.3:
                        style['style'] = 'Erratic Dominance'
                    else:
                        if shootoutIndex > 5.5:
                            if closenessIndex > 1:
                                style['style'] = 'Blowout Dealer'
                            elif closenessIndex < -2:
                                style['style'] = 'Blowout Receiver'
                            else:
                                style['style'] = 'Shootout Mania'
                        elif shootoutIndex < 4:
                            if closenessIndex > 1:
                                style['style'] = 'Brick Wall'
                            elif closenessIndex < -2:
                                style['style'] = 'Hard-Stuck'
                            else:
                                style['style'] = 'Slugger'
                        else:
                            if closenessIndex > 1:
                                style['style'] = 'Resiliant'
                            elif closenessIndex < -2:
                                style['style'] = 'Delicate'
                            else:
                                style['style'] = 'Even Fighter'
                else:
                    if wltRatio >= 0.75:
                        style['style'] = 'Big Fish Small Pond'
                    elif wltRatio < 0.3:
                        style['style'] = 'Small Fish Small Pond'
                    else:
                        if shootoutIndex > 5.5:
                            if closenessIndex > 1:
                                style['style'] = 'Cupcake Killer'
                            elif closenessIndex < -2:
                                style['style'] = 'Pourous Defense'
                            else:
                                style['style'] = 'Small Town Battler'
                        elif shootoutIndex < 4:
                            if closenessIndex > 1:
                                style['style'] = 'Local Stalwart'
                            elif closenessIndex < -2:
                                style['style'] = 'Missing Pieces'
                            else:
                                style['style'] = 'Low-key'
                        else:
                            if closenessIndex > 1:
                                style['style'] = 'Tough Small Guys'
                            elif closenessIndex < -2:
                                style['style'] = 'Tough Breaks'
                            else:
                                style['style'] = 'Local Derbies'
            
            teamStyles.append(style)


with open('./ProgramStyles.json', 'w') as f:
    json.dump(teamStyles, f, ensure_ascii=False, indent=4)