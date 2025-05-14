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

# From system imports
from abc import ABC
from typing import Generic, List, Type, TypeVar

# From package imports
from teatype.hsdb import HSDBField, HSDBQuery, HybridStorage
from teatype.util import generate_id, kebabify

_AVAILABLE_FIELDS = [
    'primary_model',
    'relation_key',
    'relation_name',
    'relation_type',
    'reverse_lookup',
    'secondary_model',
]
_SUPPORTED_TYPES = [str, List[str]]
# Type alias for attribute types
T = TypeVar('T')

# TODO: Id or something to differentiate between many-to-many relations or think about it more deeply again
# TODO: If model is string, search model database for the model
# TODO: HSDB type is Relation for metadata access, but value is always the query close
# TODO: Internal callable that returns special query with overwritten foreign model and capped queryset in the init of hsdbmodel
# TODO: Accessing the HSDB Relation value returns the query closure object without execution, a one to one executes the query and returns the object by overriding method
# TODO: Dont use references after all, just ids, otherwise whats the point of the index db
class HSDBRelation(HSDBField, Generic[T]):
    """
    This class acts as a descriptor for managing relations between models and as a interface
    for interacting with the relational index of the IndexDatabase singleton instance.
    """
    _hsdb_reference:object # HybridStorage, avoiding import loop
    primary_model:type
    relation_id:str
    relation_name:type
    relation_type:type
    relation_key:str
    reverse_lookup:str
    secondary_model:type
    
    # DEPRECATED: Moved away from caching instances since using relational index
        # def __new__(cls, *args, **kwargs):
        #     # Kwargs not working for some reason, so using args instead
        #     # relation_name = cls._stitch_relation_name(kwargs.get('primary_model'), kwargs.get('secondary_model'), kwargs.get('relation_type'))
        #     relation_name = cls._stitch_relation_name(args[1], args[3], args[4])
            
        #     if relation_name in cls._instances:
        #         instance = cls._instances[relation_name]
        #         for primary_key in args[0]:
        #             if primary_key not in instance.primary_keys:
        #                 instance.addPrimaryKey(primary_key)
        #         for secondary_key in args[2]:
        #             if secondary_key not in instance.secondary_keys:
        #                 instance.addSecondaryKey(secondary_key)
        #         return instance
            
        #     instance = super().__new__(cls)
        #     cls._instances[relation_name] = instance
        #     return instance
    
    def __init__(self,
                 primary_keys:List[str],
                 primary_model:type,
                 secondary_keys:List[str],
                 secondary_model:type,
                 relation_type:type,
                 type:T,
                 editable:bool=True,
                 relation_key:str='id',
                 required:bool=False,
                 reverse_lookup:str=None) -> None:
        super().__init__(editable, True, required, _SUPPORTED_TYPES, type)
        
        self.primary_model = primary_model
        self.relation_key = relation_key
        self.relation_type = relation_type
        self.secondary_model = secondary_model
        self.type = type # This sets the actual type based on the generic argument
        
        self.relation_name = self._stitch_relation_name(primary_model, secondary_model, relation_type)
        reverse_relation_type = relation_type
        if relation_type == 'many-to-one':
            reverse_relation_type = 'one-to-many'
        self.reverse_relation_name = self._stitch_relation_name(secondary_model, primary_model, reverse_relation_type)
        if reverse_lookup is not None:
            self.reverse_lookup = reverse_lookup
        else:
            reverse_lookup_key = kebabify(primary_model.__name__, replace=('-model', ''))
            if relation_type == 'many-to-one' or relation_type == 'many-to-many':
                reverse_lookup_key = f'{reverse_lookup_key}s'
            self.reverse_lookup = reverse_lookup_key
    
        def _query_closure(self, target_model:'type'):
            query = HSDBQuery(target_model)
            subset = { key:query._index_db_reference[key] for key in query._index_db_reference if key in self.secondary_keys }
            query._index_db_reference = subset
            query.model = self.secondary_model
            # query._index_db_reference = {{entry.id:entry for entry in self.secondary_model.query.all()}}
            return query
        
        self.relation_id = generate_id()
        self._hsdb_reference = HybridStorage()
        self._value = _query_closure
        
        self.addKeyPairs(primary_keys, secondary_keys)
    
    def __get__(self, instance, owner):
        if self._wrapper is None:
            self._wrapper = self._RelationWrapper(self._value, self)
        return self._wrapper
    
    @staticmethod
    def _stitch_relation_name(primary_model, secondary_model, relation_type):
        return f'{primary_model.__name__}_{relation_type}_{secondary_model.__name__}'
            
    def _validate_key(self, key:str) -> None:
        if not isinstance(key, str) or not key:
            raise ValueError('key must be a non-empty string')
            
    def _validate_keys(self, keys:List[str]) -> None:
        if not isinstance(keys, list) or not keys:
            raise ValueError('keys must be a non-empty list')
        for key in keys:
            self._validate_key(key)
            
    def addKeyPairs(self,
                    primary_keys:List[str],
                    secondary_keys:List[str]) -> None:
        """
        Add primary and secondary keys to the relation.
        """
        self._validate_keys(primary_keys)
        self._validate_keys(secondary_keys)
        self._hsdb_reference.index_database._relational_index.add(
            relation_name=self.relation_name,
            reverse_relation_name=self.reverse_relation_name,
            relation_type=self.relation_type,
            primary_keys=primary_keys,
            secondary_keys=secondary_keys,
        )
        
    ####################
    # Internal Classes #
    ####################

    class _RelationWrapper(HSDBField._ValueWrapper):
        def __init__(self, value:any, field:str):
            super().__init__(value, field, _AVAILABLE_FIELDS)
    
    class _RelationFactory(ABC, Generic[T]):
        editable:bool
        relation_key:str
        relation_type:str
        required:bool
        reverse_lookup:str
        secondary_model:'type'
        type:T
        
        def __init__(self,
                     secondary_model:'type',
                     editable:bool=True,
                     relation_key:str='id',
                     required:bool=False,
                     reverse_lookup:str=None) -> None:
            self.editable = editable
            self.relation_key = relation_key
            self.required = required
            self.reverse_lookup = reverse_lookup
            self.secondary_model = secondary_model
            self.type = self.__class__.type
            
            self.relation_type = kebabify(self.__class__.__name__)
            
        def lazy_init(self,
                      primary_keys:List[str],
                      primary_model:'type',
                      secondary_keys:List[str]) -> 'HSDBRelation':
            self.apply_ruleset(primary_keys, secondary_keys)
            return HSDBRelation(primary_keys=primary_keys,
                                primary_model=primary_model,
                                secondary_keys=secondary_keys,
                                secondary_model=self.secondary_model,
                                relation_type=self.relation_type,
                                editable=self.editable,
                                relation_key=self.relation_key,
                                required=self.required,
                                reverse_lookup=self.reverse_lookup,
                                type=self.type)
            
        #########
        # Hooks #
        #########
            
        def apply_ruleset(self, primary_keys:List[str], secondary_keys:List[str]) -> None:
            return
    
    class OneToOne(_RelationFactory):
        type=str
        
        def apply_ruleset(self, primary_keys:List[str], secondary_keys:List[str]) -> None:
            if len(primary_keys) > 1 or len(secondary_keys) > 1:
                raise ValueError('One-To-One relation can only have one entry')

    class ManyToOne(_RelationFactory):
        type=str
        
        def apply_ruleset(self, primary_keys:List[str], secondary_keys:List[str]) -> None:
            if len(primary_keys) > 1:
                raise ValueError('Many-To-One relation can only have one primary key entry')

    class ManyToMany(_RelationFactory):
        type=List[str]