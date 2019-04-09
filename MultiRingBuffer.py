import arcpy
import os

#Create a new .gdb that acts as a temporary workspace
out_folder_path = "D:\\PeterWhitman_Data\\Projects\\SpaceTime\\"
out_name = "Tmp.gdb"
arcpy.CreateFileGDB_management(out_folder_path, out_name)

#Define your temporary workspace, study area, and input points
Input_Points = "D:\\PeterWhitman_Data\\Projects\\SpaceTime\\For_Peter\\PresencePoints.shp"
Projected_Points = "D:\\PeterWhitman_Data\\Projects\\SpaceTime\\Test.gdb\\Projected_Points"
Temp_Workspace = out_folder_path + out_name 
Study_Area = "D:\\PeterWhitman_Data\\Projects\\SpaceTime\\Test.gdb\\StudyArea"

#Project input points
out_coordinate_system = arcpy.SpatialReference('NAD 1983 BC Environment Albers')
arcpy.Project_management(Input_Points, Projected_Points, out_coordinate_system)

#Split points by UniqueID and save in temporary workspace
arcpy.SplitByAttributes_analysis(Projected_Points, Temp_Workspace, "UniqueID")

#Iterate through points create multiring buffer and clip by study area
arcpy.env.workspace = Temp_Workspace
fclist = arcpy.ListFeatureClasses()
for fc in fclist:
    fcName = os.path.splitext(fc)[0] #log the name of the input feature class
    search = arcpy.SearchCursor(fc)
    for row in search:
         IsoYear = row.getValue("DOS_Year_y")

    MultiRingName = "D:\\PeterWhitman_Data\\Projects\\SpaceTime\\Tmp.gdb\\MultiRing_" + fcName #Name of the multiring buffer
    arcpy.MultipleRingBuffer_analysis(fc, MultiRingName, "1;2", "Kilometers", "distance", "ALL", "FULL") #Multiring buffer

    arcpy.AddField_management(MultiRingName, "IsolationYear", "SHORT")
    arcpy.CalculateField_management(MultiRingName, "IsolationYear", IsoYear, "PYTHON_9.3")
    arcpy.AddField_management(MultiRingName, "OrigID", "TEXT") #Add a new field to each buffer
    term = "'%s'" % fcName #Add double quotation marks around single quotation marks
    arcpy.CalculateField_management(MultiRingName, "OrigID", term, "PYTHON_9.3") #Populate new field with the name of the feature class (Input_Points ObjectID)

    ClippedName = "D:\\PeterWhitman_Data\\Projects\\SpaceTime\\Tmp.gdb\\ClippedRing_" + fcName #Name of the clipped multiring buffer
    arcpy.Clip_analysis(MultiRingName, Study_Area, ClippedName, "") #Clip multiring buffer by study area

#Merge clipped rings and then cross tabulate second variable
#arcpy.Merge_management(fclist2, Merged_Rings)

fclist2 = arcpy.ListFeatureClasses("ClippedRing*") #Create list of clipped multiring buffers
for fc in fclist2:
    fcName = os.path.splitext(fc)[0]
    OutputTable = "D:\\PeterWhitman_Data\\Projects\\SpaceTime\\Tmp.gdb\\OutputTable_" + fcname
    Second_Variable = "D:\\PeterWhitman_Data\\Projects\\SpaceTime\\Test.gdb\\HarvestPolygon"
    arcpy.TabulateIntersection_analysis(fc, "IsolationYear;OrigID;distance", Second_Variable, OutputTable, "gridcode", "", "", "UNKNOWN") #Tabulate deforestation area by year

    CrossTabulationPath = "D:\\PeterWhitman_Data\\Projects\\SpaceTime\\"
    TableName = "CrossTabulation_" + fcname + ".dbf"
    arcpy.TableToTable_conversion(OutputTable, CrossTabulationPath, TableName)
