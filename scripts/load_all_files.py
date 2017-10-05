#!/usr/bin/env python
import copy
import json
import os
import sys
import uuid
from os import walk

sys.path.append('/Users/chstansbury/PyCharmProjects/python-arpes/')

import arpes.utilities
from arpes.models.spectrum import load_scan
from arpes.io import save_dataset

def attach_uuid(scan):
    if 'id' not in scan:
        scan = copy.copy(scan)
        scan['id'] = str(uuid.uuid1())

    return scan

for path, _, files in walk(os.getcwd()):
    json_files = [f for f in files if '.json' in f]
    for j in json_files:
        with open(os.path.join(path, j), 'r') as f:
            metadata = json.load(f)

        metadata = [attach_uuid(scan) for scan in metadata]

        with open(os.path.join(path, j), 'w') as f:
            json.dump(metadata, f, indent=2, sort_keys=True)

        for scan in metadata:
            print(scan['file'])
            data = load_scan(scan)
            data = arpes.utilities.rename_standard_attrs(data.raw)
            save_dataset(data)