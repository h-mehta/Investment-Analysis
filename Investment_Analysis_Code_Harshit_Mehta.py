# %%
#loading libararies and reading the data

import numpy as np
import pandas as pd
import re

mapping_df = pd.read_csv("mapping.csv")
rounds2_df = pd.read_csv("rounds2.csv", encoding = 'palmos')
companies_df = pd.read_csv("companies.txt",delimiter="\t", encoding = 'palmos')

# %%
companies_df.head()

# %%
companies_df.info()

# %%
rounds2_df.head()

# %%
rounds2_df.info()

# %%
# Converting permalink (unique ID) to lower case in companies df

companies_df["permalink"] = companies_df["permalink"].apply(lambda x: x.lower())
companies_df.shape

# %%
# Converting permalink (unique ID) to lower case in companies df

rounds2_df["company_permalink"] = rounds2_df["company_permalink"].apply(lambda x: x.lower())
rounds2_df.shape

# %%
# Finding unique companies in round2 dataframe
# Alternatively : len(rounds2_df.company_permalink.unique()) 
unique_companies_rounds = set(rounds2_df.company_permalink)
print(len(unique_companies_rounds))

# %%
# Finding unique companies in companies dataframe
# Alternatively : len(companies_df.permalink.unique()) 
unique_companies_in_companies_df = set(companies_df.permalink)
print(len(unique_companies_in_companies_df))

# %%
# companies in the rounds2 file which are not present in companies file
set3 = unique_companies_rounds.difference(unique_companies_in_companies_df)
print(len(set3))

# %%
# Renaming the column company_permanlink of rounds to permalink
rounds2_df.columns = ['permalink', 'funding_round_permalink', 'funding_round_type',
       'funding_round_code', 'funded_at', 'raised_amount_usd']

# %%
# Merge the two data frames
master_frame = pd.merge(companies_df, rounds2_df, how="inner", on="permalink")
master_frame.shape

# %%
'''
## Cleaning Data
'''

# %%
# Let's have a look at the merged dataframe
master_frame.head()

# %%
master_frame.shape

# %%
master_frame.info()

# %%
#summing up missing values
master_frame.isnull().sum()

# %%
# rows having all missing values
master_frame.isnull().all(axis=1).sum()

# %%
'''
Hence no rows have all missing values
'''

# %%
# Finding percentage of missing values (column wise)
round(100*(master_frame.isnull().sum()/len(master_frame.index)),2)

# %%
# Dropping the funding_round_code column as it is not significant and has high percentage of missing value 
master_frame = master_frame.drop('funding_round_code', axis = 1)
round(100*(master_frame.isnull().sum()/len(master_frame.index)),2)

# %%
# Remaining columns

master_frame.columns

# %%
# Dropping homepage_url as not significant for our analysis

master_frame = master_frame.drop('homepage_url', axis = 1)
round(100*(master_frame.isnull().sum()/len(master_frame.index)),2)

# %%
master_frame.columns

# %%
# Dropping founded_at as not significant for our analysis

master_frame = master_frame.drop('founded_at', axis = 1)
round(100*(master_frame.isnull().sum()/len(master_frame.index)),2)

# %%
# Understanding the status column

print(set(list(master_frame.status)))

# %%
master_frame.shape

# %%
# Removing companies with status = Closed

master_frame = master_frame.loc[ master_frame["status"]!="closed", : ]
master_frame.shape

# %%
'''
#### Would do the further data cleaning based on the requirement / type of analysis.
'''

# %%
'''
# Grouping by funding round - Investment Type analysis
'''

# %%
investment_types = ["venture","angel","seed","private_equity"]

# %%
master_frame = master_frame.loc[master_frame['funding_round_type'].isin(investment_types), :]

# %%
# Now understanding the type of data we have
# Look at the summary again
round(100*(master_frame.isnull().sum()/len(master_frame.index)),2)

# %%
'''
#### Imputing values of raised_amount_usd 
'''

# %%
'''
Let's first have a look at the data for various founding_round_type :
'''

# %%
master_frame.shape

# %%
master_frame.loc[master_frame['funding_round_type']=="venture",:].raised_amount_usd.describe()

# %%
'''
The 3rd quartile is 7.5 times the 1st quartile for venture type !
'''

# %%
master_frame.loc[master_frame['funding_round_type']=="angel",:].raised_amount_usd.describe()

# %%
'''
The 3rd quartile is 6.67 times the 1st quartile for angel type !
'''

# %%
master_frame.loc[master_frame['funding_round_type']=="seed",:].raised_amount_usd.describe()

# %%
'''
The 3rd quartile is 17 times the 1st quartile for seed type !
'''

