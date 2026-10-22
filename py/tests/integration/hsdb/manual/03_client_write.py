# Copyright (C) 2024-2026 Burak Günaydin
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# Standard-library imports
from pathlib import Path

# Third-party imports
from teatype.modulo.hsdb import hsdb

# Local imports
from _common import DB_NAME, DIST

# Script 3 of 3: writing client. Creates, updates and deletes through the schema-built models and shows the files on disk.

db = hsdb[DB_NAME]
indexdb = DIST / 'hsdb' / DB_NAME / 'indexdb'
disk_count = lambda: len(list(indexdb.rglob('*.json')))

print('Fields accepted for Student:', db.Student.fields)
school = db.School.find(name='Howard High')[0]
before = (db.Student.count(), disk_count())

student = db.Student.create(name='Ada', age=21, school=school['id'])
print('Created:', student['id'][:8], '| memory + disk grew by', db.Student.count() - before[0], disk_count() - before[1])

print('Updated age:', db.Student.update(student['id'], age=22)['age'])
print('Read back:', db.Student.get(student['id'])['age'], '| on disk:', Path(indexdb / 'students' / f'{student["id"]}.json').exists())

# The schema is enforced client-side, before any request is sent
for bad in ({'name': 'No age', 'school': school['id']}, {'name': 'X', 'age': 'old', 'school': school['id']}, {'name': 'X', 'age': 1, 'school': school['id'], 'nope': 1}):
    try:
        db.Student.create(bad)
    except ValueError as error:
        print('Rejected:', error)

print('Deleted:', db.Student.delete(student['id']), '| again:', db.Student.delete(student['id']))
print('Counts back to', (db.Student.count(), disk_count()), 'expected', before)
