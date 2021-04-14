# Erwin
Various Python scripts related to the export & import of metadata to and form CA Erwin 9.x & 2020

* erwin_export.py provides a means of creating a data dictionary from an Erwin LDM/PDM

* erwin_update.py provides the ability to reverse engineer entities, attributes & relationships from an Excel data dictionary

* erwin_to_json.py creates a json metadata file covering subject areas, entites & attributes. After the JSON is created, the informaation contained within allows a 3NF DDL script and a DV2.0 DDL script to be created. Note: These are missing constraints & indexes. There are also challenges in automating the production of a Data Vault 2.0 PDM from an LDM in that for example, a Vehicle Sale in an OLTP database combines info from Vehicle, Dealer & Buyer and adds in Sales Date & Sales Amount info. The automated approach provided treats Vehicle Sale as a Hub table and creates link tables between Vehicle Sale Hub, Dealer Hub, Buyer Hub & Vehicle Hub resulting in 3 link tables required. The more efficient manual modelling technique would treat Vehicle Sale as a Link table with the Sales Date & Sales Amount attributes in a Satellite hanging off the Link table. This reduces the complexity of the raw data vault.