# %%
master_frame.loc[master_frame['funding_round_type']=="private_equity",:].raised_amount_usd.describe()

# %%
'''
The 3rd quartile is 15 times the 1st quartile for private_equity type !
'''

# %%
master_frame.raised_amount_usd.describe()

# %%
'''
The difference in Q1 and Q3 for the whole data is almost 20 times!
'''

# %%
'''
Since the variation in data is so high, I shall be using "Median" as the Representative statistic for each funding_type to compare. 
'''

# %%
'''
As far as missing values are concerned, imputting all types of funding_round_type by the same value would lead to introduction of very high bias in the data.

Then the other alternative left would be to impute rows by checking their funding_type and filling the missing value with the median of the corresponding funding_type. 

However such an exercise would be futile as I will be comparing the funding_types on the basis of median value, and filling in missing values with the median value of correponding funding_type is not going to change the median of the funding_type. 

Thus proceeding with comparison of funding_types using the median.
'''

# %%
# plot1_df to be used in - Check point 6 : graph 1

plot1_df = master_frame

# %%
master_frame_by_funding_type = master_frame.groupby("funding_round_type")

# %%
master_funding_df = pd.DataFrame(master_frame_by_funding_type["raised_amount_usd"].median())
master_funding_df

# %%
favourable_investment_type = master_funding_df.loc[(master_funding_df.raised_amount_usd >= 5000000) & (master_funding_df.raised_amount_usd <= 15000000) ]
favourable_investment_type

# %%
'''
Hence we can conclude that Venture type funding meets our requirements.

Thus keeping only those records which have "venture" as the 'funding_round_type'
'''

# %%
round(100*(master_frame.isnull().sum()/len(master_frame.index)),2)

# %%
master_frame = master_frame.loc[master_frame['funding_round_type']=="venture", :]
master_frame["funding_round_type"].describe()

# %%
'''
#### Imputting the missing values for raised_amount_usd by median value for venture

'''

# %%
# Calculating venture median
venture_median = master_frame["raised_amount_usd"].median()
venture_median

# %%
# Imputting the missing values with the median of venture funding_type
master_frame.loc[np.isnan(master_frame["raised_amount_usd"]), ["raised_amount_usd"]] = 5000000.0
round(100*(master_frame.isnull().sum()/len(master_frame.index)),2)

# %%
'''
# Country wise Analysis
'''

# %%
'''
Steps :
1. Clean the raised_amount_usd data
2. Impute country_code
3. Proceed with grouping by country_code
'''

# %%
'''
Since country wise analysis would require sum of "raised_amount_usd" per country, will be filtering out the outliers in the data (specifically the raised_amount_usd).
'''

# %%
'''
### Outlier Removal
Outlier Criteria : Data point that falls between 1st percentile and 99th percentile
'''

# %%
master_frame["raised_amount_usd"].describe()

# %%
'''
The raised_amount_usd is ranging from 0 to 17 billion!
'''

# %%
# Calculating the percentiles
first_percentile = master_frame["raised_amount_usd"].quantile([.01,.99])[.01]
ninety_nine_percentile = master_frame["raised_amount_usd"].quantile([.01,.99])[.99]

# %%
first_percentile

# %%
ninety_nine_percentile

# %%
'''
Retaining points in between 1st and 99th percentile
'''

# %%
master_frame = master_frame.loc[ (master_frame["raised_amount_usd"] >= first_percentile) & (master_frame["raised_amount_usd"] <= ninety_nine_percentile) , :]

# %%
master_frame["raised_amount_usd"].describe()

# %%
'''
Having removed outliers from raised_amount_usd,

Let's probe the data we have :
'''

# %%
round(100*(master_frame.isnull().sum()/len(master_frame.index)),2)

# %%
'''
For Country Analysis we would need to impute values for country code, let's see what other columns contain which can help us impute the value of country code if possible.
'''

# %%
master_frame.head()

# %%
# Probably region can help in imputing values for country_code; exploring the region column
print(len(set(master_frame["region"])))

# %%
master_frame.shape

# %%
q = master_frame.loc[ ( master_frame['region'].isnull() ) , :]
print(len(q))

# %%
q = master_frame.loc[ ( master_frame['region'].isnull() == False) , :]
print(len(q))

# %%
q = master_frame.loc[( master_frame.country_code.isnull() ) & ( master_frame['region'].isnull() == False ) , :]
print(len(q))

# %%
'''
However, there are no rows which have a region but not country code.

Thus we can not use region to impute value of country code. 
'''

# %%
'''
Exploring other columns like "city" :
'''

