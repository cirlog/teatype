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
from teatype.db.hsdb import RawFileStructure
from teatype.io import file, path
from teatype.logging import *

class RawFileHandler:
    _rf_structure:RawFileStructure
    cold_mode:bool
    
    def __init__(self,
                 root_path:str=None,
                 *,
                 cold_mode:bool=False):
        self.cold_mode = cold_mode
        
        self._rf_structure = RawFileStructure(root_path,
                                              cold_mode=cold_mode)
        
    ##############
    # Properties #
    ##############
        
    @property
    def fs(self):
        return self._rf_structure.get_fs()
    
    ##############
    # Public API #
    ##############
        
    # TODO: If new attributes surface (migrations), apply them to old files (backup before)
    def create_entry(self,
                     model_instance:object,
                     compress:bool=False) -> str|None:
        try:
            absolute_path = path.join(self.fs.index.path, model_instance.path)

            if self.cold_mode:
                return absolute_path
            
            if path.exists(absolute_path):
                raise Exception('File already exists')
            
            Model = model_instance.model
            # TODO: If model folder does not exist, create it and put model_meta.json into it
            # TODO: Create variable in path.create for exists ok
            file.write(absolute_path,
                       Model.serialize(model_instance),
                       force_format='json',
                       prettify=not compress,
                       create_parents=True)
            return absolute_path
        except Exception:
            err('Could not create raw file entry.', traceback=True)
            return None
        
    def delete_entry(self,
                     model_instance:object) -> bool:
        try:
            if self.cold_mode:
                return True
            
            absolute_path = path.join(self.fs.index.path, model_instance.path)
            if not path.exists(absolute_path):
                return False
            
            file.delete(absolute_path)
            return True
        except Exception:
            err('Could not delete raw file entry.', traceback=True)
            return False
        
    def update_entry(self,
                     model_instance:object,
                     compress:bool=False) -> str:
        try:
            absolute_path = path.join(self.fs.index.path, model_instance.path)
            if self.cold_mode:
                return absolute_path
            
            if not file.exists(absolute_path):
                raise Exception('File does not exist')

            Model = model_instance.model
            if not path.exists(absolute_path):
                return 'File does not exist'

            file.write(absolute_path,
                       Model.serialize(model_instance),
                       force_format='json',
                       prettify=not compress,
                       create_parents=True)
            return absolute_path
        except Exception:
            err('Could not update raw file entry.', traceback=True)
            return None