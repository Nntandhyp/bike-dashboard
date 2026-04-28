import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
import streamlit as st

# ── Page Config ───────────────────────────────────────────
st.set_page_config(page_title="Bike Sharing Dashboard", layout="wide")

# ── Load Data ─────────────────────────────────────────────
@st.cache_data
def load_data():
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    day_df  = pd.read_csv(os.path.join(BASE_DIR, 'data', 'day.csv'))
    hour_df = pd.read_csv(os.path.join(BASE_DIR, 'data', 'hour.csv'))

    for df in [day_df, hour_df]:
        df['dteday']     = pd.to_datetime(df['dteday'])
        df['season']     = df['season'].map({1:'Spring',2:'Summer',3:'Fall',4:'Winter'})
        df['yr']         = df['yr'].map({0:'2011',1:'2012'})
        df['weathersit'] = df['weathersit'].map({1:'Clear',2:'Mist',3:'Light Rain/Snow',4:'Heavy Rain/Snow'})
        df['workingday'] = df['workingday'].map({0:'No',1:'Yes'})
        df['holiday']    = df['holiday'].map({0:'No',1:'Yes'})

    def categorize_time(h):
        if 5 <= h < 11:
            return 'Morning'
        elif 11 <= h < 15:
            return 'Afternoon'
        elif 15 <= h < 19:
            return 'Evening'
        else:
            return 'Night'

    hour_df['time_category'] = hour_df['hr'].apply(categorize_time)
    return day_df, hour_df

day_df, hour_df = load_data()

# ── Header ────────────────────────────────────────────────
st.title("🚲 Bike Sharing Dashboard")
st.markdown("Analisis pola penyewaan sepeda periode **2011–2012**")
st.divider()

# ── Sidebar Filter ────────────────────────────────────────
st.sidebar.header("Filter Data")
year_filter = st.sidebar.multiselect(
    "Pilih Tahun",
    options=['2011', '2012'],
    default=['2011', '2012']
)

day_filtered  = day_df[day_df['yr'].isin(year_filter)]
hour_filtered = hour_df[hour_df['yr'].isin(year_filter)]

# ── Metrics ───────────────────────────────────────────────
col1, col2, col3 = st.columns(3)
col1.metric("Total Penyewaan",   f"{day_filtered['cnt'].sum():,.0f}")
col2.metric("Rata-rata Harian",  f"{day_filtered['cnt'].mean():,.0f}")
col3.metric("Rata-rata per Jam", f"{hour_filtered['cnt'].mean():,.0f}")
st.divider()

# ── Q1: Kategori Waktu ────────────────────────────────────
st.subheader("1. Rata-rata Penyewaan Berdasarkan Kategori Waktu")

time_order = ['Morning', 'Afternoon', 'Evening', 'Night']
time_usage = (
    hour_filtered
    .groupby('time_category')['cnt']
    .mean()
    .reindex(time_order)
    .reset_index()
)

fig1, ax1 = plt.subplots(figsize=(8, 4))
bar_colors = [
    '#2E5A88' if v == time_usage['cnt'].max() else '#D3D3D3'
    for v in time_usage['cnt']
]
sns.barplot(data=time_usage, x='time_category', y='cnt', palette=bar_colors, ax=ax1)
for p in ax1.patches:
    ax1.annotate(
        f'{p.get_height():.0f}',
        (p.get_x() + p.get_width() / 2, p.get_height()),
        ha='center', va='bottom', fontweight='bold'
    )
ax1.set_title('Rata-rata Penyewaan per Kategori Waktu')
ax1.set_xlabel('Kategori Waktu')
ax1.set_ylabel('Rata-rata Penyewaan')
sns.despine()
st.pyplot(fig1)
st.caption("Evening (sore) memiliki rata-rata penyewaan tertinggi — mencerminkan pola commuting pulang kerja.")
st.divider()

# ── Q2: Kondisi Cuaca ─────────────────────────────────────
st.subheader("2. Rata-rata Penyewaan Berdasarkan Kondisi Cuaca")

