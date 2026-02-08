import streamlit as st
import requests
import time

st.set_page_config(page_title="Scanner Gol Live", layout="wide")
st.title("Alerta Gol Prima Repriza")

def reda_sunet():
    sunet_url = "https://www.soundjay.com/buttons/sounds/button-3.mp3"
    html_string = f'<audio autoplay><source src="{sunet_url}" type="audio/mp3"></audio>'
    st.markdown(html_string, unsafe_allow_html=True)

# Introdu cheia ta API aici
API_KEY = "CHEIA_TA_AICI"
URL = "https://v3.football.api-sports.io/fixtures?live=all"
HEADERS = {"x-apisports-key": API_KEY}

st.sidebar.header("Setari Alerte")
min_atacuri = st.sidebar.number_input("Atacuri Periculoase", value=20)
min_suturi = st.sidebar.number_input("Suturi pe poarta", value=2)
min_cornere = st.sidebar.number_input("Cornere minime", value=3)
auto_refresh = st.sidebar.checkbox("Scanare automata la 2 minute")

def executa_scanare():
    try:
        response = requests.get(URL, headers=HEADERS)
        data = response.json()
        meciuri_gasite = 0
        
        for fixture in data.get("response", []):
            timp = fixture["fixture"]["status"]["elapsed"]
            scor_h = fixture["goals"]["home"]
            scor_a = fixture["goals"]["away"]
            
            if 15 <= timp <= 35 and scor_h == 0 and scor_a == 0:
                f_id = fixture["fixture"]["id"]
                stats_url = f"https://v3.football.api-sports.io/fixtures/statistics?fixture={f_id}"
                stats_res = requests.get(stats_url, headers=HEADERS).json()
                
                if stats_res["response"]:
                    suturi, atacuri, cornere = 0, 0, 0
                    for echipa in stats_res["response"]:
                        for s in echipa["statistics"]:
                            if s["type"] == "Shots on Goal": suturi += (s["value"] or 0)
                            if s["type"] == "Dangerous Attacks": atacuri += (s["value"] or 0)
                            if s["type"] == "Corner Kicks": cornere += (s["value"] or 0)

                    if atacuri >= min_atacuri and suturi >= min_suturi and cornere >= min_cornere:
                        st.success(f"Meci: {fixture['teams']['home']['name']} vs {fixture['teams']['away']['name']}")
                        st.write(f"Minut: {timp} | Atacuri: {atacuri} | Suturi: {suturi} | Cornere: {cornere}")
                        meciuri_gasite += 1
        
        if meciuri_gasite > 0:
            reda_sunet()
            st.balloons()
            
    except Exception as e:
        st.error(f"Eroare: {e}")

if st.button("Scaneaza acum") or auto_refresh:
    executa_scanare()
    if auto_refresh:
        time.sleep(120)
        st.rerun()
