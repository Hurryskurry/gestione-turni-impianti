import streamlit as st
import pandas as pd
import hashlib

# Configurazione Pagina
st.set_page_config(page_title="Gestione Turni Impianti", layout="wide")

# --- DATABASE NOMINATIVI (31 OPERATORI) ---
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

# Configurazione Postazioni: Nome, Slot, Colore Sfondo, Etichette Ruoli
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

# --- LOGICA COLORI ---
def get_color(name):
    if name == "-": return "transparent"
    hash_object = hashlib.md5(name.encode())
    return f"#{hash_object.hexdigest()[:6]}"

def color_name(name, label=""):
    if name == "-" or not name: return ""
    color = get_color(name)
    prefix = f'<small style="opacity:0.8; font-size:8px;">{label}:</small> ' if label else ""
    return f'''
    <div style="background-color:{color}; color:white; padding:3px 6px; 
    border-radius:4px; margin:2px; display:inline-block; font-size:11px; 
    font-weight:bold; border:1px solid rgba(0,0,0,0.2); white-space:nowrap;">
    {prefix}{name}
    </div>'''

# --- STILI CSS PER INTERFACCIA E STAMPA ---
st.markdown("""
    <style>
    @media print {
        .stButton, .stSelectbox, .stExpander, header, footer, [data-testid="stSidebar"], .stTabs { display: none !important; }
        .main { padding: 0 !important; }
        .main-table { width: 100% !important; border-collapse: collapse; font-size: 10px !important; }
        th, td { border: 1px solid #333 !important; padding: 4px !important; text-align: center !important; }
        div, span { -webkit-print-color-adjust: exact !important; print-color-adjust: exact !important; }
    }
    .main-table { width: 100%; border-collapse: collapse; margin-top: 10px; font-family: 'Segoe UI', sans-serif; }
    .main-table th { background-color: #333; color: white; padding: 10px; border: 1px solid #111; }
    .main-table td { border: 1px solid #ccc; padding: 5px; vertical-align: top; min-width: 120px; }
    </style>
""", unsafe_allow_html=True)

st.title("🗓️ Tabellone Turni Settimanale")

# --- 1. SEZIONE INPUT (NASCOSTA IN STAMPA) ---
with st.expander("🛡️ CONFIGURA RIPOSI E ASSENZE", expanded=False):
    cols_r = st.columns(7)
    for idx, g in enumerate(giorni):
        st.session_state.riposi[g] = cols_r[idx].multiselect(f"Riposi {g}", nominativi, key=f"r_{g}")

st.write("### ✍️ Compilazione Turni")
cols_in = st.columns(7)
matrice_turni = {g: {} for g in giorni}

for idx, g in enumerate(giorni):
    # Gli operatori a riposo non sono selezionabili per il giorno g
    occupati_oggi = list(st.session_state.riposi[g])
    
    with cols_in[idx]:
        st.markdown(f"#### {g}")
        for post_name, info in postazioni_info.items():
            st.markdown(f"**{post_name}**")
            nomi_html = []
            for s_idx in range(info["slots"]):
                label = info["labels"][s_idx]
                res = st.selectbox(f"{label}", ["-"] + [n for n in nominativi if n not in occupati_oggi], 
                                   key=f"sel_{g}_{post_name}_{s_idx}", label_visibility="collapsed")
                if res != "-":
                    occupati_oggi.append(res)
                    nomi_html.append(color_name(res, label))
            matrice_turni[g][post_name] = "".join(nomi_html) if nomi_html else "-"

# --- 2. TABELLONE DI RIEPILOGO (VISIBILE IN STAMPA) ---
st.divider()
st.header("📋 Tabellone Finale Stampabile")

html_table = '<table class="main-table"><thead><tr><th>Postazione</th>'
for g in giorni:
    html_table += f'<th>{g}</th>'
html_table += '</tr></thead><tbody>'

# Righe degli impianti
for post_name, info in postazioni_info.items():
    html_table += f'<tr style="background-color: {info["bg"]};">'
    html_table += f'<td><b>{post_name}</b></td>'
    for g in giorni:
        html_table += f'<td>{matrice_turni[g][post_name]}</td>'
    html_table += '</tr>'

# Riga finale dei riposi
html_table += '<tr style="background-color: #f2f2f2; border-top: 3px solid #333;"><td><b>RIF. RIPOSI</b></td>'
for g in giorni:
    rip_html = "".join([color_name(n) for n in st.session_state.riposi[g]])
    html_table += f'<td>{rip_html if rip_html else "-"}</td>'
html_table += '</tr></tbody></table>'

st.write(html_table, unsafe_allow_html=True)

st.markdown("""
---
**Istruzioni per la stampa:**
1. Compila i nomi nei menu a tendina sopra.
2. Controlla che il tabellone riassuntivo sia corretto.
3. Premi **CTRL + P** sulla tastiera.
4. Nel pannello di stampa, scegli **Orientamento Orizzontale** e attiva **Grafica di Sfondo**.
""")