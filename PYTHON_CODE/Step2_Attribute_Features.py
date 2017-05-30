import arcpy, sys, os, re
from collections import deque as dq
from collections import namedtuple
from collections import defaultdict
arcpy.env.overwriteOutput = 1
arcpy.Delete_management("in_memory")


## ARC Parameters
"""Bay_Area_ref = arcpy.GetParameterAsText(0)

INPUT_inSITE_Ready_GDBs = arcpy.GetParameterAsText(1)
GCC_input = arcpy.GetParameterAsText(2)"""


def split_following_num(s):
    prev_char = ''
    for i, char in enumerate(s):
        if char == '_' and prev_char in '0123456789':
            return s[:i].upper()
        prev_char = char

def SJattributes_dict(infc, sjfc, matchOption, searchRadius, fields):
    tempfc_in = r'in_memory\tempfc_in'
    tempfc_out = r'in_memory\tempfc_out'
    # tempfc_out = path.join(inGDB, 'tempfc_out')
    arcpy.Delete_management(tempfc_in)
    arcpy.Delete_management(tempfc_out)

    arcpy.FeatureClassToFeatureClass_conversion(infc, os.path.dirname(tempfc_in), os.path.basename(tempfc_in))
    arcpy.SpatialJoin_analysis(tempfc_in, sjfc, tempfc_out, match_option=matchOption, search_radius=searchRadius)
    return {row[-1]: row[:-1] for row in arcpy.da.SearchCursor(tempfc_out, fields + ['TARGET_FID'])}


def calc_geotag(lat, lon):
    if lat < 0:
        suffix = 'S'
        s_lat = str(lat).split('.')[0].zfill(3) + '.' + str(lat).split('.')[1]
    elif lat > 0:
        suffix = 'N'
        s_lat = str(lat).split('.')[0].zfill(2) + '.' + str(lat).split('.')[1]
    if lon < 0:
        prefix = 'W'
        s_lon = str(lon).split('.')[0].zfill(4) + '.' + str(lon).split('.')[1]
    elif lon > 0:
        prefix = 'E'
        s_lon = str(lon).split('.')[0].zfill(3) + '.' + str(lon).split('.')[1]

    return '{}{}{}{}'.format(prefix, ''.join([i for i in str(s_lon) if i not in '-.'])[:8], suffix,
                             ''.join([i for i in str(s_lat) if i not in '-.'])[:7])

def sub_zip(F1,F2):
    Z1 = dq(maxlen=1)
    Z2 = dq(maxlen=1)
    Z1.append(F1)
    Z2.append(F2)
    return list(Z1), list(Z2)

## Hardcode Parameters

kv_dict = {02: 2, 04: 4, 11: 12, 22: 21, 21: 21, 12: 12,17:17}

# Arc Parameters
CoordSys = arcpy.SpatialReference(4326)
Cir_GDB = arcpy.GetParameterAsText(0)
BAY_REF_GDB = arcpy.GetParameterAsText(1)



cirNAME = split_following_num(os.path.basename(Cir_GDB))
cirPAT = str(re.findall('\d+', cirNAME)[:2])
cirNUM = int(cirPAT[3:5])

arcpy.AddMessage(cirNAME)

TTs = os.path.join(Cir_GDB,'%s_CEMA_2015_TreeTops_AF' % (cirNAME))
Towers = os.path.join(Cir_GDB,"%s_CEMA_2015_Towers"%(cirNAME))
VegPolys = os.path.join(Cir_GDB,"%s_CEMA_2015_VegPolys"%(cirNAME))
Spans = os.path.join(Cir_GDB,"%s_CEMA_2015_Spans"%(cirNAME))


refSRA = os.path.join(BAY_REF_GDB, 'SRA15_1')
refCity = os.path.join(BAY_REF_GDB, 'PGE_VMD_Cities_Boundaries')
refCnty = os.path.join(BAY_REF_GDB, 'PGE_VMD_Counties_with_Code')
refDivs = os.path.join(BAY_REF_GDB, 'PGE_VM_Divisions_with_Code')
refRegs = os.path.join(BAY_REF_GDB, 'Region_Reference')
ref_PGE = os.path.join(BAY_REF_GDB, 'PG_E_BAY_AREA_INITIAL_CIRCUITS_JL_030717')
refAPN = os.path.join(BAY_REF_GDB, 'PARCEL_DATA')

