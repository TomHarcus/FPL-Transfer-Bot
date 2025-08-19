import streamlit as st
from get_data import get_data
from team_data import get_current_gameweek, get_user_team_data, manager_summary
from llm import get_ai_recommendation


st.set_page_config(page_title="FPL AI Advisor", layout="centered")

if 'recommendation' not in st.session_state:
    st.session_state.recommendation = None
if 'manager_name' not in st.session_state:
    st.session_state.manager_name = None


st.title("FPL AI Transfer Advisor")
st.divider()

manager_id_input = st.text_input("Enter your FPL Team ID:", placeholder="e.g., 12345678")

if st.button("Get My Recommendation", type="primary", use_container_width=True):
    if manager_id_input:
        try:
            manager_id = int(manager_id_input)
            with st.spinner("Analyzing your team, historical data, and current form... This might take a moment."):
                current_gameweek = get_current_gameweek()
                user_team_string = get_user_team_data(manager_id)
                summary_22_23, summary_23_24, top_players_string = get_data()
                manager_name, no_of_transfers = manager_summary(manager_id, current_gameweek)
                
                st.session_state.manager_name = manager_name 
                
                if "Error" in user_team_string:
                    st.session_state.recommendation = {"error": user_team_string}
                else:
                    st.session_state.recommendation = get_ai_recommendation(
                        user_team_string, top_players_string, summary_23_24,
                        summary_22_23, manager_name, no_of_transfers, current_gameweek
                    )
        except ValueError:
            st.session_state.recommendation = {"error": "Please enter a valid, numerical Team ID."}
        except Exception as e:
            st.session_state.recommendation = {"error": f"An unexpected error occurred: {e}"}
        
    else:
        st.warning("Please enter a Team ID to get started.")


st.divider()

if st.session_state.recommendation:
    recommendation = st.session_state.recommendation
    
    if "error" in recommendation:
        st.error(f"**An error occurred:** {recommendation['error']}")
    else:
        st.success("Analysis Complete! Here is your recommendation:")
        
        manager_name = st.session_state.manager_name
        
        with st.container(border=True):
            st.markdown(f"#### Recommendation for **{manager_name}**")
            
            for transfer in recommendation.get('transfers', []):
                col1, col2 = st.columns(2)
                with col1:
                    st.metric(label="SELL", value=transfer['player_to_sell']['name'])
                with col2:
                    st.metric(label="BUY", value=transfer['player_to_buy']['name'])
            
            st.markdown("---") 
            st.markdown("**AI Justification:**")
            st.write(recommendation['justification'])
else:
    st.info("An AI-powered recommendation will appear here once you click the button.")