# %%
q = master_frame.loc[( master_frame.country_code.isnull() ) & ( master_frame['city'].isnull() == False ) , :]
print(len(q))

# %%
'''

Thus there are no rows where country code is absent and region/city is present - Ruling out the possibility of imputing values of country on the basis of region/city .


'''

# %%
'''
Thus dropping the rows where country code is missing.
'''

# %%
# Dropping state_code, region, city as not significant for our analysis
master_frame = master_frame.drop('state_code', axis = 1)
master_frame = master_frame.drop('region', axis = 1)
master_frame = master_frame.drop('city', axis = 1)

round(100*(master_frame.isnull().sum()/len(master_frame.index)),2)

# %%
# Understanding the country_code
# Probing the value that can be imputed
master_frame.pivot_table(values = "raised_amount_usd", index = "country_code", aggfunc = ["count"]).sort_values(('count','raised_amount_usd'), ascending=False).head()


# %%
master_frame.shape

# %%
'''
Since around 70% of the dataset has USA as the country_code; we can safely impute the missing values of country_code with USA
'''

# %%
# imputting NaNs in country_code with USA
master_frame.loc[pd.isnull(master_frame["country_code"]), ["country_code"]] = "USA"
round(100*(master_frame.isnull().sum()/len(master_frame.index)),2)

# %%
'''
# Grouping by Country - Country Type analysis
'''

# %%
master_frame_by_country_code = master_frame.groupby("country_code")
master_frame_by_country_code["raised_amount_usd"].sum().sort_values(ascending = False).head()

# %%
master_frame_by_country_code_df = pd.DataFrame(master_frame_by_country_code["raised_amount_usd"].sum().sort_values(ascending = False))
master_frame_by_country_code_df.head()

# %%
# Selecting the top 9 countries based on 'raised_amount_usd'
master_frame_by_country_code_df[0:9]

# %%
'''
China (CHN), France (FRA), Germany (DEU), Switzerland (CHE) do NOT have english as its official language.
'''

# %%
# Creating list of english speaking countries
english_speaking = pd.DataFrame(["USA","GBR","IND","CAN","ISR","SGP","IRL","AUS","HKG"], columns = ["country_code"])

# %%
print(english_speaking)

# %%
# Filtering out non-english speaking countries from top 9 countries
master_frame_country_english = pd.merge(master_frame_by_country_code_df[0:9], english_speaking, how="inner", on="country_code")
master_frame_country_english

# %%
# Selecting the top 3 english speaking countries
master_frame_country_english[0:3]

# %%
'''
# Sector Analysis 1
'''

# %%
'''
Steps :
1. Exploring the mapping file
2. Cleaning data of mapping file
3. Preparing the data master_frame - adding primary_sector
4. Resolving conflicts in data in mapping and master_frame
5. Creating a main_sector : primary_sector dictionary from mapping file
6. Creating a new data frame containing primary_sector and main_sector 
7. Merging the new dataframe with master_frame - to add main_sector to master_frame 
'''

# %%
# Understanding the mapping file.
mapping_df.head()

# %%
mapping_df.columns

# %%
mapping_df.shape

# %%
round(100*(mapping_df.isnull().sum()/len(mapping_df.index)),2)

# %%
'''
#### Cleaning data of mapping file
'''

# %%
# removing NaNs in category_list
mapping_df = mapping_df[~mapping_df.category_list.isnull() ]
round(100*(mapping_df.isnull().sum()/len(mapping_df.index)),2)

# %%
mapping_df.shape

# %%
'''
Hence 1 row containing NaN as category_list has been removed.
'''

# %%
# Converting all categories to lower case for consistency
mapping_df["category_list"] = mapping_df["category_list"].apply(lambda x: x.lower())
mapping_df.head()

# %%
'''
#### Cleaning and manipulating master_frame :
'''

# %%
'''
Steps :

1. Impute category_list

2. Adding primary_sector to master_frame

3. manipulating data in primary_sector column of master_frame
'''

# %%
# Understanding the category_list
# Probing the value that can be imputed
master_frame.pivot_table(values = "raised_amount_usd", index = "category_list", aggfunc = ["count"]).sort_values(('count','raised_amount_usd'), ascending=False).head()


# %%
'''
We can see that Biotechnology has the highest occurences (10% of category_list), which is significantly higher than the frequency of other categories.

Thus we can safely impute the value of missing categories as Biotechnology.
'''

# %%
# Out of the total almost 10% of dataset has Biotechnology as the category
master_frame.shape

# %%
# Imputting the missing values of category_list with "Biotechnology"
master_frame.loc[pd.isnull(master_frame["category_list"]), ["category_list"]] = "Biotechnology"
round(100*(master_frame.isnull().sum()/len(master_frame.index)),2)

