
import openpyxl # noqa
import pandas as pd
import matplotlib.pyplot as plt


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
month_columns = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

for month in month_columns:
    df[month] = df[month].astype(int)

print(df)

#  drop the column Location
df = df.drop(columns=['Location'])

print(df)

# Melt the DataFrame
df_melted = pd.melt(df, id_vars=['Year'], var_name='Month', value_name='Deaths')

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
df_final = df_sorted[['Date', 'Deaths']]

# Display the final DataFrame
print(df_final)

print(df_final.dtypes)


# Plot the graph
df_final.plot(x='Date', y='Deaths', figsize=(10, 5))
# save the graph
plt.savefig('summary/summary_ons_deaths.png')


