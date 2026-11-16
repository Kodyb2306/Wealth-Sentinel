import datetime
import smtplib
from email.message import EmailMessage
import urllib.request
import xml.etree.ElementTree as ET
import numpy as np
import pandas as pd
import streamlit as st
import yfinance as yf
 
st.set_page_config(
    page_title="One-Stop Joint Wealth & Retirement Sentinel",
    page_icon="🛡️",
    layout="centered",
)
 
# =====================================================================
# 1. EXPANDED JOINT MILITARY (DFAS 2026/2027) & GS PAY DATABASE
# =====================================================================
PAY_TABLE = {
    # --- Officer Ranks (O-1 to O-10) ---
    "O-1 (2d Lt / Ensign)": {0: 4100, 2: 4265, 4: 5150, 6: 5150, 10: 5150},
    "O-2 (1st Lt / LTJG)": {0: 4720, 2: 5375, 4: 6515, 6: 6650, 10: 6650},
    "O-3 (Capt / LT)": {0: 5460, 2: 6190, 4: 7340, 6: 7695, 8: 8075, 10: 8325, 12: 8735, 14: 8735},
    "O-1E (Prior Enlisted 2d Lt)": {4: 5555, 6: 5935, 8: 6155, 10: 6375, 12: 6595, 14: 6895, 16: 6895},
    "O-2E (Prior Enlisted Lt)": {4: 6710, 6: 7060, 8: 7285, 10: 7390, 12: 7390, 14: 7390, 16: 7390},
    "O-3E (Prior Enlisted Capt)": {6: 7840, 8: 8230, 10: 8485, 12: 8905, 14: 9255, 16: 9255, 18: 9850},
    "O-4 (Maj / LCDR)": {0: 6215, 2: 7120, 4: 7575, 6: 8010, 8: 8480, 10: 9060, 12: 9505, 14: 9820, 16: 10005},
    "O-5 (Lt Col / CDR)": {0: 7050, 2: 8180, 4: 8650, 6: 8990, 8: 9355, 10: 9815, 12: 10150, 14: 10590, 16: 11255, 18: 11570, 20: 11890, 22: 12240},
    "O-6 (Col / Capt Navy)": {0: 8450, 2: 9285, 4: 9890, 6: 9930, 8: 10525, 10: 10580, 12: 10580, 14: 11195, 16: 12255, 18: 12880, 20: 13515, 22: 13870, 24: 14240, 26: 14925},
    "O-7 (Brig Gen / Rear Adm LH)": {0: 10980, 2: 11465, 4: 11720, 6: 12055, 8: 12435, 10: 12900, 12: 13365, 14: 13835, 16: 14925, 18: 15990, 20: 15990},
    "O-8 (Maj Gen / Rear Adm UH)": {0: 13180, 2: 13650, 4: 13800, 6: 14155, 8: 14750, 10: 14885, 12: 15535, 14: 15690, 16: 16290, 18: 17130, 20: 17790},
    "O-9 (Lt Gen / Vice Adm)": {0: 18000, 2: 18200, 4: 18200, 6: 18200, 8: 18200, 10: 18200, 12: 18200, 14: 18200, 20: 18200},
    "O-10 (General / Admiral)": {0: 18400, 2: 18400, 4: 18400, 6: 18400, 8: 18400, 20: 18400},
 
    # --- Warrant Officers (W-1 to W-5) ---
    "W-1 (Warrant Officer 1)": {0: 4115, 2: 4560, 4: 4805, 6: 5085, 8: 5350, 10: 5545, 12: 5820, 14: 6095},
    "W-2 (Chief Warrant Officer 2)": {0: 4685, 2: 5130, 4: 5250, 6: 5515, 8: 5975, 10: 6205, 12: 6430, 14: 6710, 16: 6935, 18: 7135},
    "W-3 (Chief Warrant Officer 3)": {0: 5295, 2: 5515, 4: 5755, 6: 5995, 8: 6470, 10: 6955, 12: 7175, 14: 7430, 16: 7695, 18: 8115},
    "W-4 (Chief Warrant Officer 4)": {0: 5785, 2: 6130, 4: 6455, 6: 6770, 8: 7235, 10: 7575, 12: 8040, 14: 8465, 16: 8885, 18: 9195, 20: 9635},
    "W-5 (Chief Warrant Officer 5)": {20: 10450, 22: 10985, 24: 11385, 26: 11930},
 
    # --- Enlisted Ranks (E-1 to E-9) ---
    "E-1 (Basic Enlisted)": {0: 2100, 2: 2100, 4: 2100},
    "E-2 (PFC / A1C / Pvt)": {0: 2355, 2: 2355, 4: 2355},
    "E-3 (Lcpl / SrA / PFC)": {0: 2475, 2: 2630, 4: 2790, 6: 2790},
    "E-4 (Cpl / Sgt / SrA)": {0: 2740, 2: 2880, 4: 3105, 6: 3235, 8: 3235},
    "E-5 (Sgt / SSgt / Petty Officer 2)": {0: 2990, 2: 3195, 4: 3350, 6: 3590, 8: 3835, 10: 4040, 12: 4065},
    "E-6 (SSgt / TSgt / Petty Officer 1)": {0: 3260, 2: 3585, 4: 3745, 6: 3910, 8: 4260, 10: 4395, 12: 4655, 14: 4740, 16: 4795},
    "E-7 (SFC / MSgt / Chief Petty Officer)": {2: 3950, 4: 4150, 6: 4305, 8: 4565, 10: 4710, 12: 4975, 14: 5195, 16: 5340, 18: 5495, 20: 5560},
    "E-8 (MSG / SMSgt / Senior Chief)": {8: 5260, 10: 5495, 12: 5640, 14: 5810, 16: 6000, 18: 6335, 20: 6510, 22: 6800, 24: 6965, 26: 7375},
    "E-9 (SGM / CMSgt / Master Chief)": {10: 6410, 12: 6555, 14: 6735, 16: 6950, 18: 7170, 20: 7525, 22: 7820, 24: 8130, 26: 8610, 30: 9050},
 
    # --- Federal Civilian GS-Scale (Base pay estimates per month) ---
    "GS-1 (Federal Civ)": {0: 2150, 2: 2290, 4: 2430},
    "GS-2 (Federal Civ)": {0: 2415, 2: 2570, 4: 2725},
    "GS-3 (Federal Civ)": {0: 2635, 2: 2805, 4: 2975},
    "GS-4 (Federal Civ)": {0: 2960, 2: 3150, 4: 3340},
    "GS-5 (Federal Civ)": {0: 3310, 2: 3520, 4: 3730},
    "GS-6 (Federal Civ)": {0: 3690, 2: 3925, 4: 4160},
    "GS-7 (Federal Civ)": {0: 4100, 2: 4360, 4: 4620},
    "GS-8 (Federal Civ)": {0: 4540, 2: 4830, 4: 5120},
    "GS-9 (Federal Civ)": {0: 5015, 2: 5335, 4: 5655},
    "GS-10 (Federal Civ)": {0: 5520, 2: 5875, 4: 6230},
    "GS-11 (Federal Civ)": {0: 6100, 2: 6500, 4: 6900, 8: 7300, 12: 7900},
    "GS-12 (Federal Civ)": {0: 7300, 2: 7780, 4: 8260, 8: 8760, 12: 9490},
    "GS-13 (Federal Civ)": {0: 8680, 2: 9250, 4: 9820, 8: 10415, 12: 11285},
    "GS-14 (Federal Civ)": {0: 10260, 2: 10935, 4: 11610, 8: 12310, 12: 13335},
    "GS-15 (Federal Civ)": {0: 12070, 2: 12865, 4: 13660, 8: 14450, 12: 15600},
 
    # --- Private Civilian Custom ---
    "Civilian (Custom Salary)": {},
}
 