# %%
# Adding the primary sector column to master_frame
master_frame["primary_sector"] = master_frame["category_list"].apply(lambda x:x if (x.find('|')==-1) else x[0:x.find("|")])
master_frame.head()

# %%
# Manipulating data in primary sector, so that it can be compared with mapping file category_list

master_frame["primary_sector"] = master_frame["primary_sector"].apply(lambda x: x.lower())
master_frame.head()

# %%
# Comparing the data in 2 dataframes to understand if there are any conflicts

e = set(list(master_frame["primary_sector"])).difference(set(list(mapping_df["category_list"])))
print(sorted(e))

# %%
d = set(list(mapping_df["category_list"])).difference(set(list(master_frame["primary_sector"])))
print(sorted(d))

# %%
'''
It can be seen from above output, that some sectors are missing in the mapping file.

On a closer look, it can be observed that for some sectors in mapping file, 'na' has been replaced by 0.

Hence, going to clean the data in mapping file and then re-check.
'''

# %%
mapping_df["category_list"] = mapping_df["category_list"].str.replace("0","na")

# %%
mapping_df.head()

# %%
mapping_category_list = [x for x in list(mapping_df["category_list"])]
master_frame_primary_sector_list = [x for x in list(master_frame["primary_sector"]) ]

e = set(master_frame_primary_sector_list).difference(set(mapping_category_list))
print(sorted(e))

# %%
'''
The number of mismatch has reduced !

Due to replacement of 0 by na - "enterprise 2.0" in mapping file has also changed to "enterprise 2.na" - Rectifying that first
'''

# %%
mapping_df["category_list"] = mapping_df["category_list"].str.replace("enterprise 2.na","enterprise 2.0")

# %%
mapping_category_list = [x for x in list(mapping_df["category_list"])]
master_frame_primary_sector_list = [x for x in list(master_frame["primary_sector"]) ]

e = set(master_frame_primary_sector_list).difference(set(mapping_category_list))
print(sorted(e))

# %%
'''
Since 'adaptive equipment', 'biotechnology and semiconductor', 'enterprise hardware', 'greentech', 'natural gas uses', 'rapidly expanding' categories in master_frame are missing in the mapping file, I will be adding these to Blanks category of main sector for conducting Sector Analysis.
'''

# %%
'''
#### The Sector dictionary would have a mapping of main_sector and primary_sector
'''

# %%
sector_dict = { 'Automotive & Sports' : [],
                'Blanks' : [],
                'Cleantech / Semiconductors' : [],
                'Entertainment' : [],
                'Health' : [],
                'Manufacturing' : [],
                'News, Search and Messaging' : [],
                'Others' : [],
                'Social, Finance, Analytics, Advertising' : []
              }

# %%
sector_dict["Blanks"].append('adaptive equipment')
sector_dict["Blanks"].append('biotechnology and semiconductor') 
sector_dict["Blanks"].append('greentech')
sector_dict["Blanks"].append('enterprise hardware')
sector_dict["Blanks"].append('natural gas uses')
sector_dict["Blanks"].append('rapidly expanding')

# %%
sector_dict

# %%
'''
#### Building the sector dictionary now..
'''

# %%
'''
Algorithm :
for each row in mapping_df:
    for each column in the row:
        if column == 1
            sector_dict[column].append(row)
'''

# %%
for row_index in mapping_df.index:
    for col in mapping_df:
        if mapping_df[col][row_index]==1:
            sector_dict[col].append(mapping_df["category_list"][row_index])

# %%
# The sector dictionary has been populated

sector_dict

# %%
'''
Now this dictionary contains main_sectors as the key and a list of corresponding sub_categories as the value.

The idea is to create a "primary sector" and "main_sector" mapping - in a column1 (primary sector) and column2 (main sector) structure - would be then converting it to a dataframe and then merging with master_frame
'''

# %%
'''
Algorithm :
for each row in master_frame:
    extract the column value of primary_sector
    for key, values in sector_dict.values:
        if primary_sector in values_list
            master_frame["main_sector"][row] = key
'''

# %%
# Building the primary_sector (key) and main_sector (value) dictionary

primary_to_main_dict = {}

# %%
for row_index in master_frame.index:
    primary_s = master_frame["primary_sector"][row_index]
    for key , value in sector_dict.items():
        if primary_s in value:
            primary_to_main_dict[primary_s] = key

# %%
print(primary_to_main_dict)

# %%
# Converting the primary_Sector and main_sector dictionary to a dataframe so it can be marged with master_frame

