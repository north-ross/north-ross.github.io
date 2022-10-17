"""
Converting the most recent KML from BFRO.net into a geoJSON and uploading to pythonanywhere server.
This script will scheduled to be run daily on pythonanywhere. 


author: North Ross
created: 2022-10-16
python version: 3.10.7
"""

import requests
import json
import xml.etree.ElementTree as ET
from zipfile import ZipFile
from io import BytesIO


# Build XML parser:
def parseXML(xmlfile):
  
    # create element tree object
    tree = ET.parse(xmlfile)
  
    # get root element
    root = tree.getroot()
  
    # create empty dict for features
    features = {}
    valid=False
    count=0

    # Build geoJSON dictionary skeleton:
    features["type"]= "FeatureCollection"
    features["features"]=[]
  
    # iterate items to find Placemark type categories
    for item in root.findall('.//Placemark'):
        valid=False
        point={}
        point["type"]= "Feature"
        geometry={}
        geometry["type"]="Point" # Define structure for geoJSON
        properties = {}

        # iterate child elements of item
        for child in item:
            
            # Find description tag and cast entire contents to string to find reportid, unique ID to use as dict key. (<name> tag is not unique)
            if child.tag == 'description':
                popup = str(ET.tostring(child)) # return entire <description> tag as a string, this will be the popup when displayed in leaflet
                reportid = popup[popup.find('Report ') + 7:popup.find(': ')] # return unique report ID
                classification = popup[popup.find(">Class ")+1 : popup.find(">Class ")+8] # Return report BFRO class (class A, B or C)
                properties["id"]=count
                properties["name"]= reportid
                properties["class"]=classification
                properties["popup"]=popup.replace('\\n','').replace('\t', ' ').strip()[2:-1] # Fix up the popup content a bit so it displays better on Leaflet
                valid=True # Only points are given a description tag, so this only keeps points
            elif valid and child.tag=='LookAt': # Adding spatial info
                for ele in child:
                    if ele.tag=='longitude':
                        lon=float(ele.text.strip())
                    elif ele.tag=='latitude':
                        lat=float(ele.text.strip())
                geometry["coordinates"]=[lon, lat]
                point["geometry"]=geometry
                point["properties"]=properties
                features["features"].append(point)
                valid=False
                count+=1
        
      
    # return features dictionary
    print(count, 'points found')
    return features

def main():

    # # Check if JSON on site is up to date:
    # reqRSS = requests.get('http://www.bfro.net/GDB/NewAdditionsRss.asp')
    # # reqJSON = requests.get('https://www.pythonanywhere.com/user/northross/files/home/northross/BFRO/BFRO_Points.json')
    # reqJSON = requests.get('http://localhost:8000/Documents/NorthsWebProjects/north-ross.github.io/BigfootMap/PythonServer/BFRO_Points.json')
    # RSSstring = str(BytesIO(reqRSS.content).getvalue())
    # JSONstring = str(BytesIO(reqJSON.content).getvalue())

    # lastestRepID = RSSstring[RSSstring.find('(Report ')+8:RSSstring.find(')</title>')]
    # print('Latest report #:', lastestRepID)
    # if lastestRepID in JSONstring:
    #     print('BFRO_Points.json is up to date')
    # else:
    #     print('Updating BFRO_Points.json')

        # Request the most recent KML from BFRO.net
    kmlUrl = 'http://www.bfro.net/app/AllReportsKMZ.aspx'
    r = requests.get(kmlUrl)

    filebytes = BytesIO(r.content)
    kmz = ZipFile(filebytes, 'r')
    kml = kmz.open('doc.kml', 'r')

    # Parse KML, return dictionary
    features = parseXML(kml)

    # Write to JSON:
    with open(r'D:\Documents\NorthsWebProjects\north-ross.github.io\BigfootMap\BFRO_Points.json', 'w') as pointsjson:
    # with open(r'Q:\northross\GIS325\Project\KML_toJSON_web\javascript\test_2020-04-06.json', 'w') as testjson:
        output = json.dumps(features)
        pointsjson.write(output)

    # commit and push to Github:
    from git import Repo
    repodir = r"D:\Documents\NorthsWebProjects\north-ross.github.io"
    repo = Repo(repodir)

    #%%
    #test
    import subprocess
    from datetime import date
    
    subprocess.run(r"cd /d D:\Documents\NorthsWebProjects\north-ross.github.io")
    
    subprocess.run("git add .")

    # commit = subprocess.run(f'git commit -m "points update{date.today()}"', capture_output=True, encoding='UTF-8')
    #######
    # commit
    
    # get results and if there is change then push
    # cmd = "git push"
    # subprocess.call(cmd, shell=True)
#%%
      
if __name__ == "__main__":
    main()
  
