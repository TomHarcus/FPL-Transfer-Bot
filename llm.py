import os
import google.generativeai as genai
import json

from get_data import get_data
import team_data


try:
    genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
except KeyError:
    print("no api key")
    exit()

current_gameweek = get_current_gameweek()

manager_id = int(input('Enter team ID: '))
user_team = get_user_team_data(manager_id)


summary_22_23, summary_23_24, top_players = get_data()

manager_name, no_of_transfers = manager_summary(manager_id, current_gameweek)

master_prompt = f"""
Hello my name is {manager_name}.
You are an expert Fantasy Premier League manager. Your task is to analyze the provided data and suggest the single best transfer for my team for the upcoming gameweek.

Here is my current FPL team for the 25/26 season:
{user_team}

I currently have {no_of_transfers} free transfers and it is gameweek: {current_gameweek}

The field points_per_game_rank is the players rank in number of points scored (the lower the better) so take this into account

Here are the top-performing players based on CURRENT FORM and EXPECTED POINTS (ep_next):
{top_players}

Here is a summary of the top-performing players from the 23/24 season. Use this to understand a player's long-term quality:
{summary_23_24}

Here is a summary of the top-performing players from the 22/23 season. Use this for additional historical context:
{summary_22_23}

Sadly the data for last season (24/25) was corrupt so it could not be used. Also just keep this in mind in making your decision.

**TASK:**
Greet {manager_name}.
Based on all of the above data, suggest the single best transfer for my team.
Your reasoning should be based on a player's proven historical performance, their current hot form, and their potential for the next match (ep_next).
You MUST ignore any players from the historical data who are no longer in the Premier League (like Harry Kane). 
But assume all players in my current FPL team are playing in the Premier League (recognise your data cut off point as its now late 2025)
Your final recommendation must only include players who are currently active in the Premier League.
Both players have to be from the same position and be of similar price points as there is a 100 million budget.

Format your final answer ONLY as a JSON object with the following structure:
{{
  "player_to_sell": {{ "name": "Player Name" }},
  "player_to_buy": {{ "name": "Player Name" }},
  "justification": "Your detailed reasoning here."
}}
"""


print("\nUsing AI to calculate best transfer...")
try:
    generation_config = genai.types.GenerationConfig(
        response_mime_type="application/json"
    )
    model = genai.GenerativeModel("gemini-2.5-flash", generation_config=generation_config)
    
    response = model.generate_content(master_prompt)
    
    recommendation_json = json.loads(response.text)

    print(" FPL AI Transfer Recommendation")
    print("")
    print(f"SELL:  {recommendation_json['player_to_sell']['name']}")
    print(f"BUY:   {recommendation_json['player_to_buy']['name']}")
    print("\nAI Justification:")
    print(recommendation_json['justification'])

except Exception as e:
    print(f"\nAn error occurred while calling the Gemini API: {e}")