
import openpyxl # noqa
import pandas as pd
import matplotlib.pyplot as plt
from azure.ai.anomalydetector import AnomalyDetectorClient
from azure.core.credentials import AzureKeyCredential
from decouple import config
import matplotlib.dates as mdates

# This code reads an Excel file containing a time series of monthly death data,
# preprocesses the data, and identifies anomalies using the Azure
# Anomaly Detector API. After detecting anomalies, it plots the time series,
# highlights the anomalies, and shows upper and lower margin bands.

# Read in excel file into pandas dataframe
df = pd.read_excel('summary/summary_ons_deaths.xlsx',
                   sheet_name='Sheet1', header=0)

print(df)

# drop col called code
df = df.drop(columns=['code'])

df = df.dropna()
print(df)

# Change the Year column into an integer
df['Year'] = df['Year'].astype(int)

# Iterate over month columns and change data type to integer
month_columns = ['Jan', 'Feb', 'Mar', 'Apr', 'May',
                 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

for month in month_columns:
    df[month] = df[month].astype(int)

print(df)

#  drop the column Location
df = df.drop(columns=['Location'])

print(df)

# Melt the DataFrame
df_melted = pd.melt(df, id_vars=['Year'],
                    var_name='Month', value_name='Deaths')

# Change month names to numbers
month_mapping = {'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5,
                 'Jun': 6, 'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11,
                 'Dec': 12}
df_melted['Month'] = df_melted['Month'].map(month_mapping)

# Create a datetime column
df_melted['Date'] = pd.to_datetime(df_melted[['Year', 'Month']].assign(day=1))

# Sort the DataFrame chronologically
df_sorted = df_melted.sort_values(by='Date').reset_index(drop=True)

# Drop unnecessary columns and keep only the Deaths column
df = df_sorted[['Date', 'Deaths']]


# Create a list of dictionaries for the series, thats what azure expects
series = []
for index, row in df.iterrows():
    series.append({'timestamp': row['Date'], 'value': row['Deaths']})

print(series)

# Create a request data object for the azxure anomaly detector
request_data = {
    'series': series,
    'granularity': 'monthly',
    'maxAnomalyRatio': 0.25,
    'sensitivity': 80
}


# create a client object to connect to the anomaly detector
client = AnomalyDetectorClient(
    credential=AzureKeyCredential(config('API_KEY')),
    endpoint=config('API_ENDPOINT'))

# Call the anomaly detector
anomaly_response = client.detect_univariate_entire_series(request_data)

df['is_anomaly'] = anomaly_response.is_anomaly

# Add the margins list to the DataFrame
df['upper_margin_delta'] = anomaly_response.upper_margins
df['lower_margin_delta'] = anomaly_response.lower_margins
df['upper_margin'] = df['Deaths'] + df['upper_margin_delta']
df['lower_margin'] = df['Deaths'] - df['lower_margin_delta']

# Print dataframe head as debug
print(df.head())

mask = df['is_anomaly']

fig, ax = plt.subplots(figsize=(15, 6))  # Adjust the figure size

# Plot the time series
ax.plot(df['Date'], df['Deaths'], label='Deaths')

# Plot the red markers where 'is_anomaly' is True
ax.scatter(df.loc[mask, 'Date'], df.loc[mask,
           'Deaths'], color='red', marker='o', label='Anomaly')

# Add the shaded area between the upper and lower margins
ax.fill_between(df['Date'], df['lower_margin'],
                df['upper_margin'], color='gray',
                alpha=0.3, label='Margin')

# Configure the x-axis to show year markers
ax.xaxis.set_major_locator(mdates.YearLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))

# Configure the plot
ax.set_xlabel('Date')
ax.set_ylabel('Deaths')
ax.set_title('Deaths Time Series with Anomalies and Margins')
ax.legend()

# Save the plot with a higher resolution (e.g., 300 dpi)
plt.savefig('summary/summary_ons_deaths.png', dpi=150, bbox_inches='tight')
