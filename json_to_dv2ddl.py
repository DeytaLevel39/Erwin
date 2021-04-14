from erwin_to_json import fetch_model
model = fetch_model()

primary_keys = []

def create_dv2_hub(entity):
    entity_name = entity["Entity Name"].replace(" ","_").upper()
    table_stmt = "CREATE TABLE %s_HUB\n("%entity_name
    for attribute in entity["Attributes"]:
        if attribute["Primary Key Flag"]=="Primary Key":
            primary_keys.append([entity_name,attribute["Attribute Name"].replace(" ","_").upper(), attribute["Attribute Data Type"], attribute["Not Null Flag"].upper()])
            table_stmt += "\n\t%s %s %s" % (attribute["Attribute Name"].replace(" ","_").upper(), attribute["Attribute Data Type"], attribute["Not Null Flag"].upper())
    table_stmt += ",\n\tLOAD_DATE DATE NOT NULL,\n\tSOURCE VARCHAR(100) NOT NULL,\n"
    table_stmt += "\t%s_HASH CHAR(64) NOT NULL\n);\n"%entity_name
    print(table_stmt)

def create_dv2_sat(entity):
    for attribute in entity["Attributes"]:
        table_stmt = "CREATE TABLE %s_SAT\n("%entity["Entity Name"].replace(" ","_").upper()
        for attribute in entity["Attributes"]:
            if attribute["Primary Key Flag"]!="Primary Key":
                table_stmt += "\n\t%s %s %s" % (attribute["Attribute Name"].replace(" ","_").upper(), attribute["Attribute Data Type"], attribute["Not Null Flag"].upper())
        table_stmt += ",\n\tLOAD_DATE DATE NOT NULL,\n\tSOURCE VARCHAR(100) NOT NULL"
        table_stmt += ",\n\tEFFECTIVE_FROM DATE NOT NULL"
        table_stmt += ",\n\tEFFECTIVE_TO DATE NULL"
        table_stmt += ",\n\t%s_HASH CHAR(64) NOT NULL"%(entity["Entity Name"].replace(" ","_").upper())
        table_stmt += ",\n\t%s_SK IDENTITY NOT NULL"%(entity["Entity Name"].replace(" ","_").upper())
        table_stmt += ",\n\tHASHDIFF CHAR(64) NOT NULL\n);\n"
    print(table_stmt)

def create_dv2_rels(entity):
    for subject_area in model["Subject Areas"]:
        for entity in subject_area["Entities"]:
            entity_name = entity["Entity Name"].replace(" ","_").upper()
            sql = """
            SELECT distinct
            TRAN(R.Long_Id) "Relationship ID",
            P.NAME AS 'PARENT',
            R.PARENT_TO_CHILD_VERB_PHRASE AS 'RELATIONSHIP',
            C.NAME AS CHILD
            FROM M0.RELATIONSHIP R INNER JOIN M0.ENTITY P
            ON R.PARENT_ENTITY_REF = P.ID@
            INNER JOIN M0.ENTITY C
            ON R.CHILD_ENTITY_REF = C.ID@
            WHERE C.HIDE_IN_LOGICAL is null
            AND P.HIDE_IN_LOGICAL is null
            AND UPPER(P.NAME) = '%s'
            ORDER by 2,4
            """%entity_name

            relationships = extract_defs("Relationships",sql)
            table_stmt=""
            for rel in relationships:
                parent = rel["PARENT"].replace(" ","_").upper()
                child = rel["CHILD"].replace(" ","_").upper()
                table_stmt = "CREATE TABLE %s_%s_LINK\n(\n"%(parent,child)
                table_stmt += "\t%s_%s_HASH CHAR(64) NOT NULL,\n"%(parent,child)
                table_stmt += "\t%s_HASH CHAR(64) NOT NULL,\n" % (parent)
                table_stmt += "\t%s_HASH CHAR(64) NOT NULL,\n" % (child)
            if len(table_stmt) > 0:
                table_stmt += "\tLOAD_DATE DATE NOT NULL,\n\tSOURCE VARCHAR(100) NOT NULL\n"
                table_stmt += ")\n"
                print(table_stmt)

def create_dv2_model(model):
    for subject_area in model["Subject Areas"]:
        for entity in subject_area["Entities"]:
            create_dv2_hub(entity)
            create_dv2_sat(entity)
    create_dv2_rels(model)

create_dv2_model(model)
