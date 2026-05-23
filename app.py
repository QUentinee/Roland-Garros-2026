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
    last = name.split()[-1]
    # 1. Base ESPN fetchée (data["players"]) — priorité absolue
    espn_db = st.session_state.get("data", {}).get("players", {})
    if name in espn_db:
        return espn_db[name].copy()
    if last in espn_db:
        return espn_db[last].copy()
    # 2. Dictionnaire local codé en dur (fallback)
    if name in PLAYERS:
        return PLAYERS[name].copy()
    if last in PLAYERS:
        p = PLAYERS[last].copy()
        if not p.get("first"):
            p["first"] = " ".join(name.split()[:-1])
        return p
    # 3. Joueur inconnu
    return {"first": " ".join(name.split()[:-1]), "country": "", "rank": 999}

def player_label(name: str) -> str:
    p = player_info(name)
    fl = flag(p["country"])
    first = p["first"]
    rank = p["rank"]
    rank_str = f"#{rank}" if rank and rank < 999 else "NC"
    # Si le prénom est déjà dans name (nom complet ESPN), ne pas le redoubler
    if first and not name.startswith(first):
        full = f"{first} {name}".strip()
    else:
        full = name
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
def fetch_results_espn() -> tuple[dict, str]:
    """
    Récupère les résultats terminés de Roland-Garros 2026 depuis ESPN.
    Parcourt toutes les dates du tournoi (25 mai – 8 juin 2026).
    Retourne ({clé: {winner, score, source}}, message).
    La clé = "nomA_nomB" (noms de famille en minuscules).
    Le score = "sets_gagnés_vainqueur-sets_gagnés_perdant".
    """
    import datetime as dt
    results: dict = {}
    try:
        today = dt.date.today()
        start = dt.date(2026, 5, 25)
        end   = dt.date(2026, 6, 8)
        cur   = start
        while cur <= min(today, end):
            date_str = cur.strftime("%Y%m%d")
            cur += dt.timedelta(days=1)
            r = requests.get(ESPN_SCOREBOARD, headers=ESPN_HEADERS,
                             params={"dates": date_str, "limit": 200}, timeout=10)
            if r.status_code != 200:
                continue
            for ev in r.json().get("events", []):
                if not ev.get("id", "").startswith("172-"):
                    continue
                comp = ev.get("competitions", [{}])[0]
                if not comp.get("status", {}).get("type", {}).get("completed"):
                    continue
                competitors = comp.get("competitors", [])
                if len(competitors) < 2:
                    continue
                winner_c = next((c for c in competitors if c.get("winner")), None)
                loser_c  = next((c for c in competitors if not c.get("winner")), None)
                if not winner_c or not loser_c:
                    continue
                w_name = winner_c.get("athlete", {}).get("displayName", "")
                l_name = loser_c.get("athlete",  {}).get("displayName", "")
                try:
                    w_sets = int(float(winner_c.get("score", 0)))
                    l_sets = int(float(loser_c.get("score",  0)))
                except (ValueError, TypeError):
                    w_sets, l_sets = 0, 0
                score = f"{w_sets}-{l_sets}"
                # Date du match depuis ESPN (format YYYY-MM-DDThh:mmZ → YYYY-MM-DD)
                match_date = (comp.get("date") or ev.get("date") or "")[:10]
                entry = {"winner": w_name, "score": score, "source": "ESPN", "date": match_date}
                key1 = f"{w_name.split()[-1].lower()}_{l_name.split()[-1].lower()}"
                key2 = f"{l_name.split()[-1].lower()}_{w_name.split()[-1].lower()}"
                results[key1] = entry
                results[key2] = entry
        msg = f"✅ {len(results)//2} résultats récupérés (ESPN)" if results else "Aucun résultat ESPN (tournoi pas encore commencé ?)"
        return results, msg
    except Exception as e:
        return {}, f"ESPN résultats erreur : {e}"

def fetch_livescore_scrape():
    # Conservé pour compatibilité — livescore redirige en 404, retourne vide
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

