#!/usr/bin/env python
# This is a script intended to be ran only when there are updates to the item
# database. The results are dumped into a file as JSON to be read by the app.
#
# This script requires an installed (and updated) copy of Eve Online. This
# requires Reverence, a tool which looks at the game cache to get up-to-date
# data. URL: https://github.com/ntt/reverence/
from __future__ import print_function

import bz2
import collections
import json
import os
import sqlite3
import tempfile
import urllib2

# from reverence import blue, const

COMP_TYPES = [
    659,  # Super Carriers
    547,  # Carriers
    30,   # Titans
    485,  # Dreadnoughts
    883,  # Industrial Capitals
]

SQLITE_DUMP_URL = "https://www.fuzzwork.co.uk/dump/sqlite-latest.sqlite.bz2"


def download_database(destination_path):
    decompressor = bz2.BZ2Decompressor()
    response = urllib2.urlopen(SQLITE_DUMP_URL)

    total_bytes = int(response.info().getheader('Content-Length').strip())
    chunk = 1000000  # 1 megabyte at a time
    bytes_read = 0
    with open(destination_path, 'wb') as f:
        while 1:
            data = response.read(chunk)
            if not data:
                break

            bytes_read += len(data)
            print("Progress: %d of %d bytes (%0.2f%% complete)" % (
                  bytes_read,
                  total_bytes,
                  float(bytes_read)/total_bytes * 100,
                  ))

            decompressed_data = decompressor.decompress(data)
            if decompressed_data is not None:
                f.write(decompressed_data)


def build_all_types(cursor):

    inv_type_materials = collections.defaultdict(list)
    for row in cursor.execute('SELECT * FROM invtypematerials'):
        inv_type_materials[row['typeID']].append({
            'type_id': row['typeID'],
            'material_type_id': row['materialTypeID'],
            'quantity': row['quantity'],
        })

    for (type_id,
         group_id,
         type_name,
         volume,
         market_group_id) in cursor.execute('''
SELECT
    typeID,
    groupID,
    typeName,
    volume,
    marketGroupID
FROM invtypes'''):

        print("Populating info for: %s" % type_name.encode('utf-8'))

        has_market = market_group_id is not None
        d = {
            'typeID': type_id,
            'groupID': group_id,
            'typeName': type_name,
            'volume': volume,
            'market': has_market,
        }

        # Save the components for certain types that aren't commonly found
        # on the market
        if (
            group_id in COMP_TYPES and
            type_id in inv_type_materials
        ):

            d['components'] = [{'typeID': material['type_id'],
                                'materialTypeID': material['material_type_id'],
                                'quantity': material['quantity']}
                               for material
                               in inv_type_materials[type_id]]

        yield d


def main():
    temp_dir = tempfile.mkdtemp()
    db_path = os.path.join(temp_dir, 'eve-db.sqlite')
    print("Writing sqlite database to %s" % db_path)
    download_database(db_path)

    print("Opening database file")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    print("Build type information")
    all_types = list(build_all_types(c))

    types_output_file = 'data/types.json'
    print("Output types to %s" % types_output_file)
    with open(types_output_file, 'w') as f:
        f.write(json.dumps(all_types, indent=2))


if __name__ == '__main__':
    main()
