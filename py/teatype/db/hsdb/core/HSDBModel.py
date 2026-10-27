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
from teatype.db.hsdb.core import HSDBAttribute, HSDBMeta, HSDBQuery, HSDBRelation
from teatype.toolkit import dt, staticproperty
from teatype.toolkit import generate_id, kebabify

# TODO: Implement auto-compute variable for count of reverse lookup models (amount_of_<relation_name>s)
#       - blocked: HSDBRelation._RelationWrapper only resolves 'many-to-one' lookups today;
#         one-to-many/many-to-many resolution needs to be finished in HSDBRelation.py first
# TODO: Add allowing to use string literal for relation name to avoid circular imports
#       - belongs in HSDBRelation._RelationFactory (resolve secondary_model via HybridStorage.index_db.models)
# TODO: Add language supports (needs a concrete i18n spec: which fields, storage format, fallback rules)
class HSDBModel(ABC, metaclass=HSDBMeta):
    # Private class variables
    _attribute_cache = {} # Attributes cached per-class on first instantiation (lazy init)
    _short_key_cache = {} # Compact per-attribute short keys, keyed by class then attribute name
    
    # Public class variables
    model:type['HSDBModel']
    model_name:str
    path:str
    resource_name:str
    resource_name_plural:str
    migration_id:int
    
    # HSDB attributes
    created_at = HSDBAttribute(dt,  computed=True)
    id         = HSDBAttribute(str, computed=True, unique=True)
    updated_at = HSDBAttribute(dt,  computed=True)
    
    def __init__(self,
                 data:dict=None,
                 include_base_attributes:bool=True,
                 overwrite_path:str=None,
                 _restore:dict=None,
                 **kwargs):
        data = {**(data or {}), **kwargs} # Fields may be passed as a dict, kwargs, or both
        restored = _restore or {} # Preset id/created_at/updated_at, used when loading from disk or when the client picks the id
        
        # For every class variable that is an HSDBAttribute,
        # create an instance deepcopy, assign its key to the variable name,
        # and, if the field is provided in the data dict, set its value.
        # Necessary to avoid sharing the same attribute instance across all instances.
        # Look up cached attributes for this class
        # Cache the attributes if not already cached
        if self.__class__ not in self._attribute_cache:
            self._cache_attributes()
            
        # Model name and pluralization: computed once per class, then cached as class attributes
        cls = self.__class__
        self.model = cls
        if 'model_name' not in cls.__dict__:
            cls.model_name = cls.__name__
            cls.resource_name = kebabify(cls.model_name, remove='-model', plural=False)
            cls.resource_name_plural = kebabify(cls.model_name, remove='-model', plural=True)
        
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
        
        self.id = restored.get('id') or generate_id()
                
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
        self.created_at = restored.get('created_at', current_time)
        self.updated_at = restored.get('updated_at', current_time)
            
        if overwrite_path:
            self.path = overwrite_path
        self.path = f'{self.resource_name_plural}/{self.id}.json'
    
    def __repr__(self):
        """
        Return a readable string representation of the model instance.
        """
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
                # Ids from JSON payloads are plain strings, so wrap them into a field like model-attribute ids
                def to_field(value):
                    if hasattr(value, 'instance'):
                        return value.instance
                    id_field = HSDBAttribute(str)
                    id_field.value = value
                    return id_field
                if attribute.type == List[str]:
                    instance_value = [to_field(v) for v in value]
                else:
                    instance_value = [to_field(value)]
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
    
    def _cache_attributes(self):
        """
        Cache the attributes for this class (including its ancestors).
        Runs once per class (result is memoized in `_attribute_cache`), then
        assigns each attribute a compact `shortkey` for optional compression.
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

        self._assign_short_keys(self.__class__, self._attribute_cache[self.__class__])

    @classmethod
    def _assign_short_keys(cls, model:type, attributes:dict) -> None:
        """
        Compute a compact short key for every attribute by abbreviating each
        underscore-separated segment to its first letter (e.g. `created_at` -> `ca`).
        Collisions are resolved with a numeric suffix, growing its width as needed.
        Stored separately from the attribute descriptor (rather than as a `shortkey`
        attribute on it) so it doesn't interfere with instance field reconstruction
        in `__setattr__`. Purely additive metadata; does not affect serialize()/save().
        """
        short_keys = {}
        used_short_keys = set()
        for attribute_name, attribute in attributes.items():
            if isinstance(attribute, HSDBRelation._RelationFactory):
                continue # Relations don't carry a short key
            base_short_key = ''.join(segment[0] for segment in attribute_name.split('_') if segment)
            short_key = base_short_key
            suffix_length = 1
            suffix = 0
            while short_key in used_short_keys:
                suffix += 1
                if suffix >= 10 ** suffix_length:
                    suffix_length += 1
                short_key = f'{base_short_key}{suffix:0{suffix_length}d}'
            used_short_keys.add(short_key)
            short_keys[attribute_name] = short_key
        cls._short_key_cache[model] = short_keys

    @classmethod
    def short_key(cls, attribute_name:str) -> str:
        """Return the compact short key computed for a given attribute name."""
        return cls._short_key_cache.get(cls, {}).get(attribute_name)
                    
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
    
    @classmethod
    def serialize(cls,
                  instance:'HSDBModel',
                  include_relations:bool=False,
                  expand_relations:bool=False,
                  json_dump:bool=False) -> dict|str:
        """
        Serialize a model instance to a dictionary.
        
        Args:
            instance: The model instance to serialize
            include_relations: Whether to include relations (as IDs)
            expand_relations: Whether to expand relations to full serialized objects
            json_dump: Whether to return a JSON string instead of dict
            
        Returns:
            Serialized dict or JSON string
        """
        serialized_data = instance.serializer.copy()
        
        # Handle relations
        if include_relations or expand_relations:
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
            attribute = self._attribute_cache.get(self.__class__, {}).get(key)
            if attribute is None:
                continue
            if value is None and isinstance(attribute, HSDBRelation._RelationFactory) and not attribute.required:
                relation = self.__dict__['_fields'].pop(key, None) # None unsets an optional relation
                if relation is not None:
                    storage.index_db._relational_index.discard(relation.relation_name, relation.reverse_relation_name, self.id.instance)
            else:
                setattr(self, key, value)
        
        self.updated_at = dt.now()
        
        # Re-index new values
        storage.index_db._index_entry_fields(self)
        
        return self
    
    def validate(self) -> bool:
        """
        Re-validate every cached attribute of this instance against its
        constraints (required, type, max_size). Raises ValueError on the
        first violation found; returns True if everything checks out.
        
        Returns:
            True if the instance is valid
        """
        for attribute_name, attribute in self._attribute_cache.get(self.__class__, {}).items():
            if isinstance(attribute, HSDBRelation._RelationFactory):
                if attribute.required and attribute_name not in self._fields:
                    raise ValueError(f'Model "{self.model_name}" validation error: "{attribute_name}" is required')
                continue
            
            if attribute_name not in self._fields:
                if attribute.required and not attribute.computed:
                    raise ValueError(f'Model "{self.model_name}" validation error: "{attribute_name}" is required')
                continue
            
            if attribute.computed:
                continue # Computed fields are system-managed, not user input; skip re-validation
            
            value = getattr(self, attribute_name)._value
            if value is not None and not isinstance(value, attribute.type):
                raise ValueError(f'Field "{attribute_name}" must be of type {attribute.type.__name__}')
            if attribute.type is str and value is not None and len(value) > attribute.max_size:
                raise ValueError(f'Field "{attribute_name}" exceeds maximum size ({attribute.max_size})')
        return True
    
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
        from teatype.db.hsdb.core import HSDBAttribute, HSDBRelation
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