cities_dict = {}
with arcpy.da.SearchCursor(refCity,["CODE","CITY"]) as sCur:
    for row in sCur:
        cities_dict[row[0]] = row[1]

## Attrib TreeTops


TW_city = SJattributes_dict(TTs, refCity, matchOption='CLOSEST', searchRadius='100 MILES', fields=['CODE'])
TW_cnty = SJattributes_dict(TTs, refCnty, matchOption='INTERSECT', searchRadius=None, fields=['CODE'])
TW_divs = SJattributes_dict(TTs, refDivs, matchOption='INTERSECT', searchRadius=None, fields=['CODE'])
TW_regs = SJattributes_dict(TTs, refRegs, matchOption='INTERSECT', searchRadius=None, fields=['CODE'])
TT_SRA = SJattributes_dict(TTs, refSRA, matchOption='INTERSECT', searchRadius=None,fields=['SRA'])
TT_APNs = SJattributes_dict(TTs, refAPN, matchOption='CLOSEST', searchRadius='30 FEET',
                            fields=['APN', 'MAIL_NBR',"MAIL_DIR","MAIL_STR","MAIL_MODE", 'OWN1_LAST','OWN1_FRST','OWN2_LAST','OWN2_FRST'])

### Universal Fields
            #    0            1          2        3         4      5       6         7           8
TTs_Fields = ["FALL_IN", "FI_D2W", "GCC200", "SRA_LRA", "CITY", "OID@", "VOLTAGE", "SPAN_ID", "SPAN_TAG",
              #  9       10       11       12     13        14       15
              "LINE_ID", "HEALTH", "D2W_AF", "OH", "DIVISION", "REGION", "COUNTY",
              #      16          17         18      19           20         21         22        23
              "LINE_NAME", "ACQ_DATE", "LATITUDE", "LONGITUDE", "SHAPE@", "TREEID", "FALL_IN", "DC_AF",
              #    24       25        26         27      28     29              30         31        32           33          34
              "DC_FI", "OH_D2W", "DC_VENDOR", "UG_D2W","PMD","APN_NUMBER","STREET_NUM","STREET","CUSTOMER_P","CUSTOMER_N","CUSTOMER_1"]



ATTRIBUTES = namedtuple("ATTRIBUTES",['LINE_ID','LINE_NAME','ACQ_DATE'])

Constants = None
with arcpy.da.SearchCursor(TTs, TTs_Fields) as sCur:
    for row in sCur:
        Constants = (ATTRIBUTES(row[9], row[16], row[17]))


arcpy.AddMessage("......Attributing TreeTops.......")

