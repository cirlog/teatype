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
import random
import sys

# Third-party imports
from teatype.db.hsdb.HSDBServer import HSDBServer
from teatype.logging import *
from teatype.toolkit import stopwatch

# Local imports
from api.models import *

# Define your apps
APPS = [
    'api'
]

MODELS = [
    Class,
    Professor,
    Student,
    University
]

def create_student(i:int, random_first_names, random_sur_names, random_schools):
    """
    Creates a student object with random attributes.
    """
    random.seed()
    gender = random.choice(['male', 'female'])
    student = Student({
        'age': random.randint(13, 23),
        'gender': gender,
        'height': random.randint(140, 200),
        'name': f'{random.choice(random_first_names[0] if gender == "male" else random_first_names[1])} {random.choice(random_sur_names)}',
        'university': random.choice([random_school.id for random_school in random_schools])
    })
    return student.id, student

def create_students_sequentially(number_of_students, random_first_names, random_sur_names, random_schools):
    """
    Creates students sequentially.
    """
    students = {}
    for i in range(number_of_students):
        student = create_student(i, random_first_names, random_sur_names, random_schools)
        students[student[0]] = student[1]
    return students

def random_first_names():
        return [[
            'Bob', 'Charlie', 'David', 'Frank', 'Ivan', 'Kevin', 'Michael', 'Oscar',
            'Quincy', 'Sam', 'Steve', 'Victor', 'Xander',
        ], [
            'Alice', 'Eve', 'Grace', 'Heidi', 'Judy', 'Linda','Nancy', 'Pamela',
            'Quincy', 'Rachel', 'Sam', 'Tina', 'Ursula', 'Wendy',
        ]]

def random_sur_names():
    return [
        'Anderson', 'Baker', 'Carter', 'Davidson', 'Edwards', 'Fisher', 'Garcia',
        'Hernandez', 'Ivanov', 'Johnson', 'Kowalski', 'Lopez', 'Martinez', 'Nelson',
        'Olsen', 'Perez', 'Quinn', 'Rodriguez', 'Smith', 'Taylor', 'Unger', 'Vasquez',
        'Williams', 'Xu', 'Young', 'Zhang',
    ]

def random_schools():
    return [
        University({'address': '123 Main St', 'name': 'Howard High'}),
        University({'address': '456 ElmSt', 'name': 'Jefferson High'}),
        University({'address': '789 Oak St', 'name': 'Lincoln High'}),
        University({'address': '101 Pine St', 'name': 'Madison High'}),
        University({'address': '112 Birch St', 'name': 'Monroe High'}),
        University({'address': '131 Maple St', 'name': 'Roosevelt High'}),
        University({'address': '415 Cedar St', 'name': 'Washington High'}),
        University({'address': '161 Walnut St', 'name': 'Wilson High'}),
        University({'address': 'Arcisstraße 21', 'name': 'Technische Universität München'}),
    ]

if __name__ == '__main__':
    # Create HSDBServer instance with your configuration
    server = HSDBServer(
        apps=APPS,
        cold_mode=True,
        cors_allow_all=True,
        debug=True,
        models=MODELS,
    )
    
    # Seed the database
    stopwatch('Seeding DB data')
    hybrid_storage = server.hybrid_storage
    index_db = hybrid_storage.index_db
    
    # First, create and add universities to the database
    schools = random_schools()
    universities = {str(school.id): school for school in schools}
    index_db.update_directly(universities)
    
    # Then create students with references to the persisted universities
    NUMBER_OF_STUDENTS = 1234
    students = create_students_sequentially(NUMBER_OF_STUDENTS, random_first_names(), random_sur_names(), schools)
    index_db.update_directly(students)
    stopwatch()
    
    stopwatch('Measuring memory footprint')
    log(hybrid_storage.index_db.memory_footprint)
    stopwatch()
        
    # Dynamically create and set URL patterns
    urlpatterns = server.create_urlpatterns(
        include_admin=False
    )
    
    student = Student.query.where('age').equals(18).first()
    if student:
        print(student)
        print(student.university)
    else:
        print('No student with age 18 found')
    
    # Demonstrate new features
    print('\n--- New Features Demo ---')
    
    # Model.count() - O(1) using model index
    print(f'Total students: {Student.count()}')
    print(f'Total universities: {University.count()}')
    
    # Model.all() with relation serialization
    print('\n--- Student with expanded university ---')
    students_sample = Student.query.where('age').equals(20).first()
    if students_sample:
        serialized = Student.serialize(students_sample, include_relations=True)
        print(f'With relation ID: {serialized}')
        serialized_expanded = Student.serialize(students_sample, expand_relations=True)
        print(f'With expanded relation: {serialized_expanded}')
    else:
        print('No student with age 20 found for relation demo')
    
    # Model.find_by() - O(1) using field index
    print('\n--- Fast indexed lookup ---')
    male_students = Student.find_by('gender', 'male')
    print(f'Found {len(male_students)} male students using indexed lookup')
    
    # Model.schema() - get model structure
    print('\n--- Model Schema ---')
    import json
    print(json.dumps(Student.schema(), indent=2, default=str))
    
    # Create a temporary module for URL configuration
    import types
    url_module = types.ModuleType('hsdb_server_urls')
    url_module.urlpatterns = urlpatterns
    sys.modules['hsdb_server_urls'] = url_module
        
    # Check if we're running a command or just starting the server
    if len(sys.argv) > 1:
        if sys.argv[1] == 'runserver':
            # Run the development server
            server.run()
        else:
            # Execute any Django management command
            server.execute_command(*sys.argv[1:])
    else:
        # Default: run the server
        server.run()