primary_to_main_df = pd.DataFrame(list(primary_to_main_dict.items()), columns = ['primary_sector','main_sector'])

# %%
primary_to_main_df.head()

# %%
master_frame.head()

# %%
# Merge the two data frames
master_frame = pd.merge(master_frame, primary_to_main_df, how="inner", on="primary_sector")
master_frame.shape

# %%
# Calculating occurences of "Blanks" category in the master_frame
master_frame.loc[master_frame["main_sector"]=="Blanks",:].shape

# %%
# Removing "Blanks" category from the master_frame
master_frame = master_frame.loc[master_frame["main_sector"]!="Blanks",:]
master_frame.shape

# %%
# The output of Sector Analysis 1
master_frame.head()

# %%
'''
# Sector Analysis 2
'''

# %%
'''
According to country Analysis :
'''

# %%
'''
Country 1 - USA, Country 2 - GBR, Country 3 - IND
'''

# %%
master_frame["funding_round_type"].describe()

# %%
'''
While performing Funding Type Analysis, it was determined that "venture" is the only suitable FT and hence other FTs were removed from the dataframe. Thus there will not be a need for putting condition on founding_round_type.
'''

# %%
D1 = master_frame.loc[ (master_frame["country_code"]=="USA") & (master_frame["raised_amount_usd"] >= 5000000) & (master_frame["raised_amount_usd"] <= 15000000) ,:]
D1.head()

# %%
# Finding total number of investments for country D1 - equal to number of rows
# I have not considered multiple investments in same company as a single investment
D1.shape

# %%
D1["raised_amount_usd"].sum()

# %%
D2 = master_frame.loc[ (master_frame["country_code"]=="GBR") & (master_frame["raised_amount_usd"] >= 5000000) & (master_frame["raised_amount_usd"] <= 15000000) ,:]
D2.head()

# %%
# Finding total number of investments for country D2 - equal to number of rows
D2.shape

# %%
D2["raised_amount_usd"].sum()

# %%
# Finding total number of investments for country D3 - equal to number of rows
D3 = master_frame.loc[ (master_frame["country_code"]=="CAN") & (master_frame["raised_amount_usd"] >= 5000000) & (master_frame["raised_amount_usd"] <= 15000000) ,:]
D3.head()

# %%
D3.shape

# %%
D3["raised_amount_usd"].sum()

# %%
'''
### Sector wise Calculations for D1 ( USA )
'''

# %%
D1.pivot_table(values = 'raised_amount_usd', index = 'main_sector', aggfunc = ['sum','count'])

# %%
'''
##### Company that received the highest investment for Other Sector (top sector of USA) :
'''

# %%
D1.loc[D1["main_sector"]=="Others",:].pivot_table(values = 'raised_amount_usd', index = 'permalink', aggfunc = ['count']).sort_values(('count','raised_amount_usd'), ascending=False).head()

# %%
'''
##### Company that received the highest investment for Social, Finance, Analytics, Advertising Sector (second best sector of USA) :
'''

# %%
D1.loc[D1["main_sector"]=="Social, Finance, Analytics, Advertising",:].pivot_table(values = 'raised_amount_usd', index = 'permalink', aggfunc = ['count']).sort_values(('count','raised_amount_usd'), ascending=False).head()

# %%
'''
## Sector wise Calculations for D2 ( GBR )
'''

# %%
D2.pivot_table(values = 'raised_amount_usd', index = 'main_sector', aggfunc = ['sum','count'])

# %%
'''
##### Company that received the highest investment for Other Sector (top sector of GBR) :
'''

# %%
D2.loc[D2["main_sector"]=="Others",:].pivot_table(values = 'raised_amount_usd', index = 'permalink', aggfunc = ['count']).sort_values(('count','raised_amount_usd'), ascending=False).head()

# %%
'''
##### Company that received the highest investment for Social, Finance, Analytics, Advertising (2nd Best sector of GBR) :
'''

# %%
D2.loc[D2["main_sector"]=="Social, Finance, Analytics, Advertising",:].pivot_table(values = 'raised_amount_usd', index = 'permalink', aggfunc = ['count']).sort_values(('count','raised_amount_usd'), ascending=False).head()

# %%
'''
## Sector wise Calculations for D3 ( IND )
'''

# %%
D3.pivot_table(values = 'raised_amount_usd', index = 'main_sector', aggfunc = ['sum','count'])

# %%
'''
##### Company that received the highest investment for Cleantech / Semiconductors Sector (top sector of IND) :
'''

# %%
D3.loc[D3["main_sector"]=="Cleantech / Semiconductors",:].pivot_table(values = 'raised_amount_usd', index = 'permalink', aggfunc = ['count']).sort_values(('count','raised_amount_usd'), ascending=False).head()


