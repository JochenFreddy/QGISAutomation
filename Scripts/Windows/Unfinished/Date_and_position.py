#Import the requiered modules and set the python path
import pandas as pd
import numpy
import sys
import argparse
from datetime import date
from qgis.core import *
from qgis.utils import iface
from PyQt5 import *
from PyQt5.QtCore import QVariant
from qgis.gui import *

QgsApplication.setPrefixPath('C:/PROGRA~1/QGIS32~1.5/apps/qgis-ltr',True)

qgs = QgsApplication([], False)

qgs.initQgis()

project_path = r'Path\to\project.qgz'

From_mag = ""
Event_Type = "ke"
Sort_by = "date" #M
Order = "Desc" #M
Events = 150
selectdict = {'From_d' : 'date >= ' , 'To_d' : 'date <= ' , 'From_lat' : 'latitude >= ' , 'To_lat' : 'latitude <= ' , 'From_lon' : 'longitude >= ' ,'To_lon' : 'longitude <= ', 'Event_Type' : 'type = ' }
selectlist= [From_d, To_d, From_lat, To_lat, From_lon, To_lon, From_mag, Event_Type]
selectstr= ["From_d", "To_d", "From_lat", "To_lat", "From_lon", "To_lon", "From_mag", "Event_Type"]
#set path to project, layout used for each project needs to be known
# Give the different input values with the name you want to give the map
def Online_database(name,From_d,To_d,From_lat,To_lat,From_lon,To_lon):
    selectlist[0]=From_d
    selectlist[1]= To_d
    selectlist[2]=From_lat
    selectlist[3]=To_lat
    selectlist[4]=From_lon
    selectlist[5]=To_lon
    #open the project
    project = QgsProject.instance()
    project.setFileName(project_path)
    project.read()
    #set the canvas 
    canvas = QgsMapCanvas()
    #use the helper to load in the data
    add_tecto()
    #select the newly added vector layer
    vl = QgsProject.instance().mapLayersByName('Event')[0] 
    # Load a predefined style for your events
    vl.loadNamedStyle(r'Path\to\style.qml')
    vl.triggerRepaint()
    #based on the given limits set the canvas
    p_points = [QgsPointXY(From_lon, From_lat), QgsPointXY(From_lon, To_lat), QgsPointXY(To_lon, To_lat), QgsPointXY(To_lon, From_lat)]
    canvas.setExtent(QgsGeometry.fromPolygonXY([p_points]).boundingBox())
    #Create the query based on the input values
    # get_query is adapted here to ignore empty values
    query_builder = QgsQueryBuilder(vl)
    query_builder.setSql(get_query(get_val()))
    query_builder.accept()
    query_builder.show()

    # Boolean based on if it is descending or ascending
    if Order == "Desc":
        asc = False
    else:
        asc = True

    #Order the features based on the orderparameter, and descending or ascending
    request = QgsFeatureRequest()
    clause = QgsFeatureRequest.OrderByClause(Sort_by, ascending=asc)
    orderby = QgsFeatureRequest.OrderBy([clause])
    request.setOrderBy(orderby)
    feats_point = vl.getFeatures(request)
    i=0
    for feature in feats_point:
        if i>=Events:
            break
        else:
            i +=1
            vl.selectByIds([feature.id()], QgsVectorLayer.AddToSelection)
    # use a predefined layout to make your map, this layout should be in you project so the name should suffice
    manager = QgsProject.instance().layoutManager()
    layout = manager.layoutByName("Quarry_blast") #adapt
    mapItem = layout.itemById("Map 1") #adapt
    mapItem.setExtent(canvas.extent())
    Title = layout.itemById("Title")
    Title.setText(name)

    exporter = QgsLayoutExporter(layout)
    path = "C:\\Path\\To\\Folder\\"
    exporter.exportToPdf(path + 'Constant_string' + str(name) +".pdf", QgsLayoutExporter.PdfExportSettings())
    QgsProject.instance().clear()


# Using the dictionaries and the input values to create a list of all the non-empty query values
def get_val():
    finalquery= []
    for i in range(0, len(selectlist),1):
        if (selectlist[i] == ""):
            continue
        else:
            finalquery.append(selectdict[str(selectstr[i])] + ' ' + str(selectlist[i])) 
    return finalquery

#using the created list in the get_val function the strings for the query are formed
def get_query(query):
    finalquery= ""
    for j in range(0, len(query),1):
      # To make sure the query does not end with AND
        if j==(len(query)-1):
            expression = query[j].split()
            helper=0
            for i in expression:
                if helper ==0:
                    attribute = i
                    helper+=1
                elif helper ==1:
                    expression = i
                    helper+=1
                elif helper ==2:
                    value = i
                    finalquery = finalquery + "\"%s\"%s \'%s\'" % (attribute , expression ,value)
                    helper+=1
        else:
            expression = query[j].split()
            helper=0
            for i in expression:
                if helper ==0:
                    attribute = i
                    helper+=1
                elif helper ==1:
                    expression = i
                    helper+=1
                elif helper ==2:
                    value = i
                    finalquery = finalquery + "\"%s\"%s \'%s\' AND " % (attribute , expression ,value)
                    helper = 0
    return finalquery
# Parse function
def parseArguments():
    #Create arguments parser
    parser = argparse.ArgumentParser()

    #Mandatory arguments
    parser.add_argument("name", help ="the name." , type= str)
    parser.add_argument("Fdate", help ="From date." , type= str)
    parser.add_argument("Tdate", help ="To date." , type= str)
    parser.add_argument("Flat", help ="From latitude." , type= float)
    parser.add_argument("Tlat", help ="To latitude." , type= float)
    parser.add_argument("Flon", help ="From longitude." , type= float)
    parser.add_argument("Tlon", help ="To longitude." , type= float)

    #print version
    parser.add_argument("--version", action="version", version='%(prog)s - Version 1.0')

    # parse arguments
    args = parser.parse_args()
    return args
if __name__ =='__main__':
    #parse the arguments
    args = parseArguments()

    #raw print arhuments
    print("You are running the script with arguments: ")
    for a in args.__dict__:
        print(str(a) + ": " + str(args.__dict__[a]))
    Online_database(args.name, args.Fdate, args.Tdate, args.Flat, args.Tlat, args.Flon, args.Tlon)
 # Call the function here with the input and remove the parse function and __main__ if you want to run multiple script in one go
qgs.exitQgis()
    
