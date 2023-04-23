
import openpyxl # noqa
import pandas as pd


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

# Change all the months columns into a integers in a loop
for i in range(1, 13):
    df.iloc[:, i] = df.iloc[:, i].astype(int)


print(df)


