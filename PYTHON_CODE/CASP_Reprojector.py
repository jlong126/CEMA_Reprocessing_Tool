import os, arcpy, re, math
from collections import defaultdict


# FUNCTIONS
def split_following_num(s):
    prev_char = ''
    for i, char in enumerate(s):
        if char == '_' and prev_char in '0123456789':
            return s[:i].upper()
        prev_char = char
        
#  PARAMETERS
OLD_GDBs = arcpy.GetParameterAsText(0)
OUTPUT_FOLDER = arcpy.GetParameterAsText(1)
Projection = arcpy.GetParameterAsText(2)

sr = os.path.abspath(Projection)

#sr = arcpy.SpatialReference()

#str_proj = sr.loadFromString(str(Projection))

arcpy.AddMessage("{}       THIS IS PROJECTION".format(Projection))

#sr = arcpy.SpatialReference(Projection)

#arcpy.AddMessage("%s"%(str(sr)))

REPROJECT_UPDATED_FOLDER = os.path.join(OUTPUT_FOLDER,"CASP_REPROJECTED_GDBs")

if not os.path.exists(REPROJECT_UPDATED_FOLDER):
    os.makedirs(REPROJECT_UPDATED_FOLDER)

circuit_old_GDBs = sorted(OLD_GDBs.split(";"))


for old_GDB in circuit_old_GDBs:

  cirNAME = split_following_num(os.path.basename(old_GDB))
  
  arcpy.AddMessage("....%s Updated Reprojected Geodatabase is being created....\n"%(cirNAME))
  arcpy.CreateFileGDB_management(REPROJECT_UPDATED_FOLDER, cirNAME +  "_CEMA_2015")

UPDATE_FINAL_GDBs_List = []
arcpy.env.workspace = REPROJECT_UPDATED_FOLDER
for file in arcpy.ListFiles("*.gdb"):
    UPDATE_FINAL_GDBs_List.append(file)
    
    
    
for old_GDB, update_GDB in zip(circuit_old_GDBs,UPDATE_FINAL_GDBs_List):

  cirNAME = split_following_num(os.path.basename(old_GDB))
  
  inTTs = os.path.join(old_GDB,"%s_CEMA_2015_TreeTops_AF" % (cirNAME))
  outTTs = os.path.join(update_GDB,"%s_CEMA_2015_TreeTops_AF" % (cirNAME))
  
  inSpans = os.path.join(old_GDB,"%s_CEMA_2015_Spans" % (cirNAME))
  outSpans = os.path.join(update_GDB,"%s_CEMA_2015_Spans" % (cirNAME))
  
  inVPs = os.path.join(old_GDB,"%s_CEMA_2015_VegPolys" % (cirNAME))
  outVPs = os.path.join(update_GDB,"%s_CEMA_2015_VegPolys" % (cirNAME))
  
  inTwrs = os.path.join(old_GDB,"%s_CEMA_2015_Towers" % (cirNAME))
  outTwrs = os.path.join(update_GDB,"%s_CEMA_2015_Towers" % (cirNAME))
  
  arcpy.AddMessage("....%s Reprojecting TreeTops AF...\n"%(cirNAME))
  arcpy.Project_management (inTTs, outTTs, Projection)
  
  arcpy.AddMessage("....%s Reprojecting Spans...\n"%(cirNAME))
  arcpy.Project_management (inSpans, outSpans, Projection)
  
  arcpy.AddMessage("....%s Reprojecting VegPolys..\n"%(cirNAME))
  arcpy.Project_management (inVPs, outVPs, Projection)
  
  arcpy.AddMessage("....%s Reprojecting Towers...\n"%(cirNAME))
  arcpy.Project_management (inTwrs, outTwrs, Projection)
