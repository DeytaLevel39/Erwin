import pyodbc, json

# Specifying the ODBC driver, server name, database, etc. directly
cnxn = pyodbc.connect('DSN=erwin_r9_current',server='127.0.0.1')
# Create a cursor from the connection
cursor = cnxn.cursor()

out_json = {}
keys=[]

def fetch_model_name():
    sql = """
    SELECT 
    TRAN(PEn.owner_path) "Model Name"
    FROM M0.Entity Pen
    """

    cursor.execute(sql)
    model_name = cursor.fetchone()[0]

    return model_name

def extract_defs(type_name, sql):
    cursor.execute(sql)

    # Create a worksheet if we're dealing with subject areas, entities or relationships
    #if type_name in ("Subject Areas", "Entities","Relationships"):
    keys = [column[0] for column in cursor.description]

    row_cols={}
    rows= []
    # Fetch and display the rows
    resultset = cursor.fetchall()
    for row in resultset:
        col_ctr=0
        for col in row:
            row_cols[keys[col_ctr]]=col
            col_ctr+=1
        rows.append(dict(row_cols))
    return rows


def fetch_model():
    #fetch all of the subject areas
    sql="""
    SELECT
       TRAN(SA.Long_Id) "Subject Area ID",
       SA.NAME                      'Subject Area',
       Tran(SA.Definition)          'Subject Area Definition' 
    FROM
        SUBJECT_AREA SA
    WHERE SA.Name is not null  
    order By 1
    """

    subject_areas = extract_defs("Subject Areas",sql)

    # fetch all of the entities
    sql = """
    SELECT distinct
       TRAN(PEn.Long_Id) "Entity ID",
       SA.NAME                      'Subject Area',
       replace(Tran(PEn.Physical_Name),'_',' ')      'Entity Name',
       Tran(PEn.Definition)         'Entity Definition' 
    FROM
       Entity PEn
          LEFT JOIN ER_MODEL_SHAPE EMS
            ON EMS.MODEL_OBJECT_REF = PEn.ID@
          LEFT JOIN ER_DIAGRAM ED
            ON ED.ID@ = EMS.OWNER@
          LEFT JOIN SUBJECT_AREA SA
            ON SA.ID@ = ED.OWNER@
    WHERE SA.Name is not null  
    and PEn.hide_in_logical is null
    order By 2,3
                """
    # fetch all of the attributes
    attr_sql = """
    SELECT distinct
    TRAN(PEn.Long_Id) "Entity ID",
    TRAN(PEn.Name) "Entity Name",
    TRAN(PAt.Long_Id) "Attribute ID",
    TRAN(PAt.Name) "Attribute Name",
    TRAN(PAt.Definition) "Attribute Definition",
    TRAN(PAt.Physical_Data_Type) "Attribute Data Type",
    TRAN(PAt.Type) "Primary Key Flag",
    TRAN(PAt.Null_Option_Type) "Not Null Flag",
    vv.name "Validation Rule"
    FROM M0.Entity Pen
    JOIN M0.Attribute Pat ON PAt.owner@ = PEn.Id@
    left join m0.check_constraint_usage ccu
    on Pat.id@ = ccu.owner@
    left join m0.validation_rule vr
    on vr.id@ = ccu.validation_rule_ref
    left join m0.valid_value vv
    on vv.owner@ = vr.id@
    where Pen.hide_in_logical is null
    order by "Entity Name", "Primary Key Flag" desc
                """

    for subject_area in subject_areas:
        subject_area_entities = []
        entities = extract_defs("Entities", sql)
        for entity in entities:
            attributes = extract_defs("Attributes", attr_sql)
            if entity['Subject Area']==subject_area['Subject Area']:
                del entity['Subject Area']
                entity_attributes = []
                for attribute in attributes:
                    if attribute['Entity ID'] == entity['Entity ID']:
                        del attribute['Entity ID']
                        del attribute['Entity Name']
                        entity_attributes.append(attribute)
                entity['Attributes'] = entity_attributes
                subject_area_entities.append(entity)
        subject_area['Entities'] = subject_area_entities

    out_json['Subject Areas'] = subject_areas
    #json_obj = json.dumps(out_json,indent=4)
    return out_json











