import arcpy, sys, os

try:
    arcpy.ImportToolbox("C:\Program Files (x86)\ET SpatialTechniques\ET GeoWizards 11.3 Concurrent for ArcGIS 10.3\ET GeoWizards.tbx")
    arcpy.gp.toolbox = "C:\Program Files (x86)\ET SpatialTechniques\ET GeoWizards 11.3 Concurrent for ArcGIS 10.3\ET GeoWizards.tbx"
except:
    try:
        arcpy.ImportToolbox("C:/Program Files (x86)/ET SpatialTechniques/ET GeoWizards 11.0 Concurrent for ArcGIS 10.3/ET GeoWizards.tbx")
        arcpy.gp.toolbox = "C:/Program Files (x86)/ET SpatialTechniques/ET GeoWizards 11.0 Concurrent for ArcGIS 10.3/ET GeoWizards.tbx"
    except:
        arcpy.AddError("\n~~~~ ~~~~ YOU MUST HAVE ET GEOWIZARDS INSTALLED AND LICENSED TO RUN THIS STEP! ~~~~ ~~~~\n")
        sys.exit()

arcpy.env.overwriteOutput = True
arcpy.Delete_management("in_memory")
####### FUNCTIONS

def split_following_num(s):
    prev_char = ''
    for i, char in enumerate(s):
        if char == '_' and prev_char in '0123456789':
            return s[:i].upper()
        prev_char = char


################### Hardcode Test INPUTS ######################
"""
new_TTs_ATT_LP = r"D:\SCRIPT_LIBRARY\CEMA_Reprocessing_Finalization\SAMPLE_DATA\NEW_DETECTION_EXAMPLES\FINAL_DETECTION_TT_AND_POLY\Del_Monte_detections_ATT_LP.shp"

new_Polys_LP = r"D:\SCRIPT_LIBRARY\CEMA_Reprocessing_Finalization\SAMPLE_DATA\NEW_DETECTION_EXAMPLES\FINAL_DETECTION_TT_AND_POLY\Del_Monte_detections_Polys_LP.shp"

old_GDB = r"D:\SCRIPT_LIBRARY\CEMA_Reprocessing_Finalization\SAMPLE_DATA\OLD_DELIVERABLES\DEL_MONTE_2104\ENCROACHMENT\DEL_MONTE_2104_ENCROACHMENT_JL_092915.gdb"

old_encroachment_TTs = r"D:\SCRIPT_LIBRARY\CEMA_Reprocessing_Finalization\SAMPLE_DATA\OLD_DELIVERABLES\DEL_MONTE_2104\ENCROACHMENT\DEL_MONTE_2104_ENCROACHMENT_JL_092915.gdb\DEL_MONTE_2104_TreeTops"

old_encroachment_VPs = r"D:\SCRIPT_LIBRARY\CEMA_Reprocessing_Finalization\SAMPLE_DATA\OLD_DELIVERABLES\DEL_MONTE_2104\ENCROACHMENT\DEL_MONTE_2104_ENCROACHMENT_JL_092915.gdb\DEL_MONTE_2104_VegPolygons"

old_Spans = r"D:\SCRIPT_LIBRARY\CEMA_Reprocessing_Finalization\SAMPLE_DATA\OLD_DELIVERABLES\DEL_MONTE_2104\ENCROACHMENT\DEL_MONTE_2104_ENCROACHMENT_JL_092915.gdb\DEL_MONTE_2104_Spans"

old_Tower = r"D:\SCRIPT_LIBRARY\CEMA_Reprocessing_Finalization\SAMPLE_DATA\OLD_DELIVERABLES\DEL_MONTE_2104\ENCROACHMENT\DEL_MONTE_2104_ENCROACHMENT_JL_092915.gdb\DEL_MONTE_2104_Towers"

OUTPUT_FOLDER = "D:\SCRIPT_LIBRARY\CEMA_Reprocessing_Finalization\SAMPLE_DATA\TTS_TEST"""


# ARC PARAMS

OUT_TTs = arcpy.GetParameterAsText(0)

OUT_VPs = arcpy.GetParameterAsText(1)

old_GDB = arcpy.GetParameterAsText(2)

OUTPUT_FOLDER = arcpy.GetParameterAsText(3)

cirNAME = split_following_num(os.path.basename(old_GDB))
arcpy.AddMessage(cirNAME)

arcpy.CreateFileGDB_management(OUTPUT_FOLDER, cirNAME + "_CEMA_2015")

NEW_circuit_GDB = os.path.join(OUTPUT_FOLDER, "%s_CEMA_2015.gdb"%(cirNAME))

old_encroachment_TTs = os.path.join(old_GDB,"%s_TreeTops"%(cirNAME))

old_encroachment_VPs = os.path.join(old_GDB,"%s_VegPolygons"%(cirNAME))

arcpy.AddMessage(old_encroachment_VPs)

old_Spans = os.path.join(old_GDB,"%s_Spans"%(cirNAME))

old_Tower = os.path.join(old_GDB,"%s_Towers"%(cirNAME))


## Convert New TTs and VEgPoly Heights to FT
with arcpy.da.UpdateCursor(OUT_VPs,["H"]) as uCur:
    for row in uCur:
        row[0] = (row[0] * 3.28)
        uCur.updateRow(row)


# Erase features based on overlap


erased_VPs = os.path.join(OUTPUT_FOLDER,"VPs_erased.shp")

arcpy.gp.ET_GPErase(OUT_VPs, old_encroachment_VPs,erased_VPs,'0.070674979713')

### FCs
inTowers = os.path.join(old_GDB,"%s_Towers" % (cirNAME))

tempfc_Towers = r'in_memory\tempfc_in_Towers'

outTowers =("%s_CEMA_2015_Towers" % (cirNAME))

arcpy.CopyFeatures_management(inTowers, tempfc_Towers)

Add_Tower_Fields = ["PMD","DIVISION","REGION","COUNTY","CITY","VOLTAGE","STR_GEOTAG"]