weather_usage = (
    hour_filtered
    .groupby('weathersit')['cnt']
    .mean()
    .reset_index()
    .sort_values('cnt', ascending=False)
)

fig2, ax2 = plt.subplots(figsize=(8, 4))
bar_colors2 = [
    '#2E5A88' if i == 0 else '#D3D3D3'
    for i in range(len(weather_usage))
]
sns.barplot(data=weather_usage, x='weathersit', y='cnt', palette=bar_colors2, ax=ax2)
for p in ax2.patches:
    ax2.annotate(
        f'{p.get_height():.0f}',
        (p.get_x() + p.get_width() / 2, p.get_height()),
        ha='center', va='bottom', fontweight='bold'
    )
ax2.set_title('Rata-rata Penyewaan per Kondisi Cuaca')
ax2.set_xlabel('Kondisi Cuaca')
ax2.set_ylabel('Rata-rata Penyewaan')
plt.xticks(rotation=15)
sns.despine()
st.pyplot(fig2)
st.caption("Cuaca Clear menghasilkan penyewaan tertinggi. Semakin buruk cuaca, semakin turun jumlah penyewaan.")
st.divider()

# ── Q3: Hari Kerja vs Libur ───────────────────────────────
st.subheader("3. Rata-rata Penyewaan: Hari Kerja vs Hari Libur")

working_usage = (
    day_filtered
    .groupby('workingday')['cnt']
    .mean()
    .reset_index()
)

fig3, ax3 = plt.subplots(figsize=(6, 4))
sns.barplot(
    data=working_usage, x='workingday', y='cnt',
    palette=['#D3D3D3', '#2E5A88'], ax=ax3
)
for p in ax3.patches:
    ax3.annotate(
        f'{p.get_height():.0f}',
        (p.get_x() + p.get_width() / 2, p.get_height()),
        ha='center', va='bottom', fontweight='bold'
    )
ax3.set_title('Rata-rata Penyewaan: Hari Kerja vs Hari Libur')
ax3.set_xlabel('Hari Kerja (No = Libur, Yes = Kerja)')
ax3.set_ylabel('Rata-rata Penyewaan')
sns.despine()
st.pyplot(fig3)
st.caption("Hari kerja memiliki rata-rata penyewaan lebih tinggi — sepeda lebih banyak digunakan untuk transportasi rutin.")
st.divider()

# ── Q4: Clustering Jam ────────────────────────────────────
st.subheader("4. Clustering Jam Operasional Berdasarkan Tingkat Demand")

hourly_avg = (
    hour_filtered
    .groupby('hr')['cnt']
    .mean()
    .reset_index()
)
hourly_avg.columns = ['hr', 'avg_cnt']
hourly_avg['demand_level'] = pd.cut(
    hourly_avg['avg_cnt'],
    bins=[0, 100, 250, 500],
    labels=['Low Demand', 'Medium Demand', 'High Demand']
)

color_map = {
    'Low Demand':    '#D3D3D3',
    'Medium Demand': '#88B4D4',
    'High Demand':   '#2E5A88'
}
bar_colors3 = [color_map[str(lv)] for lv in hourly_avg['demand_level']]

fig4, ax4 = plt.subplots(figsize=(12, 4))
ax4.bar(hourly_avg['hr'], hourly_avg['avg_cnt'], color=bar_colors3)

legend_elements = [
    mpatches.Patch(facecolor=v, label=k)
    for k, v in color_map.items()
]
ax4.legend(handles=legend_elements, title='Demand Level', loc='upper left')
ax4.set_title('Clustering Jam Operasional Berdasarkan Tingkat Demand')
ax4.set_xlabel('Jam (00:00 - 23:00)')
ax4.set_ylabel('Rata-rata Penyewaan')
ax4.set_xticks(range(0, 24))
sns.despine()
st.pyplot(fig4)
st.caption("Jam sibuk (High Demand) terkonsentrasi pada pagi 07-09 dan sore 16-19. Jam dini hari masuk kategori Low Demand.")

st.divider()
st.markdown("© 2024 Bike Sharing Dashboard | Dibuat dengan Streamlit")
