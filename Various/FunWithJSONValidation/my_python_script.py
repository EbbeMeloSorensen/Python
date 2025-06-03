#import pandas as pd
#import plotly
#import seaborn
#import SQLAlchemy
#import geopandas
import json
import jsonschema
from jsonschema import validate
from lxml import etree

def validate_json(json_file_path, schema_file_path):
    # Load the schema
    with open(schema_file_path, 'r') as schema_file:
        schema = json.load(schema_file)

    # Load the data
    with open(json_file_path, 'r') as json_file:
        data = json.load(json_file)

    try:
        validate(instance=data, schema=schema)
        print(f"✅ JSON is valid according to the schema: {json_file_path}")
    except jsonschema.exceptions.ValidationError as err:
        print(f"❌ JSON is invalid: {json_file_path}")
        print("Error:", err.message)

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
    # with open('myjsonfile.json', 'r', encoding='utf8') as f:
    #     json_document = json.load(f)

    # # Then I'm gonna validate it against the json schema
    # with open('schema_manually_corrected.json', 'r', encoding='utf8') as f:
    #     json_schema = json.load(f)

    # Also gonna try with xml
    validate_xml('books.xml', 'books.xsd')

    json_schema_file = 'schema_manually_corrected.json'

    validate_json('creatures_valid.json', json_schema_file)
    validate_json('creatures_invalid_enum_out_of_range.json', json_schema_file)
    validate_json('creatures_invalid_required_property_missing.json', json_schema_file)    