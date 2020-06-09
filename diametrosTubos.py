import arcpy, os

mdbRecibido = "C://CYII//diametroTubos//data//recibido//RA_58270//replica.mdb"

replicaRecibido = os.path.join("C://CYII//diametroTubos//data//recibido//RA_58270", "replicaREC.gdb")
if arcpy.Exists(replicaRecibido):
    arcpy.Delete_management(replicaRecibido)
arcpy.CreateFileGDB_management("C://CYII//diametroTubos//data//recibido//RA_58270", "replicaREC")

if os.path.exists("C://CYII//diametroTubos//diametros.txt"):
    os.remove("C://CYII//diametroTubos//diametros.txt")
f = open("C://CYII//diametroTubos//diametros.txt",'w')

arcpy.env.workspace = os.path.join(mdbRecibido, "RedAbastecimiento")

arcpy.MakeFeatureLayer_management("Tubo", "Tubo_view")
noDimfcList = ["Calderin", "Clorador", "CompuertaCanal", "NudoDeposito", "NudoDistribucion", "MuestreoFijo", "PozoCaptacionSubterranea", "Fuente", "LlavePaso", "NudoAcometida", "RedAbastecimiento_Junctions"]

for fc in arcpy.ListFeatureClasses():
    dimList = []
    if arcpy.Describe(fc).shapeType == "Point" and fc not in noDimfcList:
        arcpy.CopyFeatures_management(fc, os.path.join("C://CYII//diametroTubos//data//recibido//RA_58270//replicaREC.gdb", fc))
        with arcpy.da.SearchCursor(fc,'DIAMETRO') as cursor:
            print arcpy.Describe(fc).name
            for row in cursor:
                dimList.append(row[0])
        fieldList = []
        for dim in set(dimList):
            arcpy.MakeFeatureLayer_management(fc, fc + "_view", 'DIAMETRO = ' + str(dim))
            selection = arcpy.SelectLayerByLocation_management("Tubo_view", "INTERSECT", fc + "_view")
            arcpy.MakeFeatureLayer_management(selection,"tuboSelect_view")
            with arcpy.da.SearchCursor("tuboSelect_view", '*') as cursor2:
                for r2 in cursor2:
                    if r2[13] < dim:
                        selection2 = arcpy.SelectLayerByAttribute_management("Tubo_view", where_clause = "OBJECTID = " + str(r2[0]))
                        arcpy.MakeFeatureLayer_management(selection2, "tuboSelect2_view")
                        arcpy.MakeFeatureLayer_management(fc, fc + "2_view")
                        selection3 = arcpy.SelectLayerByLocation_management(fc + "2_view", "INTERSECT", "tuboSelect2_view")
                        arcpy.MakeFeatureLayer_management(selection3, fc + "Select_view")
                        with arcpy.da.SearchCursor(fc + "Select_view",['DIAMETRO','ID_TOPOGRAFIA']) as cursor3:
                            for r3 in cursor3:
                                lineaList = []
                                if r3[0] == dim and r3[1] is not None and r3[1] not in lineaList:
                                    linea = r3[1] + "\n"
                                    lineaList.append(linea)
                                    f.writelines(linea)
                        arcpy.Delete_management("tuboSelect2_view")
                        arcpy.Delete_management(fc + "2_view")
                        arcpy.Delete_management(fc + "Select_view")
            arcpy.Delete_management("tuboSelect_view")
            arcpy.Delete_management(fc + "_view")





f.close()