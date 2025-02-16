import json
import argparse
import pandas as pd
import os
from sqlalchemy import create_engine,text 
from dotenv import load_dotenv
from tabulate import tabulate

load_dotenv(override=True)

USERNAME=os.getenv("USERNAME",None)
PASSWORD=os.getenv("PASSWORD",None)
HOST=os.getenv("HOST",None)
PORT=os.getenv("PORT",1521)
SERVICE_NAME=os.getenv("SERVICE_NAME",None)
SID=os.getenv("SID",None)
TNS_STRING=os.getenv("TNS_STRING",None)

def arguments():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="main_command", title="Main Commands")
    project_parser = subparsers.add_parser("dependency-analyzer", help="Generate Oracle object dependency json mapping")
    project_parser.add_argument("--schemaname", required=True, help="Schema name to generate dependency json")
    project_parser.add_argument("--objectname", required=False, help="Mentioned the object name to get the dependency details")
    project_parser.add_argument("--list-objects", action="store_true", required=False,dest='list_objects', help="Lists all objects with dependencies in the schema")
    project_parser.add_argument("--generate-json", action="store_true", required=False,dest='generate_json', help="Generate Oracle dependency json file")
    project_parser.add_argument("--include-table", action="store_true",default=False, dest='include_table',required=False, help="Include Table objects as part of Dependency, Default False")
    return parser.parse_args()

def database_connection():
    try:
        if HOST and SERVICE_NAME:
            db_url = fr"oracle://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/?service_name={SERVICE_NAME}"
        elif HOST and SID:
            db_url = fr"oracle://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{SID}"
        elif TNS_STRING:
            db_url = f'oracle://{USERNAME}:{PASSWORD}@{TNS_STRING}'
        
        engine = create_engine(db_url)
        conn =  engine.connect()
        if conn:
            return conn
        else:
            raise ValueError("Failed to connect to Databasea")
    except Exception as e:
        raise Exception(f"Error in Oracle Database connection: {e}")
    
def get_dependency_objects(conn,schemaname,includetable):

    try:
        query = r"""SELECT referenced_owner, name, type, referenced_name, referenced_type FROM dba_dependencies WHERE type !='TABLE' and 
                    referenced_type != 'TABLE' AND owner = :schema  AND referenced_owner not in ('SYS','SYSTEM','PUBLIC')AND 
                    type != 'PACKAGE BODY' AND referenced_type != 'PACKAGE BODY'""" if not includetable else r"""SELECT referenced_owner, name, type, referenced_name, referenced_type FROM dba_dependencies WHERE owner = :schema AND referenced_owner not in ('SYS','SYSTEM','PUBLIC') AND type != 'PACKAGE BODY' AND referenced_type != 'PACKAGE BODY'"""
        result = conn.execute(text(query), {"schema": schemaname.upper()}) 
        column_names = result.keys()
        rows = result.fetchall()
        df = pd.DataFrame(rows, columns=column_names)
        df.columns = df.columns.str.upper()
        return df  
    except Exception as e:
        print(fr"Exception occured - get_dependency_objects: {e}")
        return pd.DataFrame()

def get_dependency_objects_all(conn,schemaname,includetable):
    try:
        
        query = r"""SELECT owner, name, type FROM dba_dependencies WHERE type !='TABLE' and 
                    referenced_type != 'TABLE' AND owner IN (:schema) AND referenced_owner not in ('SYS','SYSTEM','PUBLIC')
                    UNION ALL
                    SELECT referenced_owner, referenced_name, referenced_type FROM dba_dependencies WHERE type !='TABLE' and 
                    referenced_type != 'TABLE' AND owner IN (:schema) AND referenced_owner not in ('SYS','SYSTEM','PUBLIC')""" if not includetable else r""" SELECT owner, name, type FROM dba_dependencies WHERE owner IN (:schema) AND referenced_owner not in ('SYS','SYSTEM','PUBLIC')
                    UNION ALL
                    SELECT referenced_owner, referenced_name, referenced_type FROM dba_dependencies WHERE  owner IN (:schema) 
                    AND referenced_owner not in ('SYS','SYSTEM','PUBLIC')""" 
  
        result = conn.execute(text(query), {"schema": schemaname.upper()}) 
        column_names = result.keys()
        rows = result.fetchall()
        
        df = pd.DataFrame(rows, columns=column_names)
        df.columns = df.columns.str.upper()
        objects = df["NAME"].unique().tolist()
        return objects 
    except Exception as e:
        print(fr"Exception occured - get_dependency_objects_all: {e}")
        return None

