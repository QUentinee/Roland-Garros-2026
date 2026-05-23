import streamlit as st
import requests
import json
import base64
from datetime import datetime
import time

st.set_page_config(page_title="Paris Roland-Garros 2026", page_icon="🎾", layout="wide")

# ── Tous les matchs du 1er tour depuis le PDF ─────────────────────────────────
PREMIER_TOUR = [
    # Haut du tableau
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
    # Bas du tableau
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
    "players": {}, # Va stocker dynamiquement { "Nom": {"first": "Prénom", "rank": 999, "flag": "🏳️"} }
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
    if "players" not in content:
        content["players"] = {}
        
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

# ── Init & Gestion des Joueurs ────────────────────────────────────────────────
def init_players(data):
    """S'assure que tous les joueurs des matchs existent dans la base de données dynamique."""
    updated = False
    for m in data["matchs"]:
        for p in [m["ja"], m["jb"]]:
            if p not in data["players"]:
                data["players"][p] = {"first": "", "rank": 999, "flag": "🏳️"}
                updated = True
    return updated

def get_player_info(player_name, data):
    return data["players"].get(player_name, {"first": "", "rank": 999, "flag": "🏳️"})

# ── Fetch API (Résultats & Classements) ───────────────────────────────────────
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
                winner = match.get("event_winner", "")
                if not p1 or not p2 or not score_str:
                    continue
                sets1, sets2 = 0, 0
                for part in score_str.split(","):
                    part = part.strip()
                    if "-" in part:
                        a, b = part.split("-")[0], part.split("-")[1].split("(")[0]
                        if int(a) > int(b): sets1 += 1
                        else: sets2 += 1
                score_fmt = f"{max(sets1,sets2)}-{min(sets1,sets2)}"
                w = p1 if sets1 > sets2 else p2
                key = f"{p1.split()[-1].lower()}_{p2.split()[-1].lower()}"
                results[key] = {"winner": w, "score": score_fmt, "source": "ATP"}
            except Exception:
                continue
        return results
    except Exception:
        return {}

def fetch_atp_rankings():
    """Tente de récupérer les classements ATP via RapidAPI."""
    try:
        if "rapidapi_key" not in st.secrets:
            return {}
        url = "https://api-tennis.p.rapidapi.com/tennis/"
        params = {"method": "get_standings", "type": "ATP"}
        headers = {
            "X-RapidAPI-Key": st.secrets["rapidapi_key"],
            "X-RapidAPI-Host": "api-tennis.p.rapidapi.com"
        }
        r = requests.get(url, headers=headers, params=params, timeout=8)
        if r.status_code != 200:
            return {}
        data = r.json()
        rankings = {}
        # L'API API-Tennis retourne souvent les classements sous la clé "result"
        for rank_data in data.get("result", []):
            try:
                full_name = rank_data.get("player_name", "")
                parts = full_name.split()
                if len(parts) > 1:
                    last_name = parts[-1]
                    first_name = " ".join(parts[:-1])
                else:
                    last_name = full_name
                    first_name = ""
                
                rank = int(rank_data.get("standing_place", 999))
                # Simplification pour le drapeau: si l'API ne le donne pas, on laisse vide pour la saisie manuelle
                rankings[last_name.lower()] = {"first": first_name, "rank": rank}
            except Exception:
                continue
        return rankings
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
        text = r.text
        import re
        blocks = re.findall(r'"home_name":"([^"]+)","away_name":"([^"]+)".*?"home_score":"([^"]+)","away_score":"([^"]+)"', text)
        results = {}
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

def auto_fill_results(matchs, atp_res, ls_res):
    updated = False
    for m in matchs:
        if m["rw"]: continue
        key  = f"{m['ja'].split()[-1].lower()}_{m['jb'].split()[-1].lower()}"
        key2 = f"{m['jb'].split()[-1].lower()}_{m['ja'].split()[-1].lower()}"
        res  = atp_res.get(key) or atp_res.get(key2) or ls_res.get(key) or ls_res.get(key2)
        if res:
            m["rw"] = res["winner"]
            m["rs"] = res["score"]
            m["source"] = res["source"]
            updated = True
    return matchs, updated

# ── Points & Outsiders ────────────────────────────────────────────────────────
def calc_pts(pw, ps, rw, rs, pts_w, pts_e, tour, fm, ja, jb, data):
    if not rw or not pw or pw != rw:
        return 0, 1 # Points, Multiplicateur Outsider
    
    base_pts = pts_e if (ps == rs) else pts_w
    mult_finale = fm if tour == "Finale" else 1
    
    # Gestion Outsider basée sur le classement dynamique
    opponent = jb if pw == ja else ja
    rank_pw = get_player_info(pw, data)["rank"]
    rank_opp = get_player_info(opponent, data)["rank"]
    
    underdog_mult = 1
    if rank_pw > rank_opp: # Si rank est plus grand, il est moins bien classé
        diff = rank_pw - rank_opp
        if 1 <= diff <= 30:
            underdog_mult = 2
        elif diff >= 31:
            underdog_mult = 3
            
    return base_pts * mult_finale * underdog_mult, underdog_mult

def totaux(matchs, pw, pe, fm, data):
    t1 = t2 = 0
    for m in matchs:
        pts1, _ = calc_pts(m["p1w"], m["p1s"], m["rw"], m["rs"], pw, pe, m.get("tour",""), fm, m["ja"], m["jb"], data)
        pts2, _ = calc_pts(m["p2w"], m["p2s"], m["rw"], m["rs"], pw, pe, m.get("tour",""), fm, m["ja"], m["jb"], data)
        t1 += pts1
        t2 += pts2
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
.outsider-badge{font-size:11px;background:#fff3cd;color:#856404;padding:2px 6px;border-radius:4px;font-weight:bold;}
</style>
""", unsafe_allow_html=True)

# ── Init session ──────────────────────────────────────────────────────────────
if "data" not in st.session_state:
    data, sha = gh_load()
    if len(data.get("matchs", [])) < 30:
        data["matchs"] = DEFAULT_STATE["matchs"]
    
    # S'assurer que tous les joueurs existent dans la DB dynamique
    if init_players(data):
        gh_save(data, sha) # Sauvegarde initiale si de nouveaux joueurs sont ajoutés
        
    st.session_state["data"] = data
    st.session_state["sha"]  = sha

data = st.session_state["data"]

def save():
    st.session_state["sha"] = gh_save(st.session_state["data"], st.session_state["sha"])

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown('<p class="main-title">🎾 Paris Roland-Garros 2026</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Pronostics partagés — classements et résultats dynamiques.</p>', unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Paramètres")

    nom1 = st.text_input("Votre prénom", value=data.get("nom1", "Joueur 1"))
    nom2 = st.text_input("Prénom de l'adversaire", value=data.get("nom2", "Joueur 2"))
    if nom1 != data["nom1"] or nom2 != data["nom2"]:
        data["nom1"] = nom1; data["nom2"] = nom2
        save()

    st.divider()
    st.subheader("Points & Multiplicateurs")
    pts_winner  = st.number_input("Bon vainqueur", min_value=0, max_value=99, value=data.get("pts_winner",1))
    pts_exact   = st.number_input("Vainqueur + score exact", min_value=0, max_value=99, value=data.get("pts_exact",3))
    finale_mult = st.number_input("Multiplicateur finale ×", min_value=1, max_value=10, value=data.get("finale_mult",2))
    st.caption("Parier sur un outsider rapporte plus :\n- Diff. 1 à 30 places : **×2**\n- Diff. > 31 places : **×3**")
    
    if st.button("💾 Sauvegarder les règles"):
        data["pts_winner"] = pts_winner
        data["pts_exact"]  = pts_exact
        data["finale_mult"]= finale_mult
        save(); st.success("Sauvegardé !")

    st.divider()
    st.subheader("Résultats auto")
    last = data.get("last_fetch","jamais")
    st.caption(f"Dernier fetch résultats : {last}")
    if st.button("🔄 Fetch résultats"):
        with st.spinner("Récupération ATP..."):
            atp = fetch_atp_results()
        with st.spinner("Fallback livescore..."):
            ls  = fetch_livescore_scrape()
        data["matchs"], updated = auto_fill_results(data["matchs"], atp, ls)
        data["last_fetch"] = datetime.now().strftime("%d/%m %H:%M")
        save()
        if updated: st.success("Résultats mis à jour !")
        else: st.info("Aucun nouveau résultat.")
        st.rerun()

    st.divider()
    st.subheader("Classements dynamiques")
    if st.button("🔄 Fetch Classements ATP"):
        with st.spinner("Mise à jour des classements..."):
            new_ranks = fetch_atp_rankings()
            updates = 0
            for p_name in data["players"]:
                key = p_name.split()[-1].lower()
                if key in new_ranks:
                    data["players"][p_name]["rank"] = new_ranks[key]["rank"]
                    if new_ranks[key]["first"]:
                        data["players"][p_name]["first"] = new_ranks[key]["first"]
                    updates += 1
            if updates > 0:
                save()
                st.success(f"{updates} classements mis à jour !")
                st.rerun()
            else:
                st.warning("Aucune donnée trouvée via l'API.")
                
    with st.expander("Modifier un joueur manuellement"):
        edit_p = st.selectbox("Sélectionner un joueur", list(data["players"].keys()))
        if edit_p:
            p_data = data["players"][edit_p]
            new_f = st.text_input("Prénom", value=p_data["first"])
            new_r = st.number_input("Classement (999=NC)", value=p_data["rank"], min_value=1)
            new_fl = st.text_input("Drapeau (Emoji)", value=p_data["flag"])
            if st.button("Appliquer"):
                data["players"][edit_p] = {"first": new_f, "rank": new_r, "flag": new_fl}
                save(); st.success("Modifié !"); st.rerun()

    if st.button("🔃 Recharger depuis GitHub"):
        del st.session_state["data"]
        st.rerun()

# ── Scores ────────────────────────────────────────────────────────────────────
t1, t2 = totaux(data["matchs"], pts_winner, pts_exact, finale_mult, data)
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
    if tour_filter != "Tous" and m.get("tour","1er tour") != tour_filter: continue
    if status_filter == "À pronostiquer" and m["rw"]: continue
    if status_filter == "Terminés" and not m["rw"]: continue

    ja, jb = m["ja"], m["jb"]
    info_a = get_player_info(ja, data)
    info_b = get_player_info(jb, data)
    
    display_ja = f"{info_a['flag']} {info_a['first']} {ja} ({info_a['rank']})"
    display_jb = f"{info_b['flag']} {info_b['first']} {jb} ({info_b['rank']})"
    
    src_badge = f'<span class="auto-badge">auto {m.get("source","")}</span>' if m.get("source") else ""
    result_str = f"✅ {m['rw']} {m['rs']}" if m["rw"] else "⏳ en attente"
    label = f"**{display_ja}** vs **{display_jb}** —  _{m.get('tour','1er tour')}_  —  {result_str}"

    with st.expander(label, expanded=False):
        cp1, cp2, cr = st.columns(3)
        changed = False
        opts = ["", ja, jb]

        with cp1:
            st.markdown(f"**{nom1}**")
            new_p1w = st.selectbox("Vainqueur", opts, index=opts.index(m["p1w"]) if m["p1w"] in opts else 0, key=f"p1w_{m['id']}")
            new_p1s = st.selectbox("Score", SCORES, index=SCORES.index(m["p1s"]) if m["p1s"] in SCORES else 0, key=f"p1s_{m['id']}")
            if new_p1w != m["p1w"] or new_p1s != m["p1s"]:
                m["p1w"] = new_p1w; m["p1s"] = new_p1s; changed = True
                
            if m["rw"]:
                pts, u_mult = calc_pts(m["p1w"], m["p1s"], m["rw"], m["rs"], pts_winner, pts_exact, m.get("tour",""), finale_mult, ja, jb, data)
                bonus_str = f' <span class="outsider-badge">Outsider x{u_mult}</span>' if u_mult > 1 and pts > 0 else ""
                
                if m["p1w"] == m["rw"] and m["p1s"] == m["rs"]: st.markdown(f'<span class="correct">✓ Parfait ! +{pts} pts</span>{bonus_str}', unsafe_allow_html=True)
                elif m["p1w"] == m["rw"]: st.markdown(f'<span class="partial">~ Vainqueur ok +{pts} pt(s)</span>{bonus_str}', unsafe_allow_html=True)
                elif m["p1w"]: st.markdown(f'<span class="wrong">✗ Raté — 0 pt</span>', unsafe_allow_html=True)

        with cp2:
            st.markdown(f"**{nom2}**")
            new_p2w = st.selectbox("Vainqueur ", opts, index=opts.index(m["p2w"]) if m["p2w"] in opts else 0, key=f"p2w_{m['id']}")
            new_p2s = st.selectbox("Score ", SCORES, index=SCORES.index(m["p2s"]) if m["p2s"] in SCORES else 0, key=f"p2s_{m['id']}")
            if new_p2w != m["p2w"] or new_p2s != m["p2s"]:
                m["p2w"] = new_p2w; m["p2s"] = new_p2s; changed = True
                
            if m["rw"]:
                pts, u_mult = calc_pts(m["p2w"], m["p2s"], m["rw"], m["rs"], pts_winner, pts_exact, m.get("tour",""), finale_mult, ja, jb, data)
                bonus_str = f' <span class="outsider-badge">Outsider x{u_mult}</span>' if u_mult > 1 and pts > 0 else ""
                
                if m["p2w"] == m["rw"] and m["p2s"] == m["rs"]: st.markdown(f'<span class="correct">✓ Parfait ! +{pts} pts</span>{bonus_str}', unsafe_allow_html=True)
                elif m["p2w"] == m["rw"]: st.markdown(f'<span class="partial">~ Vainqueur ok +{pts} pt(s)</span>{bonus_str}', unsafe_allow_html=True)
                elif m["p2w"]: st.markdown(f'<span class="wrong">✗ Raté — 0 pt</span>', unsafe_allow_html=True)

        with cr:
            st.markdown(f"**Résultat réel** {src_badge}", unsafe_allow_html=True)
            new_rw = st.selectbox("Vainqueur  ", opts, index=opts.index(m["rw"]) if m["rw"] in opts else 0, key=f"rw_{m['id']}")
            new_rs = st.selectbox("Score  ", SCORES, index=SCORES.index(m["rs"]) if m["rs"] in SCORES else 0, key=f"rs_{m['id']}")
            if new_rw != m["rw"] or new_rs != m["rs"]:
                m["rw"] = new_rw; m["rs"] = new_rs; m["source"] = "manuel"; changed = True

        if changed:
            save(); st.rerun()

st.divider()
st.caption(f"Roland-Garros 2026 · {len(data['matchs'])} matchs · Classements dynamiques inclus")