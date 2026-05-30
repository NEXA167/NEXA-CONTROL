import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import sqlite3

# --- 1. FUNZIONE DATABASE (THREAD-SAFE) ---
def esegui_query(query, params=(), fetch="none"):
    conn = sqlite3.connect("nexa_cloud.db", check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute(query, params)
    risultato = None
    if fetch == "all": risultato = cursor.fetchall()
    elif fetch == "one": risultato = cursor.fetchone()
    conn.commit()
    conn.close()
    return risultato # CORRETTO QUI: Ritorno pulito senza errori di sintassi

# Righe di manutenzione per aggiornare il database esistente
try:
    esegui_query("ALTER TABLE dati_mensili ADD COLUMN scadenze_attive REAL DEFAULT 0.0;")
except:
    pass

try:
    esegui_query("ALTER TABLE dati_mensili ADD COLUMN rateizzazioni_extra REAL DEFAULT 0.0;")
except:
    pass

# Righe di manutenzione per aggiornare il database esistente (NON TOCCARE LE VECCHIE)
try:
    esegui_query("ALTER TABLE dati_mensili ADD COLUMN scadenze_attive REAL DEFAULT 0.0;")
except: pass

try:
    esegui_query("ALTER TABLE dati_mensili ADD COLUMN rateizzazioni_extra REAL DEFAULT 0.0;")
except: pass

# AGGIUNGI QUESTA NUOVA RIGA DI MANUTENZIONE QUI SOTTO:
try:
    esegui_query("ALTER TABLE dati_mensili ADD COLUMN finanziamenti_extra REAL DEFAULT 0.0;")
except: pass

# Inizializzazione tabelle aziendali (SOSTITUISCI CON QUESTA NUOVA STRUTTURA)
esegui_query("CREATE TABLE IF NOT EXISTS utenti (username TEXT PRIMARY KEY, password TEXT, azienda TEXT)")
esegui_query("""
    CREATE TABLE IF NOT EXISTS dati_mensili (
        id TEXT PRIMARY KEY, username TEXT, mese TEXT, fatturato REAL,
        margine REAL, cassa REAL, costi_variabili REAL, costi_fissi REAL,
        mutui_leasing REAL, iva_contributi REAL, magazzino REAL,
        scadenze_attive REAL, rateizzazioni_extra REAL, finanziamenti_extra REAL
    )
""")
esegui_query("INSERT OR IGNORE INTO utenti VALUES ('arteq', 'bloom2026', 'Arteq S.r.l.')")
esegui_query("INSERT OR IGNORE INTO utenti VALUES ('luca', 'nexa123', 'Consulenza Luca')")
esegui_query("INSERT OR IGNORE INTO utenti VALUES ('monica','monica2026', 'MONICA')")

# --- 2. CONFIGURAZIONE PAGINA ED ELEGANZA VISIVA ---
st.set_page_config(page_title="Nexa SaaS Platform", layout="wide", initial_sidebar_state="collapsed")

if "autenticato" not in st.session_state:
    st.session_state.autenticato = False
    st.session_state.utente_attuale = ""
    st.session_state.azienda_attuale = ""

# --- 3. SCHERMATA DI LOGIN ULTRA-BLINDATA ANTI AUTOFILL ---
if not st.session_state.autenticato:
    st.markdown("""
        <style>
        .stApp { background-color: #EBF0F5 !important; } 
        .login-minimal-container { max-width: 530px; margin: 120px auto; text-align: center; }
        .login-title-minimal { color: #0F172A; font-size: 41px; font-weight: 800; letter-spacing: -0.5px; margin: 0; text-align: center !important; display: block; width: 100%; }
        .login-subtitle-minimal { color: #64748B; font-size: 15px; margin-bottom: 40px; text-align: center; }
        .field-label-minimal { color: #0F172A !important; font-size: 19px; font-weight: 700; text-align: left !important; margin-bottom: 6px; margin-top: 25px; width: 55%; margin-left: 22.5% !important; }
        div[data-testid="stTextInput"] { width: 55% !important; margin: 0 auto !important; }
        
        /* Uniformiamo i box d'inserimento bianchi puliti */
        div[data-baseweb="input"] { border: 2px solid #CBD5E1 !important; border-radius: 8px !important; background-color: #FFFFFF !important; }
        div[data-baseweb="input"] > div { background-color: #FFFFFF !important; }
        
        input { color: #0F172A !important; font-weight: 600 !important; font-size: 19px !important; text-align: center !important; }
        
        /* MASCHERA DI PROTEZIONE PER IL CAMPO PASSWORD */
        .scudo-password-input input {
            -webkit-text-security: disk !important; 
            text-security: disk !important;
        }
        
        .btn-container-minimal { width: 55%; margin: 40px auto 0 auto; }
        .btn-container-minimal button { font-size: 18px !important; font-weight: 800 !important; padding: 12px 20px !important; background-color: #0F172A !important; color: #FFFFFF !important; border-radius: 8px !important; border: none !important; box-shadow: 0 4px 10px rgba(15, 23, 42, 0.15) !important; }
        </style>
        """, unsafe_allow_html=True)
        
    st.markdown("<div class='login-minimal-container'>", unsafe_allow_html=True)
    st.markdown("<h1 class='login-title-minimal'>🚀 NEXA CONTROL</h1>", unsafe_allow_html=True)
    st.markdown("<p class='login-subtitle-minimal'>Pannello di Accesso Server Predittivo</p>", unsafe_allow_html=True)
    
    st.markdown("<p class='field-label-minimal'>👤 USERNAME</p>", unsafe_allow_html=True)
    user_input = st.text_input("nexa_field_usr_secure_gate", label_visibility="collapsed", autocomplete="off").strip().lower()
    
    st.markdown("<p class='field-label-minimal'>🔒 PASSWORD</p>", unsafe_allow_html=True)
    st.markdown("<div class='scudo-password-input'>", unsafe_allow_html=True)
    pass_input = st.text_input("nexa_field_pwd_secure_gate", label_visibility="collapsed", autocomplete="off", type="password")
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("<div class='btn-container-minimal'>", unsafe_allow_html=True)
    if st.button("ACCEDI AL SOFTWARE", use_container_width=True):
        risultato = esegui_query("SELECT password, azienda FROM utenti WHERE username = ?", (user_input,), fetch="one")
        if risultato and risultato[0] == pass_input:
            st.session_state.autenticato = True
            st.session_state.utente_attuale = user_input
            st.session_state.azienda_attuale = risultato[1]
            st.rerun()
        else:
            st.error("❌ Credenziali errate. Riprova.")
    st.markdown("</div></div>", unsafe_allow_html=True)
    st.stop()

# --- 4. STILE DASHBOARD REALE ---
st.markdown("""
    <style>
    .stApp { background-color: #EBF0F5 !important; }
    .main { background-color: #EBF0F5; color: #1E293B; }
    .stButton>button { background-color: #FFFFFF; color: #1E293B; border: 1px solid #CBD5E1; border-radius: 8px; font-weight: bold; padding: 8px 16px; }
    .titolo-grafico-libero { color: #1E293B; font-size: 15px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 5px; }
    .testo-valore-centrale { color: #0F172A; font-size: 42px; font-weight: 800; text-align: center; margin: 15px 0; }
    .kpi-mini-box { background-color: #FFFFFF; border-radius: 10px; padding: 15px; border: 1px solid #E2E8F0; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.02); }
    .anteprima-valuta { color: #15803D; font-size: 13px; font-weight: 700; margin-top: 2px; margin-bottom: 12px; }
    .label-maschera { font-weight: 700; color: #0F172A; margin-bottom: 2px; margin-top: 12px; font-size: 14px; }
    .badge-ccii { display: inline-block; padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: 700; margin-top: 5px; }
    </style>
    """, unsafe_allow_html=True)

# --- 5. CARICAMENTO DATI ---
username = st.session_state.utente_attuale

def carica_database_utente(user):
    righe = esegui_query("SELECT mese, fatturato, margine, cassa, costi_variabili, costi_fissi, mutui_leasing, iva_contributi, magazzino, scadenze_attive, rateizzazioni_extra, finanziamenti_extra FROM dati_mensili WHERE username = ?", (user,), fetch="all")
    mesi = ["Gennaio", "Febbraio", "Marzo", "Aprile", "Maggio", "Giugno", "Luglio", "Agosto", "Settembre", "Ottobre", "Novembre", "Dicembre"]
    df = pd.DataFrame({
        "Mese": mesi, "Fatturato": [0.0]*12, "Margine %": [0.25]*12, "Saldo Banca (Cassa)": [0.0]*12,
        "Costi Variabili": [0.0]*12, "Costi Fissi (Fornitori)": [0.0]*12, "Mutui e Leasing": [0.0]*12,
        "Debiti IVA e Contributi": [0.0]*12, "Valore Magazzino": [0.0]*12,
        "scadenze_attive": [0.0]*12, "rateizzazioni_extra": [0.0]*12, "finanziamenti_extra": [0.0]*12
    })
    for r in righe:
        idx = df[df["Mese"] == r[0]].index[0]
        df.at[idx, "Fatturato"] = r[1]
        df.at[idx, "Margine %"] = r[2]
        df.at[idx, "Saldo Banca (Cassa)"] = r[3]
        df.at[idx, "Costi Variabili"] = r[4]
        df.at[idx, "Costi Fissi (Fornitori)"] = r[5]
        df.at[idx, "Mutui e Leasing"] = r[6]
        df.at[idx, "Debiti IVA e Contributi"] = r[7]
        df.at[idx, "Valore Magazzino"] = r[8]
        if len(r) > 9: df.at[idx, "scadenze_attive"] = r[9]
        if len(r) > 10: df.at[idx, "rateizzazioni_extra"] = r[10]
        if len(r) > 11: df.at[idx, "finanziamenti_extra"] = r[11]
    return df

db_utente = carica_database_utente(username)

# --- 6. POP-UP MASCHERA INSERIMENTO ---
@st.dialog("📥 INSERISCI DATI MENSILI")
def mostra_maschera_inserimento():
    st.markdown("### Configura i parametri operativi del mese")
    mese_scelto = st.selectbox("Seleziona il Mese da analizzare", db_utente["Mese"].tolist())
    dati_attuali = db_utente[db_utente["Mese"] == mese_scelto].iloc[0]
    
    st.markdown("---")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("#### 🚀 Prestazioni")
        st.markdown("<p class='label-maschera'>Fatturato Imponibile (€)</p>", unsafe_allow_html=True)
        f_val = st.number_input("f_n_new", min_value=0.0, value=float(dati_attuali["Fatturato"]), step=5000.0, label_visibility="collapsed")
        st.markdown("<p class='label-maschera'>Margine Stimato (es. 0.25)</p>", unsafe_allow_html=True)
        m_val = st.number_input("m_n_new", min_value=0.0, max_value=1.0, value=float(dati_attuali["Margine %"]), format="%.2f", step=0.01, label_visibility="collapsed")

    with col2:
        st.markdown("#### 💰 Cassa e Merci")
        st.markdown("<p class='label-maschera'>Saldo Banca (Cassa) (€)</p>", unsafe_allow_html=True)
        banca_val = st.number_input("banca_n_new", min_value=0.0, value=float(dati_attuali["Saldo Banca (Cassa)"]), step=5000.0, label_visibility="collapsed")
        st.markdown("<p class='label-maschera'>Valore Stima Magazzino (€)</p>", unsafe_allow_html=True)
        mag_val = st.number_input("mag_n_new", min_value=0.0, value=float(dati_attuali["Valore Magazzino"]), step=1000.0, label_visibility="collapsed")

    with col3:
        st.markdown("#### 📉 Struttura Costi")
        st.markdown("<p class='label-maschera'>Fornitori Componenti / Produzione (€)</p>", unsafe_allow_html=True)
        cv_val = st.number_input("cv_n_new", min_value=0.0, value=float(dati_attuali["Costi Variabili"]), step=5000.0, label_visibility="collapsed")
        st.markdown("<p class='label-maschera'>Spese Fisse Struttura (Affitti/Servizi) (€)</p>", unsafe_allow_html=True)
        cf_val = st.number_input("cf_n_new", min_value=0.0, value=float(dati_attuali["Costi Fissi (Fornitori)"]), step=1000.0, label_visibility="collapsed")
        st.markdown("<p class='label-maschera'>Uscite Mutui e Leasing (€)</p>", unsafe_allow_html=True)
        ml_val = st.number_input("ml_n_new", min_value=0.0, value=float(dati_attuali["Mutui e Leasing"]), step=500.0, label_visibility="collapsed")

    with col4:
        st.markdown("#### 🏛️ Fisco e Previsioni")
        st.markdown("<p class='label-maschera'>Debiti IVA e Contributi (€)</p>", unsafe_allow_html=True)
        iva_val = st.number_input("iva_n_new", min_value=0.0, value=float(dati_attuali["Debiti IVA e Contributi"]), step=1000.0, label_visibility="collapsed")
        st.markdown("<p class='label-maschera'>🔮 Incassi Mese Prossimo (€)</p>", unsafe_allow_html=True)
        scadenze_val = st.number_input("scadenze_n_final", min_value=0.0, value=float(dati_attuali["scadenze_attive"]), step=1000.0, label_visibility="collapsed")
        st.markdown("<p class='label-maschera'>🏛️ Rateizzazioni Extra (€)</p>", unsafe_allow_html=True)
        rateizzazioni_val = st.number_input("rateizzazioni_n_final", min_value=0.0, value=float(dati_attuali["rateizzazioni_extra"]), step=500.0, label_visibility="collapsed")
        st.markdown("<p class='label-maschera'>🏦 Finanziamenti / Liquidità Extra (€)</p>", unsafe_allow_html=True)
        fin_val = st.number_input("fin_n_final", min_value=0.0, value=float(dati_attuali["finanziamenti_extra"]), step=5000.0, label_visibility="collapsed")
    
    if st.button("SALVA E RICALCOLA LOGICHE", use_container_width=True):
        id_chiave = f"{username}_{mese_scelto}"
        esegui_query("""
            INSERT OR REPLACE INTO dati_mensili (id, username, mese, fatturato, margine, cassa, costi_variabili, costi_fissi, mutui_leasing, iva_contributi, magazzino, scadenze_attive, rateizzazioni_extra, finanziamenti_extra)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (id_chiave, username, mese_scelto, f_val, m_val, banca_val, cv_val, cf_val, ml_val, iva_val, mag_val, scadenze_val, rateizzazioni_val, fin_val))
        st.rerun()

# Calcoli matematici e Previsionali (Aggiornati con Allert 30gg)
costi_fissi_totali = db_utente['Costi Fissi (Fornitori)'] + db_utente['Mutui e Leasing']
db_utente['Punto di Pareggio'] = np.where(db_utente['Margine %'] > 0, costi_fissi_totali / db_utente['Margine %'], 0.0)

df_attivi = db_utente[db_utente['Fatturato'] > 0]
media_fatturato = df_attivi['Fatturato'].mean() if not df_attivi.empty else 0.0
punto_pareggio_medio = db_utente[db_utente['Punto di Pareggio'] > 0]['Punto di Pareggio'].mean() if not db_utente[db_utente['Punto di Pareggio'] > 0].empty else 0.0

magazzini_compilati = db_utente[db_utente['Valore Magazzino'] > 0]
magazzino_attuale = magazzini_compilati['Valore Magazzino'].iloc[-1] if not magazzini_compilati.empty else 0.0

ultimo_margine_pct = df_attivi['Margine %'].iloc[-1] if not df_attivi.empty else 0.25
ultimo_costo_fisso = df_attivi['Costi Fissi (Fornitori)'].iloc[-1] if not df_attivi.empty else 0.0
ultimo_leasing = df_attivi['Mutui e Leasing'].iloc[-1] if not df_attivi.empty else 0.0
ultimo_fatturato = df_attivi['Fatturato'].iloc[-1] if not df_attivi.empty else 0.0
ultima_cassa = df_attivi['Saldo Banca (Cassa)'].iloc[-1] if not df_attivi.empty else 0.0

# Recuperiamo i dati predittivi inseriti da Monica
ultime_scadenze = df_attivi['scadenze_attive'].iloc[-1] if 'scadenze_attive' in df_attivi.columns and not df_attivi.empty else 0.0
ultime_rateizzazioni = df_attivi['rateizzazioni_extra'].iloc[-1] if 'rateizzazioni_extra' in df_attivi.columns and not df_attivi.empty else 0.0

# FORMULA PREDITTIVA CASSA A 30 GIORNI
costi_prossimo_mese = ultimo_costo_fisso + ultimo_leasing + ultime_rateizzazioni
cassa_previsionale = ultima_cassa + ultime_scadenze - costi_prossimo_mese

# NUOVO CALCOLO MATEMATICO DSCR FINANZIARIO PREDITTIVO
numeratore_dscr = ultima_cassa + ultime_scadenze - ultimo_costo_fisso
denominatore_dscr = ultimo_leasing + ultime_rateizzazioni

if denominatore_dscr > 0:
    dscr_calcolato = numeratore_dscr / denominatore_dscr
else:
    dscr_calcolato = 1.0 if numeratore_dscr >= 0 else 0.0

bep_mensile_sicurezza = (ultimo_costo_fisso + ultimo_leasing) / ultimo_margine_pct if ultimo_margine_pct > 0 else 0.0
ebitda_stimato = (ultimo_fatturato * ultimo_margine_pct) - (ultimo_costo_fisso + ultimo_leasing)

incidenza_costi_pct = (costi_fissi_totali.sum() / df_attivi['Fatturato'].sum() * 100) if not df_attivi.empty and df_attivi['Fatturato'].sum() > 0 else 0.0 
# --- 7. BARRA SUPERIORE ---
header_col1, header_col2, header_col3 = st.columns([1.8, 1.1, 1.1])
with header_col1:
    st.markdown(f"<h1 style='color: #0F172A; margin:0; font-size: 26px;'>NEXA PLATFORM — {st.session_state.azienda_attuale}</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='color: #64748B; font-size: 13px; margin:0;'>Account Cloud Attivo: <b>{username}</b></p>", unsafe_allow_html=True)

with header_col2:
    if st.button("➕ INSERISCI DATI MENSILI", use_container_width=True):
        mostra_maschera_inserimento()
    # Iniezione Fatturato Sicurezza sotto al bottone
    st.markdown(f"""
        <div style='background-color:#FFFFFF; padding:8px; border-radius:6px; border:1px solid #E2E8F0; text-align:center; margin-top:5px; box-shadow:0 1px 2px rgba(0,0,0,0.02);'>
            <p style='color:#64748B; font-size:10px; font-weight:700; text-transform:uppercase; margin:0;'>🎯 BEP Sicurezza</p>
            <h4 style='color:#0F172A; margin:2px 0; font-size:15px;'>€ {bep_mensile_sicurezza:,.2f}</h4>
        </div>
    """, unsafe_allow_html=True)

with header_col3:
    if st.button("🚪 LOGOUT", use_container_width=True):
        st.session_state.autenticato = False
        st.session_state.utente_attuale = ""
        st.rerun()
    # Iniezione EBITDA e DSCR sotto al logout
    colore_ebitda = "#15803D" if ebitda_stimato >= 0 else "#B91C1C"
    if 'scadenze_attive' in df_attivi.columns and (ultime_scadenze > 0 or ultime_rateizzazioni > 0):
        txt_dscr = f"DSCR: {dscr_calcolato:.2f}"
    else:
        txt_dscr = "DSCR: --"
        
    st.markdown(f"""
        <div style='background-color:#FFFFFF; padding:8px; border-radius:6px; border:1px solid #E2E8F0; text-align:center; margin-top:5px; box-shadow:0 1px 2px rgba(0,0,0,0.02);'>
            <p style='color:#64748B; font-size:10px; font-weight:700; text-transform:uppercase; margin:0;'>📊 EBITDA | {txt_dscr}</p>
            <h4 style='color:{colore_ebitda}; margin:2px 0; font-size:15px;'>€ {ebitda_stimato:,.2f}</h4>
        </div>
    """, unsafe_allow_html=True)
    st.markdown("<br><br>", unsafe_allow_html=True)
# --- SPAZIATURA DI RESPIRO PER L'HEADER ---
st.markdown("<br><br>", unsafe_allow_html=True)

# --- 8. DISTRIBUZIONE GRAFICI ---
col_p1, col_p2, col_p3 = st.columns(3)

with col_p1:
    st.markdown("<div class='titolo-grafico-libero'>1. Punto di Pareggio (BEP)</div>", unsafe_allow_html=True)
    if media_fatturato > 0 or punto_pareggio_medio > 0:
        valore_max = max(punto_pareggio_medio * 1.5, media_fatturato * 1.2, 50000)
        fig_gauge = go.Figure(go.Indicator(
            mode = "gauge+number", value = media_fatturato,
            number = {'prefix': "€ ", 'valueformat': ",.2f", 'font': {'size': 22, 'color': '#0F172A'}},
            domain = {'x': [0, 1], 'y': [0, 1]},
            gauge = {
                'axis': {'range': [0, valore_max], 'tickwidth': 1, 'tickcolor': "#475569"},
                'bar': {'color': "#1E293B", 'thickness': 0.22},
                'steps': [
                    {"range": [0, max(punto_pareggio_medio, 1.0)], "color": "#FEE2E2"}, 
                    {"range": [max(punto_pareggio_medio, 1.0), valore_max], "color": "#DCFCE7"}
                ],
                'threshold': {'line': {'color': "red", 'width': 3}, 'thickness': 0.75, 'value': max(punto_pareggio_medio, 0.1)}
            }
        ))
        fig_gauge.update_layout(margin=dict(l=5, r=5, t=30, b=5), height=200, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_gauge, use_container_width=True, key="gauge_v58_final")
    else:
        st.info("📥 Inserisci i dati mensili per attivare il tachimetro.")

with col_p2:
    st.markdown("<div class='titolo-grafico-libero'>2. Monitor del Magazzino</div>", unsafe_allow_html=True)
    fig_mag = go.Figure()
    fig_mag.add_trace(go.Indicator(
        mode = "number", value = magazzino_attuale,
        number = {'prefix': "€ ", 'valueformat': ",.2f", 'font': {'size': 38, 'color': '#0F172A'}},
        domain = {'x': [0, 1], 'y': [0, 1]}
    ))
    fig_mag.update_layout(margin=dict(l=5, r=5, t=5, b=5), height=140, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_mag, use_container_width=True, key="mag_v58_final")
    st.markdown("<p style='text-align:center; color:#64748B; font-size:12px; font-weight:600; margin-top:10px;'>Capitale Dormiente Attuale</p>", unsafe_allow_html=True)

with col_p3:
    st.markdown("<div class='titolo-grafico-libero'>3. Radar Cassa & Allerta Predittiva</div>", unsafe_allow_html=True)
    
    if 'scadenze_attive' in df_attivi.columns and (ultime_scadenze > 0 or ultime_rateizzazioni > 0):
        if cassa_previsionale >= 0:
            st.success(f"🟢 CASSA PREVISTA 30GG: OK\n\nSaldo stimato: € {cassa_previsionale:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
            st.markdown("<p style='font-size:12px; color:#64748B; margin-top:5px;'>Gli incassi futuri coprono interamente le scadenze e i costi di struttura del prossimo mese.</p>", unsafe_allow_html=True)
        else:
            mancano_soldi = abs(cassa_previsionale)
            st.error(f"🔴 ALLERTA SCOMPENSO DI CASSA\n\nDeficit stimato: € -{mancano_soldi:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
            st.markdown(f"<p style='font-size:12px; color:#B91C1C; font-weight:600; margin-top:5px;'>⚠️ Attenzione: pianificare anticipi fatture o fidi per almeno € {mancano_soldi:,.2f} per evitare tensioni di liquidità.</p>", unsafe_allow_html=True)
    else:
        if not df_attivi.empty:
            mesi_attivi = df_attivi['Mese'].tolist()
            fig_line = go.Figure()
            fig_line.add_trace(go.Scatter(x=mesi_attivi, y=df_attivi['Fatturato'], mode='lines+markers', name='Fatturato', line=dict(color='#1E88E5', width=3)))
            fig_line.add_trace(go.Scatter(x=mesi_attivi, y=df_attivi['Punto di Pareggio'], mode='lines', name='Pareggio', line=dict(color='red', dash='dash')))
            fig_line.update_layout(margin=dict(l=5, r=5, t=5, b=5), height=140, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', showlegend=False)
            st.plotly_chart(fig_line, use_container_width=True, key="line_v58_final")
            
            st.markdown(f"<p style='margin:0; font-size:13px; font-weight:600;'>Incidenza Costi Fissi Struttura: {incidenza_costi_pct:.1f}%</p>", unsafe_allow_html=True)
            if incidenza_costi_pct > 50.0 or media_fatturato < punto_pareggio_medio:
                st.markdown("<span class='badge-ccii' style='background-color:#FEE2E2; color:#B91C1C;'>🚨 ALLERTA RISCHIO CCII CRITICO</span>", unsafe_allow_html=True)
            elif 30.0 <= incidenza_costi_pct <= 50.0:
                st.markdown("<span class='badge-ccii' style='background-color:#FEF08A; color:#A16207;'>🟡 SOGLIA DI ATTENZIONE OPERATIVA</span>", unsafe_allow_html=True)
            else:
                st.markdown("<span class='badge-ccii' style='background-color:#DCFCE7; color:#15803D;'>🟢 SOSTENIBILITÀ AZIENDALE OTTIMALE</span>", unsafe_allow_html=True)
        else:
            st.info("📥 In attesa di storico dati.")

# --- 9. MONITORAGGIO FLUSSO DI CASSA REALE & ALLERTE PREDITTIVE ---
st.markdown("---")
st.markdown("### 💸 4. Monitoraggio Flusso di Cassa Reale & Allerte")

if not df_attivi.empty:
    df_cashflow = df_attivi.copy()
    df_cashflow['Uscite Totali Mese'] = df_cashflow['Costi Variabili'] + df_cashflow['Costi Fissi (Fornitori)'] + df_cashflow['Mutui e Leasing']
    df_cashflow['Flusso Cassa Netto'] = df_cashflow['Fatturato'] - df_cashflow['Uscite Totali Mese']
    
    # Calcolo Opzione B: Cassa Netta Generata da inizio anno + Finanziamenti Extra Inseriti
    cassa_generata_totale = df_cashflow['Flusso Cassa Netto'].sum()
    finanziamenti_ricevuti_totale = df_cashflow['finanziamenti_extra'].sum() if 'finanziamenti_extra' in df_cashflow.columns else 0.0
    cassa_disponibile_calcolata = cassa_generata_totale + finanziamenti_ricevuti_totale
    
    # SANIFICAZIONE DENOMINATORE: Se l'ultimo costo fisso è 0, prendiamo la media dei costi fissi storici, altrimenti usiamo 1.0 per evitare divisioni per zero
    costo_struttura_riferimento = ultimo_costo_fisso
    if costo_struttura_riferimento == 0:
        costo_struttura_riferimento = df_cashflow['Costi Fissi (Fornitori)'].mean() if df_cashflow['Costi Fissi (Fornitori)'].mean() > 0 else 1.0
        
    mesi_autonomia = cassa_disponibile_calcolata / costo_struttura_riferimento
    if mesi_autonomia < 0: mesi_autonomia = 0.0

    tot_acquisti = df_cashflow['Costi Variabili'].sum()
    tot_fatturato = df_cashflow['Fatturato'].sum()
    incidenza_acquisti_pct = (tot_acquisti / tot_fatturato * 100) if tot_fatturato > 0 else 0.0

    # Badge Superiori
    badge_col1, badge_col2 = st.columns(2)
    with badge_col1:
        if mesi_autonomia >= 2.0:
            colore_aut = "#15803D"
            stato_aut = "🟢 SICURA"
        elif 1.0 <= mesi_autonomia < 2.0:
            colore_aut = "#A16207"
            stato_aut = "🟡 DA MONITORARE"
        else:
            colore_aut = "#B91C1C"
            stato_aut = "🔴 CRITICA"
            
        st.markdown(f"""
            <div style='background-color:#F8FAFC; padding:12px; border-radius:8px; border:1px solid #E2E8F0; border-left:5px solid {colore_aut};'>
                <p style='color:#64748B; font-size:11px; font-weight:700; text-transform:uppercase; margin:0;'>🛡️ Autonomia Struttura (Cassa Netta + Finanziamenti)</p>
                <h3 style='color:{colore_aut}; margin:4px 0; font-size:18px;'>{mesi_autonomia:.1f} Mesi ({stato_aut})</h3>
                <p style='color:#475569; font-size:11px; margin:0;'>Autonomia stimata integrando la liquidità generata e i crediti esterni accreditati.</p>
            </div>
        """, unsafe_allow_html=True)
        
    with badge_col2:
        if incidenza_acquisti_pct <= 65.0:
            colore_term = "#15803D"
            stato_term = "🟢 EQUILIBRATO"
        elif 65.0 < incidenza_acquisti_pct <= 75.0:
            colore_term = "#A16207"
            stato_term = "🟡 MAGAZZINO IN CRESCITA"
        else:
            colore_term = "#B91C1C"
            stato_term = "🔴 SOVRA-APPROVVIGIONAMENTO CRITICO"
            
        st.markdown(f"""
            <div style='background-color:#F8FAFC; padding:12px; border-radius:8px; border:1px solid #E2E8F0; border-left:5px solid {colore_term};'>
                <p style='color:#64748B; font-size:11px; font-weight:700; text-transform:uppercase; margin:0;'>🌡️ Termometro Generale Acquisti Componenti</p>
                <h3 style='color:{colore_term}; margin:4px 0; font-size:18px;'>{incidenza_acquisti_pct:.1f}% ({stato_term})</h3>
                <p style='color:#475569; font-size:11px; margin:0;'>Impatto totale delle scadenze fornitori sul fatturato cumulativo generato.</p>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    
    # Contenitore Collassabile (Espandibile) unico per i dettagli
    with st.expander("🔍 Clicca qui per espandere il dettaglio mensile e l'analisi sovra-approvvigionamento"):
        condizioni = [
            (df_cashflow['Flusso Cassa Netto'] < 0) & (df_cashflow['Costi Variabili'] > df_cashflow['Fatturato'] * 0.50),
            (df_cashflow['Flusso Cassa Netto'] < 0),
            (df_cashflow['Flusso Cassa Netto'] >= 0)
        ]
        scelte = [
            "⚠️ CRITICO: Sovra-approvvigionamento Merci (Acquisti alti rispetto al venduto)",
            "🚨 DEFICIT CASSA: Le uscite del mese superano gli incassi",
            "🟢 CASSA ATTIVA: Il mese ha generato liquidità netta"
        ]
        df_cashflow['Stato Liquidità'] = np.select(condizioni, scelte, default="OK")
        
        df_cf_vis = df_cashflow[['Mese', 'Fatturato', 'Costi Variabili', 'Costi Fissi (Fornitori)', 'Uscite Totali Mese', 'Flusso Cassa Netto', 'Stato Liquidità']]
        
        st.dataframe(
            df_cf_vis,
            column_config={
                "Mese": st.column_config.TextColumn("Mese"),
                "Fatturato": st.column_config.NumberColumn("Incassi (Fatturato) (€)", format="€ %,.2f"),
                "Costi Variabili": st.column_config.NumberColumn("Scadenze Fornitori Merci (€)", format="€ %,.2f"),
                "Costi Fissi (Fornitori)": st.column_config.NumberColumn("Spese Fisse Struttura (€)", format="€ %,.2f"),
                "Uscite Totali Mese": st.column_config.NumberColumn("Uscite Totali (€)", format="€ %,.2f"),
                "Flusso Cassa Netto": st.column_config.NumberColumn("Cassa Netta Mese (€)", format="€ %,.2f"),
                "Stato Liquidità": st.column_config.TextColumn("Diagnosi Diagnostica Avanzata")
            },
            hide_index=True, use_container_width=True
        )
        
        drenaggio_totale = df_cashflow['Flusso Cassa Netto'].sum()
        if drenaggio_totale < 0:
            st.error(f"⚠️ **Riepilogo Flusso di Cassa Cumulativo:** Da inizio anno l'attività ha drenato **€ {abs(drenaggio_totale):,.2f}** di liquidità. Gli acquisti anticipati di componenti si trovano attualmente immobilizzati nel Magazzino come capitale dormiente.")
        else:
            st.success(f"✅ **Riepilogo Flusso di Cassa Cumulativo:** Da inizio anno l'attività ha generato **€ {drenaggio_totale:,.2f}** di cassa netta.")
else:
    st.info("📥 In attesa di dati storici per l'analisi del flusso di cassa.")

# --- 10. TABELLA REGISTRO ---
st.markdown("---")
st.subheader("📅 Registro Storico di Controllo")
st.dataframe(
    db_utente,
    column_config={
        "Mese": st.column_config.TextColumn("Mese"), 
        "Fatturato": st.column_config.NumberColumn("Fatturato", format="€ %,.2f"),
        "Margine %": st.column_config.NumberColumn("Margine %", format="%,.2f"), 
        "Saldo Banca (Cassa)": st.column_config.NumberColumn("Cassa", format="€ %,.2f"),
        "Costi Variabili": st.column_config.NumberColumn("Fornitori Componenti (Var.)", format="€ %,.2f"), 
        "Costi Fissi (Fornitori)": st.column_config.NumberColumn("Spese Fisse Struttura", format="€ %,.2f"),
        "Mutui e Leasing": st.column_config.NumberColumn("Mutui/Leasing", format="€ %,.2f"), 
        "Debiti IVA e Contributi": st.column_config.NumberColumn("IVA/INPS", format="€ %,.2f"),
        "Valore Magazzino": st.column_config.NumberColumn("Magazzino", format="€ %,.2f"), 
        "Punto di Pareggio": st.column_config.NumberColumn("Punto Pareggio", format="€ %,.2f")
    },
    hide_index=True, use_container_width=True
)
