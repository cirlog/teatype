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
import threading
import traceback
from multiprocessing import Queue
from typing import List, Tuple

# Third-party imports
from teatype.enum import EscapeColor
from teatype.db.hsdb import IndexDatabase, RawFileHandler
from teatype.db.hsdb.toolbox import parse_fixtures, parse_index_files
from teatype.io import env, file
from teatype.logging import *
from teatype.toolkit import SingletonMeta

# TODO: Implement Coroutine and Operation (Atomic)
# TODO: Implement threaded Coroutine scheduler
# TODO: Implement threaded Operations controller
class HybridStorage(threading.Thread, metaclass=SingletonMeta):
    """
    HybridStorage manages both an IndexDatabase and a RawFileHandler, 
    combining them to synchronize model entries with file storage in a 
    threaded environment. The SingletonMeta ensures only one instance exists.
    """
    coroutines:List
    coroutines_queue:Queue
    fixtures:dict
    index_db:IndexDatabase
    migrations:dict
    operations_queue:Queue
    rf_handler:RawFileHandler

    # TODO: Put this outside of class context so the first import HybridStorage initializes it
    def __init__(self, models:List[type]=[], root_path:str=None, cold_mode:bool=False) -> None:
        """
        Initialize the HybridStorage thread, ensuring singleton behavior 
        and setting up internal structures for model and file handling.
        
        Args:
            models (List[type], optional): A list of models to be used with the IndexDatabase. Defaults to None.
            root_path (str, optional): The root path for the file storage. Defaults to None.
            cold_mode (bool, optional): Whether to disable writing to disk. Defaults to False.
        """
        # Only initialize once, prevent reinitialization
        if not getattr(self, '_initialized', False):
            threading.Thread.__init__(self)  # Initialize the Thread superclass

            # Set the root data path
            if root_path is None:
                root_path = env.get('HSDB_ROOT_PATH')  # Retrieves path from environment

            self.coroutines = [] # List to keep track of coroutines
            self.coroutines_queue = Queue() # Queue for coroutine scheduling
            self.fixtures = dict # Will store fixture-related data
            self.migrations = dict # Placeholder for storing migration info
            self.operations_queue = Queue() # Queue for operations processing

            self.index_db = IndexDatabase(models) # Create or link an IndexDatabase with given models
            
            self.rf_handler = RawFileHandler(root_path, cold_mode=cold_mode) # Initialize file handler for raw data operations

            self._initialized = True # Mark as initialized
            self.__instance = self # Set the instance for Singleton
            
            success(f'HybridStorage finished initialization') # sucess the initialization
            println()
    
    @classmethod
    def instance(cls) -> 'HybridStorage':
        """
        Return or create the HybridStorage singleton instance.
        """
        print('instance()')
        if not hasattr(HybridStorage, '__instance'):
            print('instance()')
            HybridStorage.__instance = HybridStorage() # Create a default instance if none exists
        print('instance()')
        return HybridStorage.__instance
    
    # def fill(self):
    #     pass
    #
    # def register_model(self, model:object):
    #     self.index_db.models.append(model)
            
    def install_fixtures(self, fixtures_path:str=None) -> None:
        """
        Load and install fixtures from a specified path into the index database.
        """
        # TODO: Get default path if fixtures_path is None
        fixtures:List[dict] = parse_fixtures(fixtures_path=fixtures_path) # Parse fixtures from file(s)
        for fixture in fixtures:
            model_name = fixture.get('model')  # Extract model name from fixture
            matched_model = next((cls for cls in self.index_db.models if cls.__name__ == model_name), None)
            if matched_model is None:
                raise ValueError(f'Model {model_name} not found in models') # Ensure the matching model is present

            # Loop through each entry in fixture
            for entry in fixture.get('fixtures'):
                data = entry.get('data') # Retrieve the data portion of the fixture
                # Check which localized name to use
                if 'de_DE' in data.get('name'):
                    name = data['name']['de_DE']
                elif 'en_EN' in data.get('name'):
                    name = data['name']['en_EN']
                else:
                    name = data.get('name')
                data.update({'name': name}) # Update the data dict to unify 'name'
                try:
                    del data['name']['de_DE']
                    del data['name']['en_EN']
                    # del data['model_data']
                except:
                    pass # It's okay if these keys don't exist

                # Create a new entry in the index database, parse it if needed and write it
                self.create_entry(matched_model, entry, parse=True, write=True)
                
    def install_index_files(self) -> None:
        """
        Read index files, parse them, and create entries for them in the database if not already present.
        """
        parsed_index_files:List[dict] = parse_index_files(hybrid_storage_instance=self) # Parse index files
        for index_key in parsed_index_files:
            # Retrieve the model_name from the data
            model_name = parsed_index_files[index_key][0].get('model_data').get('model_name')
            matched_model = next((cls for cls in self.index_db.models if cls.__name__ == model_name), None)
            if matched_model is None:
                raise ValueError(f'Model {model_name} not found in models') # Ensure the model is present

            # For each file, check if an entry already exists; if not, create it
            for index_file in parsed_index_files[index_key]:
                id = index_file.get('base_data').get('id') # Identify the unique ID
                if self.fetch_entry(id):
                    continue # Skip creation if it already exists in the database
                
                # Create a new entry for the index file, do not write if parse is enough
                self.create_entry(matched_model, index_file, parse=True, write=False)

    def create_entry(self,
                     model:object,
                     data:dict,
                     parse:bool=False,
                     write:bool=True,
                     overwrite_path:str=None) -> Tuple[dict|None, int]:
        """
        Create a new entry for a given model, optionally parsing the 
        entry data and writing it to the file system.
        """
        try:
            # TODO: Implement implemented trap cleanup handlers in models
            # The index database is asked to create an entry from data
            model_instance, return_code = self.index_db.create_entry(model, data, parse)
            if model_instance is None: # If for some reason creation fails
                return None, return_code
            
            if write: # If writing to disk is enabled
                try:
                    if return_code == 200:
                        file_path = self.rf_handler.create_entry(model_instance, overwrite_path)
                        # If the file does not exist after creation, rollback the index entry
                        if not file.exists(file_path):
                            model_instance.delete()
                            return None, 410 # Indicate that writing failed
                except:
                    err('HybridStorage.create_entry() encountered an exception during file writing.', traceback=True)
                    model_instance.delete()
                    # self.rf_handler.delete_entry(model_instance, overwrite_path)
                    return None, 410 # Indicate internal server error
            return model_instance.serialize(), return_code # Return the serialized model instance
        except:
            # TODO: Implement global RUNTIME_CONFIG that is accessible everywhere for all modules and is modified by service modulos
            # if RUNTIME_CONFIG.DEBUG_MODE:
            traceback.print_exc()
            err('HybridStorage.create_entry() encountered an exception during entry creation.', traceback=True)
            return None, 500 # Indicate internal server error

    def fetch_entry(self,
                    id:str, 
                    *,
                    serialize:bool=False) -> dict:
        """
        Retrieve an entry from the index database by its ID, 
        optionally returning a serialized version.
        """
        return self.index_db.fetch_entry(id, serialize)

    def fetch_model_entries(self,
                            model:object, 
                            *,
                            serialize:bool=False,
                            sort_by:str='updated_at',
                            sort_desc:bool=True) -> List[dict]:
        """
        Return all entries for a given model, optionally serialized.
        """
        entries = self.index_db.fetch_model_entries(model, serialize)
        if sort_by == 'updated_at':
            entries.sort(key=lambda x: x['updated_at'], reverse=sort_desc)
        else:
            entries.sort(key=lambda x: x[sort_by], reverse=sort_desc)
        return entries

    def modify_entry(self) -> bool:
        """
        Placeholder for entry modifications, returning True for now.
        """
        # TODO: Make backup of data before modifications
        #       Delete backup when write was succesful
        return True

    def delete_entry(self) -> bool:
        """
        Placeholder for entry deletions, returning True for now.
        """
        return True
