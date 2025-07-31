# Copyright (C) 2024-2025 Burak Günaydin
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

# System imports
import os
import random

# Package imports
import pytest

# From system imports
from concurrent.futures import ProcessPoolExecutor
from pprint import pprint

# From package imports
from teatype.hsdb import HSDBAttribute, HSDBRelation, HSDBModel, HybridStorage
from teatype.logging import hint, log, println
from teatype.util import generate_id, stopwatch

##################
# Example Models #
##################
    
class SchoolModel(HSDBModel):
    address = HSDBAttribute(str, required=True)
    name    = HSDBAttribute(str, required=True)

# Assume these are your models derived from BaseModel.
class StudentModel(HSDBModel):
    age    = HSDBAttribute(int, required=True)
    gender = HSDBAttribute(str, required=True)
    height = HSDBAttribute(int, description='Height in cm', required=True)
    name   = HSDBAttribute(str, required=True)
    school = HSDBRelation.ManyToOne(SchoolModel, required=True)
    
####################
# Helper Functions #
####################

def create_student(i:int, random_first_names, random_sur_names, random_schools):
    """
    Creates a student object with random attributes.
    """
    random.seed()
    gender = random.choice(['male', 'female'])
    student = StudentModel({
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

def create_students_parallel(number_of_students, random_first_names, random_sur_names, random_schools):
    """
    Creates students in parallel using ProcessPoolExecutor.
    """
    with ProcessPoolExecutor(max_workers=os.cpu_count()) as executor:
        results = dict(
            executor.map(
                create_student,
                range(number_of_students),
                [random_first_names] * number_of_students,
                [random_sur_names] * number_of_students,
                [random_schools] * number_of_students
            )
        )
    return results

#############
#  Fixtures #
#############

@pytest.fixture(scope='module')
def random_first_names():
        return [[
            'Bob', 'Charlie', 'David', 'Frank', 'Ivan', 'Kevin', 'Michael', 'Oscar',
            'Quincy', 'Sam', 'Steve', 'Victor', 'Xander',
        ], [
            'Alice', 'Eve', 'Grace', 'Heidi', 'Judy', 'Linda','Nancy', 'Pamela',
            'Quincy', 'Rachel', 'Sam', 'Tina', 'Ursula', 'Wendy',
        ]]

@pytest.fixture(scope='module')
def random_sur_names():
    return [
        'Anderson', 'Baker', 'Carter', 'Davidson', 'Edwards', 'Fisher', 'Garcia',
        'Hernandez', 'Ivanov', 'Johnson', 'Kowalski', 'Lopez', 'Martinez', 'Nelson',
        'Olsen', 'Perez', 'Quinn', 'Rodriguez', 'Smith', 'Taylor', 'Unger', 'Vasquez',
        'Williams', 'Xu', 'Young', 'Zhang',
    ]

@pytest.fixture(scope='module')
def random_schools():
    return [
        SchoolModel({'address': '123 Main St', 'name': 'Howard High'}),
        SchoolModel({'address': '456 ElmSt', 'name': 'Jefferson High'}),
        SchoolModel({'address': '789 Oak St', 'name': 'Lincoln High'}),
        SchoolModel({'address': '101 Pine St', 'name': 'Madison High'}),
        SchoolModel({'address': '112 Birch St', 'name': 'Monroe High'}),
        SchoolModel({'address': '131 Maple St', 'name': 'Roosevelt High'}),
        SchoolModel({'address': '415 Cedar St', 'name': 'Washington High'}),
        SchoolModel({'address': '161 Walnut St', 'name': 'Wilson High'}),
        SchoolModel({'address': 'Arcisstraße 21', 'name': 'Technische Universität München'}),
    ]

@pytest.fixture
def hybrid_storage(random_schools):
    hybrid_storage = HybridStorage(cold_mode=True)
    for school in random_schools:
        hybrid_storage.index_database._db.update({school.id: school})
    return hybrid_storage

##########
# PyTest #
##########

@pytest.mark.skip
@pytest.mark.parametrize('number_of_students', [1, 11, 111, 1_111, 11_111, 111_111])
def test_create_students_parallel(number_of_students,
                                  random_first_names,
                                  random_sur_names,
                                  random_schools,
                                  hybrid_storage):
    """
    Test student creation in parallel and database update.
    """
    log('--------------------')
    
    db = hybrid_storage.index_database._db
    if number_of_students == 1:
        stopwatch('Creating student')
        student = create_student(0, random_first_names, random_sur_names, random_schools)
        students = {student[0]: student[1]}
        stopwatch()
    else:
        stopwatch('Creating students in parallel')
        students = create_students_parallel(number_of_students, random_first_names, random_sur_names, random_schools)
        stopwatch()
    println()

    assert isinstance(students, dict)
    assert len(students.keys()) == number_of_students
    # Ensure all students are instances of StudentModel
    for student in students.values():
        assert isinstance(student, StudentModel)

    stopwatch('Index DB update')
    # Simulate and verify database update
    db.update(students)
    stopwatch()
    
    total_database_entries = len(db.keys())
    println()
    log(f'Total generated students: {total_database_entries}')
    
    log('--------------------')

@pytest.mark.parametrize('number_of_students, generate_in_parallel, measure_memory_footprint', [
    (12_345, False, True),
])
def test_queries(number_of_students,
                 generate_in_parallel,
                 measure_memory_footprint,
                 random_first_names,
                 random_sur_names,
                 random_schools,
                 hybrid_storage):
    log('--------------------')

    stopwatch('Seeding DB data')
    db = hybrid_storage.index_database._db
    if generate_in_parallel:
        students = create_students_parallel(number_of_students, random_first_names, random_sur_names, random_schools)
    else:
        students = create_students_sequentially(number_of_students, random_first_names, random_sur_names, random_schools)
    db.update(students)
    total_database_entries = len(db.keys())
    stopwatch()
    log(f'Total data: {total_database_entries}')
    if measure_memory_footprint:
        stopwatch('Measuring memory footprint')
        log(hybrid_storage.index_database.memory_footprint)
        stopwatch()
    println()
    
    # Create a query chain that does not execute immediately.
    log('Test queries:')
    println()
    
    SchoolModel.query.verbose().all()
                      
    StudentModel.query.verbose().all()
    
    # Alternative: Using aliases
    StudentModel.query.w('height').gt(180).verbose().collect()
    
    StudentModel.query.where('height').less_than(150) \
                      .where('age').less_than(16) \
                      .sort_by('name') \
                      .filter_by('name') \
                      .verbose() \
                      .collect()
    
    StudentModel.query.where('height').less_than(150) \
                      .where('age').less_than(16) \
                      .verbose() \
                      .paginate(0, 10)
    
    StudentModel.query.where('height').less_than(150) \
                      .where('age').greater_than_or_equals(16) \
                      .verbose() \
                      .paginate(1, 10)
    
    StudentModel.query.where('height').less_than(150) \
                      .where('age').less_than(16) \
                      .verbose() \
                      .paginate(0, 30)
    
    StudentModel.query.where('height').less_than(150) \
                      .where('age').less_than(16) \
                      .verbose() \
                      .first()
    
    StudentModel.query.where('height').less_than(150) \
                      .where('age').less_than(16) \
                      .verbose() \
                      .last()
                      
    student = StudentModel({
        'age': 21,
        'gender': 'male',
        'height': 181,
        'name': 'Mark Grayson',
        'school': random_schools[0]
    })
    db.update({student.id: student})
    student_id = student.id
    StudentModel.query.verbose().get(id=student_id)
    
    log('--------------------')
    
@pytest.mark.skip
@pytest.mark.parametrize('number_of_students, generate_in_parallel, measure_memory_footprint', [
    (1111, False, False),
])
def test_relations(number_of_students,
                   generate_in_parallel,
                   measure_memory_footprint,
                   random_first_names,
                   random_sur_names,
                   random_schools,
                   hybrid_storage):
    log('--------------------')

    stopwatch('Seeding DB data')
    db = hybrid_storage.index_database._db
    if generate_in_parallel:
        students = create_students_parallel(number_of_students, random_first_names, random_sur_names, random_schools)
    else:
        students = create_students_sequentially(number_of_students, random_first_names, random_sur_names, random_schools)
    db.update(students)
    total_database_entries = len(db.keys())
    stopwatch()
    log(f'Total data: {total_database_entries}')
    if measure_memory_footprint:
        stopwatch('Measuring memory footprint')
        log(hybrid_storage.index_database.memory_footprint)
        stopwatch()
    println()
    
    # Create a query chain that does not execute immediately.
    log('Test queries:')
    println()

    tu_berlin = SchoolModel.query.where('name').equals('Technische Universität München').verbose().first()
    lion_reichl = StudentModel({
        'age': 30,
        'gender': 'male',
        'height': 181,
        'name': 'Lion Reichl',
        'school': tu_berlin.id
    })
    db.update({lion_reichl.id: lion_reichl})
    
    log('Test relations:')
    println()

    print(lion_reichl.school)
    print(lion_reichl.school.all())
    # print(lion_reichl.school.secondary_keys)
    # print(lion_reichl.school.relation_type)
    # print(lion_reichl.school._value.all())
    # lion_reichl.school.verbose(print=True).all()
    
    log('--------------------')