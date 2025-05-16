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

class RawFileHandler:
    root_data_path:str
    
    def __init__(self, root_data_path):
        if root_data_path:
            self.root_data_path = root_data_path
        else:
            # root_data_path = env.get('CIRLOG_DATA_PATH')
            root_data_path = '/var/lib/cirlog'
            self.root_data_path = f'{root_data_path}/raw'
            
            # path.create(backups_path)
            # path.create(migration_backups_path)
            # path.create(migration_backup_path)
        
        path.create(self.root_data_path)
        
    # TODO: If new attributes surface (migrations), apply them to old files (backup before)
    def create_entry(self, model_instance:object, overwrite_path:str) -> str:
        try:
            absolute_file_path = path.join(self.root_data_path, model_instance.file_path)
            if path.exists(absolute_file_path):
                return 'File already exists'
        
            # TODO: If model folder does not exist, create it and put model_meta.json into it
            # TODO: Create variable in path.create for exists ok
            file.write(absolute_file_path,
                       model_instance.serialize(),
                       force_format='json',
                       prettify=True,
                       create_parents=True)
            return absolute_file_path
        except Exception as exc:
            raise Exception(f'Could not create raw file entry: {exc}')