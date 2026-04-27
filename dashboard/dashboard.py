# =========================
# IMPORT LIBRARY
# =========================
import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

# =========================
# CONFIG STREAMLIT
# =========================
st.set_page_config(page_title="Bike Sharing Dashboard", layout="wide")

# =========================
# LOAD DATA (ANTI ERROR PATH)
# =========================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "..", "data")

day_df = pd.read_csv(os.path.join(DATA_DIR, "day.csv"))
hour_df = pd.read_csv(os.path.join(DATA_DIR, "hour.csv"))

day_df["dteday"] = pd.to_datetime(day_df["dteday"])
hour_df["dteday"] = pd.to_datetime(hour_df["dteday"])

# =========================
# TITLE
# =========================
st.title("🚴 Bike Sharing Dashboard")
st.write("Analisis pola penyewaan sepeda berdasarkan waktu, cuaca, dan jenis pengguna")

st.divider()

# =========================
# SIDEBAR FILTER
# =========================
st.sidebar.header("Filter Data")

start_date, end_date = st.sidebar.date_input(
    "Pilih rentang tanggal",
    [day_df["dteday"].min(), day_df["dteday"].max()]
)

day_filtered = day_df[
    (day_df["dteday"] >= pd.to_datetime(start_date)) &
    (day_df["dteday"] <= pd.to_datetime(end_date))
]

hour_filtered = hour_df[
    (hour_df["dteday"] >= pd.to_datetime(start_date)) &
    (hour_df["dteday"] <= pd.to_datetime(end_date))
]

# =========================
# KPI SECTION
# =========================
st.subheader("📊 Ringkasan Data")

col1, col2, col3 = st.columns(3)

col1.metric("Total Penyewaan", int(day_filtered["cnt"].sum()))
col2.metric("Rata-rata Harian", int(day_filtered["cnt"].mean()))
col3.metric("Total Registered User", int(day_filtered["registered"].sum()))

st.divider()

# =========================
# 1. POLA WAKTU
# =========================
st.subheader("⏰ Pola Penyewaan Berdasarkan Waktu")

def time_category(hour):
    if 5 <= hour < 11:
        return "Pagi"
    elif 11 <= hour < 15:
        return "Siang"
    elif 15 <= hour < 19:
        return "Sore"
    else:
        return "Malam"

hour_filtered["time_cat"] = hour_filtered["hr"].apply(time_category)

time_data = hour_filtered.groupby("time_cat")["cnt"].mean().reindex(
    ["Pagi", "Siang", "Sore", "Malam"]
)

fig, ax = plt.subplots()
ax.bar(time_data.index, time_data.values)
ax.set_ylabel("Rata-rata Penyewaan")
ax.set_title("Pola Penyewaan Berdasarkan Waktu")
st.pyplot(fig)

st.divider()

# =========================
# 2. CUACA
# =========================
st.subheader("🌤 Pengaruh Cuaca")

weather_map = {
    1: "Cerah",
    2: "Berkabut",
    3: "Hujan Ringan",
    4: "Hujan Berat"
}

hour_filtered["weather"] = hour_filtered["weathersit"].map(weather_map)

weather_data = hour_filtered.groupby("weather")["cnt"].mean().reset_index()

fig, ax = plt.subplots()
sns.barplot(data=weather_data, x="weather", y="cnt", ax=ax)
plt.xticks(rotation=15)
ax.set_title("Pengaruh Cuaca terhadap Penyewaan")
st.pyplot(fig)

st.divider()

# =========================
# 3. WORKING DAY
# =========================
st.subheader("📅 Hari Kerja vs Hari Libur")

working = day_filtered.groupby("workingday")["cnt"].mean().reset_index()

fig, ax = plt.subplots()
ax.bar(working["workingday"], working["cnt"])
ax.set_xticks([0, 1])
ax.set_xticklabels(["Libur", "Kerja"])
ax.set_title("Rata-rata Penyewaan: Hari Kerja vs Libur")
st.pyplot(fig)

st.divider()

# =========================
# 4. USER TYPE
# =========================
st.subheader("👥 Jenis Pengguna")

fig, ax = plt.subplots()
ax.pie(
    [day_filtered["casual"].sum(), day_filtered["registered"].sum()],
    labels=["Casual", "Registered"],
    autopct="%1.1f%%"
)
ax.set_title("Distribusi Pengguna")
st.pyplot(fig)

st.divider()

# =========================
# INSIGHT
# =========================
st.subheader("💡 Insight")

st.write("""
- Penyewaan tertinggi terjadi pada pagi dan sore hari (pola aktivitas kerja)
- Cuaca cerah meningkatkan jumlah penyewaan secara signifikan
- Hari kerja memiliki rata-rata lebih tinggi dibanding hari libur
- Pengguna registered mendominasi penggunaan layanan
""")