def fetch_draw_espn() -> tuple[list[tuple[str, str, str]], str]:
    """
    Récupère le tirage du 1er tour du tableau principal Roland-Garros 2026
    depuis l'API ESPN. 1er tour = matchs du 24-25 mai 2026 (period=1).
    Retourne (liste de (nomA, nomB, date_YYYY-MM-DD), message).
    """
    pairs: list[tuple[str, str, str]] = []
    try:
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
        first_round_dates = {"2026-05-24", "2026-05-25"}
        for comp in mens.get("competitions", []):
            date = (comp.get("date") or "")[:10]
            period = comp.get("status", {}).get("period")
            if period == 1 and date in first_round_dates:
                competitors = comp.get("competitors", [])
                if len(competitors) >= 2:
                    sorted_comp = sorted(competitors, key=lambda c: c.get("order", 99))
                    name_a = sorted_comp[1].get("athlete", {}).get("displayName", "").strip()
                    name_b = sorted_comp[0].get("athlete", {}).get("displayName", "").strip()
                    if name_a and name_b:
                        pairs.append((name_a, name_b, date))
    except Exception as e:
        return pairs, f"ESPN erreur : {e}"
    if pairs:
        return pairs, f"✅ {len(pairs)} matchs du 1er tour récupérés via ESPN"
    return [], "ESPN : aucun match du 1er tour trouvé"

# Conversion codes 3 lettres ESPN → ISO2 pour les drapeaux
ESPN_ISO3_TO_ISO2 = {
    "AFG":"AF","ALB":"AL","ALG":"DZ","AND":"AD","ANG":"AO","ARG":"AR","ARM":"AM",
    "AUS":"AU","AUT":"AT","AZE":"AZ","BAH":"BS","BAN":"BD","BAR":"BB","BEL":"BE",
    "BEN":"BJ","BER":"BM","BHU":"BT","BIH":"BA","BIZ":"BZ","BLR":"BY","BOL":"BO",
    "BOT":"BW","BRA":"BR","BRN":"BH","BUL":"BG","BUR":"BF","CAM":"KH","CAN":"CA",
    "CAY":"KY","CGO":"CG","CHI":"CL","CHN":"CN","CIV":"CI","CMR":"CM","COD":"CD",
    "COL":"CO","COM":"KM","CPV":"CV","CRC":"CR","CRO":"HR","CUB":"CU","CYP":"CY",
    "CZE":"CZ","DEN":"DK","DJI":"DJ","DOM":"DO","ECU":"EC","EGY":"EG","ESA":"SV",
    "ESP":"ES","EST":"EE","ETH":"ET","FIJ":"FJ","FIN":"FI","FRA":"FR","GAB":"GA",
    "GAM":"GM","GBR":"GB","GEO":"GE","GER":"DE","GHA":"GH","GRE":"GR","GRN":"GD",
    "GUA":"GT","GUI":"GN","GUY":"GY","HAI":"HT","HKG":"HK","HON":"HN","HUN":"HU",
    "INA":"ID","IND":"IN","IRI":"IR","IRL":"IE","IRQ":"IQ","ISL":"IS","ISR":"IL",
    "ISV":"VI","ITA":"IT","IVB":"VG","JAM":"JM","JOR":"JO","JPN":"JP","KAZ":"KZ",
    "KEN":"KE","KGZ":"KG","KOR":"KR","KSA":"SA","KUW":"KW","LAO":"LA","LAT":"LV",
    "LBA":"LY","LBN":"LB","LES":"LS","LIB":"LB","LIE":"LI","LTU":"LT","LUX":"LU",
    "MAC":"MO","MAD":"MG","MAR":"MA","MAS":"MY","MAW":"MW","MDA":"MD","MDV":"MV",
    "MEX":"MX","MGL":"MN","MKD":"MK","MLI":"ML","MLT":"MT","MNE":"ME","MON":"MC",
    "MOZ":"MZ","MRI":"MU","MTN":"MR","MYA":"MM","NAM":"NA","NCA":"NI","NED":"NL",
    "NEP":"NP","NGR":"NG","NIG":"NE","NOR":"NO","NZL":"NZ","OMA":"OM","PAK":"PK",
    "PAN":"PA","PAR":"PY","PER":"PE","PHI":"PH","PLE":"PS","PLW":"PW","PNG":"PG",
    "POL":"PL","POR":"PT","PRK":"KP","PUR":"PR","QAT":"QA","ROU":"RO","RSA":"ZA",
    "RUS":"RU","RWA":"RW","SAM":"WS","SEN":"SN","SEY":"SC","SKN":"KN","SLE":"SL",
    "SLO":"SI","SMR":"SM","SOL":"SB","SOM":"SO","SRB":"RS","SRI":"LK","SUD":"SD",
    "SUI":"CH","SUR":"SR","SVK":"SK","SWE":"SE","SWZ":"SZ","SYR":"SY","TAN":"TZ",
    "TGA":"TO","THA":"TH","TJK":"TJ","TKM":"TM","TLS":"TL","TOG":"TG","TPE":"TW",
    "TTO":"TT","TUN":"TN","TUR":"TR","UAE":"AE","UGA":"UG","UKR":"UA","URU":"UY",
    "USA":"US","UZB":"UZ","VAN":"VU","VEN":"VE","VIE":"VN","VIN":"VC","YEM":"YE",
    "ZAM":"ZM","ZIM":"ZW",
}

