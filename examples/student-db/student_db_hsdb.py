# Run this script in two terminals: the first process hosts the HSDB and seeds it,
# the second finds the running server and connects to it as a client.

# Standard-library imports
import random

# Third-party imports
from teatype.modulo.hsdb import HSDB

# Local imports
from server.models import Class, Professor, Student, University

hsdb = HSDB.attach(models=[Class, Professor, Student, University], cold_mode=True)

if hsdb.server: # Only the launching process gets here
    print('No HSDB was running, launched one in this process. Seeding ...')
    universities = [hsdb.create(University, {'name': name, 'address': f'{i} Main St'})
                    for i, name in enumerate(['Howard High', 'Jefferson High', 'TU München'])]
    for _ in range(200):
        hsdb.create(Student, {'age': random.randint(13, 23),
                              'gender': random.choice(['male', 'female']),
                              'height': random.randint(140, 200),
                              'name': random.choice(['Alice', 'Bob', 'Charlie', 'Eve']),
                              'university': random.choice(universities)['id']})
else:
    print('Connected to a running HSDB as client.')

print('Students:', hsdb.count(Student))

# Query builder, same verbs as Student.query
oldest = hsdb.query(Student).where('age').greater_than_or_equals(22).sort_by('age', 'desc').first()
print('Oldest student:', oldest)

# Keyword filters (age__gte, age__lt, ...), indexed fields are looked up in O(1)
print('Male, 18-20:', len(hsdb.find(Student, gender='male', age__gte=18, age__lte=20)))

# Relations are omitted by default; include_relations adds their ids, expand_relations the full objects
student = hsdb.all(Student, expand_relations=True)[0]
print('First student:', student['name'], 'studies at', student['university']['name'])

if hsdb.server:
    input('Hosting. Start this script again in another terminal, then press Enter to stop ...')
