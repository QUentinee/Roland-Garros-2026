import streamlit as st
import pandas as pd
import json
import base64
import requests
from datetime import datetime

# ── Config ───────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Paris Roland-Garros 2026",
    page_icon="🎾",
    layout="wide",
)

ROUNDS = ["1er tour", "2ème tour", "3ème tour", "1/8 de finale",
          "1/4 de finale", "Demi-finale", "Finale"]
SCORES = ["", "3-0", "3-1", "3-2"]

MATCHS_DEFAUT = [
    {"id": 1, "tour": "1er tour",      "ja": "Sinner",    "jb": "Tabur",       "p1w": "", "p1s": "", "p2w": "", "p2s": "", "rw": "", "rs": ""},
    {"id": 2, "tour": "1er tour",      "ja": "Moutet",    "jb": "Rinderknech", "p1w": "", "p1s": "", "p2w": "", "p2s": "", "rw": "", "rs": ""},
    {"id": 3, "tour": "1er tour",      "ja": "Bublik",    "jb": "Struff",      "p1w": "", "p1s": "", "p2w": "", "p2s": "", "rw": "", "rs": ""},
    {"id": 4, "tour": "1er tour",      "ja": "Shelton",   "jb": "Auger-Aliassime", "p1w": "", "p1s": "", "p2w": "", "p2s": "", "rw": "", "rs": ""},
    {"id": 5, "tour": "1er tour",      "ja": "Zverev",    "jb": "Fils",        "p1w": "", "p1s": "", "p2w": "", "p2s": "", "rw": "", "rs": ""},
    {"id": 6, "tour": "1er tour",      "ja": "Djokovic",  "jb": "Fritz",       "p1w": "", "p1s": "", "p2w": "", "p2s": "", "rw": "", "rs": ""},
    {"id": 7, "tour": "1er tour",      "ja": "De Minaur", "jb": "Mensik",      "p1w": "", "p1s": "", "p2w": "", "p2s": "", "rw": "", "rs": ""},
    {"id": 8, "tour": "1er tour",      "ja": "Ruud",      "jb": "Paul",        "p1w": "", "p1s": "", "p2w": "", "p2s": "", "rw": "", "rs": ""},
]

DEFAULT_STATE = {
    "matchs": MATCHS_DEFAUT,
    "nom1": "Joueur 1",
    "nom2": "Joueur 2",
    "pts_winner": 1,
    "pts_exact": 3,
    "finale_mult": 2,
}

# ── GitHub helpers ────────────────────────────────────────────────────────────
GITHUB_TOKEN = st.secrets["github_token"]
GITHUB_REPO  = st.secrets["github_repo"]   # ex: "monpseudo/paris-rg"
DATA_FILE    = "data.json"
API_BASE     = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{DATA_FILE}"
HEADERS      = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json",
}

def gh_load():
    """Charge data.json depuis GitHub. Initialise si absent."""
    r = requests.get(API_BASE, headers=HEADERS)
    if r.status_code == 404:
        return DEFAULT_STATE.copy(), None
    r.raise_for_status()
    info = r.json()
    content = json.loads(base64.b64decode(info["content"]).decode())
    return content, info["sha"]

def gh_save(data, sha):
    """Écrit data.json sur GitHub."""
    encoded = base64.b64encode(json.dumps(data, ensure_ascii=False, indent=2).encode()).decode()
    payload = {
        "message": f"update data {datetime.utcnow().isoformat()}",
        "content": encoded,
    }
    if sha:
        payload["sha"] = sha
    r = requests.put(API_BASE, headers=HEADERS, json=payload)
    if r.status_code not in (200, 201):
        st.error(f"Erreur sauvegarde GitHub : {r.status_code} — {r.text}")
        return None
    return r.json()["content"]["sha"]

# ── Points ────────────────────────────────────────────────────────────────────
def calc_pts(pw, ps, rw, rs, pts_winner, pts_exact, tour, finale_mult):
    if not rw or not pw:
        return 0
    mult = finale_mult if tour == "Finale" else 1
    if pw == rw and ps == rs:
        return pts_exact * mult
    if pw == rw:
        return pts_winner * mult
    return 0

