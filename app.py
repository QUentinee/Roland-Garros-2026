import streamlit as st
import requests
import json
import base64
from datetime import datetime
import time

st.set_page_config(page_title="Paris Roland-Garros 2026", page_icon="🎾", layout="wide")

# ── Base joueurs : prénom, pays (ISO2), classement ATP ────────────────────────
# Clé = nom tel qu'utilisé dans les matchs. Édite librement les classements.
PLAYERS = {
    "Sinner":            {"first": "Jannik",        "country": "IT", "rank": 1},
    "Tabur":             {"first": "Arthur",        "country": "FR", "rank": 280},
    "Fearnley":          {"first": "Jacob",         "country": "GB", "rank": 52},
    "Cerundolo J.M.":    {"first": "Juan Manuel",   "country": "AR", "rank": 95},
    "Landaluce":         {"first": "Martin",        "country": "ES", "rank": 140},
    "Kopriva":           {"first": "Vit",           "country": "CZ", "rank": 105},
    "Moutet":            {"first": "Corentin",      "country": "FR", "rank": 68},
    "Rinderknech":       {"first": "Arthur",        "country": "FR", "rank": 58},
    "Rodionov":          {"first": "Jurij",         "country": "AT", "rank": 155},
    "Fucsovics":         {"first": "Marton",        "country": "HU", "rank": 92},
    "Berrettini":        {"first": "Matteo",        "country": "IT", "rank": 32},
    "Quinn":             {"first": "Ethan",         "country": "US", "rank": 125},
    "Comesana":          {"first": "Francisco",     "country": "AR", "rank": 72},
    "Ofner":             {"first": "Sebastian",     "country": "AT", "rank": 105},
    "Darderi":           {"first": "Luciano",       "country": "IT", "rank": 38},
    "Bublik":            {"first": "Alexander",     "country": "KZ", "rank": 24},
    "Struff":            {"first": "Jan-Lennard",   "country": "DE", "rank": 54},
    "Shapovalov":        {"first": "Denis",         "country": "CA", "rank": 29},
    "Munar":             {"first": "Jaume",         "country": "ES", "rank": 49},
    "Hurkacz":           {"first": "Hubert",        "country": "PL", "rank": 21},
    "Spizzirri":         {"first": "Eliot",         "country": "US", "rank": 82},
    "Tiafoe":            {"first": "Frances",       "country": "US", "rank": 23},
    "Griekspoor":        {"first": "Tallon",        "country": "NL", "rank": 36},
    "Arnaldi":           {"first": "Matteo",        "country": "IT", "rank": 46},
    "Muller A.":         {"first": "Alexandre",     "country": "FR", "rank": 41},
    "Tsitsipas":         {"first": "Stefanos",      "country": "GR", "rank": 12},
    "Collignon":         {"first": "Raphael",       "country": "BE", "rank": 88},
    "Vukic":             {"first": "Aleksandar",    "country": "AU", "rank": 71},
    "Merida":            {"first": "Daniel",        "country": "ES", "rank": 195},
    "Shelton":           {"first": "Ben",           "country": "US", "rank": 6},
    "Auger-Aliassime":   {"first": "Felix",         "country": "CA", "rank": 10},
    "Altmaier":          {"first": "Daniel",        "country": "DE", "rank": 55},
    "Baez":              {"first": "Sebastian",     "country": "AR", "rank": 37},
    "Burruchaga":        {"first": "Roman Andres",  "country": "AR", "rank": 112},
    "Van Assche":        {"first": "Luca",          "country": "FR", "rank": 120},
    "Kypson":            {"first": "Patrick",       "country": "US", "rank": 145},
    "Bautista Agut":     {"first": "Roberto",       "country": "ES", "rank": 65},
    "Nakashima":         {"first": "Brandon",       "country": "US", "rank": 31},
    "Norrie":            {"first": "Cameron",       "country": "GB", "rank": 67},
    "Vallejo":           {"first": "Daniel",        "country": "PY", "rank": 185},
    "Cilic":             {"first": "Marin",         "country": "HR", "rank": 95},
    "Kouame":            {"first": "Eliakim",       "country": "FR", "rank": 180},
    "Tabilo":            {"first": "Alejandro",     "country": "CL", "rank": 33},
    "Majchrzak":         {"first": "Kamil",         "country": "PL", "rank": 78},
    "Faurel":            {"first": "Hugo",          "country": "FR", "rank": 310},
    "Vacherot":          {"first": "Valentin",      "country": "MC", "rank": 40},
    "Cobolli":           {"first": "Flavio",        "country": "IT", "rank": 19},
    "Pellegrino":        {"first": "Andrea",        "country": "IT", "rank": 158},
    "Wu Yibing":         {"first": "Yibing",        "country": "CN", "rank": 152},
    "Giron":             {"first": "Marcos",        "country": "US", "rank": 51},
    "Diaz Acosta":       {"first": "Facundo",       "country": "AR", "rank": 84},
    "Zhang Z.":          {"first": "Zhizhen",       "country": "CN", "rank": 73},
    "Garin":             {"first": "Cristian",      "country": "CL", "rank": 102},
    "Tien":              {"first": "Learner",       "country": "US", "rank": 34},
    "Cerundolo F.":      {"first": "Francisco",     "country": "AR", "rank": 22},
    "Van de Zandschulp": {"first": "Botic",         "country": "NL", "rank": 80},
    "Gaston":            {"first": "Hugo",          "country": "FR", "rank": 99},
    "Monfils":           {"first": "Gael",          "country": "FR", "rank": 48},
    "Popyrin":           {"first": "Alexei",        "country": "AU", "rank": 28},
    "Svajda":            {"first": "Zachary",       "country": "US", "rank": 115},
    "Walton":            {"first": "Adam",          "country": "AU", "rank": 86},
    "Medvedev":          {"first": "Daniil",        "country": "RU", "rank": 13},
    "De Minaur":         {"first": "Alex",          "country": "AU", "rank": 7},
    "Samuel":            {"first": "Ethan",         "country": "AU", "rank": 260},
    "Blockx":            {"first": "Alexander",     "country": "BE", "rank": 104},
    "Navone":            {"first": "Mariano",       "country": "AR", "rank": 74},
    "Brooksby":          {"first": "Jenson",        "country": "US", "rank": 83},
    "Droguet":           {"first": "Titouan",       "country": "FR", "rank": 210},
    "Mensik":            {"first": "Jakub",         "country": "CZ", "rank": 17},
    "Etcheverry":        {"first": "Tomas Martin",  "country": "AR", "rank": 53},
    "Borges":            {"first": "Nuno",          "country": "PT", "rank": 42},
    "Kecmanovic":        {"first": "Miomir",        "country": "RS", "rank": 56},
    "Marozsan":          {"first": "Fabian",        "country": "HU", "rank": 61},
    "Nava":              {"first": "Emilio",        "country": "US", "rank": 155},
    "Ugo Carabelli":     {"first": "Camilo",        "country": "AR", "rank": 79},
    "Buse":              {"first": "Ignacio",       "country": "PE", "rank": 205},
    "Rublev":            {"first": "Andrey",        "country": "RU", "rank": 15},
    "Ruud":              {"first": "Casper",        "country": "NO", "rank": 9},
    "Safiullin":         {"first": "Roman",         "country": "RU", "rank": 81},
    "Medjedovic":        {"first": "Hamad",         "country": "RS", "rank": 69},
    "Hanfmann":          {"first": "Yannick",       "country": "DE", "rank": 108},
    "Sonego":            {"first": "Lorenzo",       "country": "IT", "rank": 45},
    "Herbert":           {"first": "Pierre-Hugues", "country": "FR", "rank": 245},
    "Hijikata":          {"first": "Rinky",         "country": "AU", "rank": 76},
    "Paul":              {"first": "Tommy",         "country": "US", "rank": 14},
    "Fonseca":           {"first": "Joao",          "country": "BR", "rank": 26},
    "Pavlovic":          {"first": "Marko",         "country": "RS", "rank": 215},
    "Prizmic":           {"first": "Dino",          "country": "HR", "rank": 87},
    "Dellien":           {"first": "Hugo",          "country": "BO", "rank": 150},
    "Royer":             {"first": "Valentin",      "country": "FR", "rank": 118},
    "Mpetshi Perricard": {"first": "Giovanni",      "country": "FR", "rank": 35},
    "Djokovic":          {"first": "Novak",         "country": "RS", "rank": 5},
    "Fritz":             {"first": "Taylor",        "country": "US", "rank": 4},
    "Basavareddy":       {"first": "Nishesh",       "country": "US", "rank": 66},
    "Shevchenko":        {"first": "Alexander",     "country": "KZ", "rank": 89},
    "Michelsen":         {"first": "Alex",          "country": "US", "rank": 30},
    "Duckworth":         {"first": "James",         "country": "AU", "rank": 160},
    "Diallo":            {"first": "Gabriel",       "country": "CA", "rank": 39},
    "Kovacevic":         {"first": "Aleksandar",    "country": "US", "rank": 75},
    "Jodar":             {"first": "Carlos",        "country": "ES", "rank": 250},
    "Davidovich Fokina": {"first": "Alejandro",     "country": "ES", "rank": 20},
    "Dzumhur":           {"first": "Damir",         "country": "BA", "rank": 70},
    "Llamas Ruiz":       {"first": "Pablo",         "country": "ES", "rank": 110},
    "Tirante":           {"first": "Thiago Agustin","country": "AR", "rank": 100},
    "Kokkinakis":        {"first": "Thanasi",       "country": "AU", "rank": 85},
    "Atmane":            {"first": "Terence",       "country": "FR", "rank": 64},
    "Carreno Busta":     {"first": "Pablo",         "country": "ES", "rank": 130},
    "Lehecka":           {"first": "Jiri",          "country": "CZ", "rank": 18},
    "Khachanov":         {"first": "Karen",         "country": "RU", "rank": 16},
    "Gea":               {"first": "Pol Martin",    "country": "ES", "rank": 240},
    "Jacquet":           {"first": "Kyrian",        "country": "FR", "rank": 200},
    "Trungelliti":       {"first": "Marco",         "country": "AR", "rank": 220},
    "Cina":              {"first": "Federico",      "country": "IT", "rank": 230},
    "Opelka":            {"first": "Reilly",        "country": "US", "rank": 63},
    "Wawrinka":          {"first": "Stan",          "country": "CH", "rank": 145},
    "Fils":              {"first": "Arthur",        "country": "FR", "rank": 11},
    "Humbert":           {"first": "Ugo",           "country": "FR", "rank": 25},
    "Mannarino":         {"first": "Adrian",       "country": "FR", "rank": 91},
    "Halys":             {"first": "Quentin",       "country": "FR", "rank": 77},
    "Bellucci":          {"first": "Mattia",        "country": "IT", "rank": 62},
    "Machac":            {"first": "Tomas",         "country": "CZ", "rank": 27},
    "Bergs":             {"first": "Zizou",         "country": "BE", "rank": 44},
    "Bonzi":             {"first": "Benjamin",      "country": "FR", "rank": 50},
    "Zverev":            {"first": "Alexander",     "country": "DE", "rank": 3},
}