def get_dependency_data(schemaname,includetable):
    data = get_dependency_objects(conn,schemaname,includetable)
    if data is None:
        raise ValueError("Failed to retrieve dependency data")
    else:
        dependency_data = data.to_dict(orient="records")
        return dependency_data
    
def extract_dependencies(dependency_data, object_name, visited_obj=None):
    try:
        if visited_obj is None:
            visited_obj = set()
            
        if object_name in visited_obj:
            return set()
        
        visited_obj.add(object_name)
        for row in (d for d in dependency_data if d["NAME"] == object_name):
            yield (row["REFERENCED_TYPE"], row["REFERENCED_NAME"])
            yield from extract_dependencies(dependency_data, row["REFERENCED_NAME"], visited_obj) 
    except Exception as e:
        raise Exception(f"Issue while extracting dependency: {e}")
    
def get_dependencies(object_name,schemaname,includetable):
    type_wise_dep = {}
    dependency_data = get_dependency_data(schemaname,includetable)

    for obj_type, obj_name in extract_dependencies(dependency_data, object_name):
        if obj_type not in type_wise_dep:
            type_wise_dep[obj_type] = []
        type_wise_dep[obj_type].append(obj_name)

    if not type_wise_dep:
        print(f"{object_name} object does not exists or no dependencies found in the database")
    print(f"Parent object : {object_name}")
    print("Dependencies ")

    table_data = [[obj_type, len(set(obj_names)), ", ".join(set(obj_names))] for obj_type, obj_names in type_wise_dep.items()]
    print(tabulate(table_data, headers=["Type", "Count", "Names"], tablefmt="grid"))

def list_objects(conn,schemaname,includetable):
    objects = get_dependency_objects_all(conn,schemaname,includetable)
    if len(objects) > 0:
        print(f"Database Objects List : {objects}")
    else:
        print("No objects found")

def generate_dependency_json(object_name, dependency_data):
    def build_node(name, type, visited):
        if name in visited:
            return None
        visited.add(name)
        node = {
                "id": f"{name}+{type}",
                "name": name,
                "type": type,
                "count": 0, 
                "dependencies": []
                }
        
        for dep in [d for d in dependency_data if d["NAME"] == name]:
            dep_node = build_node(dep["REFERENCED_NAME"], dep["REFERENCED_TYPE"], visited.copy())
            if dep_node:
                node["dependencies"].append(dep_node)

        node["count"] = len(node["dependencies"])
        return node

    root = next((dep for dep in dependency_data if dep["NAME"] == object_name), None)
    if root:
        visited = set() 
        return build_node(root["NAME"], root["TYPE"], visited)
    return None

def generate_object_dependency_json(conn,schemaname,includetable):
    dependency_json = [] 
    json_file_name = schemaname.lower() + "_" + "dependency.json"
    output_path = os.path.join(os.getcwd(), json_file_name)

    dependency_data = get_dependency_data(schemaname,includetable)
    all_object_names = get_dependency_objects_all(conn,schemaname,includetable)

    for obj in all_object_names:
        dependency_json_result = generate_dependency_json(obj, dependency_data)
        if dependency_json_result:
            dependency_json.append(dependency_json_result)

    with open (output_path, "w") as file:
        json.dump(dependency_json, file, indent=4)
    
    print(f"Dependency json file is generate successfully : {output_path}")
    return json.dumps(dependency_json, indent=4)


if __name__ == "__main__":
    args = arguments()
    conn = database_connection()
    includetable = args.include_table
    try:
        if args.list_objects:
            list_objects(conn,args.schemaname,includetable)
        elif args.objectname:
            get_dependencies(args.objectname,args.schemaname,includetable)
        elif args.generate_json:
            generate_object_dependency_json(conn,args.schemaname,includetable)
        else:
            print("Please provide object_name or correct options(generate-json) for dcganalyzer")
    except Exception as e:
        print(f"Exception occured : {e}")
    finally:
        conn.close()