inSpans = os.path.join(old_GDB,"%s_Spans" % (cirNAME))

tempfc_Spans = r'in_memory\tempfc_in_Spans'

outSpans = ("%s_CEMA_2015_Spans" % (cirNAME))

arcpy.CopyFeatures_management(inSpans, tempfc_Spans)

# VEGPOLYS
in_VPs = old_encroachment_VPs

#merged_VPs = os.path.join(OUTPUT_FOLDER,"Merged_Formatted_VPs.shp")

merged_VPs = r'in_memory\tempfc_merged_VPs'



outVPs =("%s_CEMA_2015_VegPolys" % (cirNAME))

# VPs Field Map

fieldMappings_VPs = arcpy.FieldMappings()

# 1. X
fldMap_X_VPs = arcpy.FieldMap()
fldMap_X_VPs.addInputField(in_VPs, "X")

X_VPs_field = fldMap_X_VPs.outputField
X_VPs_field.name = "X"
fldMap_X_VPs.outputField = X_VPs_field

fieldMappings_VPs.addFieldMap(fldMap_X_VPs)

# 1. Y
fldMap_Y_VPs = arcpy.FieldMap()
fldMap_Y_VPs.addInputField(in_VPs, "Y")

Y_VPs_field = fldMap_Y_VPs.outputField
Y_VPs_field.name = "Y"
fldMap_Y_VPs.outputField = Y_VPs_field

fieldMappings_VPs.addFieldMap(fldMap_Y_VPs)

# 1. Z
fldMap_Z_VPs = arcpy.FieldMap()
fldMap_Z_VPs.addInputField(in_VPs, "Z")

Z_VPs_field = fldMap_Z_VPs.outputField
Z_VPs_field.name = "Z"
fldMap_Z_VPs.outputField = Z_VPs_field

fieldMappings_VPs.addFieldMap(fldMap_Z_VPs)

# 1. TREEID
fldMap_GEOTAG_1_VPs = arcpy.FieldMap()
fldMap_GEOTAG_1_VPs.addInputField(in_VPs, "TREEID")
fldMap_GEOTAG_1_VPs.addInputField(erased_VPs, "GEOTAG_1")

GEOTAG_1_VPs_field = fldMap_GEOTAG_1_VPs.outputField
GEOTAG_1_VPs_field.name = "TREEID"
GEOTAG_1_VPs_field.aliasName = "TREEID"
fldMap_GEOTAG_1_VPs.outputField = GEOTAG_1_VPs_field

fieldMappings_VPs.addFieldMap(fldMap_GEOTAG_1_VPs)

# 1. HEIGHT
fldMap_HEIGHT_VPs = arcpy.FieldMap()
fldMap_HEIGHT_VPs.addInputField(in_VPs, "HEIGHT")
fldMap_HEIGHT_VPs.addInputField(erased_VPs, "H")

HEIGHT_VPs_field = fldMap_HEIGHT_VPs.outputField
HEIGHT_VPs_field.name = "HEIGHT"
HEIGHT_VPs_field.aliasName = "HEIGHT"
fldMap_HEIGHT_VPs.outputField = HEIGHT_VPs_field

fieldMappings_VPs.addFieldMap(fldMap_HEIGHT_VPs)


arcpy.Merge_management([in_VPs, erased_VPs], merged_VPs, fieldMappings_VPs)

arcpy.FeatureClassToFeatureClass_conversion(merged_VPs, NEW_circuit_GDB, outVPs)

## Merge New VPs with OLD VPs based on field map

# TREETOPS

NEW_TTs = OUT_TTs

NEW_TTs_ATTRIB = os.path.join(OUTPUT_FOLDER,"TTs_NEW_ATTRIB.shp")

arcpy.gp.ET_GPNearFeature (NEW_TTs,old_Spans ,NEW_TTs_ATTRIB,300)

with arcpy.da.UpdateCursor(NEW_TTs_ATTRIB,["ET_Dist","H"]) as uCur:
    for row in uCur:
        row[0] = (row[0] * 3.28)
        row[1] = (row[1] * 3.28)
        uCur.updateRow(row)




merged_TTs = os.path.join(OUTPUT_FOLDER,"TTs_MERGED.shp")

outTTs =("%s_CEMA_2015_TreeTops_AF" % (cirNAME))
out_GDB_TTs = os.path.join(NEW_circuit_GDB, outTTs)

## Add Fields
arcpy.AddField_management(NEW_TTs_ATTRIB,'APN_NUMBER','TEXT',field_length=255)
arcpy.AddField_management(NEW_TTs_ATTRIB,'STREET_NUM','TEXT',field_length=255)
arcpy.AddField_management(NEW_TTs_ATTRIB,'STREET','TEXT',field_length=255)
arcpy.AddField_management(NEW_TTs_ATTRIB,'CUSTOMER_N','TEXT',field_length=255)
arcpy.AddField_management(NEW_TTs_ATTRIB,'CUSTOMER_1','TEXT',field_length=255)
arcpy.AddField_management(NEW_TTs_ATTRIB,'CITY','TEXT',field_length=255)
arcpy.AddField_management(NEW_TTs_ATTRIB,'COUNTY','TEXT',field_length=255)

arcpy.AddField_management(NEW_TTs_ATTRIB,'DIVISION','TEXT',field_length=255)
arcpy.AddField_management(NEW_TTs_ATTRIB,'SRA_LRA','TEXT',field_length=255)
arcpy.AddField_management(NEW_TTs_ATTRIB,'FALL_IN','TEXT',field_length=255)
arcpy.AddField_management(NEW_TTs_ATTRIB,'LATITUDE','TEXT',field_length=255)
arcpy.AddField_management(NEW_TTs_ATTRIB,'LONGITUDE','TEXT',field_length=255)
arcpy.AddField_management(NEW_TTs_ATTRIB,'DC_AF','TEXT',field_length=255)
arcpy.AddField_management(NEW_TTs_ATTRIB,'DC_FI','TEXT',field_length=255)
arcpy.AddField_management(NEW_TTs_ATTRIB,'OFF','TEXT',field_length=255)

