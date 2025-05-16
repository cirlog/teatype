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

# From system imports
from abc import ABC, abstractmethod
from typing import List

# From package imports
from teatype.io import file, path
from teatype.logging import err, hint, log, println, warn

# From-as system imports
from datetime import datetime as dt

__MAX_AMOUNT_OF_WORKERS = 8

class _HSDBMigrationRejection:
    migration:dict
    reason:str
    rejected_at:str
    
    def __init__(self, reason:str, migration:dict):
        self.migration = migration
        self.reason = reason
        
        self.rejected_at = dt.now().isoformat()
        
    def as_dict(self) -> dict:
        return {
            'migration': {
                'app': self.migration['app'],
                'id': self.migration['id'],
                'name': self.migration['name']
            },
            'reason': self.reason,
            'rejected_at': self.rejected_at
        }
        
class _ParsingError:
    entry_id:str
    entry_model:str
    error:str
    
    def __init__(self, entry_id:str, entry_model:str, error:str):
        self.entry_id = entry_id
        self.entry_model = entry_model
        self.error = error

# TODO: Implement migration protocol
# TODO: Implement trap mechanism to revert migration if it fails
# TODO: Migrations always count one up in id dependent on app and model
# TODO: Always create a snapshot of all models before launching index db and if there are changes, create automatic migrations
# TODO: Always create a backup of all raw db entries before every migration (with optional include_non_index_files flag)
class HSDBMigration(ABC):
    __models_snapshot:dict # Holds snapshot data for models that get migrated
    __non_index_files_snapshot:dict|None # Optionally holds snapshot data for non-index files
    _auto_creation_datetime:str|None # ISO-formatted string for auto creation time
    _from_to_string:str # String representation of the migration's origin and destination
    _hsdb_path:str='/var/lib/hsdb' # Default path on linux
    _index_path:str # Path to the index directory
    _migrated_at:str # ISO-formatted string for migration time
    _migration_ancestor:int|None # The previous migration's reference, if any
    _migration_backup_path:str # Path to the backup of the migration
    _migration_data:dict # Holds the migration data
    _migration_descendant:int # The next migration's reference, if any
    _parsed_index_data:dict # Holds the parsed index data
    _rawfiles_path:str # Path to the rawfiles directory
    _rejectpile_path:str # Path to the rejectpile directory
    _rejectpile_index_path:str # Path to the rejectpile index directory
    _rejectpile_rawfiles_path:str # Path to the rejectpile rawfiles directory
    _rejectpile:dict # Holds the rejectpile data
    _workers:int # Number of workers to use for migration
    app_name:str # Name of the application this migration is associated with
    cold_mode:bool #  Indicates if the migration is in cold mode (no applied changes)
    include_non_index_files:bool # Indicates if non-index files should be part of migration steps
    migration_id:int # Numeric identifier to order migrations
    migration_name:str # Descriptive name for the migration
    models:List[type] # List of models that are part of the migration
    was_auto_created:bool # Marks whether the migration was automatically created
    
    def __init__(self,
                 auto_migrate:bool=True, 
                 cold_mode:bool=False,
                 include_non_index_files:bool=False,
                 max_workers:int=None) -> None:
        """
        Initializes the migration. If 'auto_migrate' is True, the 'migrate' method is called immediately.
        """
        
        self.cold_mode = cold_mode
        self.include_non_index_files = include_non_index_files
        
        if max_workers is None:
            self._workers = __MAX_AMOUNT_OF_WORKERS
        else:
            self._workers = max_workers
            
        # Default ancestor is the previous migration
        self._migration_ancestor = self.migration_id - 1 if self.migration_id != None else None 
        self._migration_descendant = self.migration_id + 1 # Default descendant is the next migration
        self._from_to_string = f'{self.migration_id}->{self._migration_descendant}' # Default migration string
        
        self._migration_data = {
            'index': {},
            'rawfiles': {}
        }
        self._rejectpile = {
            'index': {},
            'rawfiles': {}
        }
        
        # Overwrites the default HSDB path with the default value
        self.overwrite_hsdb_path(self._hsdb_path) 
        if auto_migrate:
            self.run() # Proceed with migration if 'auto_migrate' is True
        
    def _parse_index_files(self) -> List[dict]:
        
        import re
        def _parse_name(raw_name:str, seperator:str='-') -> None:
            return re.sub(r'(?<!^)(?=[A-Z])', seperator, raw_name).lower()
        
        print('Parsing index files from disk')
        parsed_index_data = {}
        parsing_errors_found = False
        for model in self.models:
            model_plural_name = _parse_name(model.__name__).replace('-model', '')
            model_plural_name = model_plural_name + 's' if not model_plural_name.endswith('s') else model_plural_name + 'es'
            model_path = f'{self._index_path}/{model_plural_name}'
            if not path.exists(model_path):
                continue
            
            parsed_index_data[model_plural_name] = []
            self._migration_data['index'][model_plural_name] = []
            self._rejectpile['index'][model_plural_name] = []
            
            index_files = file.list(f'{self._index_path}/{model_plural_name}',
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
                    self.reject_migration_index(parsing_error.entry_model,
                                                { 'id': parsing_error.entry_id },
                                                reason=f'index-{parsing_error.error}')
                    err(f'      {parsing_error.error}: {parsing_error.entry_id}', use_prefix=False, verbose=False)
                println()
                
        return parsed_index_data

    def auto_create(self) -> None:
        """
        Sets '_auto_creation_datetime' to the current time in ISO format
        and marks the migration as automatically created.
        """
        self._auto_creation_datetime = str(dt.now().isoformat())
        self.was_auto_created = True # Acknowledges auto-creation
        
    def add_to_migration_index(self, model:str, data:dict) -> None:
        self._migration_data['index'][model].append(data)
        
    def add_to_migration_rawfiles(self, key:str, data:dict) -> None:
        self._migration_data['rawfiles'][key].append(data)
        
    def reject_migration_index(self, model:str, data:dict, reason:str) -> None:
        rejection = _HSDBMigrationRejection(reason, {
            'app': self.app_name,
            'id': self.migration_id,
            'name': self.migration_name
        })
        self._rejectpile['index'][model].append({'data': data, 'rejection': rejection.as_dict()})
        
    def reject_migration_rawfiles(self, key:str, data:dict, reason:str) -> None:
        rejection = _HSDBMigrationRejection(reason, {
            'app': self.app_name,
            'id': self.migration_id,
            'name': self.migration_name
        })
        self._rejectpile['rawfiles'][key].append({'data': data, 'rejection': rejection.as_dict()})

    def overwrite_hsdb_path(self, hsdb_path:str) -> None:
        """
        Allows changing the default HSDB path to a custom path.
        """
        self._hsdb_path = hsdb_path  # Updates the HSDB path with the new value
        
        self._index_path = path.join(hsdb_path, 'index') # Default index path
        self._rawfiles_path = path.join(hsdb_path, 'rawfiles') # Default rawfiles path
        
        self._rejectpile_path = path.join(hsdb_path, 'rejectpile') # Default rejectpile path
        self._rejectpile_index_path = path.join(self._rejectpile_path, 'index')
        self._rejectpile_rawfiles_path = path.join(self._rejectpile_path, 'rawfiles')
        
        backups_path = path.join(hsdb_path, 'backups')
        migration_backups_path = path.join(backups_path, 'migrations')
        self._migration_backup_path = path.join(migration_backups_path, self._from_to_string)
        
    def migrate(self) -> None:
        if self.cold_mode:
            println()
            hint('Cold mode is active, no changes will be applied.')
            migration_dump_directory = path.join(self._hsdb_path, 'dumps', 'migrations')
            file.write(path.join(migration_dump_directory, f'{self._from_to_string}_migration_data.json'),
                       self._migration_data,
                       force_format='json',
                       prettify=True)
            log('   Dumped migration data to disk')
            file.write(path.join(migration_dump_directory, f'{self._from_to_string}_rejectpile.json'),
                       self._rejectpile,
                       force_format='json',
                       prettify=True)
            log('   Dumped rejectpile data to disk')
            log('   Check path for dumped data:')
            log(f'      {migration_dump_directory}')
    
    def run(self) -> None:
        self._parsed_index_data = self._parse_index_files()
        self._migrated_at = dt.now().isoformat()
        
        println()
        hint(f'Creating a local backup of the data before the {self._from_to_string} migration in the following path:')
        log('   ' + self._migration_backup_path)
        println()
        
        hint(f'Executing migration {self._from_to_string} for app "{self.app_name}" for data in the following path:')
        log('   ' + self._index_path)
        println()
        
        try:
            self.gather()
            println()
            log('Gathering succeeded')        

            
            try:
                self.migrate()
                println()
                log('Migration succeeded')
                println()
            except:
                err('Migration failed: ', pad_after=1, exit=True, traceback=True)
        except:
            err('Gathering failed: ', pad_after=1, exit=True, traceback=True)
    
    #########
    # Hooks #
    #########
    
    def gather(self) -> None:
        """
        Gathers data for the migration. This method should be implemented in the migration-subclass.
        """
        raise NotImplementedError('"gather()" method must be implemented in migration-subclass')