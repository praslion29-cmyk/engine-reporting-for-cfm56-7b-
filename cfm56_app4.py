import streamlit as st
import pandas as pd
import plotly.express as px
from fpdf import FPDF
from datetime import date
import os

st.set_page_config(page_title="CFM56 Engine Monitoring", layout="wide")

# =========================
# HEADER
# =========================
col1, col2 = st.columns([1,5])
with col1:
    if os.path.exists("cfm56.png"):
        st.image("cfm56.png", width=120)
    else:
        st.warning("Logo not found")
with col2:
    st.title("CFM56 ENGINE HEALTH MONITORING SYSTEM")
    st.caption("Condition Monitoring | Start - Idle - Takeoff Analysis")

st.markdown("---")

# =========================
# INPUT BASIC
# =========================
col1, col2, col3, col4 = st.columns(4)
with col1:
    engine_id = st.text_input("Engine Type", "CFM56-7B")
with col2:
    engine_no = st.selectbox("Engine Position", ["ENG 1 (LH)", "ENG 2 (RH)"])
with col3:
    aircraft_reg = st.text_input("Aircraft Reg", "PK-XXX")
with col4:
    route = st.text_input("Route", "CGK-DPS")

num_cycles = st.number_input("Number of Cycles", min_value=1, max_value=10, value=3)

st.markdown("---")

data = []

# =========================
# INPUT LOOP
# =========================
for i in range(num_cycles):
    st.subheader(f"Cycle {i+1}")

    # START
    egt_start = st.number_input("EGT Start (°C)", key=f"start_{i}")

    # IDLE
    st.markdown("### Ground Idle")
    col1, col2, col3 = st.columns(3)
    with col1:
        egt_idle = st.number_input("EGT Idle (°C)", key=f"idle_egt_{i}")
        n1_idle = st.number_input("N1 Idle (%)", key=f"idle_n1_{i}")
    with col2:
        n2_idle = st.number_input("N2 Idle (%)", key=f"idle_n2_{i}")
        ff_idle = st.number_input("Fuel Flow Idle", key=f"idle_ff_{i}")
    with col3:
        vib_idle = st.number_input("Vibration Idle", key=f"idle_vib_{i}")
        oilp_idle = st.number_input("Oil Press Idle", key=f"idle_oilp_{i}")
        oilt_idle = st.number_input("Oil Temp Idle", key=f"idle_oilt_{i}")

    # TAKEOFF
    st.markdown("### Takeoff Power")
    col1, col2, col3 = st.columns(3)
    with col1:
        egt_to = st.number_input("EGT TO (°C)", min_value=0.0, max_value=1000.0, value=850.0, key=f"to_egt_{i}")
        n1_to = st.number_input("N1 TO (%)", key=f"to_n1_{i}")
    with col2:
        n2_to = st.number_input("N2 TO (%)", key=f"to_n2_{i}")
        ff_to = st.number_input("Fuel Flow TO", key=f"to_ff_{i}")
    with col3:
        vib_to = st.number_input("Vibration TO", key=f"to_vib_{i}")
        oilp_to = st.number_input("Oil Press TO", key=f"to_oilp_{i}")
        oilt_to = st.number_input("Oil Temp TO", key=f"to_oilt_{i}")

    data.append({
        "Cycle": i+1,
        "EGT_START": egt_start,
        "EGT_IDLE": egt_idle,
        "N1_IDLE": n1_idle,
        "N2_IDLE": n2_idle,
        "FF_IDLE": ff_idle,
        "VIB_IDLE": vib_idle,
        "OILP_IDLE": oilp_idle,
        "OILT_IDLE": oilt_idle,
        "EGT_TO": egt_to,
        "N1_TO": n1_to,
        "N2_TO": n2_to,
        "FF_TO": ff_to,
        "VIB_TO": vib_to,
        "OILP_TO": oilp_to,
        "OILT_TO": oilt_to
    })

df = pd.DataFrame(data)