def totaux(matchs, pts_winner, pts_exact, finale_mult):
    t1 = t2 = 0
    for m in matchs:
        t1 += calc_pts(m["p1w"], m["p1s"], m["rw"], m["rs"], pts_winner, pts_exact, m["tour"], finale_mult)
        t2 += calc_pts(m["p2w"], m["p2s"], m["rw"], m["rs"], pts_winner, pts_exact, m["tour"], finale_mult)
    return t1, t2

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
.main-title{font-size:2rem;font-weight:700;color:#c8432a;margin-bottom:0}
.subtitle{color:#888;font-size:1rem;margin-bottom:1.5rem}
.score-box{background:#f9f4ef;border-radius:12px;padding:1rem 1.5rem;text-align:center;border:1px solid #e8ddd5}
.score-name{font-size:.85rem;color:#888;margin-bottom:4px}
.score-pts{font-size:2rem;font-weight:700;color:#c8432a}
.correct{color:#3a7d44;font-weight:600}
.partial{color:#b87a1e;font-weight:600}
.wrong{color:#c8432a;font-weight:600}
</style>
""", unsafe_allow_html=True)

# ── Chargement ────────────────────────────────────────────────────────────────
if "data" not in st.session_state or st.session_state.get("force_reload"):
    data, sha = gh_load()
    st.session_state["data"] = data
    st.session_state["sha"]  = sha
    st.session_state["force_reload"] = False

data = st.session_state["data"]
sha  = st.session_state["sha"]

def save():
    new_sha = gh_save(st.session_state["data"], st.session_state["sha"])
    if new_sha:
        st.session_state["sha"] = new_sha

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown('<p class="main-title">🎾 Paris Roland-Garros 2026</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Pronostics en temps réel — données partagées avec votre frère.</p>', unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Paramètres")

    st.subheader("Vos prénoms")
    nom1 = st.text_input("Joueur 1", value=data.get("nom1", "Joueur 1"))
    nom2 = st.text_input("Joueur 2", value=data.get("nom2", "Joueur 2"))
    if nom1 != data["nom1"] or nom2 != data["nom2"]:
        data["nom1"] = nom1
        data["nom2"] = nom2
        save()

    st.divider()
    st.subheader("Système de points")
    pts_winner  = st.number_input("Bon vainqueur",             min_value=0, max_value=99, value=data.get("pts_winner", 1))
    pts_exact   = st.number_input("Vainqueur + score exact",   min_value=0, max_value=99, value=data.get("pts_exact", 3))
    finale_mult = st.number_input("Multiplicateur finale (×)", min_value=1, max_value=10, value=data.get("finale_mult", 2))
    if st.button("💾 Sauvegarder les règles"):
        data["pts_winner"]  = pts_winner
        data["pts_exact"]   = pts_exact
        data["finale_mult"] = finale_mult
        save()
        st.success("Règles sauvegardées !")

    st.divider()
    st.subheader("Ajouter un match")
    with st.form("add_match"):
        new_tour = st.selectbox("Tour", ROUNDS)
        new_ja   = st.text_input("Joueur A")
        new_jb   = st.text_input("Joueur B")
        if st.form_submit_button("➕ Ajouter") and new_ja and new_jb:
            new_id = max((m["id"] for m in data["matchs"]), default=0) + 1
            data["matchs"].append({
                "id": new_id, "tour": new_tour,
                "ja": new_ja, "jb": new_jb,
                "p1w": "", "p1s": "", "p2w": "", "p2s": "", "rw": "", "rs": ""
            })
            save()
            st.success(f"Match ajouté : {new_ja} vs {new_jb}")
            st.rerun()

    st.divider()
    if st.button("🔄 Recharger depuis GitHub"):
        st.session_state["force_reload"] = True
        st.rerun()

# ── Scores totaux ─────────────────────────────────────────────────────────────
t1, t2 = totaux(data["matchs"], pts_winner, pts_exact, finale_mult)
c1, c2, _ = st.columns([1, 1, 2])
with c1:
    st.markdown(f'<div class="score-box"><div class="score-name">{nom1}</div><div class="score-pts">{t1} pts</div></div>', unsafe_allow_html=True)
with c2:
    st.markdown(f'<div class="score-box"><div class="score-name">{nom2}</div><div class="score-pts">{t2} pts</div></div>', unsafe_allow_html=True)

st.divider()

# ── Filtre ────────────────────────────────────────────────────────────────────
tour_filter = st.selectbox("Filtrer par tour", ["Tous"] + ROUNDS)

# ── Matchs ────────────────────────────────────────────────────────────────────
for idx, m in enumerate(data["matchs"]):
    if tour_filter != "Tous" and m["tour"] != tour_filter:
        continue

    ja, jb = m["ja"], m["jb"]
    label  = f"**{ja}** vs **{jb}**  —  _{m['tour']}_"

    with st.expander(label, expanded=(m["tour"] in ["Finale", "Demi-finale"])):
        cp1, cp2, cr = st.columns(3)

        changed = False

        # Joueur 1
        with cp1:
            st.markdown(f"**{nom1}**")
            opts = ["", ja, jb]
            new_p1w = st.selectbox("Vainqueur", opts,
                index=opts.index(m["p1w"]) if m["p1w"] in opts else 0,
                key=f"p1w_{m['id']}")
            new_p1s = st.selectbox("Score", SCORES,
                index=SCORES.index(m["p1s"]) if m["p1s"] in SCORES else 0,
                key=f"p1s_{m['id']}")
            if new_p1w != m["p1w"] or new_p1s != m["p1s"]:
                m["p1w"] = new_p1w
                m["p1s"] = new_p1s
                changed = True
            if m["rw"]:
                pts = calc_pts(m["p1w"], m["p1s"], m["rw"], m["rs"], pts_winner, pts_exact, m["tour"], finale_mult)
                if m["p1w"] == m["rw"] and m["p1s"] == m["rs"]:
                    st.markdown(f'<span class="correct">✓ Parfait ! +{pts} pts</span>', unsafe_allow_html=True)
                elif m["p1w"] == m["rw"]:
                    st.markdown(f'<span class="partial">~ Vainqueur ok +{pts} pt</span>', unsafe_allow_html=True)
                elif m["p1w"]:
                    st.markdown(f'<span class="wrong">✗ Raté — 0 pt</span>', unsafe_allow_html=True)

        # Joueur 2
        with cp2:
            st.markdown(f"**{nom2}**")
            new_p2w = st.selectbox("Vainqueur ", opts,
                index=opts.index(m["p2w"]) if m["p2w"] in opts else 0,
                key=f"p2w_{m['id']}")
            new_p2s = st.selectbox("Score ", SCORES,
                index=SCORES.index(m["p2s"]) if m["p2s"] in SCORES else 0,
                key=f"p2s_{m['id']}")
            if new_p2w != m["p2w"] or new_p2s != m["p2s"]:
                m["p2w"] = new_p2w
                m["p2s"] = new_p2s
                changed = True
            if m["rw"]:
                pts = calc_pts(m["p2w"], m["p2s"], m["rw"], m["rs"], pts_winner, pts_exact, m["tour"], finale_mult)
                if m["p2w"] == m["rw"] and m["p2s"] == m["rs"]:
                    st.markdown(f'<span class="correct">✓ Parfait ! +{pts} pts</span>', unsafe_allow_html=True)
                elif m["p2w"] == m["rw"]:
                    st.markdown(f'<span class="partial">~ Vainqueur ok +{pts} pt</span>', unsafe_allow_html=True)
                elif m["p2w"]:
                    st.markdown(f'<span class="wrong">✗ Raté — 0 pt</span>', unsafe_allow_html=True)

        # Résultat réel
        with cr:
            st.markdown("**Résultat réel**")
            new_rw = st.selectbox("Vainqueur  ", opts,
                index=opts.index(m["rw"]) if m["rw"] in opts else 0,
                key=f"rw_{m['id']}")
            new_rs = st.selectbox("Score  ", SCORES,
                index=SCORES.index(m["rs"]) if m["rs"] in SCORES else 0,
                key=f"rs_{m['id']}")
            if new_rw != m["rw"] or new_rs != m["rs"]:
                m["rw"] = new_rw
                m["rs"] = new_rs
                changed = True

        if changed:
            save()
            st.rerun()

st.divider()
st.caption("Données stockées sur GitHub • Partagez l'URL Streamlit avec votre frère")