arcpy.AddField_management(NEW_TTs_ATTRIB,'DC_VENDOR','TEXT',field_length=255)
arcpy.AddField_management(NEW_TTs_ATTRIB,'OH','TEXT',field_length=255)
arcpy.AddField_management(NEW_TTs_ATTRIB,'SPAN_TAG','TEXT',field_length=255)
arcpy.AddField_management(NEW_TTs_ATTRIB,'BST_TAG','TEXT',field_length=255)
arcpy.AddField_management(NEW_TTs_ATTRIB,'AST_TAG','TEXT',field_length=255)
arcpy.AddField_management(NEW_TTs_ATTRIB,'GCC200','TEXT',field_length=255)
arcpy.AddField_management(NEW_TTs_ATTRIB,'SPAN_ID','TEXT',field_length=255)

arcpy.AddField_management(NEW_TTs_ATTRIB,'VOLTAGE','TEXT',field_length=255)
arcpy.AddField_management(NEW_TTs_ATTRIB,'PMD','TEXT',field_length=255)
arcpy.AddField_management(NEW_TTs_ATTRIB,'REGION','TEXT',field_length=255)
arcpy.AddField_management(NEW_TTs_ATTRIB,'CUSTOMER_P','TEXT',field_length=255)



## Field Map

# TTs FIELD MAP
fieldMappings = arcpy.FieldMappings()

# 33. APN_Number field
fldMap_APN_Num = arcpy.FieldMap()
fldMap_APN_Num.addInputField(NEW_TTs_ATTRIB, "APN_NUMBER")

APN_Num_field = fldMap_APN_Num.outputField
APN_Num_field.name = "APN_NUMBER"
fldMap_APN_Num.outputField = APN_Num_field

fieldMappings.addFieldMap(fldMap_APN_Num)

# 34. STREET_num field
fldMap_STREET_num = arcpy.FieldMap()
fldMap_STREET_num.addInputField(NEW_TTs_ATTRIB, "STREET_NUM")

STREET_num_field = fldMap_STREET_num.outputField
STREET_num_field.name = "STREET_NUM"
fldMap_STREET_num.outputField = STREET_num_field

fieldMappings.addFieldMap(fldMap_STREET_num)

# 35. STREET field
fldMap_STREET = arcpy.FieldMap()
fldMap_STREET.addInputField(NEW_TTs_ATTRIB, "STREET")

STREET_field = fldMap_STREET.outputField
STREET_field.name = "STREET"
fldMap_STREET.outputField = STREET_field

fieldMappings.addFieldMap(fldMap_STREET)

# 37.  CUSTOMER Name field
fldMap_CUST_NAME = arcpy.FieldMap()
fldMap_CUST_NAME.addInputField(NEW_TTs_ATTRIB, "CUSTOMER_N")

CUST_NAME_field = fldMap_CUST_NAME.outputField
CUST_NAME_field.name = "CUSTOMER_N"
fldMap_CUST_NAME.outputField = CUST_NAME_field

fieldMappings.addFieldMap(fldMap_CUST_NAME)

# 38. CUSTOMER_NAME1 field
fldMap_CUST_NAME1 = arcpy.FieldMap()
fldMap_CUST_NAME1.addInputField(NEW_TTs_ATTRIB, "CUSTOMER_1")

CUST_NAME1_field = fldMap_CUST_NAME1.outputField
CUST_NAME1_field.name = "CUSTOMER_1"
fldMap_CUST_NAME1.outputField = CUST_NAME1_field

fieldMappings.addFieldMap(fldMap_CUST_NAME1)

# 39. CITY field

fldMap_CITY = arcpy.FieldMap()
fldMap_CITY.addInputField(NEW_TTs_ATTRIB, "CITY")

CITY_field = fldMap_CITY.outputField
CITY_field.name = "CITY"
fldMap_CITY.outputField = CITY_field

fieldMappings.addFieldMap(fldMap_CITY)

# 40. COUNTY field
fldMap_COUNTY = arcpy.FieldMap()
fldMap_COUNTY.addInputField(NEW_TTs_ATTRIB, "COUNTY")

COUNTY_field = fldMap_COUNTY.outputField
COUNTY_field.name = "COUNTY"
fldMap_COUNTY.outputField = COUNTY_field

fieldMappings.addFieldMap(fldMap_COUNTY)

# 41. DIVISION field
fldMap_DIV = arcpy.FieldMap()
fldMap_DIV.addInputField(NEW_TTs_ATTRIB, "DIVISION")

DIV_field = fldMap_DIV.outputField
DIV_field.name = "DIVISION"
fldMap_DIV.outputField = DIV_field

fieldMappings.addFieldMap(fldMap_DIV)

# 19. LINE_NAME field
fldMap_LINE_NAME = arcpy.FieldMap()
#fldMap_LINE_NAME.addInputField(NEW_TTs_ATTRIB, "LINE_NAME")
fldMap_LINE_NAME.addInputField(old_encroachment_TTs, "LINE_NAME")

LINE_NAME_field = fldMap_LINE_NAME.outputField
LINE_NAME_field.name = "LINE_NAME"
fldMap_LINE_NAME.outputField = LINE_NAME_field

fieldMappings.addFieldMap(fldMap_LINE_NAME)

# SRA/LRA Field
fldMap_SRA = arcpy.FieldMap()
fldMap_SRA.addInputField(NEW_TTs_ATTRIB, "SRA_LRA")

SRA_field = fldMap_SRA.outputField
SRA_field.name = "SRA_LRA"
fldMap_SRA.outputField = SRA_field

fieldMappings.addFieldMap(fldMap_SRA)

# 3. D2W_AF
fldMap_DTW = arcpy.FieldMap()

fldMap_DTW.addInputField(old_encroachment_TTs, "GI_D2W")