def fetch_player_db_espn() -> tuple[dict, str]:
    """
    Récupère la base joueurs complète depuis ESPN Rankings.
    Retourne ({nom_complet: {first, last, country, rank}, ...}, message).
    Les clés sont le nom complet ET le nom de famille pour la recherche.
    """
    players: dict = {}
    try:
        r = requests.get(ESPN_RANKINGS, headers=ESPN_HEADERS,
                         params={"limit": 500}, timeout=12)
        if r.status_code != 200:
            return {}, f"ESPN Rankings : HTTP {r.status_code}"
        data = r.json()
        ranks_list = data.get("rankings", [{}])[0].get("ranks", [])
        for entry in ranks_list:
            rank  = entry.get("current", 0)
            ath   = entry.get("athlete", {})
            first = ath.get("firstName", "").strip()
            last  = ath.get("lastName", "").strip()
            full  = ath.get("displayName", f"{first} {last}").strip()
            iso3  = ath.get("citizenshipCountry", "").upper()
            iso2  = ESPN_ISO3_TO_ISO2.get(iso3, "")
            if not full or not rank:
                continue
            entry_data = {"first": first, "last": last, "country": iso2, "rank": rank}
            players[full] = entry_data
            if last and last not in players:
                players[last] = entry_data
        return players, f"✅ {len([k for k in players if ' ' in k])} joueurs chargés depuis ESPN"
    except Exception as e:
        return {}, f"ESPN erreur : {e}"

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

def rebuild_premier_tour(matchs: list, pairs: list) -> list:
    """
    Remplace TOUS les matchs du 1er tour par les nouvelles paires.
    pairs peut être list[tuple[str,str]] ou list[tuple[str,str,str]] (avec date).
    Les autres tours sont conservés intacts.
    """
    autres = [m for m in matchs if m.get("tour") != "1er tour"]
    max_id = max((m["id"] for m in matchs), default=0)
    nouveaux = []
    for entry in pairs:
        ja, jb = entry[0], entry[1]
        date = entry[2] if len(entry) > 2 else ""
        max_id += 1
        nouveaux.append({
            "id": max_id,
            "tour": "1er tour",
            "ja": ja,
            "jb": jb,
            "date": date,
            "p1w": "", "p1s": "",
            "p2w": "", "p2s": "",
            "rw": "", "rs": "",
            "source": "",
        })
    return nouveaux + autres

def match_key(ja, jb):
    return f"{ja.split()[-1].lower()}_{jb.split()[-1].lower()}"

def auto_fill_results(matchs, espn_res, _ignored=None):
    updated = False
    for m in matchs:
        if m["rw"]:
            continue
        key  = match_key(m["ja"], m["jb"])
        key2 = match_key(m["jb"], m["ja"])
        res  = espn_res.get(key) or espn_res.get(key2)
        if res:
            m["rw"]     = res["winner"]
            m["rs"]     = res["score"]
            m["source"] = res.get("source", "ESPN")
            if res.get("date") and not m.get("date"):
                m["date"] = res["date"]
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
                "date": "",
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
                "date": "",
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


# ── Dates planifiées Roland-Garros 2026 (fallback par tour) ───────────────────
ROUND_DATES = {
    "1er tour":        "2026-05-25",
    "2ème tour":       "2026-05-28",
    "3ème tour":       "2026-05-30",
    "8ème de finale":  "2026-06-02",
    "Quart de finale": "2026-06-04",
    "Demi-finale":     "2026-06-06",
    "Finale":          "2026-06-08",
}

