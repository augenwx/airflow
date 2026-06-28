import os
import json
import shutil
import hashlib

BASE_PATH = r"D:\mineria data\airflow\dashboards\airflowx.Report\definition\pages"

def write_raw_json(path, raw_json_str):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(raw_json_str)

def clean_pages():
    if os.path.exists(BASE_PATH):
        for item in os.listdir(BASE_PATH):
            p = os.path.join(BASE_PATH, item)
            if os.path.isdir(p):
                shutil.rmtree(p)

def generate_id(name):
    return hashlib.md5(name.encode()).hexdigest()[:20]

def parse_field(field_str):
    if "[" in field_str and "]" in field_str:
        entity, prop = field_str.replace("]", "").split("[")
        return entity, prop
    return None, None

def wrap_visual(name, x, y, w, h, z, visual_type, query_obj, objects_obj=None):
    base = {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.7.0/schema.json",
        "name": name,
        "position": {"x": x, "y": y, "z": z, "height": h, "width": w, "tabOrder": z},
        "visual": {
            "visualType": visual_type,
            "query": {"queryState": query_obj},
            "drillFilterOtherVisuals": True
        }
    }
    if objects_obj:
        base["visual"]["objects"] = objects_obj
    return json.dumps(base, indent=2)

def make_projection(entity, prop, is_measure=False, is_active=False):
    t = "Measure" if is_measure else "Column"
    proj = {
        "field": {t: {"Expression": {"SourceRef": {"Entity": entity}}, "Property": prop}},
        "queryRef": f"{entity}.{prop}",
        "nativeQueryRef": prop
    }
    if is_active:
        proj["active"] = True
    return proj


def generate():
    with open('blueprint.json', 'r', encoding='utf-8') as f:
        bp = json.load(f)

    clean_pages()
    
    page_order = []
    
    for i, page in enumerate(bp['pages']):
        page_id = generate_id(page['page_id'])
        page_order.append(page_id)
        
        # Write page.json
        write_raw_json(os.path.join(BASE_PATH, page_id, "page.json"), json.dumps({
            "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/page/2.1.0/schema.json",
            "name": page_id,
            "displayName": page['name'],
            "displayOption": "FitToPage",
            "height": page['canvas']['height'],
            "width": page['canvas']['width']
        }, indent=2))
        
        z_index = 1
        
        # Filters (Slicers)
        # Position them at top right
        filter_x = 800
        for f in page.get('filters', []):
            ent, prop = parse_field(f['field'])
            if not ent: continue
            q = {"Values": {"projections": [make_projection(ent, prop, False, True)]}}
            obj = {"data": [{"properties": {"mode": {"expr": {"Literal": {"Value": "'Dropdown'"}}}}}]}
            v_json = wrap_visual(f'slicer_{prop}', filter_x, 10, 150, 60, z_index, "slicer", q, obj)
            write_raw_json(os.path.join(BASE_PATH, page_id, "visuals", f'slicer_{prop}', "visual.json"), v_json)
            filter_x += 160
            z_index += 1
            
        # Visuals
        for v in page.get('visuals', []):
            if v['type'] == 'text_box':
                continue # Skip text boxes to avoid crash
                
            x, y, w, h = v['position']['x'], v['position']['y'], v['position']['w'], v['position']['h']
            vtype = v['type']
            pb_type = "card" # default
            query = {}
            
            if vtype == 'card':
                pb_type = "card"
                if 'measure' in v:
                    # In PBIP, measures belong to a table. Let's assume _Measures or mart_market_snapshot
                    query = {"Values": {"projections": [make_projection("_Measures", v['measure'], True)]}}
                elif 'fields' in v:
                    ent, prop = parse_field(f"{v['fields'][0]['table']}[{v['fields'][0]['column']}]")
                    query = {"Values": {"projections": [make_projection(ent, prop, False)]}}
            
            elif vtype == 'table':
                pb_type = "tableEx"
                projs = []
                for f in v.get('fields', []):
                    ent, prop = parse_field(f)
                    projs.append(make_projection(ent, prop, False))
                query = {"Values": {"projections": projs}}
                
            elif vtype == 'bar_chart':
                pb_type = "barChart"
                ent_c, prop_c = parse_field(v['fields']['axis'])
                ent_v, prop_v = parse_field(v['fields']['values'])
                query = {
                    "Category": {"projections": [make_projection(ent_c, prop_c, False, True)]},
                    "Y": {"projections": [make_projection(ent_v, prop_v, False)]} # Assume values are numeric columns acting as implicit sums, or actual measures. If implicit, it's "Column".
                }
                
            elif vtype == 'scatter_chart':
                pb_type = "scatterChart"
                ent_x, prop_x = parse_field(v['fields']['x'])
                ent_y, prop_y = parse_field(v['fields']['y'])
                ent_d, prop_d = parse_field(v['fields']['details'])
                query = {
                    "Category": {"projections": [make_projection(ent_d, prop_d, False, True)]},
                    "X": {"projections": [make_projection(ent_x, prop_x, False, True)]},
                    "Y": {"projections": [make_projection(ent_y, prop_y, False)]}
                }
                
            elif vtype == 'line_chart':
                pb_type = "lineChart"
                ent_x, prop_x = parse_field(v['fields']['x'])
                query = {
                    "Category": {"projections": [make_projection(ent_x, prop_x, False, True)]}
                }
                if 'y' in v['fields']:
                    ent_y, prop_y = parse_field(v['fields']['y'])
                    query["Y"] = {"projections": [make_projection(ent_y, prop_y, False)]}
                    if 'legend' in v['fields']:
                        ent_l, prop_l = parse_field(v['fields']['legend'])
                        query["Series"] = {"projections": [make_projection(ent_l, prop_l, False)]}
                elif 'y_series' in v['fields']:
                    y_projs = []
                    for s in v['fields']['y_series']:
                        ent_y, prop_y = parse_field(s)
                        y_projs.append(make_projection(ent_y, prop_y, False))
                    query["Y"] = {"projections": y_projs}
                    
            if not query: continue
            
            v_json = wrap_visual(v['id'], x, y, w, h, z_index, pb_type, query)
            write_raw_json(os.path.join(BASE_PATH, page_id, "visuals", v['id'], "visual.json"), v_json)
            z_index += 1

    # Write pages.json
    write_raw_json(os.path.join(BASE_PATH, "pages.json"), json.dumps({
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/pagesMetadata/1.0.0/schema.json",
        "pageOrder": page_order,
        "activePageName": page_order[0]
    }, indent=2))

if __name__ == "__main__":
    generate()
    print("Blueprint successfully built!")
