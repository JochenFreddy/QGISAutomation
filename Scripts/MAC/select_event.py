project_path = "path"
eventdict = {'ke' : '2', 'ki': '2', 'qb':'1', 'sqb':'1', 'cb':'3', 'scb':'3'}
# Selection of event in descending order with the newest being number 1
def select_event(Newest):
    #initiate the project and read it
    project = QgsProject.instance()
    project.setFileName(project_path)
    project.read()
    canvas = iface.mapCanvas()
    #load in the necessary data
    add_tecto()
    # assign all the vectorlayers we want to use to a variable
    vl = QgsProject.instance().mapLayersByName('vectorlayer')[0]
    Mun = QgsProject.instance().mapLayersByName('vectorlayer')[0]
    Prov = QgsProject.instance().mapLayersByName('vectorlayer')[0]
    #load a predefined style
    vl.loadNamedStyle('path to style.qml')
    vl.triggerRepaint()
    # Set groups either to visible or not-visible
    QgsProject.instance().layerTreeRoot().findGroup('not_visible').setItemVisibilityChecked(False)
    QgsProject.instance().layerTreeRoot().findGroup('visible').setItemVisibilityChecked(True)
    QgsProject.instance().layerTreeRoot().findGroup('not_visible').setItemVisibilityChecked(False)
    request = qgis.core.QgsFeatureRequest()
    clause = qgis.core.QgsFeatureRequest.OrderByClause('date', ascending=False)
    orderby = qgis.core.QgsFeatureRequest.OrderBy([clause])
    request.setOrderBy(orderby)
    feats_point = vl.getFeatures(request)
    # Select the feature at the "Newest" position
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
    #get the distance in degrees using the haversine formula
    height,width = new_distance(X,Y,20,20)
    p_points = [QgsPointXY(X-height, Y-width), QgsPointXY(X-height, Y+width), QgsPointXY(X+height, Y+width), QgsPointXY(X+height, Y-width)]
    canvas.setExtent(QgsGeometry.fromPolygonXY([p_points]).boundingBox()) #setExtent based on the boundingbox
    # get_date, municipality and province from input
    Munfeat = Mun.getFeatures()
    Provfeat = Prov.getFeatures()
    for prov in Provfeat:
        if geom.intersects(prov.geometry()):
            Prov.selectByIds([prov.id()], QgsVectorLayer.AddToSelection)
    if (len(Prov.selectedFeatures())!=0):
        ProvName= " ,  " + Prov.selectedFeatures()[0]['Name_2']
    else:
        ProvName = ""
    for mun in Munfeat:
        if geom.intersects(mun.geometry()):
            Mun.selectByIds([mun.id()], QgsVectorLayer.AddToSelection)
    if (len(Mun.selectedFeatures())!=0):
        MunName = Mun.selectedFeatures()[0]['Name']
    else:
        MunName = name
    
    # Make the different language texts for all the different snapshots
    for j in range(0,4,1):
        NL= dag + ' ' + month(maand, maand_dict) + ' ,  ' + jaar + ' ' + time + ' - ' + MunName + ProvName + ' -  ML ' + str(mag) + '\n' + ' Horizontale onzekerheid ' + str(hor) + ' km'
        FR= dag + ' ' + month(maand, mois_dict) + ' ,  ' + jaar + ' ' + time + ' - ' + MunName + ProvName + ' -  ML ' + str(mag) + '\n' + ' Incertitude horizontale ' + str(hor) + ' km'
        EN= dag + ' ' + month(maand, month_dict) + ' ,  ' + jaar + ' ' + time + ' - ' + MunName + ProvName + ' -  ML ' + str(mag) + '\n' + ' Horizontal uncertainty ' + str(hor) + ' km'
        DE= dag + ' ' + month(maand, monat_dict) + ' ,  ' + jaar + ' ' + time + ' - ' + MunName + ProvName + ' -  ML ' + str(mag) + '\n' + ' Horizontale Unsicherheit ' + str(hor) + ' km'
        language = [NL,FR,EN,DE]
        stijl = ['Event NL','Event FR','Event EN','Event DE']
        manager = QgsProject.instance().layoutManager()
        layout = manager.layoutByName(stijl[j]) #adapt
        mapItem = layout.itemById("Map 1") #adapt
        mapItem.setExtent(canvas.extent())
        for i in range(1, 4, 1):
            if str(i) == eventdict[eventType]:
                legendItem = layout.itemById(str(i))
                legendItem.setVisibility(True)
            else:
                legendItem = layout.itemById(str(i))
                legendItem.setVisibility(False)
        title = layout.itemById("titel")
        title.setText(language[j]) 
        exporter = QgsLayoutExporter(layout)
        path = "/Users/jochenvlaeminck/Documents/Stage/Images/Snapshot/" #adapt
        exporter.exportToPdf(path + str(stijl[j]) + str(MunName) + '_' + jaar +".pdf", QgsLayoutExporter.PdfExportSettings())
    QgsProject.instance().clear()