DTW_field = fldMap_DTW.outputField
DTW_field.name = "D2W_AF"
DTW_field.aliasName = "D2W_AF"
fldMap_DTW.outputField = DTW_field

fieldMappings.addFieldMap(fldMap_DTW)
# 3. UG_D2W
fldMap_UDTW = arcpy.FieldMap()


fldMap_UDTW.addInputField(old_encroachment_TTs, "UG_D2W")
UDTW_field = fldMap_UDTW.outputField
UDTW_field.name = "UG_D2W"
UDTW_field.aliasName = "UG_D2W"
fldMap_UDTW.outputField = UDTW_field

fieldMappings.addFieldMap(fldMap_UDTW)

# OH D2W

fldMap_OTW = arcpy.FieldMap()

fldMap_OTW.addInputField(old_encroachment_TTs, "OH_D2W")

OTW_field = fldMap_OTW.outputField
OTW_field.name = "OH_D2W"
OTW_field.aliasName = "OH_D2W"
fldMap_OTW.outputField = OTW_field

fieldMappings.addFieldMap(fldMap_OTW)

# 1. OFF_ field

fldMap_OFF = arcpy.FieldMap()
fldMap_OFF.addInputField(NEW_TTs_ATTRIB, "OFF")

OFF_field = fldMap_OFF.outputField
OFF_field.name = "OFF"
OFF_field.aliasName = "OFF"
fldMap_OFF.outputField = OFF_field

fieldMappings.addFieldMap(fldMap_OFF)

# 8. H field
fldMap_H = arcpy.FieldMap()
fldMap_H.addInputField(NEW_TTs_ATTRIB, "H")
fldMap_H.addInputField(old_encroachment_TTs, "HEIGHT")
H_field = fldMap_H.outputField
H_field.name = "HEIGHT"
H_field.aliasName = "HEIGHT"
fldMap_H.outputField = H_field

fieldMappings.addFieldMap(fldMap_H)

# FALL_IN field
fldMap_FI = arcpy.FieldMap()
fldMap_FI.addInputField(NEW_TTs_ATTRIB, "FALL_IN")

FI_field = fldMap_FI.outputField
FI_field.name = "FALL_IN"
fldMap_FI.outputField = FI_field

fieldMappings.addFieldMap(fldMap_FI)

# 4. OVR field
fldMap_OVR = arcpy.FieldMap()
fldMap_OVR.addInputField(old_encroachment_TTs, "FI_D2W")
fldMap_OVR.addInputField(NEW_TTs_ATTRIB, "ET_Dist")

OVR_field = fldMap_OVR.outputField
OVR_field.name = "FI_D2W"
OVR_field.aliasName = "FI_D2W"
fldMap_OVR.outputField = OVR_field

fieldMappings.addFieldMap(fldMap_OVR)

# 15. LATITUDE field
fldMap_LAT = arcpy.FieldMap()
fldMap_LAT.addInputField(old_encroachment_TTs, "LAT")

LAT_field = fldMap_LAT.outputField
LAT_field.name = "LATITUDE"
fldMap_LAT.outputField = LAT_field

fieldMappings.addFieldMap(fldMap_LAT)

# 16. LONGITUTDE field
fldMap_LAT = arcpy.FieldMap()
fldMap_LAT.addInputField(old_encroachment_TTs, "LON")

LAT_field = fldMap_LAT.outputField
LAT_field.name = "LONGITUDE"
fldMap_LAT.outputField = LAT_field

fieldMappings.addFieldMap(fldMap_LAT)

# 18. LINE_ID field
fldMap_LINE_ID = arcpy.FieldMap()
fldMap_LINE_ID.addInputField(old_encroachment_TTs, "LINE_NBR")

LINE_ID_field = fldMap_LINE_ID.outputField
LINE_ID_field.name = "LINE_ID"
fldMap_LINE_ID.outputField = LINE_ID_field

fieldMappings.addFieldMap(fldMap_LINE_ID)

# 25. TREE_ID field
fldMap_TREE_ID = arcpy.FieldMap()
fldMap_TREE_ID.addInputField(old_encroachment_TTs, "TREEID")
fldMap_TREE_ID.addInputField(NEW_TTs_ATTRIB, "GEOTAG_1")

TREE_ID_field = fldMap_TREE_ID.outputField
TREE_ID_field.name = "TREEID"
TREE_ID_field.aliasName = "TREEID"
fldMap_TREE_ID.outputField = TREE_ID_field

fieldMappings.addFieldMap(fldMap_TREE_ID)

# 26. ACQ_DATE field
fldMap_ACQ_DATE = arcpy.FieldMap()
fldMap_ACQ_DATE.addInputField(old_encroachment_TTs, "ACQ_DATE")

ACQ_DATE_field = fldMap_ACQ_DATE.outputField
ACQ_DATE_field.name = "ACQ_DATE"
fldMap_ACQ_DATE.outputField = ACQ_DATE_field

fieldMappings.addFieldMap(fldMap_ACQ_DATE)

# 29. DC_AF field
fldMap_DC_AF = arcpy.FieldMap()
fldMap_DC_AF.addInputField(NEW_TTs_ATTRIB, "DC_AF")

DC_AF_field = fldMap_DC_AF.outputField
DC_AF_field.name = "DC_AF"
fldMap_DC_AF.outputField = DC_AF_field

fieldMappings.addFieldMap(fldMap_DC_AF)

# 30. DC_FI field
fldMap_DC_FI = arcpy.FieldMap()
fldMap_DC_FI.addInputField(NEW_TTs_ATTRIB, "DC_FI")

DC_FI_field = fldMap_DC_FI.outputField
DC_FI_field.name = "DC_FI"
fldMap_DC_FI.outputField = DC_FI_field

fieldMappings.addFieldMap(fldMap_DC_FI)

# 31. DC_VENDOR field
fldMap_DC_VEN = arcpy.FieldMap()
fldMap_DC_VEN.addInputField(NEW_TTs_ATTRIB, "DC_VENDOR")