FUND_METRICS = {
    "VOO": {"cagr": 0.102, "div_yield": 0.014},  # C Fund / S&P 500
    "VXF": {"cagr": 0.106, "div_yield": 0.012},  # S Fund / Small-Mid Cap
    "QQQ": {"cagr": 0.125, "div_yield": 0.006},  # Nasdaq-100 Growth
    "AGG": {"cagr": 0.045, "div_yield": 0.042},  # F Fund / Aggregate Bonds
    "SHV": {"cagr": 0.040, "div_yield": 0.040},  # G Fund / Short Treasuries
}
 
RADAR_ASSETS = {
    "VTI": "Vanguard Total Stock Market ETF (80/20 C+S Equivalent)",
    "VOO": "Vanguard S&P 500 ETF (TSP C-Fund Equivalent)",
    "VXF": "Vanguard Extended Market ETF (TSP S-Fund Equivalent)",
    "QQQ": "Invesco Nasdaq-100 ETF (Large-Cap Tech & AI Growth)",
    "SMH": "VanEck Semiconductor ETF (AI & Chip Infrastructure)",
    "ITA": "iShares U.S. Aerospace & Defense ETF (Defense & Cyber)",
    "SCHD": "Schwab U.S. Dividend Equity ETF (High Dividend Growth)",
    "XLE": "Energy Select Sector SPDR ETF (Inflation & Oil Hedge)",
    "GLD": "SPDR Gold Trust (Geopolitical Safe Haven)",
    "NVDA": "NVIDIA Corp. (AI Compute Leader)",
    "MSFT": "Microsoft Corp. (Enterprise Cloud & Cyber Leader)",
}
 
