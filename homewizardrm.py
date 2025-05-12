import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# --- Parameters ---
st.set_page_config(layout="wide")
st.title("🔋 Hugo's toolje - Terugverdientijd Homewizard Thuisbatterij")

col1, col2 = st.columns(2)

with col1:
    aanschafprijs = st.number_input("Batterijprijs (€)", value=1495)
    capaciteit_kWh = st.number_input("Capaciteit batterij (kWh)", value=2.7)
    laadvermogen_W = st.number_input("Laad-/ontlaadvermogen (W)", value=800)
    looptijd_jaren = st.slider("Simulatieperiode (jaren)", 1, 25, 15)
    saldering_eindjaar = st.slider("Jaar waarin salderingsregeling stopt", 2024, 2035, 2027)

with col2:
    terugleververgoeding = st.number_input("Terugleververgoeding per kWh (€)", value=0.09)
    stroomprijs = st.number_input("Stroomprijs per kWh (incl. belasting, €)", value=0.40)
    jaarlijkse_opwek = st.number_input("Jaarlijkse zonnepaneelopwekking (kWh)", value=4704)
    jaarlijks_verbruik = st.number_input("Jaarlijks stroomverbruik (kWh)", value=2069)
    belasting_meerekenen = st.checkbox("Energiebelasting meerekenen", value=True)

weergave_periode = st.radio("Toon resultaten per", ["Jaar", "Maand"])

# --- Berekeningen ---
verbruik_zonder_batterij = jaarlijks_verbruik
overschot_opwek = jaarlijkse_opwek - verbruik_zonder_batterij
zelfgebruik_met_batterij = min(overschot_opwek, capaciteit_kWh * 365)


# DataFrame om resultaat op te slaan
data = []
terugverdiend = False
cumulatieve_besparing = 0

for jaar in range(looptijd_jaren):
    huidig_jaar = 2024 + jaar
    saldering_geldig = huidig_jaar < saldering_eindjaar

    voordeel_per_kWh = 0 if saldering_geldig else stroomprijs - terugleververgoeding
    jaarlijkse_besparing = zelfgebruik_met_batterij * voordeel_per_kWh if not saldering_geldig else zelfgebruik_met_batterij * 0.01

    cumulatieve_besparing += jaarlijkse_besparing
    nog_terug = max(aanschafprijs - cumulatieve_besparing, 0)

    data.append({
        "Jaar": huidig_jaar,
        "Besparing (€)": jaarlijkse_besparing,
        "Cumulatief (€)": cumulatieve_besparing,
        "Nog te verdienen (€)": nog_terug,
        "Saldering?": "Ja" if saldering_geldig else "Nee"
    })

    if not terugverdiend and cumulatieve_besparing >= aanschafprijs:
        terugverdiend = True
        terugverdienjaar = huidig_jaar

result_df = pd.DataFrame(data)

# --- Grafieken ---
st.subheader("📈 Terugverdientijd & Besparingsoverzicht")
fig, ax = plt.subplots(figsize=(10,5))
ax.plot(result_df['Jaar'], result_df['Cumulatief (€)'], label='Cumulatieve besparing')
ax.axhline(aanschafprijs, color='r', linestyle='--', label='Aanschafprijs')
ax.set_ylabel("Euro")
ax.set_xlabel("Jaar")
ax.legend()
st.pyplot(fig)

# --- Resultaten samenvatting ---
if terugverdiend:
    st.success(f"✅ De batterij is terugverdiend in het jaar {terugverdienjaar}.")
else:
    st.warning("⚠️ De batterij is nog niet terugverdiend binnen de gekozen looptijd.")

# --- Detailweergave ---
st.subheader("📋 Gedetailleerde resultaten")
if weergave_periode == "Jaar":
    st.dataframe(result_df, use_container_width=True)
else:
    maand_data = []
    for _, row in result_df.iterrows():
        for m in range(12):
            maand_data.append({
                "Jaar": row['Jaar'],
                "Maand": m+1,
                "Besparing (€)": row['Besparing (€)']/12,
                "Cumulatief (€)": row['Cumulatief (€)'] * ((m+1)/12),
                "Nog te verdienen (€)": max(aanschafprijs - row['Cumulatief (€)'] * ((m+1)/12), 0),
                "Saldering?": row['Saldering?']
            })
    maand_df = pd.DataFrame(maand_data)
    st.dataframe(maand_df, use_container_width=True)

# --- Downloadoptie ---
st.download_button("📥 Download resultaten als CSV", result_df.to_csv(index=False), file_name="batterij_terugverdientijd.csv")
