from Helpers import *

#Give as input the year you want to map, the canvas is preset in the QGIS project and will not change
project_path = 'Path/to/project.qgz' #adapt

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
    vl.loadNamedStyle('Path/To/Stylelayer.qml')
    vl.triggerRepaint()
    # Change the name of the layer to events in year (The title of the legend is equal to the name of the layer)
    rename.setName('events in ' + str(year))
    # use a predefined layout to make your map, this layout should be in you project so the name should suffice
    layout = manager.layoutByName("Seismic")
    exporter = QgsLayoutExporter(layout)
    path = "path"
    #in this example we choose a pdf format
    exporter.exportToPdf(path + 'String' + str(year)+".pdf", QgsLayoutExporter.PdfExportSettings())
    QgsProject.instance().clear()
