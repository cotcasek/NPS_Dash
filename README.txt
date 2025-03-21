Dashboard of National Park Service informational data for public exploration 

This dashboard was created as a final project for a data visualization course at the University of Oregon.

Author: Clare Otcasek
Published: 3/20/2025


********************* Data ***************************************

annual_visits.csv
 - annual park attendance 2005 to 2024

monthly_visits.csv
 - attendance by park by month 2005 to 2024

npFeatures.csv
 - activities and amenities by park

park_info.csv
 - assorted stats and facts 

park_scatter.csv 
 - A duplicate of park_info with added text column "Region".  I was completing this project very near the deadline and did not want to overwrite park_info and introduce a bug.

spatial
- folder containing shapefile and geojson of park boundary polygons 


********************* Sources *************************************
nps.gov

irma.nps.gov

wikipedia for date established "National Park System Areas Listed in Chronological Order of Date Authorized under DOI" (PDF). National Park Service. June 27, 2005. Archived from the original on March 11, 2012. Retrieved January 18, 2010.
https://web.archive.org/web/20120311003821/http://home.nps.gov/applications/budget2/documents/chronop.pdf





********************** Data integrity ******************************
There were some discrepancies in the 4-letter park codes between different datasets code_miss[0] is the code that was replaced with code_miss[1].
code_dict = [ 'ARPA':'ARCH', #Arches
		'NESE':'NERI', #New River Gorge
		'WICA':'WIND', #Wind Cave
		'SEKI':'SEQU', #splitting Sequoia/Kings Canyon
		'SEKI':'KICA'] #splitting Sequoia/Kings Canyon

Sequoia and Kings Canyon National Parks were sometimes represented as a pair and sometimes as two parks.  In cases where data was split additional research was completed to verify data splits. [need source] 
