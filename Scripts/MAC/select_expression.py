import pandas as pd
import numpy
from Helpers import *
# set the path to the project
project_path = 'path to project.qgz' 


# Mandatory input values for the following functions are the expression which selects the single feature for which we want to centre the map
# and the name we want to give the map. Optional input values are a query which is used to filter the features and the amount of features included
def select_expression(expression, name, query ="", amount = 50):
    #initiate the project and read it
    project = QgsProject.instance()
    project.setFileName(project_path)
    project.read()
    canvas = iface.mapCanvas()
    # Load in the data
    add_tecto()
    vl = QgsProject.instance().mapLayersByName('Event')[0]
    # set the style of the data
    vl.loadNamedStyle('/Users/jochenvlaeminck/Documents/Stage/Styles/selected_earthquakes_cleared.qml')
    vl.triggerRepaint()
    # Select the features for which the expression is true
    # get_query is a helper function which reformats the expression String to the correct format
    vl.selectByExpression(get_query(expression))
    sf = vl.selectedFeatures()
    # Set groups either to visible or not-visible (findgroup(group_name))
    QgsProject.instance().layerTreeRoot().findGroup('visible').setItemVisibilityChecked(True)
    QgsProject.instance().layerTreeRoot().findGroup('not_visible1').setItemVisibilityChecked(False)
    QgsProject.instance().layerTreeRoot().findGroup('not_visible2').setItemVisibilityChecked(False)
    # Select only the first most recent selection
    if len(sf)>0:
        feature = sf[0]
    else:
        print("No selection made")

    #get the point geometry from the event and get it's coordinates
    geom = feature.geometry()
    coordinate = geom.asPoint()

    X,Y = coordinate[0], coordinate[1]
    #get the distance in degrees using the reverse haversine formula and create the rectangle geometry 
    height,width = new_distance(X,Y,50,50)
    p_points = [QgsPointXY(X-height, Y-width), QgsPointXY(X-height, Y+width), QgsPointXY(X+height, Y+width), QgsPointXY(X+height, Y-width)]
    # set the canvas extent based on the boundingbox of the created geometry
    canvas.setExtent(QgsGeometry.fromPolygonXY([p_points]).boundingBox()) 
    #Query filter, if not given the filter will only filter on the wanted event-types (those who are included in the legend)
    # if given the filter will be set based on the input values and on the event-types
    if query != "":
        query_builder = QgsQueryBuilder(vl)
        query = query 
        query_builder.setSql(get_query(query) + 'AND "type"IN (\'ke\',\'ki\',\'qb\',\'sqb\',\'cb\',\'scb\')')
        query_builder.accept()
        query_builder.show()
    else:
        query_builder = QgsQueryBuilder(vl)
        query_builder.setSql(get_query("type IN ('ke','ki','qb','sqb','cb','scb')"))
        query_builder.accept()
        query_builder.show()
    # remove selection and sort based on the date in ascending order, select only first 50 (or amount when changed)
    vl.removeSelection()
    request = qgis.core.QgsFeatureRequest()
    clause = qgis.core.QgsFeatureRequest.OrderByClause('date', ascending=False)
    orderby = qgis.core.QgsFeatureRequest.OrderBy([clause])
    request.setOrderBy(orderby)
    feats_point = vl.getFeatures(request)
    i=0
    for feature in feats_point:
        if i>=amount:
            break
        elif feature.geometry().intersects(QgsGeometry.fromPolygonXY([p_points])):
            i +=1
            vl.selectByIds([feature.id()], QgsVectorLayer.AddToSelection)
    #(optional) export a csv from the selected features and a map with the selected features  (Helpers)     
    export_csv(vl, name)
    manager = QgsProject.instance().layoutManager()
     # use a predefined layout to make your map, this layout should be in you project so the name should suffice
    layout = manager.layoutByName("Layout_name")
    mapItem = layout.itemById("Map 1") 
    # Set the extent of the map layout based on the canvas
    mapItem.setExtent(canvas.extent())
    # set the title of the map based on the input
    Title = layout.itemById("Title")
    Title.setText(name)

    exporter = QgsLayoutExporter(layout)
    path = "Path/To/Folder"
    #in this example we choose a pdf format to export
    exporter.exportToPdf(path + 'Constant_String' + str(name) +".pdf", QgsLayoutExporter.PdfExportSettings())
    QgsProject.instance().clear()
