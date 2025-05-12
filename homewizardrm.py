import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# --- Parameters ---
st.set_page_config(layout="wide")
st.title("🔋 Hugo's tooltje - Terugverdientijd Homewizard Thuisbatterij")

col1, col2 = st.columns(2)

with col1:
    batterij_aanschafprijs = st.number_input("Prijs per batterij (€)", value=1495.0, min_value=0.0)
    capaciteit_per_batterij_kWh = st.number_input("Capaciteit per batterij (kWh)", value=2.7, min_value=0.0)
    laadvermogen_per_batterij_W = st.number_input("Laad-/ontlaadvermogen per batterij (W)", value=800.0, min_value=0.0)
    aantal_batterijen = st.slider("Aantal batterijen", 1, 4, 1)
    installatiekosten_extra = st.number_input("Extra installatiekosten bij meer dan 2 batterijen (€)", value=500.0, min_value=0.0)
    looptijd_jaren = st.slider("Simulatieperiode (jaren)", 1, 25, 15)
    saldering_eindjaar = st.slider("Jaar waarin salderingsregeling stopt", 2024, 2035, 2027)

with col2:
    terugleververgoeding = st.number_input("Terugleververgoeding per kWh (€)", value=0.09, min_value=0.0)
    stroomprijs = st.number_input("Stroomprijs per kWh (incl. belasting, €)", value=0.40, min_value=0.0)
    jaarlijkse_opwek = st.number_input("Jaarlijkse zonnepaneelopwekking (kWh)", value=4704.0, min_value=0.0)
    jaarlijks_verbruik = st.number_input("Jaarlijks stroomverbruik (kWh)", value=2069.0, min_value=0.0)
    efficiency_percentage = st.slider("Efficiëntie van het systeem (%)", 50, 100, 90)

weergave_periode = st.radio("Toon resultaten per", ["Jaar", "Maand"])

# --- Berekeningen ---
# Total battery capacity and price
totale_capaciteit_kWh = aantal_batterijen * capaciteit_per_batterij_kWh
totale_aanschafprijs = aantal_batterijen * batterij_aanschafprijs
if aantal_batterijen > 2:
    totale_aanschafprijs += installatiekosten_extra

# Apply efficiency to usable battery capacity
efficiency_factor = efficiency_percentage / 100
bruikbare_capaciteit_kWh_per_dag = totale_capaciteit_kWh * efficiency_factor

# Calculate energy surplus
verbruik_zonder_batterij = jaarlijks_verbruik
overschot_opwek = max(jaarlijkse_opwek - verbruik_zonder_batterij, 0)
zelfgebruik_met_batterij = min(overschot_opwek, bruikbare_capaciteit_kWh_per_dag * 365)

# Prepare DataFrame for results
data = []
terugverdiend = False
cumulatieve_besparing = 0

for jaar in range(looptijd_jaren):
    huidig_jaar = 2024 + jaar
    saldering_geldig = huidig_jaar < saldering_eindjaar

    voordeel_per_kWh = stroomprijs - terugleververgoeding if not saldering_geldig else stroomprijs * 0.01
    jaarlijkse_besparing = zelfgebruik_met_batterij * voordeel_per_kWh

    cumulatieve_besparing += jaarlijkse_besparing
    nog_terug = max(totale_aanschafprijs - cumulatieve_besparing, 0)

    data.append({
        "Jaar": huidig_jaar,
        "Besparing (€)": jaarlijkse_besparing,
        "Cumulatief (€)": cumulatieve_besparing,
        "Nog te verdienen (€)": nog_terug,
        "Saldering?": "Ja" if saldering_geldig else "Nee"
    })

    if not terugverdiend and cumulatieve_besparing >= totale_aanschafprijs:
        terugverdiend = True
        terugverdienjaar = huidig_jaar

result_df = pd.DataFrame(data)

# --- Resultaten samenvatting ---
if terugverdiend:
    st.success(f"✅ De batterij(en) zijn terugverdiend in het jaar {terugverdienjaar}.")
else:
    st.warning("⚠️ De batterij(en) zijn nog niet terugverdiend binnen de gekozen looptijd.")

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
                "Nog te verdienen (€)": max(totale_aanschafprijs - row['Cumulatief (€)'] * ((m+1)/12), 0),
                "Saldering?": row['Saldering?']
            })
    maand_df = pd.DataFrame(maand_data)
    st.dataframe(maand_df, use_container_width=True)

# --- Grafieken ---
st.subheader("📈 Terugverdientijd & Besparingsoverzicht")

# Use seaborn for nicer plots
sns.set_theme(style="whitegrid")
fig, ax = plt.subplots(figsize=(12, 6))

# Plot cumulative savings
ax.plot(result_df['Jaar'], result_df['Cumulatief (€)'], label='Cumulatieve besparing', color='green', linewidth=2.5)

# Add horizontal line for total battery price
ax.axhline(totale_aanschafprijs, color='red', linestyle='--', label='Totale aanschafprijs', linewidth=1.5)

# Add labels and title
ax.set_title("Cumulatieve Besparing en Terugverdientijd", fontsize=16, fontweight='bold')
ax.set_ylabel("Besparing (€)", fontsize=12)
ax.set_xlabel("Jaar", fontsize=12)

# Add grid and legend
ax.grid(True, which="both", linestyle="--", linewidth=0.5, alpha=0.7)
ax.legend(fontsize=12)

# Format y-axis with thousands separator
ax.get_yaxis().set_major_formatter(plt.FuncFormatter(lambda x, loc: f"{int(x):,} €"))

# Display the plot
st.pyplot(fig)

# --- Downloadoptie ---
st.download_button("📥 Download resultaten als CSV", result_df.to_csv(index=False, encoding='utf-8-sig'), file_name="batterij_terugverdientijd.csv")
