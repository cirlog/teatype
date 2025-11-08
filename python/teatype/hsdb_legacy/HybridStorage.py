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

# Standard library imports
import threading
from typing import List
from datetime import datetime as dt

# Third-party imports
from multiprocessing import Queue
from teatype.hsdb_legacy import IndexDatabase, RawFileHandler
from teatype.io import env
from teatype.logging import *
from teatype.toolkit import SingletonMeta

# TODO: Implement Coroutine and Operation (Atomic)
# TODO: Implement threaded Coroutine scheduler
# TODO: Implement threaded Operations controller
class HybridStorage(threading.Thread, metaclass=SingletonMeta):
    coroutines:List
    coroutines_queue:Queue
    fixtures:dict
    index_database:IndexDatabase
    operations_queue:Queue
    raw_file_handler:RawFileHandler

    def __init__(self, init:bool=False, models:List[type]=None, overwrite_root_data_path:str=None):
        if not init:
            return
        
        # Only initialize once
        if not getattr(self, '_initialized', False):
            # Prevent re-initialization
            self.coroutines = []
            self.index_database = IndexDatabase(models=models)

            # Set the root data path
            if overwrite_root_data_path:
                root_data_path = overwrite_root_data_path
            else:
                root_data_path = env.get('HSDB_ROOT_PATH')

            self.raw_file_handler = RawFileHandler(root_path=root_data_path)

            self._initialized = True # Mark as initialized
            self.__instance = self # Set the instance
            
            log('HybridStorage finished initialization')
    
    @staticmethod
    def instance():
        if not hasattr(HybridStorage, '__instance'):
            HybridStorage.__instance = HybridStorage(init=True)
        return HybridStorage.__instance
        
    def fill(self):
        pass
    
    # def register_model(self, model:object):
    #     self.index_database.models.append(model)
            
    def install_fixtures(self, fixtures:List[dict]):
        for fixture in fixtures:
            model_name = fixture.get('model')
            
            matched_model = next((cls for cls in self.index_database.models if cls.__name__ == model_name), None)
            if matched_model is None:
                raise ValueError(f'Model {model_name} not found in models')
            
            # Loop through each entry in fixture
            for entry in fixture.get('fixtures'):
                id = entry.get('id')
                base_data = entry.get('base_data') # Retrieve the base data portion of the fixture
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
                except:
                    pass # It's okay if these keys don't exist
                
                full_data = {**base_data, **data} # Merge base_data into data
                self.feed_entry(matched_model, {'id': id, **full_data})
                
    def install_raw_data(self, parsed_raw_data:List[dict]):
        for raw_data in parsed_raw_data:
            model_name = raw_data.get('model_data').get('model_name')
            matched_model = next((cls for cls in self.index_database.models if cls.__name__ == model_name), None)
            if matched_model is None:
                raise ValueError(f'Model {model_name} not found in models')
            
            id = raw_data.get('id')
            base_data = raw_data.get('base_data')
            data = raw_data.get('data')
            migration_data = raw_data.get('migration_data') # Retrieve the migration data portion of the fixture
            full_data = {**base_data, **data, **migration_data} # Merge base_data into data
            
            if self.get_entry(id):
                continue
                
            self.feed_entry(matched_model, {'id': id, **full_data})
            
    def feed_entry(self, model:object, data:dict, overwrite_path:str=None) -> dict|None:
        try:
            model_instance = self.index_database.create_entry(model, data, overwrite_path)
            if model_instance is None:
                return None
            file_path = self.raw_file_handler.create_entry(model_instance, overwrite_path)
            return model_instance.serialize()
        except Exception as exc:
            import traceback
            traceback.print_exc()
            return None

    def create_entry(self, model:object, data:dict, overwrite_path:str=None) -> dict|None:
        try:
            model_instance = self.index_database.create_entry(model, data, overwrite_path)
            if model_instance is None:
                return None
            
            if model_instance.model_name == 'InstrumentModel':
                try:
                    instrument_type_name = model_instance.instrument_type
                    instrument_type_id = self.index_database._indexed_fields['InstrumentTypeModel_name'][instrument_type_name]
                    self.index_database._db[instrument_type_id].updated_at = dt.now()
                    
                    self.raw_file_handler.update_entry(self.index_database._db[instrument_type_id], overwrite_path)
                except Exception as exc:
                    traceback.print_exc()
                    
                try:
                    manufacturer_name = model_instance.manufacturer
                    manufacturer_id = self.index_database._indexed_fields['ManufacturerModel_name'][manufacturer_name]
                    self.index_database._db[manufacturer_id].updated_at = dt.now()
                    
                    self.raw_file_handler.update_entry(self.index_database._db[manufacturer_id], overwrite_path)
                except Exception as exc:
                    traceback.print_exc()
                    
                try:
                    surgery_type_name = model_instance.surgery_type
                    surgery_type_id = self.index_database._indexed_fields['SurgeryTypeModel_name'][surgery_type_name]
                    self.index_database._db[surgery_type_id].updated_at = dt.now()
                    
                    self.raw_file_handler.update_entry(self.index_database._db[surgery_type_id], overwrite_path)
                except Exception as exc:
                    traceback.print_exc()
                    
            file_path = self.raw_file_handler.create_entry(model_instance, overwrite_path)
            # TODO: If file save fails, delete entry from db
            # TODO: Implement implemented trap cleanup handlers in models
            return model_instance.serialize()
        except Exception as exc:
            import traceback
            traceback.print_exc()
            return None

    def get_entry(self, model_id:str, serialize:bool=False) -> dict:
        return self.index_database.get_entry(model_id, serialize)

    def get_entries(self, model:object, serialize:bool=False, sort_by:str='updated_at') -> List[dict]:
        entries = self.index_database.get_entries(model, serialize)
        if sort_by == 'updated_at':
            print('Sorting by updated_at')
            entries.sort(key=lambda x: x['base_data']['updated_at'], reverse=True)
        else:
            entries.sort(key=lambda x: x[sort_by], reverse=True)
        return entries

    def modify_entry(self) -> bool:
        return True

    def delete_entry(self) -> bool:
        return True