def get_base_pay(rank_choice, yos, custom_annual):
  if rank_choice == "Civilian (Custom Salary)":
    return custom_annual / 12.0
  brackets = PAY_TABLE[rank_choice]
  valid_keys = [k for k in brackets.keys() if k <= yos]
  best_key = max(valid_keys) if valid_keys else min(brackets.keys())
  return float(brackets[best_key])
 
# =====================================================================
# 2. MAIN SCREEN UI: INTERACTIVE INPUT PANEL
# =====================================================================
st.title("🛡️ Joint Tactical Wealth, News AI & 2008 Crash Sentinel")
st.markdown(
    "All ranks and civilian scales are fully loaded. Adjust your metrics below"
    " to generate your custom **Retirement Freedom Age & Weekly/Monthly Stock"
    " Action Reports**."
)
 
with st.container(border=True):
  st.subheader("⚙️ 1. Your Custom Profile & Investment Setup")
  c1, c2, c3 = st.columns(3)
 
  with c1:
    selected_rank = st.selectbox("Select Rank or Status", list(PAY_TABLE.keys()), index=4)  # Defaults to O-2E
    yos = st.slider("Current Years of Service / Experience", 0, 40, 13)
    if selected_rank == "Civilian (Custom Salary)":
      custom_sal = st.number_input("Annual Gross Salary ($)", value=110000, step=5000)
    else:
      custom_sal = 0
    base_pay = get_base_pay(selected_rank, yos, custom_sal)
    st.caption(f"💵 **Active Base Pay:** `${base_pay:,.2f}/mo`")
 
  with c2:
    current_age = st.number_input("Current Age", min_value=18, max_value=75, value=35)
    stop_contrib_age = st.number_input("Age You Stop Contributing / Exit Active Duty", min_value=current_age, max_value=75, value=42)
    target_retire_age = st.number_input("Target Full Dividend Retirement Age", min_value=stop_contrib_age, max_value=85, value=60)
    desired_monthly_income = st.number_input("Target Retirement Income Goal ($/mo)", value=10000, step=500)
 
  with c3:
    current_balance = st.number_input("Current Investment Balance ($)", value=47552.32, step=1000.0, format="%.2f")
    contrib_pct = st.slider("Your Monthly Contribution (%)", 1, 50, 8) / 100.0
    match_pct = st.selectbox(
        "Employer / DoD Match",
        ["0% (Legacy High-3 / No Match)", "5% (BRS / 401k Match)", "3% (Safe Harbor)"],
        index=0,
    )
    match_rate = 0.05 if "5%" in match_pct else (0.03 if "3%" in match_pct else 0.0)
    report_freq = st.selectbox("📅 Action Report Frequency", ["Monthly (30 Days)", "Quarterly (90 Days)", "Yearly (365 Days)"], index=0)
 
  monthly_deposit = base_pay * (contrib_pct + match_rate)
 
  st.divider()
  st.markdown("##### 🎖️ Active Duty / Veteran Benefits & Social Security (Select if Applicable)")
  p1, p2, p3 = st.columns(3)
  with p1:
    include_mil_pension = st.checkbox("Include Pension (20+ Years Active)", value=True)
    est_pension = st.number_input("Est. Monthly Pension ($)", value=4805, step=100) if include_mil_pension else 0
  with p2:
    include_va = st.checkbox("Include VA Disability (100% Tax-Free)", value=True)
    est_va = st.number_input("Est. Monthly VA Pay ($)", value=4537, step=100) if include_va else 0
  with p3:
    include_ss = st.checkbox("Include Social Security", value=True)
    est_ss = st.number_input("Est. Monthly SS Pay ($)", value=2800, step=100) if include_ss else 0
 
  st.divider()
  preset = st.selectbox(
      "📊 Select Your Investment Mix (Determines Compound Growth & Yield)",
      [
          "80% C Fund / 20% S Fund (Total US Stock Market - VTI Equivalent)",
          "100% C Fund / S&P 500 (Large Cap Only)",
          "Lifecycle / Balanced (60% C, 15% S, 25% G/F Bonds)",
          "Aggressive Tech + Growth (50% C, 20% S, 30% QQQ)",
          "Defensive / Capital Preservation (20% C, 80% G Fund)",
          "Custom Mix",
      ],
      index=0,
  )
 
  if "80% C Fund" in preset:
    w_def = {"VOO": 80, "VXF": 20, "QQQ": 0, "AGG": 0, "SHV": 0}
  elif "100% C Fund" in preset:
    w_def = {"VOO": 100, "VXF": 0, "QQQ": 0, "AGG": 0, "SHV": 0}
  elif "Lifecycle" in preset:
    w_def = {"VOO": 60, "VXF": 15, "QQQ": 0, "AGG": 10, "SHV": 15}
  elif "Aggressive Tech" in preset:
    w_def = {"VOO": 50, "VXF": 20, "QQQ": 30, "AGG": 0, "SHV": 0}
  elif "Defensive" in preset:
    w_def = {"VOO": 20, "VXF": 0, "QQQ": 0, "AGG": 0, "SHV": 80}
  else:
    w_def = {"VOO": 50, "VXF": 25, "QQQ": 15, "AGG": 5, "SHV": 5}
 
  with st.expander("🔧 Customize Exact Fund Percentages", expanded=(preset == "Custom Mix")):
    fc1, fc2, fc3, fc4, fc5 = st.columns(5)
    w_c = fc1.number_input("C Fund / VOO %", 0, 100, w_def["VOO"])
    w_s = fc2.number_input("S Fund / VXF %", 0, 100, w_def["VXF"])
    w_q = fc3.number_input("Tech / QQQ %", 0, 100, w_def["QQQ"])
    w_f = fc4.number_input("F Fund / Bonds %", 0, 100, w_def["AGG"])
    w_g = fc5.number_input("G Fund / Cash %", 0, 100, w_def["SHV"])
 
  tot_w = max(w_c + w_s + w_q + w_f + w_g, 1)
  weights = {"VOO": w_c / tot_w, "VXF": w_s / tot_w, "QQQ": w_q / tot_w, "AGG": w_f / tot_w, "SHV": w_g / tot_w}
 
