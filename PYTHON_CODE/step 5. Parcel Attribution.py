import arcpy, sys, os, re
from collections import deque as dq
from collections import namedtuple
from collections import defaultdict
arcpy.env.overwriteOutput = 1
arcpy.Delete_management("in_memory")


#Functions
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

def sub_zip(F1,F2):
    Z1 = dq(maxlen=1)
    Z2 = dq(maxlen=1)
    Z1.append(F1)
    Z2.append(F2)
    return list(Z1), list(Z2)

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

## Attrib TreeTops


TW_city = SJattributes_dict(TTs, refCity, matchOption='CLOSEST', searchRadius='100 MILES', fields=['CODE'])
TW_cnty = SJattributes_dict(TTs, refCnty, matchOption='INTERSECT', searchRadius=None, fields=['CODE'])
TW_divs = SJattributes_dict(TTs, refDivs, matchOption='INTERSECT', searchRadius=None, fields=['CODE'])
TW_regs = SJattributes_dict(TTs, refRegs, matchOption='INTERSECT', searchRadius=None, fields=['CODE'])
TT_SRA = SJattributes_dict(TTs, refSRA, matchOption='INTERSECT', searchRadius=None,fields=['SRA'])
TT_APNs = SJattributes_dict(TTs, refAPN, matchOption='CLOSEST', searchRadius='30 FEET',
                            fields=['APN', 'MAIL_NBR',"MAIL_DIR","MAIL_STR","MAIL_MODE", 'OWN1_LAST','OWN1_FRST','OWN2_LAST','OWN2_FRST'])

                #    29              30         31        32           33          34
TTs_Fields =   ["APN_NUMBER","STREET_NUM","STREET","CUSTOMER_P","CUSTOMER_N","CUSTOMER_1","OID@"]


with arcpy.da.UpdateCursor(TTs, TTs_Fields) as uCur:
    for row in uCur:

        oid = row[6]
        ### APN ATTRIBUTING
        apn = TT_APNs[oid]
        row[0] = apn[0] if apn[0] else None
        if row[1]:
            for r in zip(sub_zip(apn[1] ,apn[2])[0] ,sub_zip(apn[1] ,apn[2])[1]):
                row[1] = str(r[0]) + " " + str(r[1])
        else:
            row[1] = None

        if row[2]:
            for r in zip(sub_zip(apn[3], apn[4])[0], sub_zip(apn[3], apn[4])[1]):
                row[2] = str(r[0]) + " " + str(r[1])
        else:
            row[2] = None

        if row[4]:
            for r in zip(sub_zip(apn[6] ,apn[5])[0] ,sub_zip(apn[6] ,apn[5])[1]):
                row[4] = str(r[0]) + " " + str(r[1])
        else:
            row[4] = None


        if row[5]:
            for r in zip(sub_zip(apn[8] ,apn[7])[0] ,sub_zip(apn[8] ,apn[7])[1]):
                row[5] = str(r[0]) + " " + str(r[1])
        else:
            row[5] = None


        uCur.updateRow(row)