def flag(country_iso2: str) -> str:
    """Convertit un code ISO2 en emoji drapeau."""
    if not country_iso2 or len(country_iso2) != 2:
        return "🏳️"
    return chr(0x1F1E6 + ord(country_iso2[0].upper()) - ord("A")) + \
           chr(0x1F1E6 + ord(country_iso2[1].upper()) - ord("A"))

def player_info(name: str):
    p = PLAYERS.get(name, {"first": "", "country": "", "rank": 999}).copy()
    # Classements fetchés depuis ESPN, stockés dans data["rankings"]
    fetched = st.session_state.get("data", {}).get("rankings", {})
    last = name.split()[-1]
    rank_override = fetched.get(name) or fetched.get(last)
    if rank_override:
        p["rank"] = rank_override
    return p

def player_label(name: str) -> str:
    p = player_info(name)
    fl = flag(p["country"])
    first = p["first"]
    rank = p["rank"]
    rank_str = f"#{rank}" if rank and rank < 999 else "NC"
    full = f"{first} {name}".strip()
    return f"{fl} {full} ({rank_str})"

# ── Tous les matchs du 1er tour depuis le PDF ─────────────────────────────────
PREMIER_TOUR = [
    {"id":1,  "ja":"Sinner",           "jb":"Tabur"},
    {"id":2,  "ja":"Fearnley",         "jb":"Cerundolo J.M."},
    {"id":3,  "ja":"Landaluce",        "jb":"Kopriva"},
    {"id":4,  "ja":"Moutet",           "jb":"Rinderknech"},
    {"id":5,  "ja":"Rodionov",         "jb":"Fucsovics"},
    {"id":6,  "ja":"Berrettini",       "jb":"Quinn"},
    {"id":7,  "ja":"Comesana",         "jb":"Ofner"},
    {"id":8,  "ja":"Darderi",          "jb":"Bublik"},
    {"id":9,  "ja":"Struff",           "jb":"Shapovalov"},
    {"id":10, "ja":"Munar",            "jb":"Hurkacz"},
    {"id":11, "ja":"Spizzirri",        "jb":"Tiafoe"},
    {"id":12, "ja":"Griekspoor",       "jb":"Arnaldi"},
    {"id":13, "ja":"Muller A.",        "jb":"Tsitsipas"},
    {"id":14, "ja":"Collignon",        "jb":"Vukic"},
    {"id":15, "ja":"Merida",           "jb":"Shelton"},
    {"id":16, "ja":"Auger-Aliassime",  "jb":"Altmaier"},
    {"id":17, "ja":"Baez",             "jb":"Burruchaga"},
    {"id":18, "ja":"Van Assche",       "jb":"Kypson"},
    {"id":19, "ja":"Bautista Agut",    "jb":"Nakashima"},
    {"id":20, "ja":"Norrie",           "jb":"Vallejo"},
    {"id":21, "ja":"Cilic",            "jb":"Kouame"},
    {"id":22, "ja":"Tabilo",           "jb":"Majchrzak"},
    {"id":23, "ja":"Faurel",           "jb":"Vacherot"},
    {"id":24, "ja":"Cobolli",          "jb":"Pellegrino"},
    {"id":25, "ja":"Wu Yibing",        "jb":"Giron"},
    {"id":26, "ja":"Diaz Acosta",      "jb":"Zhang Z."},
    {"id":27, "ja":"Garin",            "jb":"Tien"},
    {"id":28, "ja":"Cerundolo F.",     "jb":"Van de Zandschulp"},
    {"id":29, "ja":"Gaston",           "jb":"Monfils"},
    {"id":30, "ja":"Popyrin",          "jb":"Svajda"},
    {"id":31, "ja":"Walton",           "jb":"Medvedev"},
    {"id":32, "ja":"De Minaur",        "jb":"Samuel"},
    {"id":33, "ja":"Blockx",           "jb":"Navone"},
    {"id":34, "ja":"Brooksby",         "jb":"Droguet"},
    {"id":35, "ja":"Mensik",           "jb":"Etcheverry"},
    {"id":36, "ja":"Borges",           "jb":"Kecmanovic"},
    {"id":37, "ja":"Marozsan",         "jb":"Nava"},
    {"id":38, "ja":"Ugo Carabelli",    "jb":"Buse"},
    {"id":39, "ja":"Rublev",           "jb":"Ruud"},
    {"id":40, "ja":"Safiullin",        "jb":"Medjedovic"},
    {"id":41, "ja":"Hanfmann",         "jb":"Sonego"},
    {"id":42, "ja":"Herbert",          "jb":"Hijikata"},
    {"id":43, "ja":"Paul",             "jb":"Fonseca"},
    {"id":44, "ja":"Pavlovic",         "jb":"Prizmic"},
    {"id":45, "ja":"Dellien",          "jb":"Royer"},
    {"id":46, "ja":"Mpetshi Perricard","jb":"Djokovic"},
    {"id":47, "ja":"Fritz",            "jb":"Basavareddy"},
    {"id":48, "ja":"Shevchenko",       "jb":"Michelsen"},
    {"id":49, "ja":"Duckworth",        "jb":"Diallo"},
    {"id":50, "ja":"Kovacevic",        "jb":"Jodar"},
    {"id":51, "ja":"Davidovich Fokina","jb":"Dzumhur"},
    {"id":52, "ja":"Llamas Ruiz",      "jb":"Tirante"},
    {"id":53, "ja":"Kokkinakis",       "jb":"Atmane"},
    {"id":54, "ja":"Carreno Busta",    "jb":"Lehecka"},
    {"id":55, "ja":"Khachanov",        "jb":"Gea"},
    {"id":56, "ja":"Jacquet",          "jb":"Trungelliti"},
    {"id":57, "ja":"Cina",             "jb":"Opelka"},
    {"id":58, "ja":"Wawrinka",         "jb":"Fils"},
    {"id":59, "ja":"Humbert",          "jb":"Mannarino"},
    {"id":60, "ja":"Halys",            "jb":"Bellucci"},
    {"id":61, "ja":"Machac",           "jb":"Bergs"},
    {"id":62, "ja":"Bonzi",            "jb":"Zverev"},
]

