from pathlib import Path
import sys
import json

conf_path = Path(sys.argv[1])
if conf_path.is_file():
    with open(conf_path, 'r') as file:
        conf = json.load(file)
        if not conf['address']:
            sys.exit('Address is not specified.')
else:
    sys.exit("Configuration file does not exist.")
