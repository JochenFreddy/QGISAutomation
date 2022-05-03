from qgis.core import *

#set PYTHONPATH = C:\PROGRA~1\QGIS32~1.5\apps\qgis-ltr\python

QgsApplication.setPrefixPath('C:/PROGRA~1/QGIS32~1.5/apps/qgis-ltr',True)

qgs = QgsApplication([], False)

qgs.initQgis()

qgs.exitQgis()
