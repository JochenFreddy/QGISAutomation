#Export the selected events to a csv file and give a name
def export_csv(vector_layer, name):
    layer = vector_layer
    output_path = 'Path/To/Save' + str(name) + ".csv"
    QgsVectorFileWriter.writeAsVectorFormat(layer , output_path, "UTF-8", driverName="CSV", onlySelected = True)

