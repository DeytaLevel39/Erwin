#This will update an Erwin Model Entity definitions from an Excel spreadsheet
import win32com.client as win32
from openpyxl import load_workbook
import os
wb_filename=os.environ['WB_FILENAME']
wb = load_workbook(wb_filename)
ws = wb['Entities']
rows = tuple(ws.rows)

#Create COM object
scapi = win32.Dispatch('AllFusionERwin.SCAPI')
pathname=os.environ['PATHNAME']
erwin_filename=os.environ['ERWIN_FILENAME']
newfilename=pathname+"Updated "+erwin_filename
#Build a connection to the model in the persistent device
scPUnit = scapi.PersistenceUnits.Add(pathname+erwin_filename,"RDO=yes")
#Create
# a connection to access model data in memory
scSession = scapi.Sessions.Add()
scSession.Open(scPUnit,0,0)
# 
scTranId = scSession.BeginTransaction()


#Collect all of the Entities in the Erwin Data Model
scMObjects = scSession.ModelObjects.Collect(scSession.ModelObjects.Root,'Entity')

# Collect all of the validation rules, if any exist
try:
    scValidRulesObjs = scSession.ModelObjects.Collect(scSession.ModelObjects.Root, "Validation_Rule")
    print("Collected Validation rules")
except:
    print("Unable to collect validation rules")


#Update the entity definition from the spreadsheet
for (id, subject_area, name, desc) in rows:
    # Process all of the rows apart from the header row and where the entity should not be hidden
    if name.value != "Entity Name":
        #Try and find an existing Entity in the model with the same name
        try:
            scObj = scMObjects.Item(name.value, "Entity")
        except:
            #Otherwise create a new entity
            scObj = scSession.ModelObjects.Add("Entity")
            scObj.Properties("Name").Value = name.value
            scObj.Properties('Definition').Value = str(desc.value)
            print("Creating Entity "+scObj.Properties("Name").Value)

        try:
            # If there is a 'Is_Physical_Only' property and it's false then we need to include the entity
            if scObj.Properties('Is_Physical_Only').Value == False:
                if id.value == scObj.Properties('Long_Id').Value:
                    # The value of the Definition property
                    scObj.Properties('Definition').Value = str(desc.value)
                    print("Updating definition for Entity " + scObj.Properties("Name").Value)
        # If there is no 'Is Physical Only' property then we also need to include the entity
        except:
            if id.value == scObj.Properties('Long_Id').Value:
                # The value of the Definition property
                scObj.Properties('Definition').Value = str(desc.value)
                print("Updating definition for Entity " + scObj.Properties("Name").Value)
        scObj.Properties('Is_Logical_Only').Value = False

#Lets update the attributes
for sheet in wb.worksheets:
    if sheet.title == "Attributes":
        #Gather up all of the attributes from the spreadsheet
        rows=tuple(sheet.rows)
        for (entity_id, entity, attribute_id, attribute, defn, datatype, pk, nullable, validation_rule) in rows:
            #Ignore the header row
            if attribute_id.value != "Attribute ID":
                # Create an object for the Entity
                print("Creating or updating attributes for entity "+entity.value)
                scEntObj = scSession.ModelObjects.Item(entity_id.value, "Entity")
                # Collect all of the entity's attributes
                scAttrObj = scSession.ModelObjects.Collect(scEntObj, "Attribute")
                #Search to see if attribute already exists
                try:
                    oAttObject = scAttrObj.Item(attribute_id.value, "Attribute")
                    #If there's no existing attribute then add it
                except:
                    oAttObject = scAttrObj.Add("Attribute")
                    oAttObject.Properties("Name").Value = attribute.value
                    print("Creating Attribute " + oAttObject.Properties("Attribute").Value + " for Entity "+sheet.title)
                #In either case update the other properties
                if pk.value=="Primary Key":
                    oAttObject.Properties("Type").Value = 0
                else:
                    oAttObject.Properties("Type").Value = 100
                if nullable.value=="Null":
                    oAttObject.Properties("Null_Option_Type").Value = 0
                else:
                    oAttObject.Properties("Null_Option_Type").Value = 1
                oAttObject.Properties("Logical_Data_Type").Value = datatype.value.upper()
                oAttObject.Properties("Is_Logical_Only").Value = False
                if defn.value:
                    oAttObject.Properties("Definition").Value = defn.value
                print("Updating properties for Attribute " + oAttObject.Properties("Name").Value + " for Entity " + sheet.title)

                #If there is a validation rule associated with this attribute
                if validation_rule.value:
                    #Look to see if a validation rule has been created already
                    try:
                        scValidRule = scValidRulesObjs.Item(name.value + "_Validation_Rule", "Validation_Rule")
                        print("Found existing Validation Rule " + name.value + "_Validation_Rule")
                    #Otherwise create a new validation rule
                    except:
                        scValidRule = scValidRulesObjs.Add("Validation_Rule")
                        scValidRule.Properties("Name").Value = name.value + "_Validation_Rule"
                        scValidRule.Properties("Type").Value = 0
                        print("Adding a Validation Rule placeholder for "+name.value + "_Validation_Rule")

                    #Add a valid value for the validation rule

                    # Collect all of the Valid values for the validation rule, if any exist
                    try:
                        scValidValueObjs = scSession.ModelObjects.Collect(scValidRule, "Valid_Value")
                        for scValidValue in scValidValueObjs:
                                print("Collected validation rule value " + scValidValue.Properties("Name").Value+" for "+name.value + "_Validation_Rule")
                    #Otherwise Add the validation rule value
                    except:
                        pass

                    scValidValue = scValidValueObjs.Add("Valid_Value")
                    scValidValue.Properties("Name").Value = validation_rule.value
                    print("Added Validation rule value:- "+validation_rule.value+ " for "+name.value + "_Validation_Rule")

print("Committing changes")
scSession.CommitTransaction(scTranId)

#Save as a new file
print("Saving changes to "+newfilename)
scPUnit.Save(newfilename,'OVF=yes')