# =========================
# ANALYSIS ENGINE
# =========================
def analyze(row):
    score = 100
    notes = []
    advice = []

    # -------------------------
    # START
    # -------------------------
    if row["EGT_START"] > 725:
        score -= 20
        start_status = "WARNING"
        notes.append("High EGT Start")
        advice.append("Check ignition/fuel scheduling during start")
    elif row["EGT_START"] > 700:
        start_status = "CAUTION"
    else:
        start_status = "NORMAL"

    # -------------------------
    # IDLE
    # -------------------------
    idle_status = "NORMAL"

    if row["EGT_IDLE"] > 450:
        idle_status = "WARNING"
        score -= 15
        notes.append("EGT Idle high")
        advice.append("Check compressor efficiency / bleed leakage")
    elif row["EGT_IDLE"] > 420:
        idle_status = "CAUTION"

    if row["N1_IDLE"] > 22:
        idle_status = "WARNING"
        score -= 10
        notes.append("N1 Idle high")

    if row["N2_IDLE"] > 59:
        idle_status = "WARNING"
        score -= 10
        notes.append("N2 Idle high")

    if row["FF_IDLE"] > 600:
        idle_status = "WARNING"
        score -= 10
        notes.append("Fuel flow idle high")

    if row["VIB_IDLE"] > 3:
        idle_status = "WARNING"
        score -= 15
        notes.append("Vibration idle high")

    if not (13 <= row["OILP_IDLE"] <= 40):
        idle_status = "WARNING"
        score -= 10
        notes.append("Oil pressure abnormal")

    if row["OILT_IDLE"] > 140:
        idle_status = "WARNING"
        score -= 10
        notes.append("Oil temperature high")

    # -------------------------
    # TAKEOFF (EGT CRITICAL)
    # -------------------------
    if row["EGT_TO"] >= 950:
        to_status = "EXCEEDANCE"
        score -= 30
        notes.append("EGT EXCEEDANCE")
        advice.append("BORESCOPE INSPECTION REQUIRED + ENGINE LOG EVENT")

    elif row["EGT_TO"] >= 930:
        to_status = "WARNING"
        score -= 15
        notes.append("EGT near limit")
        advice.append("Monitor trend closely - possible degradation")

    elif row["EGT_TO"] >= 900:
        to_status = "CAUTION"
    else:
        to_status = "NORMAL"

    # -------------------------
    # OTHER TAKEOFF PARAMETERS
    # -------------------------
    if row["N2_TO"] > 105:
        score -= 10
    if row["FF_TO"] > 5160:
        score -= 10
    if row["VIB_TO"] > 3:
        score -= 15
    if row["OILP_TO"] > 60:
        score -= 10
    if row["OILT_TO"] > 140:
        score -= 10

    # -------------------------
    # FINAL STATUS
    # -------------------------
    if score >= 80:
        status = "NORMAL"
    elif score >= 60:
        status = "DEGRADED"
    else:
        status = "CRITICAL"

    return score, status, start_status, idle_status, to_status, ", ".join(notes), " | ".join(advice)

# =========================
# APPLY ANALYSIS
# =========================
results = df.apply(lambda row: analyze(row), axis=1)

df["Score"] = [r[0] for r in results]
df["Status"] = [r[1] for r in results]
df["Start_Status"] = [r[2] for r in results]
df["Idle_Status"] = [r[3] for r in results]
df["TO_Status"] = [r[4] for r in results]
df["Notes"] = [r[5] for r in results]
df["Advice"] = [r[6] for r in results]

# =========================
# DASHBOARD
# =========================
st.subheader("Engine Health Summary")

st.metric("Average Score", f"{int(df['Score'].mean())}%")

st.dataframe(df)

# WARNING PANEL
if df["EGT_TO"].max() >= 950:
    st.error("⚠ EXCEEDANCE DETECTED - IMMEDIATE MAINTENANCE REQUIRED")
elif df["EGT_TO"].max() >= 930:
    st.warning("⚠ CAUTION ZONE - CLOSE MONITORING REQUIRED")

# =========================
# TREND
# =========================
st.subheader("Trend Analysis")

fig = px.line(df, x="Cycle", y="EGT_TO", markers=True, title="EGT Takeoff Trend (°C)")
fig.add_hline(y=950, line_dash="dash", line_color="red")
st.plotly_chart(fig)

fig2 = px.line(df, x="Cycle", y="VIB_TO", markers=True, title="Vibration Trend")
st.plotly_chart(fig2)

# =========================
# PDF EXPORT
# =========================
if st.button("Generate PDF Report"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial","B",14)
    pdf.cell(0,10,"CFM56 ENGINE HEALTH REPORT",0,1)

    pdf.set_font("Arial","",10)
    pdf.cell(0,8,f"Engine: {engine_id}",0,1)
    pdf.cell(0,8,f"Aircraft: {aircraft_reg}",0,1)
    pdf.cell(0,8,f"Route: {route}",0,1)
    pdf.cell(0,8,f"Score: {int(df['Score'].mean())}%",0,1)

    pdf.ln(5)

    for _, row in df.iterrows():
        pdf.cell(0,6,f"Cycle {row['Cycle']} | EGT TO {row['EGT_TO']}°C | {row['TO_Status']}",0,1)
        pdf.cell(0,6,f"Status: {row['Status']}",0,1)
        pdf.ln(2)

    file_name = f"CFM56_Report_{date.today()}.pdf"
    pdf.output(file_name)

    with open(file_name,"rb") as f:
        st.download_button("Download Report", f, file_name)

st.markdown("---")
st.caption("CFM56 Engine Monitoring System | Built by YA Prasetya")