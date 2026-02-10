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
import json
import pprint
from abc import ABC
from typing import List

# Third-party imports
from teatype.db.hsdb import HSDBAttribute, HSDBMeta, HSDBQuery, HSDBRelation
from teatype.toolkit import dt, staticproperty
from teatype.toolkit import generate_id, kebabify

# TODO: Implement a short-key map for attributes for compression
#       - automate by implementing a smart algorithm that first checks how many seperations of underscore are there and then abbreviates that way
#       - it also uses indexing for shortenting attribute names and checks for collisions and adjusts index length accordingly
# TODO: Implement auto-compute variable for count of reverse lookup models (amount_of_<relation_name>s)
# TODO: Replace data with kwargs on init
# TODO: Add allowing to use string literal for relation name to avoid circular imports (need access to hybridstorage to iterate through models)
# TODO: Add validation method inside model
# TODO: Add language supports
class HSDBModel(ABC, metaclass=HSDBMeta):
    # Private class variables
    # _app_name:str # TODO: Implement these as computed properties
    _attribute_cache = {} # Cache to store attributes once for each class # TODO: Set to None and then initialize on first access -> lazy initialization
    # _overwrite_path:str
    # _overwrite_name:str
    # _overwrite_plural_name:str
    # _relations:dict
    
    # Public class variables
    # is_cached:bool=True # Describes whether the model entries are permanently cached in memory
    # is_fixture:bool=False # Describes whether the model instance is a fixture
    model:type['HSDBModel']
    model_name:str
    path:str
    resource_name:str
    resource_name_plural:str
    # migrated_at:dt
    # migration_app_name:str
    migration_id:int
    # migration_name:str
    
    # HSDB attributes
    created_at = HSDBAttribute(dt,  computed=True)
    id         = HSDBAttribute(str, computed=True, unique=True)
    updated_at = HSDBAttribute(dt,  computed=True)
    
    def __init__(self,
                 data:dict,
                 include_base_attributes:bool=True,
                 overwrite_path:str=None):
        # For every class variable that is an HSDBAttribute,
        # create an instance deepcopy, assign its key to the variable name,
        # and, if the field is provided in the data dict, set its value.
        # Necessary to avoid sharing the same attribute instance across all instances.
        # Look up cached attributes for this class
        # Cache the attributes if not already cached
        if self.__class__ not in self._attribute_cache:
            self._cache_attributes()
            
        # TODO: Make this more efficient since only class needs to know this information
        # Model name and pluralization
        self.model_name = type(self).__name__
        self.model = self.__class__
        self.resource_name = kebabify(self.model_name, remove='-model', plural=False)
        self.resource_name_plural = kebabify(self.model_name, remove='-model', plural=True)
        
        # Create a dict to hold instance-specific field values
        self._fields = {}
        for attribute_name, attribute in self._attribute_cache[self.__class__].items():
            if isinstance(attribute, HSDBRelation._RelationFactory):
                if attribute.required and attribute_name not in data:
                    raise ValueError(f'Model "{self.model_name}" init error: "{attribute_name}" is required')
                continue
            
            if attribute.required and not attribute.computed and attribute_name not in data:
                raise ValueError(f'Model "{self.model_name}" init error: "{attribute_name}" is required')
            
            if attribute_name in data:
                # Validate type before assignment
                if not isinstance(data.get(attribute_name), attribute.type):
                    raise ValueError(f'Field "{attribute_name}" must be of type {attribute.type.__name__}')
                if attribute.computed:
                    raise ValueError(f'{attribute_name} is computed and cannot be set')
                setattr(self, attribute_name, data.get(attribute_name))
        
        # TODO: Find a more elegant solution than this ugly a** hack
        # self.id.instance.__computational_override__(generate_id(truncate=5))
        self.id = generate_id()
                
        # Having to initalize lazily, because needing id to properly intialize relations
        for attribute_name, attribute in self._attribute_cache[self.__class__].items():
            if isinstance(attribute, HSDBAttribute):
                continue
            
            # Assume that if the attribute is not an HSDBAttribute, it is a relation
            if attribute_name in data:
                attribute_value = data.get(attribute_name)
                
                if attribute.type == List[str]:
                    if not all(isinstance(item, str) for item in attribute_value) and \
                       not all(isinstance(item, HSDBModel) for item in attribute_value) and \
                       not all(isinstance(item, HSDBAttribute._AttributeWrapper) for item in attribute_value):
                        raise ValueError(f'Field "{attribute_name}" must be a list of id strings or HSDBModel instances')
                else:
                    if not isinstance(attribute_value, attribute.type) and \
                       not isinstance(attribute_value, HSDBModel) and \
                       not isinstance(attribute_value, HSDBAttribute._AttributeWrapper):
                           raise ValueError(f'Field "{attribute_name}" must be of type "{attribute.type.__name__}" or an HSDBModel instance')
                
                # Allowing to pass both model instance and id string
                if isinstance(attribute_value, HSDBModel):
                    attribute_value = attribute_value.id
                elif isinstance(attribute_value, list):
                    # If the attribute is a list of HSDBModel instances, extract their IDs
                    if all(isinstance(item, HSDBModel) for item in attribute_value):
                        attribute_value = [item.id for item in attribute_value]
                    else:
                        attribute_value = [item for item in attribute_value]
                    
                # Initialize the relation lazily
                setattr(self, attribute_name, attribute_value)
        
        current_time = dt.now()
        self.created_at = current_time
        self.updated_at = current_time
            
        if overwrite_path:
            self.path = overwrite_path
        self.path = f'{self.resource_name_plural}/{self.id}.json'
        
        # TODO: Make this dynamic
        # self.app_name = 'raw'
        # self.migration_id = 1
    
    def __repr__(self):
        """Return a readable string representation of the model instance."""
        try:
            id_val = self.id._value if hasattr(self.id, '_value') else str(self.id)
            # Get a few key fields for preview
            preview_fields = []
            for attr_name in list(self._fields.keys())[:3]:
                if attr_name not in ('id', 'created_at', 'updated_at'):
                    try:
                        val = getattr(self, attr_name)
                        val = val._value if hasattr(val, '_value') else val
                        if isinstance(val, str) and len(val) > 20:
                            val = val[:17] + '...'
                        preview_fields.append(f'{attr_name}={repr(val)}')
                    except:
                        pass
            fields_str = ', '.join(preview_fields[:2])
            return f'<{self.model_name} id={id_val[:8]}... {fields_str}>'
        except:
            return f'<{self.__class__.__name__} (uninitialized)>'
    
    def __str__(self):
        return self.__repr__()
    
    def __getattribute__(self, name):
        # If the field name is in our field cache, return the value from _fields
        _cache = object.__getattribute__(self, '_attribute_cache')
        model = type(self)
        if model in _cache and name in _cache[model]:
            return object.__getattribute__(self, '_fields').get(name).__get__(self, self.__class__)
        return object.__getattribute__(self, name)

    def __setattr__(self, name, value):
        # if attribute_name in data:
        #     instance_relation = attribute.lazy_init(
        #         self.id,
                
        #         data.get(attribute_name),
        #     )
        #     instance_relation.key = attribute_name
            
        #     instance_relation.value = attribute._query_closure
        #     setattr(self, attribute_name, attribute_value)
        
        _cache = self.__class__._attribute_cache.get(self.__class__, {})
        if name in _cache:
            attribute = _cache[name]
            if isinstance(attribute, HSDBAttribute):
                instance_attribute = HSDBAttribute(
                    attribute.type, 
                    **{key: value for key, value in vars(attribute).items() if key not in [
                        'name', 'type', '_cached_value', '_key', '_value', '_wrapper']} # Exclude these keys
                )
                instance_attribute.key = attribute.name
                instance_attribute.value = value
            elif isinstance(attribute, HSDBRelation._RelationFactory):
                if attribute.type == list:
                    instance_value = [v.instance if isinstance(v.instance, object) else v.instance for v in value]
                else:
                    instance_value = [value.instance] if isinstance(value.instance, object) else value.instance
                instance_attribute = attribute.lazy_init(
                    [self.id.instance] if isinstance(self.id.instance, object) else self.id.instance,
                    self.model,
                    instance_value
                )
                instance_attribute.key = name
                instance_attribute.value = instance_attribute._value
            self.__dict__.setdefault('_fields', {})[name] = instance_attribute
        else:
            super().__setattr__(name, value)
    
    # TODO: Optimization
    def _cache_attributes(self):
        """
        Cache the attributes for this class (including its ancestors).
        """
        self._attribute_cache[self.__class__] = {}
        seen = set()

        # Traverse through the method resolution order to gather attributes
        for model in reversed(self.__class__.__mro__):
            for attribute_name, attribute in model.__dict__.items():
                if attribute_name in seen:
                    continue
                if isinstance(attribute, HSDBAttribute) or isinstance(attribute, HSDBRelation._RelationFactory):
                    seen.add(attribute_name)
                    self._attribute_cache[self.__class__][attribute_name] = attribute
                    
    @property
    def serializer(self) -> dict:
        """
        If this method is not overridden, collect all HSDBAttribute fields.
        If this method is overridden, collect all fields that are not computed.
        """
        serialized = dict()
        for attribute_name in self.__dict__['_fields']:
            # Skip non-HSDBAttribute fields
            try:
                if attribute_name in self._fields:
                    serialized[attribute_name] = getattr(self, attribute_name)._value
            except Exception as exc:
                continue
        return serialized
        
    @staticproperty
    def query(self):
        # Always return a new query builder instance when query is accessed.
        return HSDBQuery(self)
    
    def print(self):
        pprint.pprint(self.model.serialize(self))
    
    # TODO: Optimization
    # TODO: Group data with key and base data into index data
    @classmethod
    def serialize(cls,
                  instance:'HSDBModel',
                  fuse_data:bool=False,
                  include_migration:bool=False,
                  include_model:bool=False,
                  include_relations:bool=False,
                  expand_relations:bool=False,
                  json_dump:bool=False,
                  strip_attributes:bool=False,
                  use_data_key:bool=False) -> dict|str:
        """
        Serialize a model instance to a dictionary.
        
        Args:
            instance: The model instance to serialize
            fuse_data: Whether to merge base_data and data into a flat dict
            include_migration: Whether to include migration data
            include_model: Whether to include model metadata
            include_relations: Whether to include relations (as IDs)
            expand_relations: Whether to expand relations to full serialized objects
            json_dump: Whether to return a JSON string instead of dict
            strip_attributes: Whether to strip attribute metadata
            use_data_key: Whether to use resource-specific data key
            
        Returns:
            Serialized dict or JSON string
        """
        serialized_data = instance.serializer.copy()
        
        # Handle relations
        if include_relations or expand_relations:
            from teatype.db.hsdb import HSDBRelation, HybridStorage
            
            if instance.__class__ in instance._attribute_cache:
                for attr_name, attr in instance._attribute_cache[instance.__class__].items():
                    if isinstance(attr, HSDBRelation._RelationFactory):
                        try:
                            relation_value = getattr(instance, attr_name)
                            if relation_value is not None:
                                if expand_relations:
                                    # Fully serialize the related object
                                    if hasattr(relation_value, 'model'):
                                        serialized_data[attr_name] = relation_value.model.serialize(
                                            relation_value,
                                            include_relations=False,  # Prevent infinite recursion
                                            expand_relations=False
                                        )
                                    elif isinstance(relation_value, list):
                                        serialized_data[attr_name] = [
                                            item.model.serialize(item, include_relations=False, expand_relations=False)
                                            if hasattr(item, 'model') else str(item)
                                            for item in relation_value
                                        ]
                                    else:
                                        serialized_data[attr_name] = str(relation_value)
                                else:
                                    # Just include the ID(s)
                                    if hasattr(relation_value, 'id'):
                                        rel_id = relation_value.id
                                        serialized_data[attr_name] = rel_id._value if hasattr(rel_id, '_value') else str(rel_id)
                                    elif isinstance(relation_value, list):
                                        serialized_data[attr_name] = [
                                            (item.id._value if hasattr(item.id, '_value') else str(item.id))
                                            if hasattr(item, 'id') else str(item)
                                            for item in relation_value
                                        ]
                                    else:
                                        serialized_data[attr_name] = str(relation_value)
                        except Exception as e:
                            # Relation couldn't be resolved
                            serialized_data[attr_name] = None
        
        if json_dump:
            return json.dumps(serialized_data, indent=4, default=str)
        return serialized_data
    
    def snapshot(self) -> dict:
        snapshot_dict = {}
        for key, value in self.__dict__.items():
            # TODO: If variable is of type HSDBAttribute
            if isinstance(value, dt):
                snapshot_dict[key] = str(value)
        return snapshot_dict
    
    def save(self) -> 'HSDBModel':
        """
        Save this instance to the database.
        If it already exists, updates it; otherwise creates it.
        
        Returns:
            The saved model instance
        """
        from teatype.db.hsdb import HybridStorage
        storage = HybridStorage.instance()
        entry_id = str(self.id)
        
        if entry_id in storage.index_db._db:
            # Update existing
            storage.index_db.update_entry(entry_id, self.serializer)
        else:
            # Add new
            storage.index_db._db.add(entry_id, self)
            storage.index_db._add_to_model_index(self.model_name, entry_id)
            storage.index_db._index_entry_fields(self)
        
        return self
    
    def delete(self) -> bool:
        """
        Delete this instance from the database.
        
        Returns:
            True if deletion was successful
        """
        from teatype.db.hsdb import HybridStorage
        storage = HybridStorage.instance()
        result, code = storage.index_db.delete_entry(str(self.id))
        return result
    
    def update(self, data:dict) -> 'HSDBModel':
        """
        Update this instance with new data and persist to database.
        
        Args:
            data: Dictionary of field names to new values
            
        Returns:
            The updated model instance
        """
        from teatype.db.hsdb import HybridStorage
        storage = HybridStorage.instance()
        
        # Unindex old values
        storage.index_db._unindex_entry_fields(self)
        
        # Update fields
        for key, value in data.items():
            if key in self._attribute_cache.get(self.__class__, {}):
                setattr(self, key, value)
        
        self.updated_at = dt.now()
        
        # Re-index new values
        storage.index_db._index_entry_fields(self)
        
        return self
    
    #######
    # ORM #
    #######
    
    # TODO: Replace with on-init ORM overload
    @classmethod
    def create(cls, data:dict, save:bool=True) -> 'HSDBModel':
        """
        Create a new model instance and optionally save to database.
        
        Args:
            data: Dictionary of field values
            save: Whether to immediately persist to database (default: True)
            
        Returns:
            The created model instance
        """
        instance = cls(data)
        if save:
            instance.save()
        return instance
    
    @classmethod
    def get(cls, id:str) -> 'HSDBModel':
        """
        Get a model instance by ID.
        
        Args:
            id: The entry ID
            
        Returns:
            The model instance or None if not found
        """
        from teatype.db.hsdb import HybridStorage
        storage = HybridStorage.instance()
        try:
            entry = storage.index_db.fetch_entry(str(id))
            if entry and entry.model == cls:
                return entry
            return None
        except KeyError:
            return None
    
    @classmethod
    def all(cls, serialize:bool=False, include_relations:bool=False, expand_relations:bool=False) -> List['HSDBModel']:
        """
        Get all instances of this model.
        
        Args:
            serialize: Whether to return serialized dicts
            include_relations: Whether to include relation IDs
            expand_relations: Whether to expand relations to full objects
            
        Returns:
            List of model instances or serialized dicts
        """
        from teatype.db.hsdb import HybridStorage
        storage = HybridStorage.instance()
        return storage.index_db.fetch_model_entries(
            cls, 
            serialize=serialize,
            include_relations=include_relations,
            expand_relations=expand_relations
        )
    
    @classmethod
    def find_by(cls, field:str, value:any) -> List['HSDBModel']:
        """
        Find all instances where an indexed field equals a value.
        Uses O(1) index lookup if the field is indexed.
        
        Args:
            field: The field name to search by
            value: The value to match
            
        Returns:
            List of matching model instances
        """
        from teatype.db.hsdb import HybridStorage
        storage = HybridStorage.instance()
        
        # Try indexed lookup first
        entry_ids = storage.index_db.lookup_by_field(cls.__name__, field, value)
        if entry_ids:
            return [storage.index_db.fetch_entry(eid) for eid in entry_ids]
        
        # Fall back to query
        return list(cls.query.where(field).equals(value).all())
    
    @classmethod
    def count(cls) -> int:
        """
        Get the count of all instances of this model.
        Uses O(1) model index lookup.
        
        Returns:
            Number of instances
        """
        from teatype.db.hsdb import HybridStorage
        storage = HybridStorage.instance()
        return len(storage.index_db.lookup_by_model(cls.__name__))
    
    #################
    # Class methods #
    #################
    
    @classmethod
    def schema(cls) -> dict:
        """
        Get the schema/structure of this model including all attributes and relations.
        
        Returns:
            Dictionary describing the model structure
        """
        from teatype.db.hsdb import HSDBAttribute, HSDBRelation
        from teatype.toolkit import kebabify
        
        schema = {
            'model_name': cls.__name__,
            'resource_name': kebabify(cls.__name__, remove='-model', plural=False),
            'resource_name_plural': kebabify(cls.__name__, remove='-model', plural=True),
            'attributes': {},
            'relations': {}
        }
        
        # Traverse MRO to get all attributes including inherited ones
        seen = set()
        for model in reversed(cls.__mro__):
            for attr_name, attr in model.__dict__.items():
                if attr_name in seen:
                    continue
                    
                if isinstance(attr, HSDBAttribute):
                    seen.add(attr_name)
                    schema['attributes'][attr_name] = {
                        'type': attr.type.__name__,
                        'required': attr.required,
                        'computed': attr.computed,
                        'editable': attr.editable,
                        'indexed': attr.indexed,
                        'unique': attr.unique,
                        'searchable': attr.searchable,
                        'description': attr.description,
                        'default': attr.default,
                        'max_size': attr.max_size if attr.type == str else None
                    }
                elif isinstance(attr, HSDBRelation._RelationFactory):
                    seen.add(attr_name)
                    schema['relations'][attr_name] = {
                        'type': attr.relation_type,
                        'target_model': attr.secondary_model.__name__,
                        'required': attr.required,
                        'editable': attr.editable,
                        'relation_key': attr.relation_key
                    }
        return schema