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

# From package imports
from teatype.io import env, file, path
from teatype.hsdb import RawFileStructure

class RawFileHandler:
    _raw_file_structure:RawFileStructure
    
    def __init__(self, root_path:str=None):
        self._raw_file_structure = RawFileStructure(root_path)
        
    @property
    def fs(self):
        return self._raw_file_structure.get_fs()
        
    # TODO: If new attributes surface (migrations), apply them to old files (backup before)
    def create_entry(self,
                     model_instance:object,
                     overwrite_path:str,
                     compress:bool=False,
                     include_relational_data:bool=False) -> str:
        try:
            absolute_path = path.join(self.fs.hsdb.index.path, model_instance.path)
            if path.exists(absolute_path):
                return 'File already exists'

            Model = model_instance.model
            # TODO: If model folder does not exist, create it and put model_meta.json into it
            # TODO: Create variable in path.create for exists ok
            file.write(absolute_path,
                       Model.serialize(model_instance),
                       force_format='json',
                       prettify=not compress,
                       create_parents=True)
            return absolute_path
        except Exception as exc:
            raise Exception(f'Could not create raw file entry: {exc}')