# %%
'''
##### Company that received the highest investment for Others Sector (2nd best sector of IND) :
'''

# %%
D3.loc[D3["main_sector"]=="Others",:].pivot_table(values = 'raised_amount_usd', index = 'permalink', aggfunc = ['count']).sort_values(('count','raised_amount_usd'), ascending=False).head()

# %%
'''
# Plotting
'''

# %%
'''
### Plotting Graph 1
'''

# %%
# Plotting graph 1 - The dataframe to be used is plot1_df - 

plot1_df.head()

# %%
# Checking column values for funding_round_type

print(set(list(plot1_df["funding_round_type"])))

# %%
# Removing "angel" type - as per instructions

plot1_df = plot1_df.loc[ plot1_df["funding_round_type"]!="angel" , : ]

# %%
# Checking column values for funding_round_type

print(set(list(plot1_df["funding_round_type"])))

# %%
# Selecting only the relevant columns for plotting graph 1

plot1_df = plot1_df.loc[ : , ['permalink','funding_round_type','raised_amount_usd']]
plot1_df.head()

# %%
plot1_df.shape

# %%
# Imputting values of raised_amount_usd as per the median value of corresponding funding_type

# Segregating data as per funding type

plot1_venture = plot1_df.loc[ plot1_df["funding_round_type"]=="venture" , : ]

plot1_seed = plot1_df.loc[ plot1_df["funding_round_type"]=="seed" , : ]

plot1_private_equity = plot1_df.loc[ plot1_df["funding_round_type"]=="private_equity" , : ]

# %%
'''
Understanding Venture type data :
'''

# %%
plot1_venture.shape

# %%
plot1_venture.describe()

# %%
# Checking if missing values exist
round(100*(plot1_venture.isnull().sum()/len(plot1_venture.index)),2)

# %%
# Calculating median value to impute with
plot1_venture.raised_amount_usd.median()

# %%
# Imputting the missing values of raised_amount_usd with median of venture_type

plot1_venture.loc[np.isnan(plot1_venture["raised_amount_usd"]), ["raised_amount_usd"]] = 5000000.0
round(100*(plot1_venture.isnull().sum()/len(plot1_venture.index)),2)

# %%
# Removing Outliers - 

first_percentile_venture = plot1_venture["raised_amount_usd"].quantile([.01,.99])[.01]
ninety_nine_percentile_venture = plot1_venture["raised_amount_usd"].quantile([.01,.99])[.99]

# %%
first_percentile_venture

# %%
ninety_nine_percentile_venture

# %%
plot1_venture = plot1_venture.loc[ (plot1_venture["raised_amount_usd"] >= first_percentile_venture) & (plot1_venture["raised_amount_usd"] <= ninety_nine_percentile_venture) , :]


# %%
# Checking the data again - to confirm that outliers have been removed 

plot1_venture.describe()

# %%
'''
Understanding Seed type data :
'''

# %%
plot1_seed.shape

# %%
# Checking if missing values exist
round(100*(plot1_seed.isnull().sum()/len(plot1_seed.index)),2)

# %%
# Calculating median value to impute with
plot1_seed.raised_amount_usd.median()

# %%
# Imputting the missing values of raised_amount_usd with median of seed_type

plot1_seed.loc[np.isnan(plot1_seed["raised_amount_usd"]), ["raised_amount_usd"]] = 300000.0
round(100*(plot1_seed.isnull().sum()/len(plot1_seed.index)),2)

# %%
plot1_seed.describe()

# %%
# Removing Outliers - 

first_percentile_seed = plot1_seed["raised_amount_usd"].quantile([.01,.99])[.01]
ninety_nine_percentile_seed = plot1_seed["raised_amount_usd"].quantile([.01,.99])[.99]


# %%
plot1_seed = plot1_seed.loc[ (plot1_seed["raised_amount_usd"] >= first_percentile_seed) & (plot1_seed["raised_amount_usd"] <= ninety_nine_percentile_seed) , :]


# %%
plot1_seed.describe()

# %%
'''
Understanding private_equity type data :
'''

# %%
plot1_private_equity.shape

# %%
round(100*(plot1_private_equity.isnull().sum()/len(plot1_private_equity.index)),2)

# %%
plot1_private_equity.raised_amount_usd.median()

# %%
# Imputting the missing values of raised_amount_usd with median of private_equity

plot1_private_equity.loc[np.isnan(plot1_private_equity["raised_amount_usd"]), ["raised_amount_usd"]] = 20000000.0
round(100*(plot1_venture.isnull().sum()/len(plot1_venture.index)),2)

