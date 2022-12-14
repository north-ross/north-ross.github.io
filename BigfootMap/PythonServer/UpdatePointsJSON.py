"""
Converting the most recent KML from BFRO.net into a geoJSON and publishing to Github Pages.
This script is scheduled to be run weekly on my PC. 

To do: TESTING especially coordinate handling
Fix BadPoints.csv not writing certain coordinates
Move CSV reading to its own function to be called later

Low priority:
Fix escape character backslash displaying on popup (ie report 637)



author: North Ross
created: 2022-10-16
python version: 3.10.7
"""
#%%
import requests
import json
import xml.etree.ElementTree as ET
import re
from shapely.geometry import Polygon
from pyproj import Geod
from zipfile import ZipFile
from io import BytesIO
import csv
import subprocess
import os
from win10toast import ToastNotifier

#%%
# Build XML parser:
def parseXML(xmlfile):
  
    # create element tree object
    tree = ET.parse(xmlfile)
  
    # get root element
    root = tree.getroot()
  
    # create empty dict for features
    features = {}
    validPt=False
    validPoly=False
    badPolys = []
    count=0
    polyMissingPtList = []

    # Build geoJSON dictionary skeleton:
    features["type"]= "FeatureCollection"
    features["features"]=[]
  
    # iterate items to find Placemark type categories
    for item in root.findall('.//Placemark'):
        validPt=False
        point={}
        point["type"]= "Feature"
        geometry={}
        geometry["type"]="Point" # Define structure for geoJSON
        properties = {}

        # iterate child elements of item
        for child in item:
            
            # Find description tag and cast entire contents to string to find reportid, unique ID to use as dict key. (<name> tag is not unique)
            # todo: replace these with regex?
            if child.tag == 'description':
                popup = str(ET.tostring(child)) # return entire <description> tag as a string, this will be the popup when displayed in leaflet
                reportid = popup[popup.find('Report ') + 7:popup.find(': ')] # return unique report ID
                classification = popup[popup.find(">Class ")+1 : popup.find(">Class ")+8] # Return report BFRO class (class A, B or C)
                popup = popup.replace('\\n','').replace('\t', ' ').strip()[2:-1]
                title = popup[popup.find("Report ") : popup.find("</b><br")] # return title tag
                
                
                properties["id"]=count
                properties["name"]= reportid
                properties["class"]=classification
                properties["title"]=title.strip().replace('\\n','').replace('\t', ' ')
                validPt=True # Only points are given a description tag, so this only keeps points
            elif validPt and child.tag=='LookAt': # Adding spatial info
                for ele in child:
                    if ele.tag=='longitude':
                        lon=float(ele.text.strip())
                    elif ele.tag=='latitude':
                        lat=float(ele.text.strip())
                geometry["coordinates"]=[lon, lat]
                point["geometry"]=geometry
                point["properties"]=properties
                features["features"].append(point)
                validPt=False
                count+=1
            
            # Convert "location boundaries" polygon into radius and add as a property to matching id
            if child.tag == 'name' and "Location Boundaries for" in str(ET.tostring(child)):
                
                validPoly = True
                polyNumList = re.findall('[0-9]+', str(ET.tostring(child)).strip())
                polyReportID = polyNumList[0]

            elif validPoly and child.tag == 'Polygon':

                coords = child.find("./outerBoundaryIs/LinearRing/coordinates")
                coordsStr = coords.text.replace(" ", "")[:-2]
                coordsList = coordsStr.split("\n")

                for i, coords in enumerate(coordsList):
                    try:
                        coordsList[i] = [float(x) for x in coords.split(',')]
                    except:
                        validPoly = False
                        # print(f"BAD coords in {polyReportID}")
                        badPolys.append(polyReportID)

                        break
                #calculate area, then get radius of circle with this area.
                if validPoly: # check coords are good
                    
                    geod = Geod(ellps="WGS84")
                    poly = Polygon(coordsList)
                    area = abs(geod.geometry_area_perimeter(poly)[0])


                    radius = round((area/3.1416)**0.5)
                    if features['features'][-1]['properties']['name'] == polyReportID:
                        features['features'][-1]['properties']['errorRadius'] = radius
                    else: 
                        print("couldn't find point for report {polyReportID}")
                        polyMissingPtList.append({polyReportID: radius})
      
    # return features dictionary
    print(count, 'points found')
    print(f"{len(badPolys)} bad polygons")
    return features
def BadPointPrint(id, issue):
    print(f"Report #{id} coords invalid because {issue}")
