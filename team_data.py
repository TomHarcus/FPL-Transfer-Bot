import requests
import pandas as pd
import json

def get_current_gameweek():
    fpl_current_season_data = 'https://fantasy.premierleague.com/api/bootstrap-static/'
    response = requests.get(fpl_current_season_data)
    data = response.json()

    for gameweek_info in data['events']:
        if gameweek_info['is_current']:
            return gameweek_info['id']


def get_user_team_data(manager_id):

    fpl_current_season_data = 'https://fantasy.premierleague.com/api/bootstrap-static/'
    response = requests.get(fpl_current_season_data)
    data = response.json()

    players_df = pd.DataFrame(data['elements'])
    positions_map = {row['id']: row['singular_name_short'] for row in data['element_types']}
    teams_map = {row['id']: row['short_name'] for row in data['teams']}
    
    current_gameweek = next((gw['id'] for gw in data['events'] if gw['is_current']), None)
    if not current_gameweek:
        return "Could not determine current gameweek."

    try:
        team_id = manager_id
        user_team_url = f'https://fantasy.premierleague.com/api/entry/{team_id}/event/{current_gameweek}/picks/'
        user_team_response = requests.get(user_team_url)
        user_team_response.raise_for_status()
        user_team_data = user_team_response.json()


        picks_list = user_team_data.get('picks', [])
        user_player_ids = [pick['element'] for pick in picks_list]

        user_team_df = players_df[players_df['id'].isin(user_player_ids)].copy()

        id_to_lineup_position_map = {pick['element']: pick['position'] for pick in picks_list}

        user_team_df['position'] = user_team_df['element_type'].map(positions_map)
        user_team_df['team_name'] = user_team_df['team'].map(teams_map)
        user_team_df['price'] = user_team_df['now_cost'] / 10
        user_team_df['lineup_position'] = user_team_df['id'].map(id_to_lineup_position_map)
        user_team_df['lineup_position'] = user_team_df['lineup_position'].fillna(99) # Handle missing values
        user_team_df['status'] = user_team_df['lineup_position'].apply(
            lambda pos: 'Starting' if pos <= 11 else 'Benched'
        )

        sorted_user_team_df = user_team_df.sort_values(by='lineup_position')

        user_team_string = sorted_user_team_df[
            ['web_name', 'team_name', 'position', 'price', 'status']
        ].to_string(index=False)
        
        return user_team_string

    except (requests.exceptions.RequestException, json.JSONDecodeError) as e:
        error_message = f"Error fetching data for team ID {manager_id}. The ID might be invalid. Error: {e}"
        print(error_message)
        return error_message


def manager_summary(manager_id, current_gameweek):
    manager_url = f'https://fantasy.premierleague.com/api/entry/{manager_id}/'
    manager_data = requests.get(manager_url)

    transfers_url = f' https://fantasy.premierleague.com/api/entry/{manager_id}/event/{current_gameweek-1}/picks/'
    transfers_data = requests.get(transfers_url)

    manager_json = json.loads(manager_data.text)

    manager_name = manager_json['player_first_name']

    transfers_json = json.loads(transfers_data.text)

    last_gw_transfers = transfers_json.get('event_transfers', 0)
    chip_played = transfers_json.get('active_chip', None)

    if (last_gw_transfers == 0 and chip_played == None and current_gameweek != 1):
        no_free_transfers = 2
    else:
        no_free_transfers = 1


    return manager_name, no_free_transfers





