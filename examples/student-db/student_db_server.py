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
        'school': random.choice([random_school.id for random_school in random_schools])
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
    db = hybrid_storage.index_db._db
    NUMBER_OF_STUDENTS = 1234
    students = create_students_sequentially(NUMBER_OF_STUDENTS, random_first_names(), random_sur_names(), random_schools())
    db.update(students)
    stopwatch()
    
    stopwatch('Measuring memory footprint')
    log(hybrid_storage.index_db.memory_footprint)
    stopwatch()
        
    # Create URL patterns
    from django.urls import path
    import sys
    
    # Dynamically create and set URL patterns
    urlpatterns = server.create_urlpatterns(
        include_admin=False
    )
    
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