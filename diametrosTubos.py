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
        # fieldList = []
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

# Se buscan las lalaves de paso que no coincidan en el diametro con las acometidas distribucion
arcpy.env.workspace = os.path.join(mdbRecibido, "RedAbastecimiento")
arcpy.MakeFeatureLayer_management("AcometidaDistribucion", "ACO_view")

dimAcoList = []
arcpy.CopyFeatures_management("LlavePaso", os.path.join("C://CYII//diametroTubos//data//recibido//RA_58270//replicaREC.gdb", "LlavePaso"))
with arcpy.da.SearchCursor("LlavePaso",'DIAMETRO') as cursorLP:
    print "LlavePaso"
    for rowLP in cursorLP:
        dimAcoList.append(rowLP[0])
# fieldList = []
for dim2 in set(dimAcoList):
    arcpy.MakeFeatureLayer_management("LlavePaso", "LlavePaso_view", 'DIAMETRO = ' + str(dim2))
    selectionACO = arcpy.SelectLayerByLocation_management("ACO_view", "INTERSECT", "LlavePaso_view")
    arcpy.MakeFeatureLayer_management(selectionACO, "ACOSelect_view")
    with arcpy.da.SearchCursor("ACOSelect_view", '*') as cursor4:
        for r4 in cursor4:
            if r4[4] < dim2:
                selectionAco2 = arcpy.SelectLayerByAttribute_management("ACO_view",
                                                                     where_clause="OBJECTID = " + str(r4[0]))
                arcpy.MakeFeatureLayer_management(selectionAco2, "ACOSelect2_view")
                arcpy.MakeFeatureLayer_management("LlavePaso", "LlavePaso2_view")
                selection3 = arcpy.SelectLayerByLocation_management("LlavePaso2_view", "INTERSECT", "ACOSelect2_view")
                arcpy.MakeFeatureLayer_management(selection3, "LlavePaso" + "Select_view")
                with arcpy.da.SearchCursor("LlavePaso" + "Select_view", ['DIAMETRO', 'ID_TOPOGRAFIA']) as cursor5:
                    for r5 in cursor5:
                        lineaACOList = []
                        if r5[0] == dim2 and r5[1] is not None and r5[1] not in lineaACOList:
                            lineaACO = r5[1] + "\n"
                            lineaACOList.append(lineaACO)
                            f.writelines(lineaACO)
                arcpy.Delete_management("ACOSelect2_view")
                arcpy.Delete_management("LlavePaso2_view")
                arcpy.Delete_management("LlavePaso" + "Select_view")
    arcpy.Delete_management("ACOSelect_view")
    arcpy.Delete_management("LlavePaso" + "_view")
f.close()