# =====================================================================
# 3. COMPOUND INTEREST & RETIREMENT ENGINE
# =====================================================================
blended_cagr = sum(weights[k] * FUND_METRICS[k]["cagr"] for k in weights)
natural_div_yield = sum(weights[k] * FUND_METRICS[k]["div_yield"] for k in weights)
 
age_schedule = []
running_bal = current_balance
predicted_freedom_age = None
 
for age in range(current_age, 71):
  active_monthly_add = monthly_deposit if age < stop_contrib_age else 0.0
  div_natural_mo = (running_bal * natural_div_yield) / 12.0
  div_balanced_45_mo = (running_bal * 0.045) / 12.0  # 4.5% Yield Switch
  div_high_65_mo = (running_bal * 0.065) / 12.0      # 6.5% Yield Switch
 
  mil_inc = (est_pension + est_va) if (age >= stop_contrib_age and "Civ" not in selected_rank and "Civilian" not in selected_rank) else 0.0
  ss_inc = est_ss if age >= 66 else (est_ss * 0.75 if age >= 62 else 0.0)
  total_monthly_at_age = div_balanced_45_mo + mil_inc + ss_inc
 
  if predicted_freedom_age is None and total_monthly_at_age >= desired_monthly_income and age >= stop_contrib_age:
    predicted_freedom_age = age
 
  age_schedule.append({
      "Age": age,
      "Compounded Balance": running_bal,
      "Monthly Deposit": active_monthly_add,
      "Natural Dividend ($/mo)": div_natural_mo,
      "4.5% Dividend Paycheck ($/mo)": div_balanced_45_mo,
      "6.5% High-Yield Paycheck ($/mo)": div_high_65_mo,
      "Pension + VA + SS ($/mo)": mil_inc + ss_inc,
      "Total Monthly Income ($/mo)": total_monthly_at_age,
  })
 
  for _ in range(12):
    running_bal = (running_bal * (1.0 + (blended_cagr / 12.0))) + active_monthly_add
 