def GitUpload():
    #push changes to github and update github page
    # commit and push to Github:

    gitdir = r"D:\Documents\NorthsWebProjects\north-ross.github.io"

    subprocess.run("git add .", cwd = gitdir)

    commit = subprocess.run('git commit -m "points update python"', cwd = gitdir)

    if commit.returncode == 0:
         subprocess.run("git push origin main", cwd = gitdir)

#%%
def main():
    #%%
    kmlUrl = 'http://www.bfro.net/app/AllReportsKMZ.aspx'
    r = requests.get(kmlUrl)

    filebytes = BytesIO(r.content)
    kmz = ZipFile(filebytes, 'r')
    kml = kmz.open('doc.kml', 'r')

    # Parse KML, return dictionary
    
    # kml = f"D:\Documents\Maps\BigfootMap\BFROReports.kml"
    features = parseXML(kml)

    
    # read csv of suggested changes (collected from google form) and write to nested dict with reportid as key
    # move this to its own function and TEST especially bad coordinate handling.
    
    #%%
    csvUrl = "https://docs.google.com/spreadsheets/d/1mE6If-j1BgB3X0AS3zZlLboPv0_oDoP9g_DptUYmV7o/export?gid=142859818&format=csv"
    correctionsDict = {}
    with requests.Session() as s:
    # with open('test.csv') as testcsv:
        download = s.get(csvUrl)
        decoded_content = download.content.decode('utf-8')
        reader = csv.DictReader(decoded_content.splitlines(), delimiter=',')
        # reader = csv.DictReader(testcsv, delimiter=',')
        BadPointList=[]
        for line in reader:
            if 'Report ID' in line.keys():
                reportid = line.pop('Report ID')
            # try to cast error radius to float:
            radiusNumeric = re.findall('[0-9]+', line['Report area radius'].strip())
            try: 
                floatRadius = float(radiusNumeric)
                if floatRadius < 0:
                    floatRadius = None
            except: 
                floatRadius = None
            # validate coordinates and cast to list of floats:
            line['Issue'] = ""
            badCSVstr = r"D:\Documents\NorthsWebProjects\north-ross.github.io\BigfootMap\PythonServer\BadPoints.csv"
            with open(badCSVstr, 'w') as badCSV:
                badWriter = csv.DictWriter(badCSV, line.keys())
                badWriter.writeheader()
                
                try: 
                    coordsList = line['Updated Coordinates'].split(',')
                    coordsList = [ float(x.strip()) for x in coordsList ]
                    # check if coordinates are generally located in north america:
                    if not 17.0 < float(coordsList[0]) < 84.0 or not -202 < float(coordsList[1]) < -41.37:
                        # TO ADD - try checking if the user just forgot to add a - for the longitude
                        # also try removing non numeric/math chars with regex
                        line['Issue'] = "Coordinates out of range"
                        BadPointPrint(reportid, line['Issue'])
                        BadPointList.append(reportid)
                        badWriter.writerow(line)
                        print(line)
                    else: 
                        # add line to dict
                        line['Updated Coordinates'] = coordsList[::-1]
                        correctionsDict[reportid] = line
                except: 
                    line['Issue'] = 'Invalid Coords'
                    BadPointPrint(reportid, line['Issue'])
                    BadPointList.append(reportid)
                    badWriter.writerow(line) # not working....
                    print(line)


            
    updateCount = 0
    print("\n\n")
    for feature in features['features']:
        featureID = feature['properties']['name']
        if  featureID in correctionsDict.keys():
            print(f"replacing report {featureID} coords from {feature['geometry']['coordinates']} ", end="")
            feature['geometry']['coordinates'] = correctionsDict[featureID]['Updated Coordinates']
            print(f"to {correctionsDict[featureID]['Updated Coordinates']}")
            feature['properties']['correctedTime'] = correctionsDict[featureID]['Timestamp'].split(' ')[0]
            if 'Your Name (optional)' in correctionsDict[featureID].keys():
                feature['properties']['correctedBy'] = correctionsDict[featureID]['Your Name (optional)']
            if floatRadius != None:
                feature['properties']['errorRadius'] = floatRadius
            updateCount += 1
    print(f"{updateCount} points updated from user submissions")
    #%%
    # Update coordinates in JSON:
    jsonfile = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'BFRO_Points.json'))
    with open(jsonfile, 'w') as pointsjson:
        output = json.dumps(features)
        pointsjson.write(output)
    
    #%%
    
    GitUpload()

    if len(BadPointList) != 0:
        n = ToastNotifier()
        n.show_toast("BFRO Points Updater", f"{len(BadPointList)} bad points were found in google sheet. Review BadPointCSV.")
#%%

if __name__ == "__main__":
    main()
  
# %%