# %%
plot1_private_equity.describe()

# %%
# Removing Outliers - 

first_percentile_private_equity = plot1_private_equity["raised_amount_usd"].quantile([.01,.99])[.01]
ninety_nine_percentile_private_equity = plot1_private_equity["raised_amount_usd"].quantile([.01,.99])[.99]

# %%
plot1_private_equity = plot1_private_equity.loc[ (plot1_private_equity["raised_amount_usd"] >= first_percentile_private_equity) & (plot1_private_equity["raised_amount_usd"] <= ninety_nine_percentile_private_equity) , :]


# %%
plot1_private_equity.describe()

# %%
'''
##### Having cleaned the data separately for each funding type, now I will merge the 3 different dataframes to get a consolidated dataframe which will be used for plotting
'''

# %%
plot1_df = pd.concat([plot1_venture,plot1_seed, plot1_private_equity], axis = 0)

# %%
plot1_df.shape

# %%
total_amount_invested = plot1_df.raised_amount_usd.sum()
total_amount_invested

# %%
sum_venture = plot1_venture.raised_amount_usd.sum()
percent_venture = sum_venture/total_amount_invested*100
percent_venture = round(percent_venture,2)
percent_venture

# %%
sum_seed = plot1_seed.raised_amount_usd.sum()
percent_seed = sum_seed/total_amount_invested*100
percent_seed = round(percent_seed,2)
percent_seed

# %%
sum_private_equity = plot1_private_equity.raised_amount_usd.sum()
percent_private_equity = sum_private_equity/total_amount_invested*100
percent_private_equity = round(percent_private_equity,2)
percent_private_equity

# %%
median_venture = plot1_venture.raised_amount_usd.median()
median_seed = plot1_seed.raised_amount_usd.median()
median_private_equity = plot1_private_equity.raised_amount_usd.median()

# %%
data_plot = [["venture",percent_venture,median_venture], ["seed",percent_seed,median_seed], ["private_equity",percent_private_equity,median_private_equity]]


# %%
data_plot

# %%
plot1_final = pd.DataFrame(data_plot, columns = ["funding_type","percent","average_amount"])
plot1_final

# %%
import matplotlib.pyplot as plt

# %%
list(plot1_final["funding_type"])

# %%
list(plot1_final["percent"])

# %%
fig = plt.figure()
ax = fig.add_axes([0,0,1,1])
ax.axis('equal')
explode = (0.1, 0, 0)  
ax.pie(list(plot1_final["percent"]), labels = list(plot1_final["funding_type"]),autopct='%1.2f%%', explode = explode)
plt.title("Sector wise Investment distribution", bbox={'facecolor':'0.8', 'pad':5})
plt.show()

# %%
fig = plt.figure()
ax = fig.add_axes([0,0,1,1])
y_axis_data = [x/1000000 for x in list(plot1_final["average_amount"])]
ax.bar( list(plot1_final["funding_type"]) , y_axis_data )
ax.set_xlabel('Funding Types')
ax.set_ylabel('Average Investment Amount (in millions)')
ax.set_title('Average Investment Amount per Sector')
plt.show()

# %%
# Create a figure having 4 subplots

fig, axs = plt.subplots(2, 2, figsize=(16,15))

# subplot 1
explode = (0.1, 0, 0)  
axs[0, 0].pie(list(plot1_final["percent"]), labels = list(plot1_final["funding_type"]),autopct='%1.2f%%', explode = explode)
axs[0, 0].set_title("Funding Type wise Investment distribution", bbox={'facecolor':'0.8', 'pad':5})

# subplot 2  
y_axis_data = [x/1000000 for x in list(plot1_final["average_amount"])]
axs[0, 1].bar( list(plot1_final["funding_type"]) , y_axis_data )
axs[0, 1].set_xlabel('Funding Types')
axs[0, 1].set_ylabel('Average Investment Amount (in millions)')
axs[0, 1].set_title("Funding Type Average Investment Amount ", bbox={'facecolor':'0.8', 'pad':5})

fig.delaxes(axs[1,0])
fig.delaxes(axs[1,1])
fig.savefig("Investment_Analysis_Plot1_Harshit_Mehta.png")

# %%
'''
### Plotting Graph 2
'''

# %%
# Filtering out non-english speaking countries from top 9 countries
plot2_df = pd.merge(master_frame_by_country_code_df[0:30], english_speaking, how="inner", on="country_code")
plot2_df