ROUNDS = ["1er tour", "2ème tour", "3ème tour", "1/8 de finale", "1/4 de finale", "Demi-finale", "Finale"]
SCORES = ["", "3-0", "3-1", "3-2"]

MATCHS_DEFAUT = [dict(m, tour="1er tour", p1w="", p1s="", p2w="", p2s="", rw="", rs="", source="") for m in PREMIER_TOUR]

DEFAULT_STATE = {
    "matchs": MATCHS_DEFAUT,
    "nom1": "Joueur 1",
    "nom2": "Joueur 2",
    "pts_winner": 1,
    "pts_exact": 3,
    "finale_mult": 2,
    "last_fetch": "",
}

# ── GitHub ────────────────────────────────────────────────────────────────────
GITHUB_TOKEN = st.secrets["github_token"]
GITHUB_REPO  = st.secrets["github_repo"]
DATA_FILE    = "data.json"
API_BASE     = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{DATA_FILE}"
HEADERS      = {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}

def gh_load():
    r = requests.get(API_BASE, headers=HEADERS)
    if r.status_code == 404:
        return DEFAULT_STATE.copy(), None
    r.raise_for_status()
    info = r.json()
    content = json.loads(base64.b64decode(info["content"]).decode())
    if "matchs" not in content:
        content["matchs"] = DEFAULT_STATE["matchs"]
    return content, info["sha"]

