#import pandas as pd
#import plotly
#import seaborn
#import SQLAlchemy
#import geopandas
import json
import jsonschema
from lxml import etree

def validate_xml(xml_file_path, xsd_file_path):
    try:
        # Parse the XML schema
        with open(xsd_file_path, 'rb') as schema_file:
            schema_doc = etree.XML(schema_file.read())
            schema = etree.XMLSchema(schema_doc)

        # Parse the XML file
        with open(xml_file_path, 'rb') as xml_file:
            xml_doc = etree.XML(xml_file.read())

        # Validate
        schema.assertValid(xml_doc)
        print("✅ The XML file is valid according to the XSD schema.")

    except etree.DocumentInvalid as e:
        print("❌ XML is not valid:")
        print(e)
    except Exception as e:
        print("⚠️ An error occurred:")
        print(e)
if __name__ == '__main__':

    print("Fun with xml validation")

    # First, I'm just gonna read a json file
    with open('myjsonfile.json', 'r', encoding='utf8') as f:
        file_contents = json.load(f)

    print(file_contents)




