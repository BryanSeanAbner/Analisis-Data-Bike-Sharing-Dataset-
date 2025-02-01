import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
sns.set(style='dark')
    
def create_daily_registered_df(df):
    daily_registered_df = df.resample(rule='D', on='dteday').agg({
        "registered": "sum",
    })
    daily_registered_df = daily_registered_df.reset_index()
    daily_registered_df.rename(columns={
        "registered": "total_registered",
    }, inplace=True)
    
    return daily_registered_df

def create_monthly_registered_df(df):
    monthly_registered_df = df.resample(rule='M', on='dteday').agg({
        "registered": "sum",
    })
    monthly_registered_df = monthly_registered_df.reset_index()
    monthly_registered_df.rename(columns={
        "registered": "total_registered",
    }, inplace=True)
    
    return monthly_registered_df

def create_byhour_df(df):
    byhour_df = df.groupby(by="hr").registered.sum().reset_index()
    byhour_df.rename(columns={
        "registered": "total_customer"
    }, inplace=True)

    return byhour_df

data_df = pd.read_csv("https://raw.githubusercontent.com/BryanSeanAbner/Analisis-Data-Bike-Sharing-Dataset-/refs/heads/main/dashboard/main_data.csv")
data_df = pd.read_csv("https://raw.githubusercontent.com/BryanSeanAbner/Analisis-Data-Bike-Sharing-Dataset-/refs/heads/main/dashboard/main_data1.csv")

datetime_columns = ["dteday"]
data_df.sort_values(by="dteday", inplace=True)
data_df.reset_index(inplace=True)
 
for column in datetime_columns:
    data_df[column] = pd.to_datetime(data_df[column])

min_date = data_df["dteday"].min()
max_date = data_df["dteday"].max()

with st.sidebar:    
    start_date, end_date = st.date_input(
        label='Rentang Waktu', min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

main_df = data_df[(data_df["dteday"] >= str(start_date)) & 
                (data_df["dteday"] <= str(end_date))]

byhour_df = create_byhour_df(main_df)
daily_registered_df = create_daily_registered_df(main_df)
monthly_registered_df = create_monthly_registered_df(main_df)

total_registered= daily_registered_df["total_registered"].sum()

st.header('Bike Sharing Dashboard')
st.subheader(f'Total Registered: {total_registered}')

st.subheader('Monthly Registered')
fig, ax = plt.subplots(figsize=(16, 8))
ax.plot(
    monthly_registered_df["dteday"],
    monthly_registered_df["total_registered"],
    marker='o', 
    linewidth=2,
    color="green"
)
ax.set_xlabel("Month", fontsize=15)
ax.set_ylabel("Total Registered", fontsize=15)
ax.set_title("Monthly Registered", fontsize=20)
ax.grid(True)

st.pyplot(fig)

st.subheader("Registered based on Hour")
plt.figure(figsize=(10, 6))
byhour_df.plot(kind='bar', color='skyblue', legend=False, edgecolor='none', linewidth=2)
plt.title('Total Bike Registered by Hour of the Day')
plt.xlabel('Hour')
plt.ylabel('Total Registered')
plt.xticks(rotation=0)
plt.grid(axis='y')
plt.tight_layout()
st.pyplot(plt)

st.subheader("Analysis by RFM")

latest_date = daily_registered_df['dteday'].max()
rfm_df = daily_registered_df.groupby('dteday').agg(
    Frequency=('total_registered', 'count'),
    Monetary=('total_registered', 'sum')
).reset_index()
rfm_df['Recency'] = (latest_date - rfm_df['dteday']).dt.days

plt.figure(figsize=(15, 5))

plt.subplot(1, 3, 1)
sns.histplot(rfm_df['Recency'], bins=30, kde=True, color='blue')
plt.title('Distribusi Recency')
plt.xlabel('Hari sejak terakhir menyewa')
plt.ylabel('Jumlah Hari')

plt.subplot(1, 3, 2)
sns.histplot(rfm_df['Frequency'], bins=10, kde=True, color='green')
plt.title('Distribusi Frequency')
plt.xlabel('Frekuensi Sewa per Hari')
plt.ylabel('Jumlah Hari')

plt.subplot(1, 3, 3)
sns.histplot(rfm_df['Monetary'], bins=30, kde=True, color='red')
plt.title('Distribusi Monetary')
plt.xlabel('Total Sewa Terdaftar per Hari')
plt.ylabel('Jumlah Hari')

plt.tight_layout()
st.pyplot(plt)
