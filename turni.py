import streamlit as st
import pandas as pd
import hashlib

# Configurazione Pagina ottimizzata per Mobile
st.set_page_config(page_title="Turni Impianti Mobile", layout="wide", initial_sidebar_state="collapsed")

# --- DATABASE NOMINATIVI ---
nominativi = sorted([
    "Gobber Michael", "Bettega Giovanni", "Furlan Luca", "Battiston Francesco",
    "Longo Roberto", "Salamon Giandomenico", "Roana Luca", "Obber Jacopo",
    "Alex Cannella", "Andrea Cortesi", "Moser Valerio", "Rosante Davide",
    "Gambarini Kent", "Loss Elvis", "Bettega Mathias", "Zamborlin Mirko",
    "Tollardo Luca", "Loss Marco", "Remzi Seferi", "Cusin Giorgio",
    "Piccinini Lorenzo", "Tisot Andrea", "Cossa Roberto", "Gobber Luca",
    "De Rossi Stefano", "Arcati Ivan", "Carazzai Samuele", "Sperandio Marco",
    "Bottegal Ettore", "Bellani Cristian", "Lucian Sergio"
])

postazioni_info = {
    "CA15": {"slots": 4, "bg": "#E3F2FD", "labels": ["M1", "M2", "R1", "R2"]},
    "SA4": {"slots": 3, "bg": "#F1F8E9", "labels": ["M", "R1", "R2"]},
    "CIGOLERA": {"slots": 3, "bg": "#FCE4EC", "labels": ["M", "R1", "R2"]},
    "CIMA": {"slots": 3, "bg": "#FFFDE7", "labels": ["M", "R1", "R2"]},
    "SCANDOLA": {"slots": 3, "bg": "#F3E5F5", "labels": ["M", "R1", "R2"]},
    "CONCA": {"slots": 3, "bg": "#EFEBE9", "labels": ["M", "R1", "R2"]},
    "BABY": {"slots": 3, "bg": "#E0F7FA", "labels": ["M", "R1", "R2"]},
    "PISTE": {"slots": 3, "bg": "#FFF3E0", "labels": ["M", "R1", "R2"]},
    "SOCCORSO PISTE": {"slots": 2, "bg": "#FFEBEE", "labels": ["S1", "S2"]},
    "GARAGE GATTI": {"slots": 1, "bg": "#F9FBE7", "labels": ["Addetto"]},
    "PIAZZALI": {"slots": 1, "bg": "#E8EAF6", "labels": ["Addetto"]}
}

giorni = ["Lun", "Mar", "Mer", "Gio", "Ven", "Sab", "Dom"]

if 'riposi' not in st.session_state:
    st.session_state.riposi = {g: [] for g in giorni}

# --- FUNZIONI COLORI ---
def get_color(name):
    if name == "-": return "transparent"
    hash_object = hashlib.md5(name.encode())
    return f"#{hash_object.hexdigest()[:6]}"

def color_name(name, label=""):
    if name == "-" or not name: return ""
    color = get_color(name)
    prefix = f'<small style="font-size:9px; opacity:0.8;">{label}:</small> ' if label else ""
    return f'''<div style="background-color:{color}; color:white; padding:4px 8px; border-radius:6px; 
    margin:2px; display:inline-block; font-size:12px; font-weight:bold; border:1px solid rgba(0,0,0,0.2);">{prefix}{name}</div>'''

# --- CSS PER MOBILE E STAMPA ---
st.markdown("""
    <style>
    /* Ottimizzazione per Mobile */
    .stSelectbox { margin-bottom: -15px; }
    .main-table-container { width: 100%; overflow-x: auto; -webkit-overflow-scrolling: touch; }
    .main-table { width: 100%; border-collapse: collapse; min-width: 800px; }
    .main-table th, .main-table td { border: 1px solid #ddd; padding: 10px; text-align: left; vertical-align: top; }
    
    @media print {
        .stTabs, .stExpander, header, footer, .stButton { display: none !important; }
        .main-table { min-width: 100% !important; font-size: 10px; }
    }
    </style>
""", unsafe_allow_html=True)

st.title("📱 Gestione Turni Mobile")

# --- SEZIONE RIPOSI ---
with st.expander("🛡️ CONFIGURA RIPOSI"):
    st.info("Seleziona chi è in riposo per ogni giorno.")
    tabs_rip = st.tabs(giorni)
    for idx, g in enumerate(giorni):
        with tabs_rip[idx]:
            st.session_state.riposi[g] = st.multiselect(f"Chi riposa il {g}?", nominativi, key=f"r_{g}")

st.divider()

# --- COMPILAZIONE TURNI (Tabs per Mobile) ---
st.write("### ✍️ Compila i Turni")
tabs_giorni = st.tabs(giorni)
matrice_turni = {g: {} for g in giorni}

for idx, g in enumerate(giorni):
    occupati_oggi = list(st.session_state.riposi[g])
    with tabs_giorni[idx]:
        for post_name, info in postazioni_info.items():
            with st.expander(f"🚠 {post_name}", expanded=(post_name=="CA15")):
                nomi_html = []
                # Layout interno a colonne per gli slot
                grid_slots = st.columns(2 if info["slots"] > 1 else 1)
                for s_idx in range(info["slots"]):
                    label = info["labels"][s_idx]
                    target_col = grid_slots[s_idx % 2]
                    with target_col:
                        res = st.selectbox(f"{label}", ["-"] + [n for n in nominativi if n not in occupati_oggi], 
                                           key=f"sel_{g}_{post_name}_{s_idx}")
                        if res != "-":
                            occupati_oggi.append(res)
                            nomi_html.append(color_name(res, label))
                matrice_turni[g][post_name] = "".join(nomi_html) if nomi_html else "-"

# --- TABELLONE FINALE (Scrollabile su Mobile) ---
st.divider()
st.header("📋 Tabellone Settimanale Completo")
st.caption("Scorri verso destra se sei su smartphone ➡️")

html_table = '<div class="main-table-container"><table class="main-table"><thead><tr><th>Postazione</th>'
for g in giorni:
    html_table += f'<th>{g}</th>'
html_table += '</tr></thead><tbody>'

for post_name, info in postazioni_info.items():
    html_table += f'<tr style="background-color: {info["bg"]};">'
    html_table += f'<td><b>{post_name}</b></td>'
    for g in giorni:
        html_table += f'<td>{matrice_turni[g][post_name]}</td>'
    html_table += '</tr>'

html_table += '<tr style="background-color: #f2f2f2;"><td><b>RIF. RIPOSI</b></td>'
for g in giorni:
    rip_html = "".join([color_name(n) for n in st.session_state.riposi[g]])
    html_table += f'<td>{rip_html if rip_html else "-"}</td>'
html_table += '</tr></tbody></table></div>'

st.write(html_table, unsafe_allow_html=True)

st.markdown("""
---
**Consigli Mobile:**
- Usa i **Tabs** (Lun, Mar...) per cambiare giorno velocemente.
- Gli **Expander** (nomi impianti) tengono la pagina pulita.
- Per stampare da telefono, usa la funzione 'Condividi' -> 'Stampa'.
""")
