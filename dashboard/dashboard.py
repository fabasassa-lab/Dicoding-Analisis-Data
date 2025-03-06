# library
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency
sns.set(style='dark')

# load berkas hour_dash.csv day_dash.csv
hour_df = pd.read_csv("hour_dash.csv")
day_df = pd.read_csv("day_dash.csv")

hour_df["dteday"] = pd.to_datetime(hour_df["dteday"])
day_df["dteday"] = pd.to_datetime(day_df["dteday"])

# Sidebar date filter
min_date = day_df['dteday'].min()
max_date = day_df['dteday'].max()

with st.sidebar:
    st.image("bg.png")
    start_date, end_date = st.date_input(
        label='Pilih **2** Rentang Waktu', min_value=min_date,
        max_value=max_date, value=[min_date, max_date]
    )

# Filter dataset based on date range
filtered_day_df = day_df[(day_df['dteday'] >= str(start_date)) & (day_df['dteday'] <= str(end_date))]
filtered_hour_df = hour_df[(hour_df['dteday'] >= str(start_date)) & (hour_df['dteday'] <= str(end_date))]

# Dashboard Title
st.header('Bike Sharing Dashboard 🚲')

# Daily Rental Analysis
st.subheader('Daily Rental Trends')
total_rentals = filtered_day_df['count'].sum()
st.metric("Total Rentals", value=total_rentals)

fig, ax = plt.subplots(figsize=(16, 8))
ax.plot(filtered_day_df['dteday'], filtered_day_df['count'], marker='o', linewidth=2, color="#90CAF9")
ax.set_xlabel("Date")
ax.set_title("Daily Rental Trends", fontsize=18)
st.pyplot(fig)



# Agregasi jumlah penyewaan per musim
season_rentals = day_df.groupby("season", observed=False)["count"].sum().reset_index()

# Menentukan musim dengan penyewaan terbanyak
max_season = season_rentals["count"].idxmax()

# Warna default dan menyoroti musim dengan penyewaan terbanyak
colors = ["#D3D3D3"] * len(season_rentals)
colors[max_season] = "#72BCD4"  # Warna berbeda untuk musim dengan penyewaan terbanyak

# Streamlit Layout
st.subheader("Total Bike Rentals by Season")

# Plot bar chart
fig, ax = plt.subplots(figsize=(8, 5))
ax.bar(season_rentals["season"], season_rentals["count"], color=colors)
ax.set_title("Total Bike Rentals by Season", fontsize=10)
ax.set_xlabel("Season", fontsize=10)
ax.set_xticks(season_rentals["season"])
ax.set_xticklabels(["Spring", "Summer", "Fall", "Winter"])

# Tambahkan angka di atas setiap bar
for i, txt in enumerate(season_rentals["count"]):
    ax.text(season_rentals["season"][i], txt + 10000, f"{txt:,}",
            fontsize=8, fontweight="medium", ha="center")

# Tampilkan plot di Streamlit
st.pyplot(fig)


# Agregasi jumlah penyewaan untuk pengguna casual dan registered
total_casual = day_df["casual"].sum()
total_registered = day_df["registered"].sum()

# Data untuk plotting
categories = ["Casual", "Registered"]
values = [total_casual, total_registered]
colors = ["#D3D3D3", "#72BCD4"]  # Warna berbeda untuk masing-masing kategori

# Streamlit Layout
st.subheader("User Demographics")

# **Hitung total casual dan registered setelah filter**
total_casual = filtered_day_df["casual"].sum()
total_registered = filtered_hour_df["registered"].sum()

# Data untuk plotting
categories = ["Casual", "Registered"]
values = [total_casual, total_registered]
colors = ["#D3D3D3", "#72BCD4"]  # Warna berbeda untuk masing-masing kategori

# **Buat bar chart**
fig, ax = plt.subplots(figsize=(7, 5))
ax.bar(categories, values, color=colors)

# Tambahkan angka di atas setiap bar
for i, txt in enumerate(values):
    ax.text(i, txt + max(values) * 0.05, f"{txt:,}", fontsize=8, fontweight="medium", ha="center")

# Judul dan label
ax.set_title("Numbers of Users", fontsize=10)
ax.set_ylim(0, max(values) * 1.1)  # Mulai dari 0 dan memberi sedikit ruang atas

# **Tampilkan plot di Streamlit**
st.pyplot(fig)


# Tentukan tanggal referensi sebagai tanggal terakhir dalam dataset
reference_date = day_df["dteday"].max()

# Hitung RFM berdasarkan kategori 'season'
rfm_df = day_df.groupby("season", observed=False).agg(
    Recency=("dteday", lambda x: (reference_date - x.max()).days),  # Selisih hari dari transaksi terakhir
    Frequency=("dteday", "count"),  # Total jumlah hari dengan penyewaan
    Monetary=("count", "sum")  # Total jumlah penyewaan
).reset_index()

# Streamlit Layout
st.subheader("Best Season Based on RFM Parameters")

# Hitung rata-rata RFM
avg_recency = round(rfm_df["Recency"].mean(), 1)
avg_frequency = round(rfm_df["Frequency"].mean(), 2)
avg_monetary = round(rfm_df["Monetary"].mean(), 2)  # Rata-rata jumlah penyewaan

# Layout dengan 3 kolom
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Average Recency (days)", value=avg_recency)

with col2:
    st.metric("Average Frequency", value=avg_frequency)

with col3:
    st.metric("Average Monetary", value=avg_monetary)

# Membuat figure untuk menampilkan 3 barplot secara horizontal
fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(30, 6))

colors = ["#90CAF9", "#90CAF9", "#90CAF9", "#90CAF9"]

sns.barplot(y="Recency", x="season", data=rfm_df.sort_values(by="Recency", ascending=True), palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel(None)
ax[0].set_title("By Recency (days)", loc="center", fontsize=18)
ax[0].tick_params(axis='x', labelsize=15)

sns.barplot(y="Frequency", x="season", data=rfm_df.sort_values(by="Frequency", ascending=False), palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel(None)
ax[1].set_title("By Frequency", loc="center", fontsize=18)
ax[1].tick_params(axis='x', labelsize=15)

sns.barplot(y="Monetary", x="season", data=rfm_df.sort_values(by="Monetary", ascending=False), palette=colors, ax=ax[2])
ax[2].set_ylabel(None)
ax[2].set_xlabel(None)
ax[2].set_title("By Monetary", loc="center", fontsize=18)
ax[2].tick_params(axis='x', labelsize=15)

# Tampilkan plot di Streamlit
st.pyplot(fig)
