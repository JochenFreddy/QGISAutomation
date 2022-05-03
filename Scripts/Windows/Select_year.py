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

#Give as input the year you want to map, the canvas is preset in the QGIS project and will not change

project_path = r'Path\to\project.qgz' 

def select_year(year):
    canvas = QgsMapCanvas()
    #open the project
    project = QgsProject.instance()
    project.setFileName(project_path)
    project.read()
    manager = QgsProject.instance().layoutManager()
    #use the helper to load in the data
    add_tecto()
    #select the newly added vector layer
    vl = QgsProject.instance().mapLayersByName('Event')[0]
    rename = QgsProject.instance().mapLayersByName('Catalogue')[0]
    query_builder = QgsQueryBuilder(vl)
    #Build string for the query with Starting year and the following year to filter correctly
    query = '"date"' + ">=" + "'" + str(year) +"'" + 'AND' + '"date"' + "<" + "'" + str(year+1) + "'" 
    query_builder.setSql(str(query))
    query_builder.accept()
    query_builder.show()
    # Load a predefined style for your events
    vl.loadNamedStyle(r'Path\to\style.qml')
    vl.triggerRepaint()
    # Change the name of the layer to events in year (The title of the legend is equal to the name of the layer)
    rename.setName('events in ' + str(year))
    # use a predefined layout to make your map, this layout should be in you project so the name should suffice
    layout = manager.layoutByName("Layout_name")
    exporter = QgsLayoutExporter(layout)
    path = "C:\\Path\\To\\Folder\\"
    exporter.exportToPdf(path + 'Constant_string' + str(year)+".pdf", QgsLayoutExporter.PdfExportSettings())
    rename.setName('Merged_earthquake_catalogue')
    QgsProject.instance().clear()
# Parse function
def parseArguments():
    #Create arguments parser
    parser = argparse.ArgumentParser()

    #Mandatory arguments
    parser.add_argument("year", help ="the year." , type= int)
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
    select_year(args.year)
# Call the function here with the input and remove the parse function and __main__ if you want to run multiple script in one go
qgs.exitQgis()
