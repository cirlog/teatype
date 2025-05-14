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
import json
import re

# From system imports
from typing import List

# From package imports
from teatype.io import file, path
from teatype.logging import err, hint, println, warn
from teatype.util import kebabify

class _ParsingError:
    entry_id:str
    entry_model:str
    error:str
    
    def __init__(self, entry_id:str, entry_model:str, error:str):
        self.entry_id = entry_id
        self.entry_model = entry_model
        self.error = error

# TODO: Implement a better solution for this - only use one instance, check via type which class it is
def parse_index_files(hybrid_storage_instance:object=None, migrator:object=None) -> List[dict]:
    if hybrid_storage_instance is None and migrator is None:
        raise ValueError('At least one of the parameters should be provided')
    
    if hybrid_storage_instance is not None and migrator is not None:
        raise ValueError('Only one of the parameters should be provided')
    
    # Parsing variables from the two different sources
    if hybrid_storage_instance:
        models = hybrid_storage_instance.index_database.models
        index_path = hybrid_storage_instance.raw_file_handler.fs.hsdb.index.path
    else:
        models = migrator.models
        index_path = migrator._index_path
    
    print('Parsing index files from disk')
    parsed_index_data = {}
    parsing_errors_found = False
    for model in models:
        model_plural_name = kebabify(model.__name__, plural=True, remove='-model')
        model_path = f'{index_path}/{model_plural_name}'
        if not path.exists(model_path):
            continue
        
        parsed_index_data[model_plural_name] = []
        if migrator:
            migrator._migration_data['index'][model_plural_name] = []
            migrator._rejectpile['index'][model_plural_name] = []
        
        index_files = file.list(f'{index_path}/{model_plural_name}',
                                walk=False)
        if len(index_files) == 0:
            continue
        
        parsing_errors = []
        for index_file in index_files:
            index_id = index_file.name.replace('.json', '')
            try:
                index_data = file.read(index_file.path, force_format='json', silent_fail=True)
                if index_data is None or index_data == {} or index_data == []:
                    parsing_errors.append(_ParsingError(index_id,
                                                        model_plural_name,
                                                        'empty'))
                    continue
                parsed_index_data[model_plural_name].append(index_data)
            except json.JSONDecodeError as jde:
                # TODO: More edge cases?
                if jde.msg == 'Expecting value' and jde.doc == '' and jde.pos == 0 and jde.lineno == 1 and jde.colno == 1:
                    parsing_errors.append(_ParsingError(index_id,
                                                        model_plural_name,
                                                        'empty'))
                else:
                    parsing_errors.append(_ParsingError(index_id,
                                                        model_plural_name,
                                                        'corrupt'))
                if not parsing_errors_found:
                    parsing_errors_found = True
                    
        print(f'    Found "{model_plural_name}" index files: {len(index_files)}')
        amount_of_parsing_errors = len(parsing_errors)
        if amount_of_parsing_errors > 0:
            warn(f'    Found {amount_of_parsing_errors} parsing error{"s" if amount_of_parsing_errors > 1 else ""}:', use_prefix=False)
            for parsing_error in parsing_errors:
                # TODO: Implement a better solution for this - seperate method in HSDBMigration
                if migrator:
                    migrator.reject_migration_index(parsing_error.entry_model,
                                                    { 'id': parsing_error.entry_id },
                                                    reason=f'index-{parsing_error.error}')
                err(f'      {parsing_error.error}: {parsing_error.entry_id}', use_prefix=False, verbose=False)
            println()
            
    if not migrator:
        if parsing_errors_found:
            hint(f'Parsing errors can cause database integrity to degrade, please check these files manually',
                pad_before=1,
                verbose=False)
    return parsed_index_data