DC_VEN_field = fldMap_DC_VEN.outputField
DC_VEN_field.name = "DC_VENDOR"
fldMap_DC_VEN.outputField = DC_VEN_field

fieldMappings.addFieldMap(fldMap_DC_VEN)

# 9. OH field
fldMap_OH = arcpy.FieldMap()
fldMap_OH.addInputField(NEW_TTs_ATTRIB, "OH")
fldMap_OH.addInputField(old_encroachment_TTs, "OH_D2W")
OH_field = fldMap_OH.outputField
OH_field.name = "OH"
fldMap_OH.outputField = OH_field

fieldMappings.addFieldMap(fldMap_OH)

# 5. X field
fldMap_X = arcpy.FieldMap()
fldMap_X.addInputField(NEW_TTs_ATTRIB, "X")

X_field = fldMap_X.outputField
X_field.name = "X"
fldMap_X.outputField = X_field

fieldMappings.addFieldMap(fldMap_X)

# 6. Y field
fldMap_Y = arcpy.FieldMap()
fldMap_Y.addInputField(NEW_TTs_ATTRIB, "Y")

Y_field = fldMap_Y.outputField
Y_field.name = "Y"
fldMap_Y.outputField = Y_field

fieldMappings.addFieldMap(fldMap_Y)

# 7. Z field
fldMap_Z = arcpy.FieldMap()
fldMap_Z.addInputField(NEW_TTs_ATTRIB, "Z")

Z_field = fldMap_Z.outputField
Z_field.name = "Z"
fldMap_Z.outputField = Z_field

fieldMappings.addFieldMap(fldMap_Z)

# 10. SPAN_TAG field
fldMap_ST = arcpy.FieldMap()
fldMap_ST.addInputField(NEW_TTs_ATTRIB, "SPAN_TAG")

ST_field = fldMap_ST.outputField
ST_field.name = "SPAN_TAG"
fldMap_ST.outputField = ST_field

fieldMappings.addFieldMap(fldMap_ST)

# 11. BST_TAG field
fldMap_BST = arcpy.FieldMap()
fldMap_BST.addInputField(NEW_TTs_ATTRIB, "BST_TAG")

BST_field = fldMap_BST.outputField
BST_field.name = "BST_TAG"
fldMap_BST.outputField = BST_field

fieldMappings.addFieldMap(fldMap_BST)

# 12. AST_TAG field
fldMap_AST = arcpy.FieldMap()
fldMap_AST.addInputField(NEW_TTs_ATTRIB, "AST_TAG")

AST_field = fldMap_AST.outputField
AST_field.name = "AST_TAG"
fldMap_AST.outputField = AST_field

fieldMappings.addFieldMap(fldMap_AST)

# 13. GCC200 field
fldMap_GCC = arcpy.FieldMap()
fldMap_GCC.addInputField(NEW_TTs_ATTRIB, "GCC200")

GCC_field = fldMap_GCC.outputField
GCC_field.name = "GCC200"
fldMap_GCC.outputField = GCC_field

fieldMappings.addFieldMap(fldMap_GCC)

# 14. SPAN_ID field
fldMap_SPAN_ID = arcpy.FieldMap()
fldMap_SPAN_ID.addInputField(NEW_TTs_ATTRIB, "SPAN_ID")

SPAN_ID_field = fldMap_SPAN_ID.outputField
SPAN_ID_field.name = "SPAN_ID"
fldMap_SPAN_ID.outputField = SPAN_ID_field

fieldMappings.addFieldMap(fldMap_SPAN_ID)

# 17. VOLTAGE field
fldMap_V = arcpy.FieldMap()
fldMap_V.addInputField(NEW_TTs_ATTRIB, "VOLTAGE")

V_field = fldMap_V.outputField
V_field.name = "VOLTAGE"
fldMap_V.outputField = V_field

fieldMappings.addFieldMap(fldMap_V)

# 27. HEALTH field
fldMap_ACQ_DATE = arcpy.FieldMap()
fldMap_ACQ_DATE.addInputField(old_encroachment_TTs, "HEALTH")

ACQ_DATE_field = fldMap_ACQ_DATE.outputField
ACQ_DATE_field.name = "HEALTH"
fldMap_ACQ_DATE.outputField = ACQ_DATE_field

fieldMappings.addFieldMap(fldMap_ACQ_DATE)

# 32. PMD field
fldMap_PMD = arcpy.FieldMap()
fldMap_PMD.addInputField(NEW_TTs_ATTRIB, "PMD")

PMD_field = fldMap_PMD.outputField
PMD_field.name = "PMD"
PMD_field.aliasName = "PMD"
fldMap_PMD.outputField = PMD_field

fieldMappings.addFieldMap(fldMap_PMD)

# 24. Region field
fldMap_Region = arcpy.FieldMap()
fldMap_Region.addInputField(NEW_TTs_ATTRIB, "REGION")

Region_field = fldMap_Region.outputField
Region_field.name = "REGION"
fldMap_Region.outputField = Region_field

fieldMappings.addFieldMap(fldMap_Region)

# 36. CUSTOMER PHONE field
fldMap_CUST_PH = arcpy.FieldMap()
fldMap_CUST_PH.addInputField(NEW_TTs_ATTRIB, "CUSTOMER_P")

CUST_PH_field = fldMap_CUST_PH.outputField
CUST_PH_field.name = "CUSTOMER_P"
CUST_PH_field.aliasName = "CUSTOMER_P"
fldMap_CUST_PH.outputField = CUST_PH_field

fieldMappings.addFieldMap(fldMap_CUST_PH)



arcpy.Merge_management([NEW_TTs_ATTRIB, old_encroachment_TTs], merged_TTs, fieldMappings)

arcpy.FeatureClassToFeatureClass_conversion(merged_TTs, NEW_circuit_GDB,outTTs)

arcpy.DeleteField_management(out_GDB_TTs,"OFF")

