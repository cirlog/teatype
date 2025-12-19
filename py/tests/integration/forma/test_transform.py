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
from teatype.forma.base_forma import BaseForma
from teatype.forma.base_transformer import BaseTransformer, PathRule
from teatype.logging import *

global StudentForma
global TeacherForma
global UniTransformer

class UniTransformer(BaseTransformer):
    forma_a=None
    forma_b=None
    
    def lazy_load(self):
        if UniTransformer.forma_a is None:
            UniTransformer.forma_a = StudentForma
            UniTransformer.forma_b = TeacherForma

    rules = [
        PathRule(a_path='first_name',
                 b_path='full_name',
                 a_to_b=lambda x: x.first_name + ' ' + x.last_name,
                 b_to_a=lambda x: x.full_name.split(' ')[0] if ' ' in x.full_name else ''),
        PathRule(a_path='last_name',
                 b_path='full_name',
                 a_to_b=lambda x: x.first_name + ' ' + x.last_name,
                 b_to_a=lambda x: x.full_name.split(' ')[1] if ' ' in x.full_name else '' ),
        PathRule(a_path='major',
                 b_path='subject'),
        PathRule(a_path='graduation_year',
                 b_path='years_of_experience',
                 a_to_b=lambda x: 2024 - x.graduation_year,
                 b_to_a=lambda x: 2024 - x.years_of_experience)
    ]

class StudentForma(BaseForma):
    __transformer_class=UniTransformer
    age:int=None
    first_name:str
    graduation_year:int
    last_name:str
    major:str
    
class TeacherForma(BaseForma):
    __transformer_class=UniTransformer
    full_name:str
    subject:str
    years_of_experience:int
    
student_data = {
    'age': 22,
    'first_name': 'Alice',
    'last_name': 'Smith',
    'graduation_year': 2023,
    'major': 'Computer Science'
}

teacher_data = {
    'full_name': 'Bob Johnson',
    'subject': 'Mathematics',
    'years_of_experience': 10
}

student = StudentForma(**student_data)

println()
log('Student->Teacher:')
log('From:', color='yellow')
log(student_data, prettify=True)
log('To:', color='cyan')
log(student.transform(), prettify=True)

teacher = TeacherForma(**teacher_data)
println()
log('Teacher->Student:')
log('From:', color='yellow')
log(teacher_data, prettify=True)
log('To:', color='cyan')
log(teacher.transform(), prettify=True)
println()