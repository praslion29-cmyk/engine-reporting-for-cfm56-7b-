# engine-reporting-for-cfm56-7b-
# ✈️ CFM56 Engine Health Monitoring System

A Streamlit-based predictive engine health monitoring dashboard for CFM56 turbofan engines.  
This project simulates Skywise-style condition monitoring for aircraft engine parameters including EGT, vibration, oil system, and fuel flow.

---

## 🚀 Features

- Real-time engine cycle input (multi-cycle analysis)
- EGT Takeoff monitoring with aviation-grade limits:
  - NORMAL ≤ 900°C
  - CAUTION 930–949°C
  - EXCEEDANCE ≥ 950°C
- Health scoring system (0–100)
- Automatic anomaly detection:
  - EGT exceedance
  - Vibration increase trend
  - Oil pressure/temperature abnormality
- Trend visualization using Plotly
- PDF report generation for maintenance documentation
- Maintenance warning alerts

---

## ⚙️ Tech Stack

- Python 3.x
- Streamlit
- Pandas
- Plotly
- FPDF

---

## 📊 Engine Parameters Monitored

### Takeoff Phase
- EGT (Exhaust Gas Temperature)
- N1 / N2 RPM
- Fuel Flow
- Vibration
- Oil Pressure
- Oil Temperature

### Ground Idle Phase
- EGT Idle
- N1 / N2 Idle
- Fuel Flow Idle
- Vibration Idle
- Oil system parameters

---

## ⚠️ EGT Takeoff Logic

| Range (°C) | Status | Action |
|------------|--------|--------|
| ≤ 900°C | NORMAL | Monitor trend |
| 930–949°C | CAUTION | Close monitoring required |
| ≥ 950°C | EXCEEDANCE | Immediate maintenance required |

---

## 📦 Installation

```bash
pip install streamlit pandas plotly fpdf
