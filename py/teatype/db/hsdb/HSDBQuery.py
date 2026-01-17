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
import re
from functools import reduce
from pprint import pprint
from typing import Dict, List, Union
from urllib.parse import parse_qs, urlencode

# Third-party imports
from teatype.db.hsdb import HybridStorage
from teatype.logging import *
from teatype.toolkit import stopwatch

_EXECUTION_HOOKS = ['__iter__', '__len__', '__getitem__', 'all', 'collect', 'first', 'last', 'set']
_OPERATOR_VERBS = [('eq', 'equals'),
                   ('ge', 'greater_than_or_equals'),
                   ('le', 'less_than_or_equals'),
                   ('lt', 'less_than'),
                   ('gt', 'greater_than')]

# Reserved query params that are not field conditions
_RESERVED_PARAMS = {'sort', 'order', 'page', 'page_size', 'limit', 'offset', 
                    'include_relations', 'expand_relations', 'fields', 'ids_only'}

# Operator pattern for parsing: field__op=value or field=value (default: equals)
_OPERATOR_PATTERN = re.compile(r'^(.+?)__(eq|ne|gt|gte|lt|lte|contains|in)$')

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
    subset:List[str] # Subset of ids, typically from an index
    
    def __init__(self, model:type):
        # model is used later to help interpret attribute types and relations
        self.model = model
        
        self.already_executed = False
        self.subset = None
        
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
        
    @classmethod
    def from_params(cls, model:type, params:Dict[str, any]) -> 'HSDBQuery':
        """
        Build an HSDBQuery from a dictionary of query parameters.
        
        Supports the following parameter formats:
            - field=value: Equals condition (field == value)
            - field__eq=value: Equals condition
            - field__ne=value: Not equals condition (not yet implemented)
            - field__gt=value: Greater than condition
            - field__gte=value: Greater than or equals condition
            - field__lt=value: Less than condition
            - field__lte=value: Less than or equals condition
            - field__contains=value: Contains condition (for lists)
            - field__in=value1,value2: In condition (not yet implemented)
            
        Reserved parameters:
            - sort: Sort by field (e.g., sort=name or sort=-name for descending)
            - order: Sort order ('asc' or 'desc'), defaults to 'asc'
            - page: Page number (0-indexed)
            - page_size: Number of items per page
            - limit: Alias for page_size
            - offset: Skip first N items
            - include_relations: Include relation IDs in serialization
            - expand_relations: Expand relations to full objects
            - fields: Comma-separated list of fields to return
            - ids_only: Return only IDs
        
        Args:
            model: The HSDBModel class to query
            params: Dictionary of query parameters (e.g., from request.GET)
            
        Returns:
            HSDBQuery instance ready to be executed
            
        Example:
            >>> params = {'age__gte': '18', 'gender': 'male', 'sort': '-name'}
            >>> query = HSDBQuery.from_params(Student, params)
            >>> results = query.collect()
        """
        query = cls(model)
        
        for key, value in params.items():
            # Skip reserved parameters
            if key in _RESERVED_PARAMS:
                continue
                
            # Handle list values (e.g., from QueryDict)
            if isinstance(value, list):
                value = value[0] if len(value) == 1 else value
            
            # Try to parse operator from key
            match = _OPERATOR_PATTERN.match(key)
            if match:
                field_name = match.group(1)
                operator = match.group(2)
            else:
                field_name = key
                operator = 'eq'  # Default to equals
            
            # Convert value to appropriate type
            parsed_value = cls._parse_value(value)
            
            # Add condition based on operator
            query.where(field_name)
            if operator == 'eq':
                query.equals(parsed_value)
            elif operator == 'gt':
                query.greater_than(parsed_value)
            elif operator == 'gte':
                query.greater_than_or_equals(parsed_value)
            elif operator == 'lt':
                query.less_than(parsed_value)
            elif operator == 'lte':
                query.less_than_or_equals(parsed_value)
            elif operator == 'contains':
                query.contains(parsed_value)
            # TODO: Add 'ne' and 'in' operators
        
        # Handle sorting
        sort_field = params.get('sort')
        if sort_field:
            if isinstance(sort_field, list):
                sort_field = sort_field[0]
            
            # Support -field for descending order
            if sort_field.startswith('-'):
                query.sort_by(sort_field[1:], 'desc')
            else:
                sort_order = params.get('order', 'asc')
                if isinstance(sort_order, list):
                    sort_order = sort_order[0]
                query.sort_by(sort_field, sort_order)
        
        # Handle pagination
        page = params.get('page')
        page_size = params.get('page_size') or params.get('limit')
        if page is not None and page_size is not None:
            if isinstance(page, list):
                page = page[0]
            if isinstance(page_size, list):
                page_size = page_size[0]
            query._pagination = (int(page), int(page_size))
        
        # Handle ids_only
        if params.get('ids_only') in ('true', 'True', '1', True):
            query.return_ids()
        
        # Handle filter_by (fields)
        fields = params.get('fields')
        if fields and isinstance(fields, str):
            # For now, only support single field filtering
            query.filter_by(fields.split(',')[0])
        
        return query
    
    @staticmethod
    def _parse_value(value:any) -> any:
        """
        Parse a string value to the appropriate Python type.
        
        Handles:
            - Integers: '123' -> 123
            - Floats: '12.34' -> 12.34
            - Booleans: 'true'/'false' -> True/False
            - None: 'null'/'none' -> None
            - Lists: 'a,b,c' (when comma present and not in quotes)
            - Strings: Everything else
        """
        if value is None:
            return None
            
        if not isinstance(value, str):
            return value
            
        # Handle boolean strings
        if value.lower() == 'true':
            return True
        if value.lower() == 'false':
            return False
            
        # Handle null/none
        if value.lower() in ('null', 'none'):
            return None
            
        # Handle integers
        try:
            return int(value)
        except ValueError:
            pass
            
        # Handle floats
        try:
            return float(value)
        except ValueError:
            pass
        
        # Return as string
        return value
    
    def to_query_string(self) -> str:
        """
        Convert the current query state to a URL query string.
        
        Returns:
            URL-encoded query string (without leading ?)
            
        Example:
            >>> query = Student.query.where('age').gte(18).sort_by('name', 'desc')
            >>> query.to_query_string()
            'age__gte=18&sort=-name'
        """
        params = {}
        
        # Add conditions
        operator_map = {
            '==': 'eq',
            '>': 'gt',
            '>=': 'gte',
            '<': 'lt',
            '<=': 'lte',
            '∋': 'contains'
        }
        
        for attribute, operator, value in self._conditions:
            op_suffix = operator_map.get(operator, 'eq')
            if op_suffix == 'eq':
                param_key = attribute  # No suffix for equals
            else:
                param_key = f'{attribute}__{op_suffix}'
            params[param_key] = str(value)
        
        # Add sorting
        if self._sort_key:
            if self._sort_order == 'desc':
                params['sort'] = f'-{self._sort_key}'
            else:
                params['sort'] = self._sort_key
        
        # Add pagination
        if self._pagination:
            page, page_size = self._pagination
            params['page'] = str(page)
            params['page_size'] = str(page_size)
        
        # Add ids_only
        if self._return_ids:
            params['ids_only'] = 'true'
        
        # Add filter_by
        if self._filter_key:
            params['fields'] = self._filter_key
        
        return urlencode(params)

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
            Uses model index for O(1) model filtering and field indices for O(1) equality lookups.

            Parameters:
            query: HSDBQuery instance with conditions and sort_key.

            Returns:
            List of identifiers that match the query if self._return_ids is True.
            List of entry that match the query if self._return_ids is False.
            """
            # Check if the database is empty
            if not self._hsdb_reference.index_db._db:
                raise KeyError('No db entries found')
                
            if self._verbose and self._measure_time:
                stopwatch('Query runtime')
            
            if id:
                print('fetch')
                queryset = [self._hsdb_reference.index_db._db.fetch(id)]
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
                    actual_value = actual_attribute._value if hasattr(actual_attribute, '_value') else actual_attribute
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

                # Try to use indexed lookups for equality conditions
                candidate_ids = None
                remaining_conditions = []
                model_name = self.model.__name__
                
                for condition in self._conditions:
                    attribute, operator, expected = condition
                    
                    # Only use index for simple equality on non-nested attributes
                    if operator == '==' and '.' not in attribute:
                        indexed_ids = self._hsdb_reference.index_db.lookup_by_field(
                            model_name, attribute, expected
                        )
                        if indexed_ids:
                            if candidate_ids is None:
                                candidate_ids = indexed_ids
                            else:
                                # Intersection for multiple indexed conditions
                                candidate_ids = candidate_ids & indexed_ids
                        else:
                            # No index for this field, check later
                            remaining_conditions.append(condition)
                    else:
                        remaining_conditions.append(condition)
                
                # If no indexed conditions matched, use model index to get all entries of this model
                if candidate_ids is None:
                    candidate_ids = self._hsdb_reference.index_db.lookup_by_model(model_name)
                
                # Use subset if provided
                if self.subset:
                    candidate_ids = candidate_ids & set(self.subset)
                
                # Filter using remaining non-indexed conditions
                queryset = []
                for entry_id in candidate_ids:
                    try:
                        entry = self._hsdb_reference.index_db._db.fetch(entry_id)
                        
                        # Verify model type (safety check)
                        if entry.model != self.model:
                            continue
                            
                        # Check remaining conditions
                        if all(__condition_matches(entry, condition) for condition in remaining_conditions):
                            if self._return_ids:
                                queryset.append(entry_id)
                            else:
                                queryset.append(entry)
                    except KeyError:
                        # Entry was deleted
                        continue

                # TODO: Add support for nested values in sorting and filtering
                # Sort the queryset if needed.
                if self._sort_key:
                    def get_sort_value(entry):
                        val = getattr(entry, self._sort_key, None)
                        return val._value if hasattr(val, '_value') else val
                    queryset.sort(key=get_sort_value, reverse=self._sort_order == 'desc')
                    
                if self._filter_key:
                    queryset = [getattr(entry, self._filter_key) for entry in queryset]
                
                # TODO: Implement pagination for first and range properly, only execute entire queryset for last()  
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
        return self._run_query(id=id)[0] if self._run_query(id=id) else None
    
    def first(self):
        """
        Get the first result or None if no results.
        """
        executed_query = self.paginate(0, 1)
        self._executed_hook = 'first'
        return executed_query[0] if executed_query else None
        
    def last(self):
        """
        Get the last result or None if no results.
        """
        executed_query = self.paginate(-1, 1)
        self._executed_hook = 'last'
        return executed_query[0] if executed_query else None
    
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