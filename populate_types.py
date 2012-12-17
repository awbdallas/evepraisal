#!/usr/bin/env python
# This is a script intended to be ran only when there are updates to the item
# database. The results are dumped into a file as JSON to be read by the app.
#
# This script requires an installed (and updated) copy of Eve Online. This
# requires Reverence, a tool which looks at the game cache to get up-to-date
# data. URL: https://github.com/ntt/reverence/

import json
from reverence import blue


if __name__ == '__main__':
    eve_path = '/Applications/EVE Online.app/Contents/Resources/EVE Online.app/Contents/Resources/transgaming/c_drive/Program Files/CCP/EVE'
    # eve_path = 'C:\\Program Files\\CCP\\EVE\\'
    # eve_path = 'C:\\Program Files (x86)\\CCP\\EVE\\'
    eve = blue.EVE()
    cfg = eve.getconfigmgr()
    all_types = {}
    for (typeID, groupID, typeName) in cfg.invtypes.Select('typeID',
                                                    'groupID', 'typeName'):
        all_types[typeName.strip().lower()] = {'typeID': typeID,
                                               'groupID': groupID,
                                               'typeName': typeName}

    with open('data/types.json', 'w') as f:
        f.write(json.dumps(all_types, indent=2))
