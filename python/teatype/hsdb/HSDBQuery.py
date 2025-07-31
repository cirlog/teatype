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
from functools import reduce
from pprint import pprint
from typing import List, Union

# From package imports
from teatype.hsdb import HybridStorage
from teatype.logging import log, println
from teatype.util import stopwatch

_EXECUTION_HOOKS = ['__iter__', '__len__', '__getitem__', 'all', 'collect', 'first', 'last', 'set']
_OPERATOR_VERBS = [('eq', 'equals'),
                   ('ge', 'greater_than_or_equals'),
                   ('le', 'less_than_or_equals'),
                   ('lt', 'less_than'),
                   ('gt', 'greater_than')]

# TODO: Add support for running queries on querysets again after execution to allow reducing even further after initial query
class HSDBQuery:
    _conditions:List
    _current_attribute:str
    _executed_hook:str
    _filter_key:str
    _hsdb_reference:object # HybridStorage, avoiding import loop
    _measure_time:bool
    _pagination:Union[int, int]
    _print:bool
    _return_ids:bool
    _sort_key:str
    _sort_order:str
    _verbose:bool
    already_executed:bool
    model:type # HSDBModel class, avoiding import loop
    
    def __init__(self, model:type):
        # model is used later to help interpret attribute types and relations
        self.model = model
        
        self.already_executed = False
        
        self._conditions = [] # list of (attribute_path, operator, value)
        self._current_attribute = None
        self._executed_hook = None
        self._filter_key = None
        self._hsdb_reference = HybridStorage()
        self._measure_time = False
        self._pagination = None
        self._print = False
        self._return_ids = False
        self._sort_key = None
        self._sort_order = None
        self._verbose = False

    def __repr__(self):
        repr = '<HSDBQuery '
        model_name = str(self.model).split('.')[-1].replace('\'', '').replace('>', '')
        repr += f'model={model_name} '
        
        if self._conditions:
            repr += f'conditions={str(self._conditions)} '
            
        if self._filter_key:
            repr += f'filter_key="{self._filter_key}" '
            
        if self._sort_key:
            repr += f'sort_by="{self._sort_key}" '
            repr += f'sort_order="{self._sort_order}" '
            
        if self.already_executed:
            repr += f'exec={self._executed_hook}()'
        repr += '>'
        return repr
                
    def __str__(self):
        return self.__repr__()

    def _add_condition(self, op, value):
        if self._current_attribute is None:
            raise ValueError('No attribute specified. Call where() first.')
        # Each condition is stored with its attribute path, operator, and value.
        self._conditions.append((self._current_attribute, op, value))
        self._current_attribute = None
        
    def _block_executed_query(self, include_pending_condition:bool=False):
        # Including this check to prevent repetition of unnecessary code since all methods need to check for ran query anyways
        if include_pending_condition:
            if self._current_attribute is not None:
                raise ValueError('No value specified for attribute. Call a operator verb first: ' + ', '.join([v for k, v in _OPERATOR_VERBS]))
            
        if self.already_executed:
            raise ValueError('Query already executed. Call a new query property to start a new query.')
    
    def _run_query(self, id:str=None):
        self._block_executed_query()
        
        try:
            """
            Execute a query representation on an in-memory db.

            Parameters:
            query: HSDBQuery instance with conditions and sort_key.

            Returns:
            List of identifiers that match the query if self._return_ids is True.
            List of entry that match the query if self._return_ids is False.
            """
            with self._hsdb_reference.index_database._db_lock:
                # Check if the database is empty
                if not self._hsdb_reference.index_database._db:
                    raise KeyError('No db entries found')
                    
                if self._verbose and self._measure_time:
                    stopwatch('Query runtime')
                
                if id:
                    queryset = [self._hsdb_reference.index_database._db[id]]
                else:
                    def __get_nested_value(entry, attribute_path:str) -> any:
                        """
                        Retrieve the value of a nested attribute path in the entry.

                        This method now handles nested class attributes and avoids repeated class lookups
                        by utilizing the attribute index.
                        """
                        parts = attribute_path.split('.')
                        # Use a reduce to iterate over the attribute parts
                        def lookup_value(accumulated_value, part):
                            if isinstance(accumulated_value, dict):
                                # If it's a dict, look up the value by key
                                return accumulated_value.get(part, None)
                            elif hasattr(accumulated_value, part):
                                # If it's an object, use getattr to get the attribute
                                return getattr(accumulated_value, part, None)
                            else:
                                return None
                        # Initial value is the entry object itself (which may be a dictionary or class instance)
                        return reduce(lookup_value, parts, entry)

                    def __condition_matches(entry, condition):
                        attribute, operator, expected = condition
                        actual_attribute = __get_nested_value(entry, attribute)
                        actual_value = actual_attribute._value
                        if operator == '==':
                            return actual_value == expected
                        elif operator == '<':
                            return actual_value is not None and actual_value < expected
                        elif operator == '>':
                            return actual_value is not None and actual_value > expected
                        elif operator == '<=':
                            return actual_value is not None and actual_value <= expected
                        elif operator == '>=':
                            return actual_value is not None and actual_value >= expected
                        elif operator == '∋':
                            # Check if the value is in the list
                            return expected in actual_value if isinstance(actual_value, list) else False
                        else:
                            raise ValueError(f'Unsupported operator {operator}')
                        
                    self._block_executed_query()

                    # First filter using conditions.
                    queryset = []
                    for entry_id, entry in self._hsdb_reference.index_database._db.items():
                        if entry.model != self.model:
                            continue
                        if all(__condition_matches(entry, condition) for condition in self._conditions):
                            if self._return_ids:
                                queryset.append(entry_id)
                            else:
                                queryset.append(entry)

                    # TODO: Add support for nested values in sorting and filtering
                    # Sort the queryset if needed.
                    if self._sort_key:
                        queryset.sort(key=lambda entry: getattr(entry, self._sort_key)._value, reverse=self._sort_order == 'desc')
                        
                    if self._filter_key:
                        queryset = [getattr(entry, self._filter_key) for entry in queryset]
                        
                    # Pagination logic
                    if self._pagination:
                        page, page_size = self._pagination
                        total_entries = len(queryset)
                        if page < 0:
                            page = max((total_entries // page_size) - 1, 0) # Last page
                        start_index = page * page_size
                        end_index = start_index + page_size
                        queryset = queryset[start_index:end_index]
                        
                    self.already_executed = True
                    
                if self._verbose:
                    log(self)
                    if self._measure_time:
                        stopwatch()
                    found_message = f'Found {len(queryset)} hit' + ('s' if len(queryset) > 1 else '')
                    log(found_message)
                    
                    if self._print:
                        print('Queryset:')
                        for entry in queryset:
                            pprint(entry.model.serialize(entry))
                    println()
            
            # Return list of ids.
            return queryset
        except KeyError as ke:
            self.already_executed = True
            if id:
                raise KeyError(f'No db entry found with id "{id}"')
            raise KeyError(ke)
    
    def sort_by(self, attribute_name:str, sort_order:str='asc'):
        self._block_executed_query(include_pending_condition=True)
        self._sort_key = attribute_name
        self._sort_order = sort_order
        return self

    def filter_by(self, attribute_name:str):
        self._block_executed_query(include_pending_condition=True)
        # Set the attribute to include in the query results.
        # When the query is executed, only records with this attribute will be returned 
        # as dictionaries containing just that attribute.
        self._filter_key = attribute_name
        return self
    
    #####################
    # Runtime modifiers #
    #####################
    
    def return_ids(self):
        self._block_executed_query()
        self._return_ids = True
        return self
    
    def verbose(self, measure_time:bool=True, print:bool=False):
        self._block_executed_query()
        self._print = print
        self._measure_time = measure_time
        self._verbose = True
        return self
    
    ###################
    # Execution hooks #
    ###################
    
    def __iter__(self):
        """
        Trigger execution when iterating.
        """
        self._executed_hook = '__iter__'
        return iter(self._run_query())

    def __len__(self):
        """
        Trigger execution when len() is called.
        """
        self._executed_hook = '__len__'
        return len(self._run_query())

    def __getitem__(self, index):
        """
        Trigger execution when accessing an item.
        """
        self._executed_hook = '__getitem__'
        return self._run_query()[index]

    def all(self):
        # Calling all resets any previous conditions
        self._conditions = []
        self._executed_hook = 'all'
        return self._run_query()
    
    def collect(self):
        """
        Forcing the query to execute and return the results without any special actions.
        """
        self._executed_hook = 'collect'
        return self._run_query()
    
    def count(self):
        """
        Alias for len().
        """
        self._executed_hook = 'count'
        return len(self)
    
    # TODO: Dynamically generate args with kwargs with unique model fields
    def get(self, id:str):
        # Get a record with the given id.
        self._executed_hook = 'get'
        return self._run_query(id)[0]
    
    def first(self):
        self._executed_hook = 'first'
        return self.paginate(0, 1)[0]
        
    def last(self):
        self._executed_hook = 'last'
        return self.paginate(-1, 1)[0]
    
    def paginate(self, page:int, page_size:int):
        self._pagination = (page, page_size)
        self._executed_hook = 'paginate'
        return self._run_query()
    
    ##################
    # Operator verbs #
    ##################
    
    def contains(self, value:any):
        self._block_executed_query()
        self._add_condition('∋', value)
        return self
    
    def equals(self, value:any):
        self._block_executed_query()
        self._add_condition('==', value)
        return self

    def greater_than(self, value:any):
        self._block_executed_query()
        self._add_condition('>', value)
        return self
    
    def greater_than_or_equals(self, value:any):
        self._block_executed_query()
        self._add_condition('>=', value)
        return self

    def less_than(self, value:any):
        self._block_executed_query()
        self._add_condition('<', value)
        return self
    
    def less_than_or_equals(self, value:any):
        self._block_executed_query()
        self._add_condition('<=', value)
        return self

    def where(self, attribute_name:str):
        self._block_executed_query(include_pending_condition=True)
        # Set current attribute that the following operator verb will apply to
        self._current_attribute = attribute_name
        return self
    
    ####################
    # Operator aliases #
    ####################
    
    def eq(self, value:any) -> 'HSDBQuery': return self.equals(value)
    def gt(self, value:any) -> 'HSDBQuery': return self.greater_than(value)
    def gte(self, value:any) -> 'HSDBQuery': return self.greater_than_or_equals(value)
    def lt(self, value:any) -> 'HSDBQuery': return self.less_than(value)
    def lte(self, value:any) -> 'HSDBQuery': return self.less_than_or_equals(value)
    def w(self, attribute_name: str) -> 'HSDBQuery': return self.where(attribute_name)