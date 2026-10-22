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
from teatype.modulo.hsdb import hsdb

# Local imports
from _common import DB_NAME

# Script 2 of 3: read-only client. No model classes are imported, everything comes from the published schemas.

db = hsdb[DB_NAME]
print('Server is a remote process:', db.server is None)
print('Models:', list(db.models))
print(db.Student)
print(db.School)

print('Students:', db.Student.count())
print('Aged 18:', len(db.Student.find(age=18)))
print('Aged 17-19, oldest first:', [(s['name'], s['age']) for s in db.Student.query().where('age').greater_than_or_equals(17).sort_by('age', 'desc').paginate(0, 3)])

student = db.Student.all(expand_relations=True)[0]
print(f'{student["name"]} studies at {student["school"]["name"]} ({student["school"]["city"]})')
