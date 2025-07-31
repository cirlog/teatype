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
from abc import ABC, abstractmethod
from typing import List

# From package imports
from teatype.hsdb.util import parse_index_files
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

# TODO: Split between migration number and migration id that gets automatically generated from app, name and number (number still increments)
# TODO: Only list number of errors, write errors into logfile
# TODO: Implement migration protocol
# TODO: Implement trap mechanism to revert migration if it fails
# TODO: Migrations always count one up in id dependent on app and model
# TODO: Always create a snapshot of all models before launching index db and if there are changes, create automatic migrations
# TODO: Always create a backup of all raw db entries before every migration (with optional include_rawfiles flag)
class HSDBMigration(ABC):
    __models_snapshot:dict # Holds snapshot data for models that get migrated
    __rawfiles_snapshot:dict|None # Optionally holds snapshot data for non-index files
    _auto_creation_datetime:str|None # ISO-formatted string for auto creation time
    _from_to_string:str # String representation of the migration's origin and destination
    _hsdb_path:str='/var/lib/hsdb' # Default path on linux
    _index_path:str # Path to the index directory
    _migrated_at:str # ISO-formatted string for migration time
    _migration_ancestor:int # The previous migration's reference, if any
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
    include_rawfiles:bool # Indicates if non-index files should be part of migration steps
    migration_id:int # Numeric identifier to order migrations
    migration_name:str # Descriptive name for the migration
    models:List[type] # List of models that are part of the migration
    was_auto_created:bool # Marks whether the migration was automatically created
    
    def __init__(self,
                 auto_migrate:bool=True, 
                 cold_mode:bool=False,
                 include_rawfiles:bool=False,
                 max_workers:int=None) -> None:
        """
        Initializes the migration. If 'auto_migrate' is True, the 'migrate' method is called immediately.
        """
        self.cold_mode = cold_mode
        self.include_rawfiles = include_rawfiles
        
        if max_workers is None:
            self._workers = __MAX_AMOUNT_OF_WORKERS
        else:
            self._workers = max_workers
            
        # Default ancestor is the previous migration
        self._migration_ancestor = self.migration_id - 1
        self._migration_descendant = self.migration_id + 1 # Default descendant is the next migration
        self._from_to_string = f'{self._migration_ancestor}->{self.migration_id}' # Default migration string
        
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
        println()
        log('Final summary (index):')
        for migration_data_key in self._migration_data['index']:
            print(f'    Migrated {migration_data_key}: {len(self._migration_data["index"][migration_data_key])}')
            for migration_entry in self._migration_data['index'][migration_data_key]:
                migration_entry_path = path.join(self._index_path, migration_data_key, migration_entry['base_data']['id'] + '.json')
                file.write(migration_entry_path,
                            migration_entry,
                            force_format='json',
                            prettify=True)
        println()
        for rejectpile_key in self._rejectpile['index']:
            print(f'    Rejected {rejectpile_key}: {len(self._rejectpile["index"][rejectpile_key])}')
            for rejectpile_entry in self._rejectpile['index'][rejectpile_key]:
                id = rejectpile_entry['data']['base_data']['id']
                rejectpile_source_path = path.join(self._index_path, rejectpile_key, id + '.json')
                rejectpile_target_path = path.join(self._rejectpile_index_path, rejectpile_key, id + '.json')
                file.move(rejectpile_source_path, rejectpile_target_path)
        println()
        
        # TODO: Write migration for rawfiles data
    
    def run(self) -> None:
        self._parsed_index_data = parse_index_files(migrator=self)
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
                else:
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