sched_df = pd.DataFrame(age_schedule)
row_42 = sched_df[sched_df["Age"] == stop_contrib_age].iloc[0]
row_ret = sched_df[sched_df["Age"] == target_retire_age].iloc[0]
 
# =====================================================================
# 4. RETIREMENT FREEDOM DISPLAY
# =====================================================================
st.subheader("🏦 2. Retirement Age Predictor & Monthly Dividend Paycheck")
 
if predicted_freedom_age:
  st.success(
      f"🎯 **PREDICTED RETIREMENT FREEDOM AGE: Age {predicted_freedom_age}** —"
      " Based on your compounded investments, dividend yield, and benefits, you"
      f" will surpass your **${desired_monthly_income:,.0f}/month** income goal"
      f" at **Age {predicted_freedom_age}**!"
  )
else:
  st.warning(
      f"⚠️ To hit **${desired_monthly_income:,.0f}/month**, consider increasing"
      " your contribution % or shifting to higher-growth equity funds."
  )
 
col_a, col_b = st.columns(2)
with col_a:
  with st.container(border=True):
    st.markdown(f"#### 🎖️ Milestone 1: Transition/Exit (Age {stop_contrib_age})")
    st.metric("Compounded Portfolio Balance", f"${row_42['Compounded Balance']:,.0f}", f"{blended_cagr*100:.1f}% Est. Annual CAGR")
    st.write(f"• **If Left to Compound Untouched:** Grows to **${row_ret['Compounded Balance']:,.0f}** by Age {target_retire_age}")
    st.write(f"• **4.5% Monthly Dividend If Tapped:** `${row_42['4.5% Dividend Paycheck ($/mo)']:,.0f} / mo`")
    st.write(f"• **Pension + Tax-Free VA Paycheck:** `${row_42['Pension + VA + SS ($/mo)']:,.0f} / mo`")
    st.write(f"• **Total Monthly Cash Flow at Age {stop_contrib_age}:** **`${row_42['Total Monthly Income ($/mo)']:,.0f} / mo`**")
 
