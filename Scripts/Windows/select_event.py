#Import the requiered modules and set the python path
import pandas as pd
import numpy
import sys
import argparse
from qgis.core import *
from qgis.utils import iface
from PyQt5 import *
from PyQt5.QtCore import QVariant
from qgis.gui import *

QgsApplication.setPrefixPath('C:/PROGRA~1/QGIS32~1.5/apps/qgis-ltr',True)

qgs = QgsApplication([], False)

qgs.initQgis()

project_path = r'Path\to\project.qgz' 
eventdict = {'ke' : '2', 'ki': '2', 'qb':'1', 'sqb':'1', 'cb':'3', 'scb':'3'}

# Selection of event in descending order with the newest being number 1
def select_event(Newest):
    #open the project
    project = QgsProject.instance()
    project.setFileName(project_path)
    project.read()
    canvas = QgsMapCanvas()
    #use the helper to load in the data
    add_tecto()
    # assign all the vectorlayers we want to use to a variable
    vl = QgsProject.instance().mapLayersByName('vectorlayer')[0]
    Mun = QgsProject.instance().mapLayersByName('vectorlayer')[0]
    Prov = QgsProject.instance().mapLayersByName('vectorlayer')[0]
    #load a predefined style
    vl.loadNamedStyle('path to style.qml')
    vl.triggerRepaint()
    # Set groups either to visible or not-visible (findgroup(group_name))
    QgsProject.instance().layerTreeRoot().findGroup('not_visible1').setItemVisibilityChecked(False)
    QgsProject.instance().layerTreeRoot().findGroup('visible').setItemVisibilityChecked(True)
    QgsProject.instance().layerTreeRoot().findGroup('not_visible2').setItemVisibilityChecked(False)
    # Order the Vl vector layer (loaded in by add tecto) by date in descending order
    request = QgsFeatureRequest()
    clause = QgsFeatureRequest.OrderByClause('date', ascending=False)
    orderby = QgsFeatureRequest.OrderBy([clause])
    request.setOrderBy(orderby)
    feats_point = vl.getFeatures(request)
    # Select the features at the "Newest" position
    i=0
    for feature in feats_point:
        if i==Newest:
            vl.selectByIds([feature.id()], QgsVectorLayer.AddToSelection)
            break
        else:
            i +=1
            
    sf = vl.selectedFeatures()
    # Select the first of the selected features
    if len(sf)>0:
        feature = sf[0]
    else:
        print("No selection made")
    #assign variables to the features of the data 
    name = feature['name']
    eventType = feature['type']
    hor = feature['errh']
    mag = feature['ML']   
    date = feature['date']
    time = feature['time']
    jaar, maand, dag = date.split("-",3)
    #get the point geometry from the event and get it's coordinates
    geom = feature.geometry()
    coordinate = geom.asPoint()

    X,Y = coordinate[0], coordinate[1]
    #get the distance in degrees using the reverse haversine formula and create the rectangle geometry 
    height,width = new_distance(X,Y,20,20)
    p_points = [QgsPointXY(X-height, Y-width), QgsPointXY(X-height, Y+width), QgsPointXY(X+height, Y+width), QgsPointXY(X+height, Y-width)]
    # set the canvas extent based on the boundingbox of the created geometry
    canvas.setExtent(QgsGeometry.fromPolygonXY([p_points]).boundingBox()) #setExtent based on the boundingbox
    # Get the date of the municipality and province from the variables
    Munfeat = Mun.getFeatures()
    Provfeat = Prov.getFeatures()
    # If the point is outside of Belgium no province is selected
    for prov in Provfeat:
        if geom.intersects(prov.geometry()):
            Prov.selectByIds([prov.id()], QgsVectorLayer.AddToSelection)
    if (len(Prov.selectedFeatures())!=0):
        ProvName= " ,  " + Prov.selectedFeatures()[0]['Name_2']
    else:
        ProvName = ""
    # If the point is outside of Belgium the name is selected from the event database
    for mun in Munfeat:
        if geom.intersects(mun.geometry()):
            Mun.selectByIds([mun.id()], QgsVectorLayer.AddToSelection)
    if (len(Mun.selectedFeatures())!=0):
        MunName = Mun.selectedFeatures()[0]['Name']
    else:
        MunName = name
    
     # Make the different language texts for all the different snapshots the month function is used to account for the different months
    for j in range(0,4,1):
        NL= dag + ' ' + month(maand, maand_dict) + ' ,  ' + jaar + ' ' + time + ' - ' + MunName + ProvName + ' -  ML ' + str(mag) + '\n' + ' Horizontale onzekerheid ' + str(hor) + ' km'
        FR= dag + ' ' + month(maand, mois_dict) + ' ,  ' + jaar + ' ' + time + ' - ' + MunName + ProvName + ' -  ML ' + str(mag) + '\n' + ' Incertitude horizontale ' + str(hor) + ' km'
        EN= dag + ' ' + month(maand, month_dict) + ' ,  ' + jaar + ' ' + time + ' - ' + MunName + ProvName + ' -  ML ' + str(mag) + '\n' + ' Horizontal uncertainty ' + str(hor) + ' km'
        DE= dag + ' ' + month(maand, monat_dict) + ' ,  ' + jaar + ' ' + time + ' - ' + MunName + ProvName + ' -  ML ' + str(mag) + '\n' + ' Horizontale Unsicherheit ' + str(hor) + ' km'
        language = [NL,FR,EN,DE]
        stijl = ['Event NL','Event FR','Event EN','Event DE']
        # Use the layout for the selected language with a premade legend
        manager = QgsProject.instance().layoutManager()
        layout = manager.layoutByName(stijl[j]) 
        mapItem = layout.itemById("Map 1") 
        # Set the extent of the map canvas of the layout to the current map canvas of the project
        mapItem.setExtent(canvas.extent())
        # Select the legend based on the event type and set to visible
        for i in range(1, 4, 1):
            if str(i) == eventdict[eventType]:
                legendItem = layout.itemById(str(i))
                legendItem.setVisibility(True)
            else:
                legendItem = layout.itemById(str(i))
                legendItem.setVisibility(False)
        # adapt the title based on the language
        title = layout.itemById("titel")
        title.setText(language[j]) 
        # export the map
        exporter = QgsLayoutExporter(layout)
        path = "C:\\Path\\To\\Folder\\"
        exporter.exportToPdf(path + str(stijl[j]) + str(MunName) + '_' + jaar +".pdf", QgsLayoutExporter.PdfExportSettings())
    QgsProject.instance().clear()



