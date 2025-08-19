import requests
import pandas as pd

def get_user_team_data():

    fpl_current_season_data = 'https://fantasy.premierleague.com/api/bootstrap-static/'
    response = requests.get(fpl_current_season_data)
    data = response.json()

    players_df = pd.DataFrame(data['elements'])
    teams_df = pd.DataFrame(data['teams'])

    positions_map = {
        row['id']: row['singular_name_short']
        for row in data['element_types']
    }

    teams_map = {
        row['id']: row['short_name']
        for row in data['teams']
    }

    current_gameweek = None

    for gameweek in data['events']:
        if gameweek['is_current']:
            current_gameweek = gameweek['id']
            break

    team_id = int(input("Please enter your team ID: "))

    user_team_url = f'https://fantasy.premierleague.com/api/entry/{team_id}/event/{current_gameweek}/picks/'
    user_team = requests.get(user_team_url)

    user_team_data = user_team.json()

    user_player_ids = [pick['element'] for pick in user_team_data['picks']]


    user_team_df = players_df[players_df['id'].isin(user_player_ids)].copy()

    #print(user_team_df.columns)

    user_team_df['position'] = user_team_df['element_type'].map(positions_map)
    user_team_df['team_name'] = user_team_df['team'].map(teams_map)
    user_team_df['price'] = user_team_df['now_cost'] / 10

    sorted_user_team_df = user_team_df.sort_values(by='element_type')

    user_team_string = sorted_user_team_df[['web_name', 'team_name', 'position', 'price', 'points_per_game_rank']].to_string(index=False)

    print(user_team_string)
    return user_team_string