def gh_save(data, sha):
    encoded = base64.b64encode(json.dumps(data, ensure_ascii=False, indent=2).encode()).decode()
    payload = {"message": f"update {datetime.utcnow().isoformat()}", "content": encoded}
    if sha:
        payload["sha"] = sha
    r = requests.put(API_BASE, headers=HEADERS, json=payload)
    if r.status_code not in (200, 201):
        st.warning(f"Erreur sauvegarde : {r.status_code}")
        return sha
    return r.json()["content"]["sha"]

# ── Fetch résultats ATP (RapidAPI) ────────────────────────────────────────────
def fetch_atp_results():
    try:
        if "rapidapi_key" not in st.secrets:
            return {}
        url = "https://api-tennis.p.rapidapi.com/tennis/"
        params = {"method": "get_H2H", "event_id": "roland-garros-2026"}
        headers = {
            "X-RapidAPI-Key": st.secrets["rapidapi_key"],
            "X-RapidAPI-Host": "api-tennis.p.rapidapi.com"
        }
        r = requests.get(url, headers=headers, params=params, timeout=5)
        if r.status_code != 200:
            return {}
        data = r.json()
        results = {}
        for match in data.get("result", []):
            try:
                p1 = match.get("event_first_player", "")
                p2 = match.get("event_second_player", "")
                score_str = match.get("event_final_result", "")
                if not p1 or not p2 or not score_str:
                    continue
                sets1, sets2 = 0, 0
                for part in score_str.split(","):
                    part = part.strip()
                    if "-" in part:
                        a, b = part.split("-")[0], part.split("-")[1].split("(")[0]
                        if int(a) > int(b):
                            sets1 += 1
                        else:
                            sets2 += 1
                score_fmt = f"{max(sets1,sets2)}-{min(sets1,sets2)}"
                w = p1 if sets1 > sets2 else p2
                key = f"{p1.split()[-1].lower()}_{p2.split()[-1].lower()}"
                results[key] = {"winner": w, "score": score_fmt, "source": "ATP"}
            except Exception:
                continue
        return results
    except Exception:
        return {}

def fetch_livescore_scrape():
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept-Language": "fr-FR,fr;q=0.9",
        }
        r = requests.get("https://www.livescore.com/en/tennis/atp-french-open/", headers=headers, timeout=8)
        if r.status_code != 200:
            return {}
        results = {}
        text = r.text
        import re
        blocks = re.findall(r'"home_name":"([^"]+)","away_name":"([^"]+)".*?"home_score":"([^"]+)","away_score":"([^"]+)"', text)
        for p1, p2, s1, s2 in blocks:
            try:
                i1, i2 = int(s1), int(s2)
                score_fmt = f"{max(i1,i2)}-{min(i1,i2)}"
                w = p1 if i1 > i2 else p2
                key = f"{p1.split()[-1].lower()}_{p2.split()[-1].lower()}"
                results[key] = {"winner": w, "score": score_fmt, "source": "livescore"}
            except Exception:
                continue
        return results
    except Exception:
        return {}

# ── Fetch tableau & classements depuis ESPN (API publique) ────────────────────
ESPN_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "fr-FR,fr;q=0.9,en;q=0.8",
}
ESPN_SCOREBOARD = "https://site.web.api.espn.com/apis/site/v2/sports/tennis/atp/scoreboard"
ESPN_RANKINGS   = "https://site.web.api.espn.com/apis/site/v2/sports/tennis/atp/rankings"

