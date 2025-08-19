import pandas as pd
import requests
import streamlit as st

@st.cache_data(ttl=3600)
def get_data():

    fpl_current_season_data = 'https://fantasy.premierleague.com/api/bootstrap-static/'
    response = requests.get(fpl_current_season_data)
    data = response.json()
    players_df = pd.DataFrame(data['elements'])

    url_22_23 = 'https://raw.githubusercontent.com/vaastav/Fantasy-Premier-League/master/data/2022-23/gws/merged_gw.csv'
    url_23_24 = 'https://raw.githubusercontent.com/vaastav/Fantasy-Premier-League/master/data/2023-24/gws/merged_gw.csv'

    full_df_22_23 = pd.read_csv(url_22_23)
    full_df_23_24 = pd.read_csv(url_23_24)


    player_season_22_23 = full_df_22_23.groupby(['name', 'element']).agg(
        position=('position', 'last'),
        total_points=('total_points', 'sum'),
        goals_scored=('goals_scored', 'sum'),
        expected_goals=('expected_goals', 'sum'),
        assists=('assists', 'sum'),
        expected_assists=('expected_assists', 'sum'),
        minutes=('minutes', 'sum')
    ).reset_index()

    player_season_23_24 = full_df_23_24.groupby(['name', 'element']).agg(
        position=('position', 'last'),
        total_points=('total_points', 'sum'),
        goals_scored=('goals_scored', 'sum'),
        expected_goals=('expected_goals', 'sum'),
        assists=('assists', 'sum'),
        expected_assists=('expected_assists', 'sum'),
        minutes=('minutes', 'sum'),
    ).reset_index()



    filtered_player_season_22_23 = player_season_22_23[player_season_22_23['minutes'] > 600].copy()
    summary_22_23 = filtered_player_season_22_23.sort_values(by='total_points', ascending=False)

    filtered_player_season_23_24 = player_season_23_24[player_season_23_24['minutes'] > 600].copy()
    summary_23_24 = filtered_player_season_23_24.sort_values(by='total_points', ascending=False)


    string_summary_22_23 = summary_22_23.head(100).to_string()
    string_summary_23_24 = summary_23_24.head(100).to_string()

    top_form_players = players_df.sort_values(by='form', ascending=False).head(100)
    top_form_players_string = top_form_players[['web_name', 'form', 'now_cost', 'ep_next']].to_string(index=False)

    
    return string_summary_22_23, string_summary_23_24, top_form_players_string

    