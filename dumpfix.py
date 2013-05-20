import json
import sys

def fix_dump(in_file, out_file, model, *remove_fields):
    content = json.load(open(in_file))
    
    for item in content:
        if item['model'] == model:
            for field in remove_fields:
                if field in item['fields']:
                    del item['fields'][field]
    
    json.dump(content, open(out_file, 'w'))
    
if __name__ == "__main__":
    """ 
    Usage: 
    python dumpfix.py olddump.json newdump.json myapp.mymodel field1 field2 ...
    """
    fix_dump(*sys.argv[1:])