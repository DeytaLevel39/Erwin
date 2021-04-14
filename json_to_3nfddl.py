from erwin_to_json import fetch_model

model = fetch_model()

def create_3nf_model(model):
    ddl = ""
    for subject_area in model["Subject Areas"]:
        for entity in subject_area["Entities"]:
            table_stmt = "CREATE TABLE %s\n("%entity["Entity Name"]
            for index, attribute in enumerate(entity["Attributes"]):
                table_stmt += "\n\t%s %s %s"%(attribute["Attribute Name"],attribute["Attribute Data Type"],attribute["Not Null Flag"].upper())
                if index != len(entity["Attributes"]):
                    table_stmt+=","
            table_stmt+="\n);\n"
            ddl += table_stmt
    return ddl

ddl = create_3nf_model(model)

print(ddl)