# %%
fig = plt.figure()
ax = fig.add_axes([0,0,1,1])
y_axis_data = [x/1000000000 for x in list(plot2_df["raised_amount_usd"])]
ax.bar( list(plot2_df["country_code"]) , y_axis_data )
ax.set_xlabel('Country')
ax.set_ylabel('Total Investment Amount (in billions)')
ax.set_title('Country wise Investment Break Up')
plt.show()
fig.savefig("Investment_Analysis_Plot2_Harshit_Mehta.png")

# %%
'''
## Plotting Graph 3
'''

# %%
D1

# %%
# Preparing data from graph 1 of plot 3 - USA (D1)
plot3_D1 = D1.pivot_table(values = 'raised_amount_usd', index = 'main_sector', aggfunc = ['count']).sort_values(('count','raised_amount_usd'), ascending=False)
plot3_D1

# %%
# Selecting top 3 Sectors
plot3_D1.columns = ['count']
plot3_D1 = plot3_D1.loc[[True,True,True],:]
plot3_D1

# %%
# Extracting the index for plotting
plot3_D1 = plot3_D1.reset_index()
plot3_D1

# %%
fig = plt.figure()
ax = fig.add_axes([0,0,1,1])
ax.axis('equal')
explode = (0.1, 0, 0)  
ax.pie(list(plot3_D1["count"]), labels = list(plot3_D1["main_sector"]),autopct='%1.2f%%', explode = explode)
plt.title("Sector wise Investment distribution for USA (D1) ", bbox={'facecolor':'0.8', 'pad':5})
plt.show()

# %%
# Preparing data from graph 2 of plot 3 - GBR (D2)
plot3_D2 = D2.pivot_table(values = 'raised_amount_usd', index = 'main_sector', aggfunc = ['count']).sort_values(('count','raised_amount_usd'), ascending=False)
plot3_D2

# %%
# Selecting top 3 Sectors
plot3_D2.columns = ['count']
plot3_D2 = plot3_D2.loc[[True,True,True],:]
plot3_D2

# %%
# Extracting the index for plotting
plot3_D2 = plot3_D2.reset_index()
plot3_D2

# %%
fig = plt.figure()
ax = fig.add_axes([0,0,1,1])
ax.axis('equal')
explode = (0.1, 0, 0)  
ax.pie(list(plot3_D2["count"]), labels = list(plot3_D2["main_sector"]),autopct='%1.2f%%', explode = explode)
plt.title("Sector wise Investment distribution for GBR (D2) ", bbox={'facecolor':'0.8', 'pad':5})
plt.show()

# %%
# Preparing data from graph 3 of plot 3 - IND (D3)
plot3_D3 = D3.pivot_table(values = 'raised_amount_usd', index = 'main_sector', aggfunc = ['count']).sort_values(('count','raised_amount_usd'), ascending=False)
plot3_D3

# %%
# Selecting top 3 Sectors
plot3_D3.columns = ['count']
plot3_D3 = plot3_D3.loc[[True,True,True],:]
plot3_D3

# %%
# Extracting the index for plotting
plot3_D3 = plot3_D3.reset_index()
plot3_D3

# %%
fig = plt.figure()
ax = fig.add_axes([0,0,1,1])
ax.axis('equal')
explode = (0.1, 0, 0)  
ax.pie(list(plot3_D3["count"]), labels = list(plot3_D3["main_sector"]),autopct='%1.2f%%', explode = explode)
plt.title("Sector wise Investment distribution for IND (D3) ", bbox={'facecolor':'0.8', 'pad':5})
plt.show()

# %%
# Create a figure having 3 subplots

fig, axs = plt.subplots(2, 2, figsize=(20,15))

# subplot 1
explode = (0.1, 0, 0)  
axs[0, 0].pie(list(plot3_D1["count"]), labels = list(plot3_D1["main_sector"]),autopct='%1.2f%%', explode = explode)
axs[0, 0].set_title("Sector wise Investment distribution for USA (D1) ", bbox={'facecolor':'0.8', 'pad':5})

# subplot 2 
explode = (0.1, 0, 0)  
axs[0, 1].pie(list(plot3_D2["count"]), labels = list(plot3_D2["main_sector"]),autopct='%1.2f%%', explode = explode)
axs[0, 1].set_title("Sector wise Investment distribution for GBR (D2) ", bbox={'facecolor':'0.8', 'pad':5})

# subplot 3
explode = (0.1, 0, 0)  
axs[1, 0].pie(list(plot3_D3["count"]), labels = list(plot3_D3["main_sector"]),autopct='%1.2f%%', explode = explode)
axs[1, 0].set_title("Sector wise Investment distribution for IND (D3) ", bbox={'facecolor':'0.8', 'pad':5})

fig.delaxes(axs[1,1])
fig.savefig("Investment_Analysis_Plot3_Harshit_Mehta.png")