with col_b:
  with st.container(border=True):
    st.markdown(f"#### 🌴 Milestone 2: Full Dividend Retirement (Age {target_retire_age})")
    st.metric(f"Compounded Balance at Age {target_retire_age}", f"${row_ret['Compounded Balance']:,.0f}", "Zero Principal Depletion")
    st.write(f"• **Conservative Dividend/Interest (4.5% Yield):** **`${row_ret['4.5% Dividend Paycheck ($/mo)']:,.0f} / mo`**")
    st.write(f"• **High-Income Dividend/Options (6.5% Yield):** **`${row_ret['6.5% High-Yield Paycheck ($/mo)']:,.0f} / mo`**")
    st.write(f"• **Pension + VA + Social Security:** `${row_ret['Pension + VA + SS ($/mo)']:,.0f} / mo`")
    st.write(f"• **Total Combined Monthly Salary:** **`${row_ret['Total Monthly Income ($/mo)']:,.0f} / mo`**")
 
# =====================================================================
# 5. MARKET DATA, 2008 CRASH SENTINEL & WORLD/LOCAL NEWS PREDICTOR
# =====================================================================
@st.cache_data(ttl=1800)
def fetch_all_market_data():
  all_tickers = list(set(["VOO", "VXF", "QQQ", "AGG", "SHV", "HYG", "IEF", "XLF", "^VIX"] + list(RADAR_ASSETS.keys())))
  df = yf.download(all_tickers, period="2y", interval="1d", progress=False)["Close"]
  return df.dropna()
 