#For each language we use a dictionary to show the different months
maand_dict= {"01":"Januari","02":"Februari", "03":"Maart", "04":"April", "05":"Mei", "06":"Juni","07":"Juli","08":"Augustus", "09":"September", "10":"Oktober", "11":"November", "12":"December"}
mois_dict = {"01" : "Janvier", "02" : "Février", "03" : "Mars", "04" : "Avril", "05" : "Mai", "06" : "Juin", "07" : "Juillet", "08" : "Août", "09" : "Septembre", "10" : "Octobre", "11" : "Novembre", "12" : "Décembre"}
month_dict = {"01": "January", "02": "February", "03": "March", "04": "April", "05": "May", "06": "June", "07": "July", "08": "August", "09": "September", "10": "October", "11": "November", "12": "December"}
monat_dict = {"01":"Januar","02":"Februar", "03":"März", "04":"April", "05":"Mai", "06":"Juni","07":"Juli","08":"August", "09":"September", "10":"Oktober", "11":"November", "12":"Dezember"}

# Return the month for the given language
def month(month,x):
    return x[str(month)]
    
# Parse function
def parseArguments():
    #Create arguments parser
    parser = argparse.ArgumentParser()

    #Mandatory arguments
    parser.add_argument("Newest", help ="the Newest." , type= float)
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
    select_event(args.Newest)
# Call the function here with the input and remove the parse function and __main__ if you want to run multiple script in one go
qgs.exitQgis()
