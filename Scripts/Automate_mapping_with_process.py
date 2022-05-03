# For MAC OS
import pandas as pd
import numpy
# Set the path to the project
project_path = "path.qgz"
# Selection of buffer of the station with number id
def get_station(number):
    #initiate the project and read it
    project= QgsProject.instance()
    project.setFileName(project_path)
    project.read()
    #set the canvas and select the feature from the vector layer (only the first)
    canvas = iface.mapCanvas()
    vl = QgsProject.instance().mapLayersByName('Final')[0]
    # Select the buffer for the station station based on the id
    vl.selectByExpression("\"fid\" = %s" %(number) )
    sf = vl.selectedFeatures()[0]
    # Zoom to the selected station
    canvas.zoomToSelected( vl )
    #assign variables to the features of the data 
    name = sf['name']
    pop_den = sf['density']
    pop_tot = sf['Tot_pop']
    # assign all the vectorlayers we want to use to a variable
    water = QgsProject.instance().mapLayersByName('Hydro_08')[0]
    roads = QgsProject.instance().mapLayersByName('Roads_Europe')[0]
    rails = QgsProject.instance().mapLayersByName('Ch_Fer_LB08')[0]

    #run the clip tool
    water_result= processing.run("native:clip", {'INPUT':water,'OVERLAY':QgsProcessingFeatureSourceDefinition(vl.id(), True),'OUTPUT':'TEMPORARY_OUTPUT'})
    roads_result= processing.run("native:clip", {'INPUT':roads,'OVERLAY':QgsProcessingFeatureSourceDefinition(vl.id(), True),'OUTPUT':'TEMPORARY_OUTPUT'})
    rails_result= processing.run("native:clip", {'INPUT':rails,'OVERLAY':QgsProcessingFeatureSourceDefinition(vl.id(), True),'OUTPUT':'TEMPORARY_OUTPUT'})
    # add the new clipped layers to the project and make visible (original layers were set to invisible)
    water = QgsProject.instance().addMapLayer(water_result['OUTPUT'], True)
    roads = QgsProject.instance().addMapLayer(roads_result['OUTPUT'], True)
    rails = QgsProject.instance().addMapLayer(rails_result['OUTPUT'], True)
    # Load the styles for each layer
    water.loadNamedStyle('path/To/Style.qml')
    water.triggerRepaint()
    roads.loadNamedStyle('path/To/Style.qml')
    roads.triggerRepaint()
    rails.loadNamedStyle('path/To/Style.qml')
    rails.triggerRepaint()
    
    # count the length of each feature
    w_features = water.getFeatures()
    water_length = 0
    for f in w_features:
        geom = f.geometry()
        water_length += geom.length()
    t_features = rails.getFeatures()
    t_length = 0
    for f in t_features:
        geom = f.geometry()
        t_length += geom.length()
    r_features = roads.getFeatures()
    r_length = 0
    for f in r_features:
        geom = f.geometry()
        r_length += geom.length()

    # use the premade layout
    manager = QgsProject .instance().layoutManager()
    layout = manager.layoutByName("Layout name")
    mapItem = layout.itemById("Map 1")
    mapItem.setExtent(canvas.extent())
    title = layout.itemById("Meas")
    title.setText(name)
    # adapt the text-item with the calaculated features
    stat = 'Pop density: ' + str(int(pop_den)) + '\n'+ '\n' + 'Pop total: ' + str(int(pop_tot)) + '\n'+ '\n' + 'Roads: ' + str(int(r_length*100)) + ' km' + '\n' + '\n'+ 'Water: ' + str(int(water_length/1000)) + ' km' + '\n' + '\n'+ 'Train tracks: ' + str(int(t_length/1000)) + 'km'
    text = layout.itemById("Stats")
    text.setText(stat)
    # export the map
    path = "Path/To/File/" #adapt
    exporter = QgsLayoutExporter(layout)
    exporter.exportToPdf(path + name + "Constant_String" +".pdf", QgsLayoutExporter.PdfExportSettings())
    QgsProject.instance().clear()
    
#optional Run        
for i in range(1,56,1):
    get_station(i)
    
        