def fetch_draw_espn() -> tuple[list[tuple[str, str]], str]:
    """
    Récupère le tirage du 1er tour du tableau principal Roland-Garros 2026
    depuis l'API ESPN. 1er tour = matchs du 24-25 mai 2026 (period=1).
    Retourne (liste de (nomA, nomB), message).
    """
    pairs: list[tuple[str, str]] = []
    try:
        # Récupère les données du scoreboard au 25 mai (contient tout le tournoi)
        r = requests.get(ESPN_SCOREBOARD, headers=ESPN_HEADERS,
                         params={"dates": "20260525", "limit": 200}, timeout=12)
        if r.status_code != 200:
            return [], f"ESPN : HTTP {r.status_code}"
        data = r.json()
        events = data.get("events", [])
        rg = next((e for e in events if e.get("id") == "172-2026"), None)
        if rg is None:
            return [], "ESPN : événement Roland-Garros 2026 introuvable"
        groupings = rg.get("groupings", [])
        mens = next((g for g in groupings if g.get("grouping", {}).get("slug") == "mens-singles"), None)
        if mens is None:
            return [], "ESPN : tableau hommes introuvable"
        # 1er tour principal = period 1, dates 24 ou 25 mai 2026
        first_round_dates = {"2026-05-24", "2026-05-25"}
        for comp in mens.get("competitions", []):
            date = (comp.get("date") or "")[:10]
            period = comp.get("status", {}).get("period")
            if period == 1 and date in first_round_dates:
                competitors = comp.get("competitors", [])
                if len(competitors) >= 2:
                    # order=2 = 1er dans l'affichage ESPN, order=1 = 2ème
                    sorted_comp = sorted(competitors, key=lambda c: c.get("order", 99))
                    name_a = sorted_comp[1].get("athlete", {}).get("displayName", "").strip()
                    name_b = sorted_comp[0].get("athlete", {}).get("displayName", "").strip()
                    if name_a and name_b:
                        pairs.append((name_a, name_b))
    except Exception as e:
        return pairs, f"ESPN erreur : {e}"
    if pairs:
        return pairs, f"✅ {len(pairs)} matchs du 1er tour récupérés via ESPN"
    return [], "ESPN : aucun match du 1er tour trouvé"

def fetch_atp_rankings_espn() -> dict[str, int]:
    """
    Récupère le classement ATP live depuis ESPN.
    Retourne {nom_complet: rang, nom_de_famille: rang}.
    """
    rankings: dict[str, int] = {}
    try:
        r = requests.get(ESPN_RANKINGS, headers=ESPN_HEADERS,
                         params={"limit": 300}, timeout=10)
        if r.status_code != 200:
            return rankings
        data = r.json()
        ranks_list = data.get("rankings", [{}])[0].get("ranks", [])
        for entry in ranks_list:
            rank = entry.get("current", 0)
            athlete = entry.get("athlete", {})
            full = athlete.get("displayName", "").strip()
            last = athlete.get("lastName", full.split()[-1] if full else "").strip()
            if full and rank:
                rankings[full] = rank
                if last:
                    rankings[last] = rank
    except Exception:
        pass
    return rankings

def parse_draw_text(text: str) -> list[tuple[str, str]]:
    """
    Parse une saisie manuelle du tableau.
    Formats acceptés par ligne :
      - "Joueur A vs Joueur B"
      - "Joueur A - Joueur B"
      - "Joueur A / Joueur B"
    Lignes vides ou sans séparateur → ignorées.
    """
    import re
    pairs: list[tuple[str, str]] = []
    for line in text.strip().splitlines():
        line = line.strip()
        if not line:
            continue
        m = re.split(r'\s+(?:vs\.?|[-/])\s+', line, maxsplit=1, flags=re.IGNORECASE)
        if len(m) == 2:
            a, b = m[0].strip(), m[1].strip()
            if a and b:
                pairs.append((a, b))
    return pairs

def rebuild_premier_tour(matchs: list, pairs: list[tuple[str, str]]) -> list:
    """
    Remplace TOUS les matchs du 1er tour par les nouvelles paires.
    Les autres tours sont conservés intacts.
    Les matchs supprimés voient leurs pronostics perdus.
    """
    autres = [m for m in matchs if m.get("tour") != "1er tour"]
    max_id = max((m["id"] for m in matchs), default=0)
    nouveaux = []
    for i, (ja, jb) in enumerate(pairs):
        max_id += 1
        nouveaux.append({
            "id": max_id,
            "tour": "1er tour",
            "ja": ja,
            "jb": jb,
            "p1w": "", "p1s": "",
            "p2w": "", "p2s": "",
            "rw": "", "rs": "",
            "source": "",
        })
    return nouveaux + autres

def match_key(ja, jb):
    return f"{ja.split()[-1].lower()}_{jb.split()[-1].lower()}"

def auto_fill_results(matchs, atp_res, ls_res):
    updated = False
    for m in matchs:
        if m["rw"]:
            continue
        key  = match_key(m["ja"], m["jb"])
        key2 = match_key(m["jb"], m["ja"])
        res  = atp_res.get(key) or atp_res.get(key2) or ls_res.get(key) or ls_res.get(key2)
        if res:
            m["rw"] = res["winner"]
            m["rs"] = res["score"]
            m["source"] = res["source"]
            updated = True
    return matchs, updated

# ── Progression automatique du tableau ───────────────────────────────────────
def next_round(current_round: str) -> str | None:
    idx = ROUNDS.index(current_round) if current_round in ROUNDS else -1
    if idx == -1 or idx >= len(ROUNDS) - 1:
        return None
    return ROUNDS[idx + 1]

