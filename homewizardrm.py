import streamlit as st

st.title("HomeWizard Thuisbatterij – Terugverdienmodel")
st.markdown("""
Dit model helpt je bepalen hoe snel je een HomeWizard thuisbatterij terugverdient.
Je kunt het aantal batterijen, gebruiksdagen, energieprijzen en meer aanpassen.
""")

st.sidebar.header("Instellingen")

num_batterijen = st.sidebar.slider("Aantal batterijen", 1, 3, 1)
capaciteit_per_batterij = 2.7  # kWh
vermogen_per_batterij = 0.8  # kW

dagen_gebruik = st.sidebar.selectbox("Aantal dagen per jaar dat de batterij effectief wordt benut", [120, 180, 240], index=1)

stroomprijs = st.sidebar.number_input("Stroomprijs (€ per kWh)", value=0.40, min_value=0.0, step=0.01)
terugleververgoeding = st.sidebar.number_input("Terugleververgoeding (€ per kWh)", value=0.10, min_value=0.0, step=0.01)
batterijprijs = st.sidebar.number_input("Aanschafprijs per batterij (€)", value=1495.0, min_value=0.0, step=50.0)

dagelijkse_opslag = capaciteit_per_batterij * num_batterijen
jaarlijkse_besparing_kWh = dagelijkse_opslag * dagen_gebruik
besparing_per_kWh = stroomprijs - terugleververgoeding
jaarlijkse_besparing_euro = jaarlijkse_besparing_kWh * besparing_per_kWh

totale_kosten = batterijprijs * num_batterijen
terugverdientijd = totale_kosten / jaarlijkse_besparing_euro if jaarlijkse_besparing_euro > 0 else float("inf")

st.subheader("Resultaten")
st.write(f"📦 Totale batterijcapaciteit: **{dagelijkse_opslag:.2f} kWh per dag**")
st.write(f"📆 Jaarlijkse benutting: **{jaarlijkse_besparing_kWh:.0f} kWh**")
st.write(f"💸 Jaarlijkse besparing: **€{jaarlijkse_besparing_euro:,.2f}**")
st.write(f"⏳ Terugverdientijd: **{terugverdientijd:.1f} jaar**")

st.subheader("Scenario-analyse (vast aantal batterijen)")
st.markdown("Besparing per jaar bij verschillende gebruiksdagen:")

scenario_output = ""
for dagen in [120, 180, 240, 300]:
    besparing = capaciteit_per_batterij * num_batterijen * dagen * besparing_per_kWh
    terugverdientijd_scenario = totale_kosten / besparing if besparing > 0 else float("inf")
    scenario_output += f"- **{dagen} dagen/jaar**: €{besparing:,.2f} besparing – {terugverdientijd_scenario:.1f} jaar terugverdientijd\n"

st.markdown(scenario_output)
