import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# --- Parameters ---
st.set_page_config(layout="wide")
st.title("🔋 Hugo's tooltje - Terugverdientijd Homewizard Thuisbatterij")

col1, col2 = st.columns(2)

with col1:
    batterij_aanschafprijs = st.number_input("Prijs per batterij (€)", value=1495.00, min_value=0.00, format="%.2f")
    capaciteit_per_batterij_kWh = st.number_input("Capaciteit per batterij (kWh)", value=2.7, min_value=0.0)
    laadvermogen_per_batterij_W = st.number_input("Laad-/ontlaadvermogen per batterij (W)", value=800.00, min_value=0.00, format="%.2f")
    aantal_batterijen = st.slider("Aantal batterijen", 1, 4, 1)
    installatiekosten_extra = st.number_input("Extra installatiekosten bij meer dan 2 batterijen (€)", value=500.00, min_value=0.00, format="%.2f")
    looptijd_jaren = st.slider("Simulatieperiode (jaren)", 1, 25, 15)

with col2:
    terugleververgoeding = st.number_input("Terugleververgoeding per kWh (€)", value=0.09, min_value=0.00, format="%.2f")
    stroomprijs = st.number_input("Stroomprijs per kWh (incl. belasting, €)", value=0.40, min_value=0.00, format="%.2f")
    jaarlijkse_opwek = st.number_input("Jaarlijkse zonnepaneelopwekking (kWh)", value=4704.0, min_value=0.0)
    jaarlijks_verbruik = st.number_input("Jaarlijks stroomverbruik (kWh)", value=2069.0, min_value=0.0)
    efficiency_percentage = st.slider("Efficiëntie van het systeem (%)", 50, 100, 90)

# Radiobutton for salderingsregeling
saldering_regeling = st.radio("Stopt salderingsregeling?", ["Ja", "Nee"], index=0)  # Default set to "Ja"
if saldering_regeling == "Ja":
    saldering_eindjaar = st.slider("Jaar waarin salderingsregeling stopt", 2024, 2035, 2027)
else:
    saldering_eindjaar = None  # Indicates no specific end year; always salderen.

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
    if saldering_regeling == "Nee":
        saldering_geldig = True  # Always salderen if "Nee" is selected.
    else:
        saldering_geldig = huidig_jaar < saldering_eindjaar

    voordeel_per_kWh = stroomprijs - terugleververgoeding if not saldering_geldig else stroomprijs * 0.01
    jaarlijkse_besparing = zelfgebruik_met_batterij * voordeel_per_kWh

    cumulatieve_besparing += jaarlijkse_besparing
    nog_terug = max(totale_aanschafprijs - cumulatieve_besparing, 0)

    data.append({
        "Jaar": huidig_jaar,
        "Besparing (€)": f"€ {jaarlijkse_besparing:,.2f}",
        "Cumulatief (€)": f"€ {cumulatieve_besparing:,.2f}",
        "Nog te verdienen (€)": f"€ {nog_terug:,.2f}",
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
                "Besparing (€)": f"€ {float(row['Besparing (€)'][2:].replace(',', ''))/12:,.2f}",
                "Cumulatief (€)": f"€ {float(row['Cumulatief (€)'][2:].replace(',', '')) * ((m+1)/12):,.2f}",
                "Nog te verdienen (€)": f"€ {max(totale_aanschafprijs - float(row['Cumulatief (€)'][2:].replace(',', '')) * ((m+1)/12), 0):,.2f}",
                "Saldering?": row['Saldering?']
            })
    maand_df = pd.DataFrame(maand_data)
    st.dataframe(maand_df, use_container_width=True)

# --- Grafieken ---
st.subheader("📊 Terugverdientijd & Besparingsoverzicht")

# Use seaborn for nicer plots
sns.set_theme(style="whitegrid")
fig, ax = plt.subplots(figsize=(12, 6))

# Plot cumulative savings as a bar chart
cumulatief_values = [float(value[2:].replace(',', '')) for value in result_df['Cumulatief (€)']]
ax.bar(result_df['Jaar'], cumulatief_values, label='Cumulatieve besparing', color='green')

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
ax.get_yaxis().set_major_formatter(plt.FuncFormatter(lambda x, loc: f"€ {x:,.2f}"))

# Display the plot
st.pyplot(fig)

# --- Downloadoptie ---
st.download_button("📥 Download resultaten als CSV", result_df.to_csv(index=False, encoding='utf-8-sig'), file_name="batterij_terugverdientijd.csv")