def generate_next_round(matchs: list) -> tuple[list, bool]:
    """
    Pour chaque tour, si tous les matchs sont terminés (rw rempli) et que le tour
    suivant n'existe pas encore, crée les matchs du tour suivant en appariant les
    vainqueurs par paires consécutives (match 1 gagnant vs match 2 gagnant, etc.).
    Retourne (matchs mis à jour, True si des matchs ont été ajoutés).
    """
    added = False
    for round_name in ROUNDS[:-1]:
        round_matchs = [m for m in matchs if m.get("tour") == round_name]
        if not round_matchs:
            continue
        if any(not m["rw"] for m in round_matchs):
            continue
        next_r = next_round(round_name)
        if not next_r:
            continue
        if any(m.get("tour") == next_r for m in matchs):
            continue
        winners = [m["rw"] for m in round_matchs]
        max_id = max((m["id"] for m in matchs), default=0)
        for i in range(0, len(winners) - 1, 2):
            max_id += 1
            matchs.append({
                "id": max_id,
                "tour": next_r,
                "ja": winners[i],
                "jb": winners[i + 1],
                "p1w": "", "p1s": "",
                "p2w": "", "p2s": "",
                "rw": "", "rs": "",
                "source": "",
            })
            added = True
        if len(winners) % 2 == 1:
            max_id += 1
            matchs.append({
                "id": max_id,
                "tour": next_r,
                "ja": winners[-1],
                "jb": "TBD",
                "p1w": "", "p1s": "",
                "p2w": "", "p2s": "",
                "rw": "", "rs": "",
                "source": "",
            })
            added = True
    return matchs, added

# ── Bonus underdog ────────────────────────────────────────────────────────────
def underdog_multiplier(pred_winner: str, ja: str, jb: str) -> int:
    """Si le pronostic porte sur le moins bien classé : ×2 (1-30 places d'écart), ×3 (31+)."""
    if not pred_winner or pred_winner not in (ja, jb):
        return 1
    other = jb if pred_winner == ja else ja
    r_pred  = player_info(pred_winner).get("rank", 999)
    r_other = player_info(other).get("rank", 999)
    # underdog = classement numériquement plus grand
    if r_pred <= r_other:
        return 1
    diff = r_pred - r_other
    if diff >= 31:
        return 3
    if diff >= 1:
        return 2
    return 1

# ── Points ────────────────────────────────────────────────────────────────────
def calc_pts(pw, ps, rw, rs, pts_w, pts_e, tour, fm, ja="", jb=""):
    if not rw or not pw:
        return 0
    mult = fm if tour == "Finale" else 1
    ud = underdog_multiplier(pw, ja, jb)
    if pw == rw and ps == rs:
        return pts_e * mult * ud
    if pw == rw:
        return pts_w * mult * ud
    return 0

