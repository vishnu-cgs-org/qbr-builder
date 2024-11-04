import pandas as pd

df = pd.read_csv(r'C:\Users\vanikumar\slide-maker\resources\crs_sheet.csv')


headers = ['Partner/Distributor Name', 'Account ID',  'GEO', 'Assigned CRS',
         'Country', 'Total ACV 2024','Total TCV 2024']
filtered_df = df[headers]
cleaned_df = filtered_df.dropna(subset=['Account ID'])