@st.cache_data(ttl=1800)
def scan_world_and_local_news():
  bull_words = ["surge", "beat", "growth", "rally", "record", "upgrade", "bull", "gain", "strong", "cut rates", "expansion", "boom", "ai", "profit", "outperform"]
  bear_words = ["crash", "recession", "inflation", "default", "war", "tariff", "downgrade", "drop", "plunge", "layoff", "crisis", "slowdown", "bear", "miss", "fear"]
  headlines = []
  rss_urls = [
      ("World News", https://news.google.com/rss/headlines/section/topic/WORLD?hl=en-US&gl=US&ceid=US:en),
      ("US/Local Economy", https://news.google.com/rss/headlines/section/topic/BUSINESS?hl=en-US&gl=US&ceid=US:en),
  ]
  for category, url in rss_urls:
    try:
      req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
      with urllib.request.urlopen(req, timeout=5) as resp:
        root = ET.fromstring(resp.read())
      for item in root.findall(".//item")[:6]:
        title = item.find("title").text if item.find("title") is not None else ""
        if title:
          headlines.append((category, title))
    except Exception:
      pass
 
  macro_score = 0
  scored_headlines = []
  for cat, title in headlines:
    t_low = title.lower()
    net = sum(1 for w in bull_words if w in t_low) - sum(1 for w in bear_words if w in t_low)
    macro_score += net
    scored_headlines.append({"Scope": cat, "Sentiment": "🟢 Bullish" if net > 0 else ("🔴 Bearish" if net < 0 else "⚪ Neutral"), "Headline": title})
  return macro_score, scored_headlines
 
df = fetch_all_market_data()
macro_news_score, live_headlines = scan_world_and_local_news()
 
lookback_days = 21 if "Monthly" in report_freq else (63 if "Quarterly" in report_freq else 252)
period_label = "30-Day (Monthly)" if lookback_days == 21 else ("90-Day (Quarterly)" if lookback_days == 63 else "365-Day (Yearly)")
 
port_return = sum(float((df[tkr].iloc[-1] / df[tkr].iloc[-lookback_days]) - 1.0) * w for tkr, w in weights.items())
dollar_profit_loss = current_balance - (current_balance / (1.0 + port_return))
 
voo_now = float(df["VOO"].iloc[-1])
voo_sma200 = float(df["VOO"].rolling(200).mean().iloc[-1])
voo_sma50 = float(df["VOO"].rolling(50).mean().iloc[-1])
sma_dist_pct = ((voo_now - voo_sma200) / voo_sma200) * 100
credit_ratio = df["HYG"] / df["IEF"]
credit_stress = float(credit_ratio.iloc[-1]) < float(credit_ratio.rolling(100).mean().iloc[-1]) * 0.975
vix_now = float(df["^VIX"].iloc[-1])
bank_contagion = float((df["XLF"].iloc[-1] / df["XLF"].iloc[-60]) - (df["VOO"].iloc[-1] / df["VOO"].iloc[-60])) < -0.07
 
crash_score = (35 if (voo_now < voo_sma200 * 0.98 and voo_sma50 < voo_sma200) else (20 if voo_now < voo_sma200 else 0)) + (30 if credit_stress else 0) + (20 if vix_now > 28 else (10 if vix_now > 22 else 0)) + (15 if bank_contagion else 0)
sc_zscore = float((df["VXF"].iloc[-1] / df["VOO"].iloc[-1] - (df["VXF"] / df["VOO"]).rolling(252).mean().iloc[-1]) / (df["VXF"] / df["VOO"]).rolling(252).std().iloc[-1])
 
# =====================================================================
# 6. MAIN SCREEN SECTION 3: P&L, 2008 CRASH SENTINEL & NEWS STOCK PICKS
# =====================================================================
st.subheader(f"📊 3. {period_label} Profit/Loss & 2008 Crash Sentinel")
m1, m2, m3, m4 = st.columns(4)
m1.metric(f"{period_label} Return", f"{port_return*100:+.2f}%", f"${dollar_profit_loss:+,.2f} P/L")
m2.metric("2008 Crash Score", f"{crash_score} / 100", "Danger >= 70", delta_color="inverse")
m3.metric("S/C Spread Z-Score", f"{sc_zscore:+.2f} σ", "Small vs Large Cap")
m4.metric("Active Monthly Deposit", f"${monthly_deposit:,.0f}/mo", f"CAGR: {blended_cagr*100:.1f}%")
 
def rank_and_project_stocks(price_df, macro_sentiment, crash_risk):
  results = []
  for tkr, desc in RADAR_ASSETS.items():
    if tkr not in price_df.columns:
      continue
    s = price_df[tkr].dropna()
    curr = float(s.iloc[-1])
    ret_1y = float((s.iloc[-1] / s.iloc[-252]) - 1.0)
    ret_6m = float((s.iloc[-1] / s.iloc[-126]) - 1.0)
    vol = float(s.pct_change().dropna().tail(252).std() * np.sqrt(252))
    sharpe = (ret_1y - 0.042) / max(vol, 0.01)
    above_sma = curr > float(s.rolling(200).mean().iloc[-1])
 
    catalyst = "Total US Market / Core Institutional Inflows (Matches 80/20 C+S)" if tkr in ["VTI", "VOO", "VXF"] else (
        "Global AI, Cyber & Cloud CapEx Expansion" if tkr in ["QQQ", "SMH", "NVDA", "MSFT"] else (
            "Global Defense & DoW Modernization Budgets" if tkr == "ITA" else "High-Cash-Flow Dividend & Inflation Protection"
        )
    )
    news_adj = 0.02 if (macro_sentiment >= 0 and tkr in ["VTI", "VOO", "VXF", "QQQ", "SMH", "NVDA"]) else (0.025 if (macro_sentiment < 0 and tkr in ["ITA", "GLD", "SCHD"]) else 0.01)
    proj_1y = (0.55 * 0.102) + (0.30 * np.clip((0.6 * ret_1y + 0.4 * ret_6m * 2), -0.15, 0.35)) + news_adj
    score = (sharpe * 35) + (proj_1y * 100 * 3.5) + (15 if above_sma else -10)
 
    results.append({
        "Ticker": tkr,
        "Asset Name": desc,
        "Current Price": f"${curr:,.2f}",
        "1-Yr Past Return": f"{ret_1y*100:+.1f}%",
        "Proj. 1-Yr Return": f"{proj_1y*100:+.1f}%",
        "Proj. 1-Yr Target": f"${curr*(1+proj_1y):,.2f}",
        "World/Local News Catalyst": catalyst,
        "Quant Score": round(score, 1),
        "_raw": score,
    })
  return pd.DataFrame(results).sort_values(by="_raw", ascending=False).reset_index(drop=True)
 
ranked_stocks_df = rank_and_project_stocks(df, macro_news_score, crash_score)
 
st.subheader("🌍 4. AI World/Local News Top Stock & ETF Predictions")
st.dataframe(ranked_stocks_df.drop(columns=["_raw"]), use_container_width=True, hide_index=True)
 
# =====================================================================
# 7. MAIN SCREEN SECTION 5: ONE-STOP ACTION REPORT (EMAIL / SMS)
# =====================================================================
st.subheader(f"📩 5. Your One-Stop {period_label} Action Report")
action_report = f"""============================================================
🛡️ ONE-STOP JURISDICTIONAL WEALTH & RETIREMENT SENTINEL REPORT
============================================================
Profile: {selected_rank} (Age {current_age}) | Active Deposit: ${monthly_deposit:,.2f}/mo
Predicted Financial Freedom Age: Age {predicted_freedom_age if predicted_freedom_age else '60+'} (Goal: ${desired_monthly_income:,.0f}/mo)
 
1. {period_label.upper()} PROFIT / LOSS & CRASH RISK:
   • Current Balance: ${current_balance:,.2f} ({port_return*100:+.2f}% | ${dollar_profit_loss:+,.2f} P/L)
   • 2008 Systemic Crash Score: {crash_score} / 100 (Danger Threshold >= 70)
 
2. COMPOUND RETIREMENT & MONTHLY DIVIDEND PAYCHECK FORECAST:
   • At Age {stop_contrib_age} (Transition Exit): ${row_42['Compounded Balance']:,.0f} Portfolio | Total Monthly Income: ${row_42['Total Monthly Income ($/mo)']:,.0f}/mo
   • At Age {target_retire_age} (Full Retirement): ${row_ret['Compounded Balance']:,.0f} Portfolio
     - 4.5% Safe Dividend Paycheck: ${row_ret['4.5% Dividend Paycheck ($/mo)']:,.0f}/mo (Principal untouched)
     - 6.5% High-Yield Dividend Paycheck: ${row_ret['6.5% High-Yield Paycheck ($/mo)']:,.0f}/mo
     - Pension + VA + Social Security: ${row_ret['Pension + VA + SS ($/mo)']:,.0f}/mo
     - TOTAL COMBINED MONTHLY SALARY AT AGE {target_retire_age}: ${row_ret['Total Monthly Income ($/mo)']:,.0f}/mo
 
3. TOP 3 NEWS & QUANTITATIVE STOCK/ETF PICKS (NEXT 12 MONTHS):
   • #1 {ranked_stocks_df.iloc[0]['Ticker']}: {ranked_stocks_df.iloc[0]['Current Price']} -> {ranked_stocks_df.iloc[0]['Proj. 1-Yr Target']} ({ranked_stocks_df.iloc[0]['Proj. 1-Yr Return']})
   • #2 {ranked_stocks_df.iloc[1]['Ticker']}: {ranked_stocks_df.iloc[1]['Current Price']} -> {ranked_stocks_df.iloc[1]['Proj. 1-Yr Target']} ({ranked_stocks_df.iloc[1]['Proj. 1-Yr Return']})
   • #3 {ranked_stocks_df.iloc[2]['Ticker']}: {ranked_stocks_df.iloc[2]['Current Price']} -> {ranked_stocks_df.iloc[2]['Proj. 1-Yr Target']} ({ranked_stocks_df.iloc[2]['Proj. 1-Yr Return']})
============================================================
"""
st.code(action_report, language="text")