#MergeBeetleData.py

#Import modules
import sys, os, glob
import pandas as pd

#Set the base folder (containing field and pinning csv files
baseFolder = '../Data/BeetleData'

#Set the output filename
outFN = baseFolder + os.sep + "BeetleData.csv"

#Create lists of field and pinning csv files (downloaded from GetBeetleData.py)
fldFiles = glob.glob(baseFolder + os.sep + '*fielddata.csv')
idFiles = glob.glob(baseFolder + os.sep + '*IDandpinning.csv')

#Merge field csvs and write out to a single data frame
print "Reading in field csv files"
dfField = pd.read_csv(fldFiles[0])                   
for file in fldFiles[1:]: 
    df = pd.read_csv(file)
    dfField = dfField.append(df)

#Merge pinning csvs, using only first 15 columns, and write to single data frame
print "Reading in IDandpinning csv files"
dfPinning = pd.read_csv(idFiles[0], usecols=range(15))
for file in idFiles[1:]: 
    df = pd.read_csv(file, usecols=range(15))
    dfPinning = dfPinning.append(df)

#Group the field data into a table of plot attributes (combining trapIDs)
print "Grouping raw field data to plot level attributes"
groupPlots = dfField.groupby('plotID')
dfPlots = groupPlots.agg({'nlcdClass':'first',
                          'decimalLatitude':'mean',
                          'decimalLongitude':'mean',
                          'elevation':'mean'})

#Group the field data again, but this time sum the days of trapping as
#  indication of effort for a given date
print "Computing sampling effort for each plot-date combination"
pivotEffort = dfField.pivot_table(values = 'daysOfTrapping',
                                  index=('siteID','plotID','setDate'),
                                  aggfunc="sum",
                                  fill_value=0)
dfEffort = pd.DataFrame(pivotEffort) #Convert to data frame

#Join the static plot attributes to each plot/date/effort
print "Joining plot attributes to effort"
dfPlotData = pd.merge(dfPlots,dfEffort,how='right',left_index=True,right_index=True)

#Pivot the pinning data so each species is a column with a tally of trap occurrence
pivotPinning = dfPinning.pivot_table(columns='scientificName',
                              values='taxonID',
                              index=('siteID','plotID','collectDate'),
                              aggfunc="count",
                              fill_value=0)

#Use reset_index to convert siteID and plotID indices to columns 
dfPlotData.reset_index(inplace=True)
pivotPinning.reset_index(inplace=True)

#Create a table listing occurrance tallies of species at each plot-date combination
print "Creating species occurrence tables for each plot-date combination"
dfAll = pd.merge(dfPlotData,pivotPinning,how='right',right_on=['plotID','collectDate'],left_on=['plotID','setDate'])

#Remove reduntant columns
del dfAll['siteID_y']
del dfAll['collectDate']

#Rename columns
dfAll.rename(columns={'siteID_x':'siteID',
                      'setDate':'date',
                      'decimalLongitude':'longitude',
                      'decimalLatitude':'latitude'},inplace=True)

#Rearrange columns
colList = dfAll.columns.tolist()
colList[4],colList[5] = colList[5],colList[4]


#Write result to a csv file
dfAll.to_csv(outFN,columns=colList,index=False)