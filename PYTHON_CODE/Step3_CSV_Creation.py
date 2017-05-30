import csv, arcpy, os, sys

arcpy.env.overwriteOutput = True
arcpy.Delete_management("in_memory")

# INPUTS

INPUT_Final_Del_GDBs= arcpy.GetParameterAsText(0)
outFolder = arcpy.GetParameterAsText(1)


GDB_SPLIT = sorted(INPUT_Final_Del_GDBs.split(";"))

def split_following_num(s):
    prev_char = ''
    for i, char in enumerate(s):
        if char == '_' and prev_char in '0123456789':
            return s[:i]
        prev_char = char


exclude_fields = ('FID', 'OBJECTID', 'Shape')

arcpy.AddMessage("Creating TreeTop Detection CSVs...\n")

for i, circuit_GDB in enumerate(GDB_SPLIT):

    cirNAME = split_following_num(os.path.basename(circuit_GDB))

    cir_csv = os.path.join(outFolder, "%s_CEMA_2015_TreeTops_AF.csv" % (cirNAME))

    inTTs = os.path.join(circuit_GDB, "%s_CEMA_2015_TreeTops_AF" % (cirNAME))

    fields = [field.name for field in arcpy.ListFields(inTTs) if field.name not in exclude_fields]

    arcpy.AddMessage("{0:<60} ({1} of {2})".format(os.path.basename(cir_csv), i + 1, len(GDB_SPLIT)))

    with arcpy.da.SearchCursor(inTTs, fields) as sCur, open(cir_csv, 'wb') as outcsv:
        writer = csv.writer(outcsv)
        writer.writerow(fields)
        for row in sCur:
            records = list(row)
            writer.writerow(records)








