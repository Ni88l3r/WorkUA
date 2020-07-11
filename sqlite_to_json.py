import json
import sqlite3


# "row_factory" from sqlite3 documentation
def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


connection = sqlite3.connect("WorkUA.db")
connection.row_factory = dict_factory
cursor = connection.cursor()
cursor.execute("select * from vacancy")
data = cursor.fetchall()
with open('WorkUA.json', 'w') as file:
    file.write(json.dumps(data, sort_keys=True, indent=4, ensure_ascii=False))
connection.close()
