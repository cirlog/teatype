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

# Third-party imports
from teatype.db.hsdb.core import HSDBAttribute, HSDBModel, HSDBRelation
from teatype.modulo.hsdb import hsdb

# Local imports
from _common import DB_NAME, DIST

# Script 1 of 3: the only script that knows the model classes. Run it first and keep it running.
# It hosts the database "school" (non-cold, files in teatype/dist/hsdb/school/) and publishes the
# model schemas to <db>/models/*.json, which scripts 2 and 3 use instead of the classes.

class School(HSDBModel):
    name = HSDBAttribute(str, required=True, indexed=True, unique=True)
    city = HSDBAttribute(str, required=True)

class Student(HSDBModel):
    age    = HSDBAttribute(int, required=True, indexed=True)
    name   = HSDBAttribute(str, required=True)
    school = HSDBRelation.ManyToOne(School, required=True)

db = hsdb.init(DB_NAME, models=[School, Student])
if not db.server:
    raise SystemExit(f'"{DB_NAME}" is already hosted by another process, nothing to do here')

schools = [db.create(School, {'name': name, 'city': city})
           for name, city in [('Howard High', 'Springfield'), ('TU München', 'Munich')]]
for i in range(50):
    db.create(Student, {'age': 15 + i % 10, 'name': f'Student {i}', 'school': schools[i % 2]['id']})

print(f'Hosting "{DB_NAME}" on {db.base_url}')
print(f'Files: {DIST / "hsdb" / DB_NAME}')
print(f'Counts: { {name: db.count(name) for name in db.models} }')
input('Run scripts 02 and 03 in other terminals, then press Enter to stop ...')