## SPANS CONVERSION



arcpy.AddField_management(tempfc_Spans,'BST_TAG','TEXT',field_length=255)
arcpy.AddField_management(tempfc_Spans,'AST_TAG','TEXT',field_length=255)
arcpy.AddField_management(tempfc_Spans,'SPAN_TAG','TEXT',field_length=255)
arcpy.AddField_management(tempfc_Spans,'LINE_ID','TEXT',field_length=255)
arcpy.AddField_management(tempfc_Spans,'CIRCUIT_1','TEXT',field_length=255)
arcpy.AddField_management(tempfc_Spans,'CIRCUIT_2','TEXT',field_length=255)
arcpy.AddField_management(tempfc_Spans,'CIRCUIT_3','TEXT',field_length=255)
arcpy.AddField_management(tempfc_Spans,'GCC200','TEXT',field_length=255)
arcpy.AddField_management(tempfc_Spans,'PMD','TEXT',field_length=255)

# SPANS FIELD MAP
fieldMappings_spans = arcpy.FieldMappings()

# 1. BST TAG
fldMap_BST_TAG_spans = arcpy.FieldMap()
fldMap_BST_TAG_spans.addInputField(tempfc_Spans, "BST_TAG")

BST_TAG_spans_field = fldMap_BST_TAG_spans.outputField
BST_TAG_spans_field.name = "BST_TAG"
fldMap_BST_TAG_spans.outputField = BST_TAG_spans_field

fieldMappings_spans.addFieldMap(fldMap_BST_TAG_spans)

# 2. AST TAG
fldMap_AST_TAG_spans = arcpy.FieldMap()
fldMap_AST_TAG_spans.addInputField(tempfc_Spans, "AST_TAG")

AST_TAG_spans_field = fldMap_AST_TAG_spans.outputField
AST_TAG_spans_field.name = "AST_TAG"
fldMap_AST_TAG_spans.outputField = AST_TAG_spans_field

fieldMappings_spans.addFieldMap(fldMap_AST_TAG_spans)

# 3. SPAN TAG
fldMap_SPAN_TAG_spans = arcpy.FieldMap()
fldMap_SPAN_TAG_spans.addInputField(tempfc_Spans, "SPAN_TAG")

SPAN_TAG_spans_field = fldMap_SPAN_TAG_spans.outputField
SPAN_TAG_spans_field.name = "SPAN_TAG"
SPAN_TAG_spans_field.length = 255
fldMap_SPAN_TAG_spans.outputField = SPAN_TAG_spans_field

fieldMappings_spans.addFieldMap(fldMap_SPAN_TAG_spans)

# 4. SPAN ID
fldMap_SPAN_ID_spans = arcpy.FieldMap()
fldMap_SPAN_ID_spans.addInputField(tempfc_Spans, "SPAN_ID")

SPAN_ID_spans_field = fldMap_SPAN_ID_spans.outputField
SPAN_ID_spans_field.name = "SPAN_ID"
SPAN_ID_spans_field.length = 255
fldMap_SPAN_ID_spans.outputField = SPAN_ID_spans_field

fieldMappings_spans.addFieldMap(fldMap_SPAN_ID_spans)

# 5. SPAN LGTH
fldMap_SPAN_LGTH_spans = arcpy.FieldMap()
fldMap_SPAN_LGTH_spans.addInputField(tempfc_Spans, "SPAN_LGTH")

SPAN_LGTH_spans_field = fldMap_SPAN_LGTH_spans.outputField
SPAN_LGTH_spans_field.name = "SPAN_LGTH"
fldMap_SPAN_LGTH_spans.outputField = SPAN_LGTH_spans_field

fieldMappings_spans.addFieldMap(fldMap_SPAN_LGTH_spans)

# 6. VOLTAGE
fldMap_VOLT_spans = arcpy.FieldMap()
fldMap_VOLT_spans.addInputField(tempfc_Spans, "VOLTAGE")

VOLT_spans_field = fldMap_VOLT_spans.outputField
VOLT_spans_field.name = "VOLTAGE"
fldMap_VOLT_spans.outputField = VOLT_spans_field

fieldMappings_spans.addFieldMap(fldMap_VOLT_spans)

# 7. LINE_ID
fldMap_LINE_ID_spans = arcpy.FieldMap()
fldMap_LINE_ID_spans.addInputField(tempfc_Spans, "LINE_ID")

LINE_ID_spans_field = fldMap_LINE_ID_spans.outputField
LINE_ID_spans_field.name = "LINE_ID"
fldMap_LINE_ID_spans.outputField = LINE_ID_spans_field

fieldMappings_spans.addFieldMap(fldMap_LINE_ID_spans)

# 8. LINE_NAME
fldMap_LINE_NAME_spans = arcpy.FieldMap()
fldMap_LINE_NAME_spans.addInputField(tempfc_Spans, "LINE_NAME")

LINE_NAME_spans_field = fldMap_LINE_NAME_spans.outputField
LINE_NAME_spans_field.name = "LINE_NAME"
fldMap_LINE_NAME_spans.outputField = LINE_NAME_spans_field

fieldMappings_spans.addFieldMap(fldMap_LINE_NAME_spans)

# 9. LINE_NBR
fldMap_LINE_NBR_spans = arcpy.FieldMap()
fldMap_LINE_NBR_spans.addInputField(tempfc_Spans, "LINE_NBR")

LINE_NBR_spans_field = fldMap_LINE_NBR_spans.outputField
LINE_NBR_spans_field.name = "LINE_NBR"
fldMap_LINE_NBR_spans.outputField = LINE_NBR_spans_field

fieldMappings_spans.addFieldMap(fldMap_LINE_NBR_spans)

# 10. CIRCUIT 1
fldMap_CIR_1_spans = arcpy.FieldMap()
fldMap_CIR_1_spans.addInputField(tempfc_Spans, "CIRCUIT_1")