def totaux(matchs, pw, pe, fm):
    t1 = t2 = 0
    for m in matchs:
        t1 += calc_pts(m["p1w"], m["p1s"], m["rw"], m["rs"], pw, pe, m["tour"], fm, m["ja"], m["jb"])
        t2 += calc_pts(m["p2w"], m["p2s"], m["rw"], m["rs"], pw, pe, m["tour"], fm, m["ja"], m["jb"])
    return t1, t2

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
.main-title{font-size:2rem;font-weight:700;color:#c8432a}
.subtitle{color:#888;font-size:.95rem;margin-bottom:1.5rem}
.score-box{background:#f9f4ef;border-radius:12px;padding:1rem 1.5rem;text-align:center;border:1px solid #e8ddd5}
.score-name{font-size:.8rem;color:#888;margin-bottom:2px}
.score-pts{font-size:2rem;font-weight:700;color:#c8432a}
.correct{color:#3a7d44;font-weight:600}
.partial{color:#b87a1e;font-weight:600}
.wrong{color:#c8432a;font-weight:600}
.auto-badge{font-size:10px;background:#e8f4fd;color:#185FA5;padding:1px 7px;border-radius:10px;margin-left:6px}
.underdog-badge{font-size:10px;background:#fef3c7;color:#92400e;padding:1px 7px;border-radius:10px;margin-left:6px;font-weight:600}
</style>
""", unsafe_allow_html=True)

# ── Init session ──────────────────────────────────────────────────────────────
if "data" not in st.session_state:
    data, sha = gh_load()
    if len(data.get("matchs", [])) < 30:
        data["matchs"] = DEFAULT_STATE["matchs"]
    st.session_state["data"] = data
    st.session_state["sha"]  = sha

data = st.session_state["data"]

def save():
    data = st.session_state["data"]
    data["matchs"], added = generate_next_round(data["matchs"])
    if added:
        st.toast("🎾 Nouveaux matchs générés pour le tour suivant !", icon="🎉")
    st.session_state["sha"] = gh_save(data, st.session_state["sha"])

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown('<p class="main-title">🎾 Paris Roland-Garros 2026</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Pronostics partagés — bonus underdog ×2 (1-30) / ×3 (31+).</p>', unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Paramètres")

    nom1 = st.text_input("Votre prénom", value=data.get("nom1", "Joueur 1"))
    nom2 = st.text_input("Prénom de votre frère", value=data.get("nom2", "Joueur 2"))
    if nom1 != data["nom1"] or nom2 != data["nom2"]:
        data["nom1"] = nom1; data["nom2"] = nom2
        save()

    st.divider()
    st.subheader("Points")
    pts_winner  = st.number_input("Bon vainqueur",           min_value=0, max_value=99, value=data.get("pts_winner",1))
    pts_exact   = st.number_input("Vainqueur + score exact", min_value=0, max_value=99, value=data.get("pts_exact",3))
    finale_mult = st.number_input("Multiplicateur finale ×", min_value=1, max_value=10, value=data.get("finale_mult",2))
    st.caption("Bonus underdog : ×2 si écart de classement 1-30, ×3 si 31+.")
    if st.button("💾 Sauvegarder les règles"):
        data["pts_winner"] = pts_winner
        data["pts_exact"]  = pts_exact
        data["finale_mult"]= finale_mult
        save(); st.success("Sauvegardé !")

    st.divider()
    st.subheader("Résultats auto")
    last = data.get("last_fetch","jamais")
    st.caption(f"Dernier fetch : {last}")
    if st.button("🔄 Fetch résultats maintenant"):
        with st.spinner("Récupération ATP..."):
            atp = fetch_atp_results()
        with st.spinner("Fallback livescore..."):
            ls  = fetch_livescore_scrape()
        data["matchs"], updated = auto_fill_results(data["matchs"], atp, ls)
        data["last_fetch"] = datetime.now().strftime("%d/%m %H:%M")
        save()
        if updated:
            st.success(f"Résultats mis à jour ! (ATP:{len(atp)} | LS:{len(ls)})")
        else:
            st.info("Aucun nouveau résultat trouvé.")
        st.rerun()

    st.divider()
    st.subheader("🏗️ Reconstruire le tableau")
    st.caption("Repart de zéro pour le 1er tour — les pronostics déjà saisis seront perdus.")

    if st.button("🔍 Fetch auto via ESPN"):
        with st.spinner("Connexion à ESPN..."):
            pairs, msg = fetch_draw_espn()
        if pairs:
            st.session_state["draw_preview"] = pairs
            st.success(f"{msg} — vérifiez ci-dessous puis confirmez.")
        else:
            st.warning(f"{msg}\n\nSaisissez le tableau manuellement ci-dessous.")

    if st.button("📊 Fetch classements ATP"):
        with st.spinner("Récupération classements ESPN..."):
            rankings = fetch_atp_rankings_espn()
        if rankings:
            data["rankings"] = rankings
            st.session_state["fetched_rankings"] = rankings
            save()
            st.success(f"✅ {len(rankings)} classements sauvegardés et appliqués.")
            st.rerun()
        else:
            st.warning("Classements non disponibles.")

    preview = st.session_state.get("draw_preview", [])
    if preview:
        st.caption(f"Aperçu ({len(preview)} matchs) :")
        for i, (a, b) in enumerate(preview[:5]):
            st.markdown(f"  {i+1}. {a} vs {b}")
        if len(preview) > 5:
            st.caption(f"… et {len(preview)-5} autres matchs")
        if st.button("✅ Confirmer et reconstruire le 1er tour"):
            data["matchs"] = rebuild_premier_tour(data["matchs"], preview)
            rankings = st.session_state.get("fetched_rankings", {})
            if rankings:
                for m in data["matchs"]:
                    for name in [m["ja"], m["jb"]]:
                        last = name.split()[-1]
                        if last in rankings and name not in PLAYERS:
                            PLAYERS[name] = {"first": "", "country": "", "rank": rankings[last]}
            del st.session_state["draw_preview"]
            save()
            st.rerun()

    st.markdown("**Ou saisissez manuellement :**")
    st.caption("Un match par ligne : `Joueur A vs Joueur B`")
    draw_text = st.text_area("Tableau 1er tour", height=180, placeholder="Sinner vs Tabur\nFearnley vs Cerundolo\n...")
    if st.button("📋 Appliquer la saisie manuelle") and draw_text.strip():
        pairs = parse_draw_text(draw_text)
        if pairs:
            data["matchs"] = rebuild_premier_tour(data["matchs"], pairs)
            save()
            st.success(f"✅ {len(pairs)} matchs reconstruits.")
            st.rerun()
        else:
            st.error("Format non reconnu. Utilisez : Joueur A vs Joueur B")

    st.divider()
    st.subheader("Ajouter un match")
    with st.form("add"):
        nt = st.selectbox("Tour", ROUNDS)
        na = st.text_input("Joueur A")
        nb = st.text_input("Joueur B")
        if st.form_submit_button("➕ Ajouter") and na and nb:
            nid = max((m["id"] for m in data["matchs"]), default=0)+1
            data["matchs"].append({"id":nid,"tour":nt,"ja":na,"jb":nb,"p1w":"","p1s":"","p2w":"","p2s":"","rw":"","rs":"","source":""})
            save(); st.success("Ajouté !"); st.rerun()

    if st.button("🔃 Recharger depuis GitHub"):
        del st.session_state["data"]
        st.rerun()

# ── Scores ────────────────────────────────────────────────────────────────────
t1, t2 = totaux(data["matchs"], pts_winner, pts_exact, finale_mult)
c1, c2, _ = st.columns([1,1,2])
with c1:
    st.markdown(f'<div class="score-box"><div class="score-name">{nom1}</div><div class="score-pts">{t1} pts</div></div>', unsafe_allow_html=True)
with c2:
    st.markdown(f'<div class="score-box"><div class="score-name">{nom2}</div><div class="score-pts">{t2} pts</div></div>', unsafe_allow_html=True)

st.divider()

# ── Filtres ───────────────────────────────────────────────────────────────────
col_f1, col_f2 = st.columns(2)
with col_f1:
    tour_filter = st.selectbox("Tour", ["Tous"] + ROUNDS)
with col_f2:
    status_filter = st.selectbox("Statut", ["Tous", "À pronostiquer", "Terminés"])

# ── Matchs ────────────────────────────────────────────────────────────────────
for idx, m in enumerate(data["matchs"]):
    if tour_filter != "Tous" and m.get("tour","1er tour") != tour_filter:
        continue
    if status_filter == "À pronostiquer" and m["rw"]:
        continue
    if status_filter == "Terminés" and not m["rw"]:
        continue

    ja, jb = m["ja"], m["jb"]
    la, lb = player_label(ja), player_label(jb)
    src_badge = f'<span class="auto-badge">auto {m.get("source","")}</span>' if m.get("source") else ""
    result_str = f"✅ {m['rw']} {m['rs']}" if m["rw"] else "⏳ en attente"
    label = f"{la}  vs  {lb}  —  _{m.get('tour','1er tour')}_  —  {result_str}"

    with st.expander(label, expanded=False):
        cp1, cp2, cr = st.columns(3)
        changed = False
        opts = ["", ja, jb]
        # libellés affichés dans les selectbox (mais valeur retournée = nom de famille)
        def fmt(name): return player_label(name) if name else "—"

        with cp1:
            st.markdown(f"**{nom1}**")
            new_p1w = st.selectbox("Vainqueur", opts, format_func=fmt,
                index=opts.index(m["p1w"]) if m["p1w"] in opts else 0, key=f"p1w_{m['id']}")
            new_p1s = st.selectbox("Score", SCORES,
                index=SCORES.index(m["p1s"]) if m["p1s"] in SCORES else 0, key=f"p1s_{m['id']}")
            ud1 = underdog_multiplier(new_p1w, ja, jb)
            if ud1 > 1:
                st.markdown(f'<span class="underdog-badge">🔥 underdog ×{ud1}</span>', unsafe_allow_html=True)
            if new_p1w != m["p1w"] or new_p1s != m["p1s"]:
                m["p1w"] = new_p1w; m["p1s"] = new_p1s; changed = True
            if m["rw"]:
                pts = calc_pts(m["p1w"], m["p1s"], m["rw"], m["rs"], pts_winner, pts_exact, m.get("tour",""), finale_mult, ja, jb)
                if m["p1w"] == m["rw"] and m["p1s"] == m["rs"]:
                    st.markdown(f'<span class="correct">✓ Parfait ! +{pts} pts</span>', unsafe_allow_html=True)
                elif m["p1w"] == m["rw"]:
                    st.markdown(f'<span class="partial">~ Vainqueur ok +{pts} pt</span>', unsafe_allow_html=True)
                elif m["p1w"]:
                    st.markdown(f'<span class="wrong">✗ Raté — 0 pt</span>', unsafe_allow_html=True)

        with cp2:
            st.markdown(f"**{nom2}**")
            new_p2w = st.selectbox("Vainqueur ", opts, format_func=fmt,
                index=opts.index(m["p2w"]) if m["p2w"] in opts else 0, key=f"p2w_{m['id']}")
            new_p2s = st.selectbox("Score ", SCORES,
                index=SCORES.index(m["p2s"]) if m["p2s"] in SCORES else 0, key=f"p2s_{m['id']}")
            ud2 = underdog_multiplier(new_p2w, ja, jb)
            if ud2 > 1:
                st.markdown(f'<span class="underdog-badge">🔥 underdog ×{ud2}</span>', unsafe_allow_html=True)
            if new_p2w != m["p2w"] or new_p2s != m["p2s"]:
                m["p2w"] = new_p2w; m["p2s"] = new_p2s; changed = True
            if m["rw"]:
                pts = calc_pts(m["p2w"], m["p2s"], m["rw"], m["rs"], pts_winner, pts_exact, m.get("tour",""), finale_mult, ja, jb)
                if m["p2w"] == m["rw"] and m["p2s"] == m["rs"]:
                    st.markdown(f'<span class="correct">✓ Parfait ! +{pts} pts</span>', unsafe_allow_html=True)
                elif m["p2w"] == m["rw"]:
                    st.markdown(f'<span class="partial">~ Vainqueur ok +{pts} pt</span>', unsafe_allow_html=True)
                elif m["p2w"]:
                    st.markdown(f'<span class="wrong">✗ Raté — 0 pt</span>', unsafe_allow_html=True)

        with cr:
            st.markdown(f"**Résultat réel** {src_badge}", unsafe_allow_html=True)
            new_rw = st.selectbox("Vainqueur  ", opts, format_func=fmt,
                index=opts.index(m["rw"]) if m["rw"] in opts else 0, key=f"rw_{m['id']}")
            new_rs = st.selectbox("Score  ", SCORES,
                index=SCORES.index(m["rs"]) if m["rs"] in SCORES else 0, key=f"rs_{m['id']}")
            if new_rw != m["rw"] or new_rs != m["rs"]:
                m["rw"] = new_rw; m["rs"] = new_rs; m["source"] = "manuel"; changed = True

        if changed:
            save(); st.rerun()

        # ── Édition manuelle des noms ──────────────────────────────────────
        with st.expander("✏️ Modifier les noms des joueurs de ce match"):
            with st.form(key=f"edit_players_{m['id']}"):
                col_ea, col_eb = st.columns(2)
                with col_ea:
                    new_ja = st.text_input("Joueur A", value=m["ja"])
                with col_eb:
                    new_jb = st.text_input("Joueur B", value=m["jb"])
                if st.form_submit_button("✅ Appliquer"):
                    if new_ja != m["ja"] or new_jb != m["jb"]:
                        # Réinitialise les pronostics si le nom change
                        if m["p1w"] == m["ja"]: m["p1w"] = new_ja
                        if m["p1w"] == m["jb"]: m["p1w"] = new_jb
                        if m["p2w"] == m["ja"]: m["p2w"] = new_ja
                        if m["p2w"] == m["jb"]: m["p2w"] = new_jb
                        if m["rw"]  == m["ja"]: m["rw"]  = new_ja
                        if m["rw"]  == m["jb"]: m["rw"]  = new_jb
                        m["ja"] = new_ja
                        m["jb"] = new_jb
                        save()
                        st.rerun()

st.divider()
st.caption(f"Roland-Garros 2026 · {len(data['matchs'])} matchs · données GitHub · fetch auto ATP+livescore · bonus underdog ×2/×3")
