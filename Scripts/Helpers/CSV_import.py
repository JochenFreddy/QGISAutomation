import pandas as pd
import requests
import json
import csv
import time


#This function imports indirectly the dataset in QGis, the data needs to be saved on a local machine as a csv file
#The fastest solution
        
def add_tecto():
    # Read the url in as a dataframe Token needs to be adapted
    # the amount of features are set to an amount larger than the datasets to ensure that all the datapoints are included
    dataT = pd.read_csv('API-link-with-Token')
    dataN = pd.read_csv('API-link-with-Token')
    frames = [dataT, dataN]
    # The 2 dataframes are combined (Concatenated). The columns for both frames are equal
    data = pd.concat(frames)
    data = data.to_csv(r'path_to_file/Events.csv')

    # To imediatly geolocate the dataframe both the lon and lat fields are set and the coordinate system is given
    # This is the most important reason that this method is more efficient
    uri = 'file:////path_to_file/Events.csv?delimiter=%s&xField=%s&yField=%s&crs=%s' %(",","longitude","latitude","epsg:4326")
    #create the vector layer
    Tecto = QgsVectorLayer(uri, "Tecto", "delimitedtext")
    #Add map layer to project
    QgsProject.instance().addMapLayer(Tecto)

#This code does not save the CSV to the local machine
def add_tecto_directly(crs):
    # Read the url in as a dataframe Token needs to be adapted
    # the amount of features are set to an amount larger than the datasets to ensure that all the datapoints are included
    dataT = pd.read_csv('API-link-with-Token')
    dataN = pd.read_csv('API-link-with-Token')
    frames = [dataT, dataN]
    # The 2 dataframes are combined (Concatenated). The columns for both frames are equal
    data = pd.concat(frames)
    #Create and empty point vector with the name result
    temp = QgsVectorLayer(f"Point?crs={crs}","result","memory")
    temp_data = temp.dataProvider()

    temp.startEditing()

    # When a vectorlayer is added we need to give the dataType, which needs to be the same for each column.
    # We help QGIS by setting the correct datatype for them 
    for head in data:
        if data[head].dtypes.name == 'object' or data[head].dtypes.name == 'bool': 
            myField = QgsField(head, QVariant.String)
            temp.addAttribute(myField)
        else:
            myField = QgsField(head, QVariant.Double)
            temp.addAttribute(myField)
            
    temp.updateFields()
    #Add every feature to the vector layer and set the geometry
    for index,row in data.iterrows():
        list = []
        for head in data:
            f = QgsFeature()
            list.append(str(row[head]))
        f.setAttributes(list)
        x=row['longitude']
        y=row['latitude']
        
        f.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(x,y)))
        temp.addFeature(f)
    #commit changes and add layer
    temp.commitChanges()
    QgsProject.instance().addMapLayer(temp)

    
