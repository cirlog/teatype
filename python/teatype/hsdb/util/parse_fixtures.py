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

# From system imports
from typing import List

# From package imports
from teatype.io import file
from teatype.logging import println

def parse_fixtures(fixtures_path:str) -> List[dict]:
    fixture_files = file.list(fixtures_path, walk=False)
    if len(fixture_files) == 0:
        return
    
    println()
    print('Found fixtures')
    fixtures = []
    for fixture_file in fixture_files:
        if not fixture_file.name.endswith('.json'):
            continue
        
        fixture = file.read(fixture_file.path, force_format='json')
        fixture_model = fixture.get('model').split('.')
        app_name = fixture_model[0]
        model_name = fixture_model[1]
        
        fixture_entries = fixture.get('fixtures')
        amount_of_fixture_entries = len(fixture_entries)
        if fixture_entries == 0:
            continue
        
        # TODO: Validate
        fixtures.append(fixture)
        fixture['app'] = app_name
        fixture['model'] = model_name
        
        print(f'    Installed {app_name}.{model_name} fixtures: {amount_of_fixture_entries}')
    println()
    return fixtures