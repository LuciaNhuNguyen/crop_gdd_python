import pandas as pd
import numpy as np

df = pd.read_csv("weather.csv") #Turn a CSV into a DataFrame

print(df)

df.info()

#1.	Extract latitude and longitude values from the first column Loc_ID
#Method 1st:
df['latitude']= df['Loc_ID'].map(lambda x: x.split('_')[0]) 
df['longitude'] = df['Loc_ID'].map(lambda x: x.split('_')[1])

#Method 2nd:
df[['latitude', 'longitude', 'plantingDate']] = df['Loc_ID'].str.split(
    '_', expand=True)
del df['plantingDate']

print(df['latitude'])
print(df['longitude'])

#2.	Calculate daily GDD values for crop winter wheat 
"""
Corn growing degree days (GDD) are calculated by subtracting the plant's lower 
base or threshold temperature of 30°C) from the average daily air temperature 
in °C. 

Average daily air temperature is calculated by averaging the daily maximum and 
minimum air temperatures measured in any 24-hour period.

If the daily Max Temperature > 30°C, it's set equal to 30°C

The Daily Average Temp (°C) = (Daily Max Temp °C + Daily Min Temp °C) / 2

Daily Corn GDD (°C) = Daily Average Temperature °F - 30°C

Reference: NDAWN. NDAWN Corn Growing Degree Days Information - 
North Dakota State University. [online] NDAWN. 
Available at https://www.ndawn.ndsu.nodak.edu/help-corn-growing-degree-days.html 
[Accessed 19 August. 2022].
"""

def gdd(x, var1, var2, var3):
    if x[var2] > 30 :
       x[var3] = 30 
    else:
        x[var3] = (x[var1]+x[var2])/2 - 0
    return x    
df = df.apply(lambda x: gdd(x, 'minimum temperature' , 'maximum temperature' , 
    'GDD'), axis=1)
print(df['GDD'])

#3.	Sum up daily GDD values to generate accumulated GDD values on daily basis
"""
The Accumulated Corn GDD is the sum of all daily GDD that have occurred from 
the day after your specified planting date until the indicated date. 
Reference: NDAWN. NDAWN Corn Growing Degree Days Information - 
North Dakota State University. [online] NDAWN. 
Available at https://www.ndawn.ndsu.nodak.edu/help-corn-growing-degree-days.html 
[Accessed 19 August. 2022].
"""

df['accmulated GDD'] = df['GDD'].cumsum()
print(df['accmulated GDD'])

#4.	Calculate day length values for each day using the latitude, longitude and day of the year
"""
Parameters :
    dayOfYear : int
        The day of the year. 1 corresponds to 1st of January and 365 to 
        31st December (on a non-leap year).
    lat : float
        Latitude of the location in degrees. Positive values for north 
        and negative for south.
Returns :
    d : float
        Daylength in hours.
"""

#Calculate the day of year
import datetime
df['date'] = pd.to_datetime(df['date']) #Convert String Object to Date in DataFrame
dayofyear = df['date'].dt.dayofyear
lat = df['latitude'].astype(float) #Convert String Object to Date in DataFrame
df.info()

"""
Computes the length of the day (the time between sunrise and sunset) 
given the day of the year and latitude of the location.

Function uses the Brock model for the computations.

Reference: 
1. Antti Lipponen. (2016). Python function to compute the length of the day 
given day of the year and latitude. [online] Gist.
Available at https://gist.github.com/anttilipp/ed3ab35258c7636d87de6499475301ce 
[Accessed 19 August. 2022].
2. Forsythe, W. C., Rykiel Jr, E. J., Stahl, R. S., Wu, H. I., & Schoolfield, 
R. M. (1995). A model comparison for daylength as a function of latitude and 
day of year. Ecological Modelling, 80(1), 87-95.
"""

def daylength(dayOfYear, lat):
    latInRad = np.deg2rad(lat)
    declinationOfEarth = 23.45*np.sin(np.deg2rad(360.0*(283.0+dayOfYear)/365.0))
    if -np.tan(latInRad) * np.tan(np.deg2rad(declinationOfEarth)) <= -1.0:
        return 24.0
    elif -np.tan(latInRad) * np.tan(np.deg2rad(declinationOfEarth)) >= 1.0:
        return 0.0
    else:
        hourAngle = np.rad2deg(np.arccos(-np.tan(latInRad) * np.tan(np.deg2rad(declinationOfEarth))))
        return 2.0*hourAngle/15.0

vec_daylength = np.vectorize(daylength) #np.vectorize is to transform functions which are not numpy-aware (e.g. take floats as input and return floats as output) into functions that can operate on (and return) numpy arrays.
arr_daylength = np.array(vec_daylength(dayofyear, lat)).round(decimals=3) #Convert np.vectorize (arraylist) to np.array, apply function 'daylength',round array elements
df['daylength'] = pd.DataFrame(arr_daylength) #Convert a multidimensional array to a known column in the dataframe
print(df['daylength'])
print(df)

df.to_csv("weatherpython.csv") #Python Write CSV File