with arcpy.da.UpdateCursor(TTs, TTs_Fields) as uCur:
    for row in uCur:
        oid = row[5]
        #row[0] = 'NO' if row[1] > -5 else 'YES'
        row[2] = None
        row[3] = 'SRA' if TT_SRA[oid][0] == 'SRA' or TT_SRA[oid][0] == 'FRA'  else 'LRA'

        row[4] = (TW_city[oid][0])
        row[4] = cities_dict[row[4]]
        row[6] = kv_dict[cirNUM]
        #row[7] = info[cirNAME]["Circuit_ID"] + '+' + row[8]

        #row[10] = str(row[10]).split(".")[0] + "." + str(row[10]).split(".")[1][:1]
        #row[11] = str(row[11]).split(".")[0] + "." + str(row[11]).split(".")[1][:1]

        row[13] = TW_divs[oid][0]
        row[14] = TW_regs[oid][0]
        row[15] = str(TW_cnty[oid][0])

        row[9] = Constants.LINE_ID
        row[16] = Constants.LINE_NAME
        row[17] = Constants.ACQ_DATE

        pnt_coord = row[20].projectAs(CoordSys)
        row[18] = pnt_coord.centroid.Y
        row[19] = pnt_coord.centroid.X
        row[21] = str(row[21]).replace("E","W")
        row[22] =  'YES' if row[1] != 9999 else 'NO'
        if row[11]  == 0:
            row[11] = 9999

        if row[27] == 0:
            row[27] = 9999
        ## grow-in ranking


        for r in zip(sub_zip(row[11],row[27])[0],sub_zip(row[11],row[27])[1]):
            #arcpy.AddMessage("{}      ".format(r))
            if min(r) <= 2.0:
                row[23] = 'ZONE1'
            elif min(r) <= 4.0:
                row[23] = 'ZONE2'
            elif min(r) <= 6.0:
                row[23] = 'ZONE3'
            elif min(r) <= 15.0:
                row[23] = 'ZONE4'
            else:
                row[23] = None


        """
        if min(row[11] ,row[26]) <= 2.0:
            row[23] = 'ZONE1'
        elif min(row[11] ,row[26]) <= 4.0:
            row[23] = 'ZONE2'
        elif min(row[11] ,row[26]) <= 6.0:
            row[23] = 'ZONE3'
        elif min(row[11] ,row[26]) <= 15.0:
            row[23] = 'ZONE4'
        else:
            row[23] = None"""
        # OH
        if row[25] <=0:
            row[12] = None
        elif row[25] <= 6:
            row[12] = '_OH2'
        elif row[25] <=15:
            row[12] = '_OH1'
        else:
            row[12] = None

        if row[12]:
            if row[23]:
                row[23] += row[12]
            else:
                row[23] = 'ZONE0_OH'

        row[24] = 'FI_' + '0' if row[1] != 9999 else None

        row[26] = row[23].replace('ONE', '').replace('_', '') if row[23] else row[23]
        row[26] = row[26] + row[24] if (row[24] and row[26]) else filter(lambda r: r, (row[26], row[24]))[0]
        row[26] = row[26].replace('_', '')

        row[28] = None

        ### APN ATTRIBUTING
        apn = TT_APNs[oid]
        row[29] = apn[0] if apn[0] else None
        if row[30]:
            for r in zip(sub_zip(apn[1],apn[2])[0],sub_zip(apn[1],apn[2])[1]):
                row[30] = str(r[0]) + " " + str(r[1])
        else:
            row[30] = None

        if row[31]:
            for r in zip(sub_zip(apn[3], apn[4])[0], sub_zip(apn[3], apn[4])[1]):
                row[31] = str(r[0]) + " " + str(r[1])
        else:
            row[31] = None

        if row[33]:
            for r in zip(sub_zip(apn[6],apn[5])[0],sub_zip(apn[6],apn[5])[1]):
                row[33] = str(r[0]) + " " + str(r[1])
        else:
            row[33] = None


        if row[34]:
            for r in zip(sub_zip(apn[8],apn[7])[0],sub_zip(apn[8],apn[7])[1]):
                row[34] = str(r[0]) + " " + str(r[1])
        else:
            row[34] = None



        uCur.updateRow(row)

arcpy.DeleteField_management(TTs,["OH_D2W"])

# ATTRIBUTE TOWERS
arcpy.AddMessage("......Attributing Towers.......")

Tower_Fields = ["OID@","VOLTAGE","DIVISION","REGION","COUNTY","CITY","STR_GEOTAG","LONGITUDE","LATITUDE"]

TWR_city = SJattributes_dict(Towers, refCity, matchOption='CLOSEST', searchRadius='100 MILES', fields=['CODE'])
TWR_cnty = SJattributes_dict(Towers, refCnty, matchOption='INTERSECT', searchRadius=None, fields=['CODE'])
TWR_divs = SJattributes_dict(Towers, refDivs, matchOption='INTERSECT', searchRadius=None, fields=['CODE'])
TWR_regs = SJattributes_dict(Towers, refRegs, matchOption='INTERSECT', searchRadius=None, fields=['CODE'])