CIR_1_spans_field = fldMap_CIR_1_spans.outputField
CIR_1_spans_field.name = "CIRCUIT_1"
fldMap_CIR_1_spans.outputField = CIR_1_spans_field

fieldMappings_spans.addFieldMap(fldMap_CIR_1_spans)

# 12. CIRCUIT 2
fldMap_CIR_2_spans = arcpy.FieldMap()
fldMap_CIR_2_spans.addInputField(tempfc_Spans, "CIRCUIT_2")

CIR_2_spans_field = fldMap_CIR_2_spans.outputField
CIR_2_spans_field.name = "CIRCUIT_2"
fldMap_CIR_2_spans.outputField = CIR_2_spans_field

fieldMappings_spans.addFieldMap(fldMap_CIR_2_spans)

# 13. CIRCUIT 3
fldMap_CIR_3_spans = arcpy.FieldMap()
fldMap_CIR_3_spans.addInputField(tempfc_Spans, "CIRCUIT_3")

CIR_3_spans_field = fldMap_CIR_3_spans.outputField
CIR_3_spans_field.name = "CIRCUIT_3"
fldMap_CIR_3_spans.outputField = CIR_3_spans_field

fieldMappings_spans.addFieldMap(fldMap_CIR_3_spans)

# 14. GCC 200
fldMap_GCC_spans = arcpy.FieldMap()
fldMap_GCC_spans.addInputField(tempfc_Spans, "GCC200")

GCC_spans_field = fldMap_GCC_spans.outputField
GCC_spans_field.name = "GCC200"
fldMap_GCC_spans.outputField = GCC_spans_field

fieldMappings_spans.addFieldMap(fldMap_GCC_spans)

# 15. LATITUDE
fldMap_LATITUDE_spans = arcpy.FieldMap()
fldMap_LATITUDE_spans.addInputField(tempfc_Spans, "SPAN_LAT")

LATITUDE_spans_field = fldMap_LATITUDE_spans.outputField
LATITUDE_spans_field.name = "LATITUDE"
LATITUDE_spans_field.aliasName = "LATITUDE"
fldMap_LATITUDE_spans.outputField = LATITUDE_spans_field

fieldMappings_spans.addFieldMap(fldMap_LATITUDE_spans)

# 16. LONGITUDE
fldMap_LONGITUDE_spans = arcpy.FieldMap()
fldMap_LONGITUDE_spans.addInputField(tempfc_Spans, "SPAN_LON")

LONGITUDE_spans_field = fldMap_LONGITUDE_spans.outputField
LONGITUDE_spans_field.name = "LONGITUDE"
LONGITUDE_spans_field.aliasName = "LONGITUDE"
fldMap_LONGITUDE_spans.outputField = LONGITUDE_spans_field

fieldMappings_spans.addFieldMap(fldMap_LONGITUDE_spans)

# 17. PMD
fldMap_PMD_spans = arcpy.FieldMap()
fldMap_PMD_spans.addInputField(tempfc_Spans, "PMD")

PMD_spans_field = fldMap_PMD_spans.outputField
PMD_spans_field.name = "PMD"
PMD_spans_field.aliasName = "PMD"
fldMap_PMD_spans.outputField = PMD_spans_field

fieldMappings_spans.addFieldMap(fldMap_PMD_spans)

arcpy.FeatureClassToFeatureClass_conversion(tempfc_Spans, NEW_circuit_GDB, outSpans, '#', fieldMappings_spans)

### TOWERS CONVERSION


arcpy.AddField_management(tempfc_Towers,'PMD','TEXT',field_length=255)
arcpy.AddField_management(tempfc_Towers,'DIVISION','TEXT',field_length=255)
arcpy.AddField_management(tempfc_Towers,'REGION','TEXT',field_length=255)
arcpy.AddField_management(tempfc_Towers,'COUNTY','TEXT',field_length=255)
arcpy.AddField_management(tempfc_Towers,'CITY','TEXT',field_length=255)
arcpy.AddField_management(tempfc_Towers,'VOLTAGE','TEXT',field_length=255)
arcpy.AddField_management(tempfc_Towers,'STR_GEOTAG','TEXT',field_length=255)

Tower_fields = [field.name for field in arcpy.ListFields(tempfc_Towers)]


print Tower_fields

    # TOWERS FIELD MAP

fieldMappings_towers = arcpy.FieldMappings()

# 1. STR GEOTAG
fldMap_STR_TAG_towers = arcpy.FieldMap()
fldMap_STR_TAG_towers.addInputField(tempfc_Towers, "STR_GEOTAG")

STR_TAG_towers_field = fldMap_STR_TAG_towers.outputField
STR_TAG_towers_field.name = "STR_GEOTAG"
fldMap_STR_TAG_towers.outputField = STR_TAG_towers_field

fieldMappings_towers.addFieldMap(fldMap_STR_TAG_towers)

# 2. LONGITUDE
fldMap_LONG_towers = arcpy.FieldMap()
fldMap_LONG_towers.addInputField(tempfc_Towers, "STR_LON")

LONG_towers_field = fldMap_LONG_towers.outputField
LONG_towers_field.name = "LONGITUDE"
LONG_towers_field.aliasName = "LONGITUDE"
fldMap_LONG_towers.outputField = LONG_towers_field

fieldMappings_towers.addFieldMap(fldMap_LONG_towers)

# 3. LONGITUDE
fldMap_LAT_towers = arcpy.FieldMap()
fldMap_LAT_towers.addInputField(tempfc_Towers, "STR_LAT")

LAT_towers_field = fldMap_LAT_towers.outputField
LAT_towers_field.name = "LATITUDE"
LAT_towers_field.aliasName = "LATITUDE"
fldMap_LAT_towers.outputField = LAT_towers_field

fieldMappings_towers.addFieldMap(fldMap_LAT_towers)

# 4. X
fldMap_X_towers = arcpy.FieldMap()
fldMap_X_towers.addInputField(tempfc_Towers, "STR_X")

