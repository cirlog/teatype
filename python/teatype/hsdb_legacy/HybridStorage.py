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
import threading

# From system imports
from typing import List

# From package imports
from multiprocessing import Queue
from teatype.hsdb_legacy import IndexDatabase, RawFileHandler
from teatype.io import env
from teatype.logging import log
from teatype.util import SingletonMeta

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

            self.raw_file_handler = RawFileHandler(root_data_path=root_data_path)

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
            
            for entry in fixture.get('fixtures'):
                id = entry.get('id')
                data = entry.get('data')
                if data.get('de_DE'):
                    name = data['de_DE']['name']
                elif data.get('en_EN'):
                    name = data['en_EN']['name']
                else:
                    name = data.get('name')
                data.update({'name': name})
                try:
                    del data['de_DE']
                    del data['en_EN']
                    del data['model_meta']
                except:
                    pass
                    
                self.create_entry(matched_model, {'id': id, **data})
                
    def install_raw_data(self, parsed_raw_data:List[dict]):
        for raw_data in parsed_raw_data:
            model_name = raw_data.get('model_meta').get('model_name')
            matched_model = next((cls for cls in self.index_database.models if cls.__name__ == model_name), None)
            if matched_model is None:
                raise ValueError(f'Model {model_name} not found in models')
            
            id = raw_data.get('id')
            data = raw_data.get('data')
            
            if self.get_entry(id):
                continue
                
            self.create_entry(matched_model, {'id': id, **data})

    def create_entry(self, model:object, data:dict, overwrite_path:str=None) -> dict|None:
        try:
            model_instance = self.index_database.create_entry(model, data, overwrite_path)
            if model_instance is None:
                return None
            
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

    def get_entries(self, model:object, serialize:bool=False) -> List[dict]:
        return self.index_database.get_entries(model, serialize)

    def modify_entry(self) -> bool:
        return True

    def delete_entry(self) -> bool:
        return True