with arcpy.da.UpdateCursor(Towers, Tower_Fields) as uCur:
    for row in uCur:
        oid = row[0]
        row[1] = kv_dict[cirNUM]
        row[2] = TWR_divs[oid][0]
        row[3] =  TWR_regs[oid][0]
        row[4] = TWR_cnty[oid][0]
        row[5] =  (TWR_city[oid][0])
        row[5] = cities_dict[row[5]]
        row[6] = "W" + (str(row[7])[:10].replace("-","").replace(".","")) + "N" + str(row[8])[:8].replace(".","")

        uCur.updateRow(row)

arcpy.DeleteField_management(Towers,["ELEVATION"])

# ATTRIBUTE VEGPOLYS
arcpy.AddMessage("......Attributing Veg Polys......")

VegPolys_Fields = ["TREEID"]
with arcpy.da.UpdateCursor(VegPolys, VegPolys_Fields) as uCur:
    for row in uCur:
        row[0] = str(row[0]).replace("E", "W")
        uCur.updateRow(row)

# ATTRIBUTE SPANS
###############    0         1          2             3          4        5          6            7        8        9         10
Span_Fields = ["SPAN_TAG","LINE_ID","CIRCUIT_1","LONGITUDE","LATITUDE","LINE_NBR","LINE_NAME","SHAPE@","BST_TAG","AST_TAG","SPAN_ID"]

arcpy.AddMessage("......Attributing Spans.......")

with arcpy.da.UpdateCursor(Spans, Span_Fields,spatial_reference=CoordSys) as uCur:
    for row in uCur:
        #row[0] = "W" + (str(row[3])[:10].replace("-", "").replace(".", "")) + "N" + str(row[4])[:10].replace(".", "")
        row[1] = row[5]
        row[2] = row[6]
        #arcpy.AddMessage(row[7])

        bst,ast = row[7].firstPoint,row[7].lastPoint
        row[8] = calc_geotag(bst.Y,bst.X)
        row[9] = calc_geotag(ast.Y,ast.X)
        row[0] = '-'.join([row[8],row[9]])
        row[10]= str(row[5]+"+"+row[0])
        uCur.updateRow(row)

## SPATIAL JOIN IN MEMORY FC TTs:




tempfc_TTs = r'in_memory\tempfc_in_TTs'

arcpy.SpatialJoin_analysis(TTs, Spans,tempfc_TTs, match_option='CLOSEST', search_radius='1000 FEET',distance_field_name='OFF_')

Spans_Dict = defaultdict(list)
with arcpy.da.SearchCursor(tempfc_TTs, ["TREEID","SPAN_TAG_1","BST_TAG_1","AST_TAG_1","SPAN_ID_1"]) as sCur:
    for row in sCur:
        Spans_Dict[row[0]].append(row[1])
        Spans_Dict[row[0]].append(row[2])
        Spans_Dict[row[0]].append(row[3])
        Spans_Dict[row[0]].append(row[4])
        #arcpy.AddMessage("{}     {}".format(row[0],row[1]))
#arcpy.AddMessage(Spans_Dict.items())

arcpy.Delete_management("in_memory")

with arcpy.da.UpdateCursor(TTs,["TREEID","SPAN_TAG","BST_TAG","AST_TAG","SPAN_ID"]) as uCur:
    for row in uCur:
        if str(row[0]) in Spans_Dict.keys():
            row[1] = Spans_Dict.get(row[0])[0]
            row[2] = Spans_Dict.get(row[0])[1]
            row[3] = Spans_Dict.get(row[0])[2]
            row[4] = Spans_Dict.get(row[0])[3]

        uCur.updateRow(row)

arcpy.MakeFeatureLayer_management (VegPolys,"VegPolys")

arcpy.SelectLayerByLocation_management("VegPolys","INTERSECT",TTs,selection_type="NEW_SELECTION")

arcpy.SelectLayerByLocation_management("VegPolys","INTERSECT",TTs,selection_type="SWITCH_SELECTION")

arcpy.DeleteFeatures_management("VegPolys")