X_towers_field = fldMap_X_towers.outputField
X_towers_field.name = "X"
X_towers_field.aliasName = "X"
fldMap_X_towers.outputField = X_towers_field

fieldMappings_towers.addFieldMap(fldMap_X_towers)

# 5. Y
fldMap_Y_towers = arcpy.FieldMap()
fldMap_Y_towers.addInputField(tempfc_Towers, "STR_Y")

Y_towers_field = fldMap_Y_towers.outputField
Y_towers_field.name = "Y"
Y_towers_field.aliasName = "Y"
fldMap_Y_towers.outputField = Y_towers_field

fieldMappings_towers.addFieldMap(fldMap_Y_towers)

# 6. ELEVATION
fldMap_ELEVATION_towers = arcpy.FieldMap()
fldMap_ELEVATION_towers.addInputField(tempfc_Towers, "STR_ELEV")

ELEVATION_towers_field = fldMap_ELEVATION_towers.outputField
ELEVATION_towers_field.name = "ELEVATION"
ELEVATION_towers_field.aliasName = "ELEVATION"
fldMap_ELEVATION_towers.outputField = ELEVATION_towers_field

fieldMappings_towers.addFieldMap(fldMap_ELEVATION_towers)

# 7. VOLTAGE
fldMap_VOLTAGE_towers = arcpy.FieldMap()
fldMap_VOLTAGE_towers.addInputField(tempfc_Towers, "VOLTAGE")

VOLTAGE_towers_field = fldMap_VOLTAGE_towers.outputField
VOLTAGE_towers_field.name = "VOLTAGE"
fldMap_VOLTAGE_towers.outputField = VOLTAGE_towers_field

fieldMappings_towers.addFieldMap(fldMap_VOLTAGE_towers)

# 8. LINE_ID
fldMap_LINE_ID_towers = arcpy.FieldMap()
fldMap_LINE_ID_towers.addInputField(tempfc_Towers, "LINE_NBR")

LINE_ID_towers_field = fldMap_LINE_ID_towers.outputField
LINE_ID_towers_field.name = "LINE_ID"
LINE_ID_towers_field.aliasName = "LINE_ID"
fldMap_LINE_ID_towers.outputField = LINE_ID_towers_field

fieldMappings_towers.addFieldMap(fldMap_LINE_ID_towers)

# 10. LINE_NAME
fldMap_LINE_NAME_towers = arcpy.FieldMap()
fldMap_LINE_NAME_towers.addInputField(tempfc_Towers, "LINE_NAME")

LINE_NAME_towers_field = fldMap_LINE_NAME_towers.outputField
LINE_NAME_towers_field.name = "LINE_NAME"
LINE_NAME_towers_field.aliasName = "LINE_NAME"
fldMap_LINE_NAME_towers.outputField = LINE_NAME_towers_field

fieldMappings_towers.addFieldMap(fldMap_LINE_NAME_towers)

# 11. PMD

fldMap_PMD_towers = arcpy.FieldMap()
fldMap_PMD_towers.addInputField(tempfc_Towers, "PMD")

PMD_towers_field = fldMap_PMD_towers.outputField
PMD_towers_field.name = "PMD"
fldMap_PMD_towers.outputField = PMD_towers_field

fieldMappings_towers.addFieldMap(fldMap_PMD_towers)

# 12. DIVISION
fldMap_DIVISION_towers = arcpy.FieldMap()
fldMap_DIVISION_towers.addInputField(tempfc_Towers, "DIVISION")

DIVISION_towers_field = fldMap_DIVISION_towers.outputField
DIVISION_towers_field.name = "DIVISION"
fldMap_DIVISION_towers.outputField = DIVISION_towers_field

fieldMappings_towers.addFieldMap(fldMap_DIVISION_towers)

# 13. REGION
fldMap_REGION_towers = arcpy.FieldMap()
fldMap_REGION_towers.addInputField(tempfc_Towers, "REGION")

REGION_towers_field = fldMap_REGION_towers.outputField
REGION_towers_field.name = "REGION"
fldMap_REGION_towers.outputField = REGION_towers_field

fieldMappings_towers.addFieldMap(fldMap_REGION_towers)

# 14. COUNTY
fldMap_COUNTY_towers = arcpy.FieldMap()
fldMap_COUNTY_towers.addInputField(tempfc_Towers, "COUNTY")

COUNTY_towers_field = fldMap_COUNTY_towers.outputField
COUNTY_towers_field.name = "COUNTY"
fldMap_COUNTY_towers.outputField = COUNTY_towers_field

fieldMappings_towers.addFieldMap(fldMap_COUNTY_towers)

# 15. CITY
fldMap_CITY_towers = arcpy.FieldMap()
fldMap_CITY_towers.addInputField(tempfc_Towers, "CITY")

CITY_towers_field = fldMap_CITY_towers.outputField
CITY_towers_field.name = "CITY"
fldMap_CITY_towers.outputField = CITY_towers_field

fieldMappings_towers.addFieldMap(fldMap_CITY_towers)

# 16. VOLTAGE
fldMap_ACQ_DATE_towers = arcpy.FieldMap()
fldMap_ACQ_DATE_towers.addInputField(tempfc_Towers, "ACQ_DATE")

ACQ_DATE_towers_field = fldMap_ACQ_DATE_towers.outputField
ACQ_DATE_towers_field.name = "ACQ_DATE"
ACQ_DATE_towers_field.aliasName = "ACQ_DATE"
fldMap_ACQ_DATE_towers.outputField = ACQ_DATE_towers_field

fieldMappings_towers.addFieldMap(fldMap_ACQ_DATE_towers)

arcpy.FeatureClassToFeatureClass_conversion(tempfc_Towers, NEW_circuit_GDB, outTowers, "#", fieldMappings_towers)

arcpy.Delete_management (NEW_TTs_ATTRIB)
arcpy.Delete_management (erased_VPs)
arcpy.Delete_management("in_memory")
arcpy.Delete_management (merged_TTs)