@st.cache_data(ttl=3600)
def _espn_date_map() -> dict:
    """Construit {clé_noms: date} depuis les groupings ESPN — mis en cache 1h."""
    result = {}
    try:
        r = requests.get(ESPN_SCOREBOARD, headers=ESPN_HEADERS,
                         params={"dates": "20260525", "limit": 200}, timeout=12)
        if r.status_code != 200:
            return result
        events = r.json().get("events", [])
        rg = next((e for e in events if e.get("id") == "172-2026"), None)
        if not rg:
            return result
        mens = next((g for g in rg.get("groupings", [])
                     if g.get("grouping", {}).get("slug") == "mens-singles"), None)
        if not mens:
            return result
        for comp in mens.get("competitions", []):
            date = (comp.get("date") or "")[:10]
            if not date:
                continue
            names = [
                c.get("athlete", {}).get("displayName", "").split()[-1].lower()
                for c in comp.get("competitors", [])
            ]
            if len(names) >= 2 and all(names):
                result[f"{names[0]}_{names[1]}"] = date
                result[f"{names[1]}_{names[0]}"] = date
    except Exception:
        pass
    return result

def backfill_dates(matchs: list) -> tuple[list, bool]:
    """
    Pour chaque match sans date : ESPN par noms, puis ROUND_DATES par tour.
    Retourne (matchs, changed).
    """
    if all(m.get("date") for m in matchs):
        return matchs, False
    date_map = _espn_date_map()
    changed = False
    for m in matchs:
        if m.get("date"):
            continue
        key1 = match_key(m["ja"], m["jb"])
        key2 = match_key(m["jb"], m["ja"])
        espn_date = date_map.get(key1) or date_map.get(key2)
        if espn_date:
            m["date"] = espn_date
        else:
            tour = m.get("tour", "1er tour")
            m["date"] = ROUND_DATES.get(tour, "")
        changed = True
    return matchs, changed

# ── Helpers date ──────────────────────────────────────────────────────────────
_MOIS_FR = ["","jan","fév","mars","avr","mai","juin","juil","août","sep","oct","nov","déc"]

def fmt_date(d: str) -> str:
    """'2026-05-25' → '25 mai' ; '' → ''"""
    try:
        parts = d[:10].split("-")
        return f"{int(parts[2])} {_MOIS_FR[int(parts[1])]}"
    except Exception:
        return ""

# ── Clé de tri par date ───────────────────────────────────────────────────────
def _sort_key(m):
    return (m.get("date") or "9999", m.get("tour", ""), m.get("id", 0))

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
    # Peuple les dates manquantes (ESPN + calendrier fixe) et persiste sur GitHub
    data["matchs"], dates_changed = backfill_dates(data["matchs"])
    # Génère les tours suivants si tous les matchs d'un tour sont terminés
    data["matchs"], rounds_added = generate_next_round(data["matchs"])
    if dates_changed or rounds_added:
        st.session_state["sha"] = gh_save(data, st.session_state["sha"])

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
        with st.spinner("Récupération résultats ESPN..."):
            espn, msg = fetch_results_espn()
        data["matchs"], updated = auto_fill_results(data["matchs"], espn)
        data["last_fetch"] = datetime.now().strftime("%d/%m %H:%M")
        save()
        if updated:
            st.success(msg)
        else:
            st.info(msg)
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

    if st.button("📊 Fetch joueurs & classements ESPN"):
        with st.spinner("Récupération joueurs ESPN..."):
            players_db, msg = fetch_player_db_espn()
        if players_db:
            data["players"] = players_db
            save()
            st.success(msg)
            st.rerun()
        else:
            st.warning(msg)

    preview = st.session_state.get("draw_preview", [])
    if preview:
        st.caption(f"Aperçu ({len(preview)} matchs) :")
        for i, (a, b) in enumerate(preview[:5]):
            st.markdown(f"  {i+1}. {a} vs {b}")
        if len(preview) > 5:
            st.caption(f"… et {len(preview)-5} autres matchs")
        if st.button("✅ Confirmer et reconstruire le 1er tour"):
            data["matchs"] = rebuild_premier_tour(data["matchs"], preview)
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


matchs_affiches = [
    m for m in sorted(data["matchs"], key=_sort_key)
    if (tour_filter == "Tous" or m.get("tour","1er tour") == tour_filter)
    and (status_filter != "À pronostiquer" or not m["rw"])
    and (status_filter != "Terminés" or m["rw"])
]

for idx, m in enumerate(matchs_affiches):
    ja, jb = m["ja"], m["jb"]
    la, lb = player_label(ja), player_label(jb)
    src_badge = f'<span class="auto-badge">auto {m.get("source","")}</span>' if m.get("source") else ""
    result_str = f"✅ {m['rw']} {m['rs']}" if m["rw"] else "⏳ en attente"
    date_str = fmt_date(m.get("date",""))
    date_part = f"  📅 {date_str}  —" if date_str else ""
    label = f"{la}  vs  {lb}  —{date_part}  _{m.get('tour','1er tour')}_  —  {result_str}"

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
