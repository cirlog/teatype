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
from typing import Any, Dict, Optional, Union

# Third-party imports
from pydantic import BaseModel as PydanticBaseModel
from pydantic import model_validator, field_serializer
from teatype.toolkit import kebabify

class BaseForma(PydanticBaseModel):
    """
    Base forma for all template formas with automatic transformation capabilities.
    
    The transformer is lazily loaded on first use to avoid circular import issues.
    Transformer instances are cached per class for performance.
    """
    
    #################
    # Class methods #
    #################
    
    @model_validator(mode='before')
    @classmethod
    def auto_kebabify_fields(cls, data: Any) -> Any:
        """
        Automatically kebabify any field that contains 'kebabified' in its name.
        If the kebabified field is None or empty, derive it from the base field.
        
        For example, if 'name_kebabified' is None, it will be populated
        from 'name' using the kebabify function.
        """
        if not isinstance(data, dict):
            return data
        
        
        # Get all model fields to check for kebabified fields
        model_fields = cls.model_fields if hasattr(cls, 'model_fields') else {}
        
        # Check both existing data keys and model fields for kebabified fields
        kebabified_fields = set()
        
        # Find kebabified fields in data
        for field_name in data.keys():
            if 'kebabified' in field_name.lower():
                kebabified_fields.add(field_name)
        
        # Find kebabified fields in model definition
        for field_name in model_fields.keys():
            if 'kebabified' in field_name.lower():
                kebabified_fields.add(field_name)
        
        # Process each kebabified field
        for field_name in kebabified_fields:
            # If the kebabified field is missing, None, or empty, try to derive it
            if not data.get(field_name):
                # Extract the base field name (e.g., 'name' from 'name_kebabified')
                base_field = field_name.replace('_kebabified', '').replace('kebabified', '')
                if base_field in data and data[base_field]:
                    data[field_name] = kebabify(str(data[base_field]))
        return data
    
    @classmethod
    def parse_obj(cls, obj:Any) -> 'BaseForma':
        if isinstance(obj, str):
            # Treat as JSON string
            try:
                obj = json.loads(obj)
            except json.JSONDecodeError as e:
                raise ValueError(f'Invalid JSON string: {e}')
        return super().parse_obj(obj)
    
    @classmethod
    def from_json(cls, json_string:str) -> 'BaseForma':
        return cls.parse_obj(json_string)
    
    @classmethod
    def from_dict(cls, data:Dict[str,Any]) -> 'BaseForma':
        return cls.parse_obj(data)
    
    @classmethod
    def _get_transformer_instance(cls, transformer_class):
        """
        Get or create a cached transformer instance.
        
        Args:
            transformer_class: The transformer class (not instance)
            
        Returns:
            Cached transformer instance
        """
        # Cache key based on the transformer class name
        cache_key = f'_transformer_cache_{transformer_class.__name__}'
        
        # Check if we already have a cached instance
        if not hasattr(cls, cache_key):
            # Create transformer without specifying direction - it will auto-detect
            transformer = transformer_class()
            setattr(cls, cache_key, transformer)
        return getattr(cls, cache_key)
    
    ##############
    # Public API #
    ##############
    
    def to_dict(self, mode:str='python') -> Dict[str,Any]:
        if mode == 'json':
            return json.loads(self.json())
        return self.model_dump()
    
    def to_json(self, **kwargs) -> str:
        return self.model_dump_json(**kwargs)
    
    def merge_into(self, other:Union['BaseForma', Dict[str, Any]]) -> Union['BaseForma', Dict[str, Any]]:
        """
        Merge this model's data into another model or dictionary.
        
        If 'other' is a BaseForma instance, update its fields with this model's fields.
        If 'other' is a dictionary, update it with this model's fields.
        
        Returns the updated model or dictionary.
        """
        if isinstance(other, BaseForma):
            # Update fields of the other model
            for field_name, value in self.model_dump().items():
                setattr(other, field_name, value)
            return other
        elif isinstance(other, dict):
            # Update the dictionary
            other.update(self.model_dump())
            return other
        else:
            raise TypeError("The 'other' parameter must be a BaseForma instance or a dictionary.")
    
    def merge_from(self, other:Union['BaseForma', Dict[str, Any]]) -> 'BaseForma':
        """
        Merge another model's or dictionary's data into this model.
        
        If 'other' is a BaseForma instance, update this model's fields with its fields.
        If 'other' is a dictionary, update this model's fields with the dictionary's entries.
        
        Returns this updated model.
        """
        if isinstance(other, BaseForma):
            # Update fields of this model
            for field_name, value in other.model_dump().items():
                setattr(self, field_name, value)
            return self
        elif isinstance(other, dict):
            # Update this model with the dictionary
            for field_name, value in other.items():
                setattr(self, field_name, value)
            return self
        else:
            raise TypeError("The 'other' parameter must be a BaseForma instance or a dictionary.")
    
    def update_last_modified(self) -> None:
        """
        Update the 'last_modified' field to the current datetime.
        """
        from datetime import datetime
        if hasattr(self, 'last_modified'):
            setattr(self, 'last_modified', datetime.now())
    
    def transform(self, 
                  return_dict:bool=True,
                  hydrate:Optional[Dict[str, Any]]=None,
                  dict_mode:str='json') -> Union[PydanticBaseModel, Dict[str,Any]]:
        # Get transformer class from class attributes
        transformer_attr = getattr(
            self.__class__, 
            f'_{self.__class__.__name__}__transformer_class', 
            None
        )
        
        if transformer_attr is None:
            raise AttributeError(f'{self.__class__.__name__} must define __transformer_class attribute.')
        
        # Extract the actual transformer class from Pydantic's ModelPrivateAttr wrapper
        if hasattr(transformer_attr, 'default'):
            transformer_class = transformer_attr.default
        else:
            transformer_class = transformer_attr
        
        # Get or create cached transformer instance
        transformer_instance = self._get_transformer_instance(transformer_class)
        
        # Use the transformer to convert this instance
        return transformer_instance.transform(
            data=self,
            return_dict=return_dict,
            hydrate=hydrate,
            dict_mode=dict_mode
        )
    
    #####################
    # Field serializers #
    #####################

    @field_serializer('created_at', check_fields=False)
    def serialize_created_at(self, value):
        if value is not None:
            return value.isoformat()
        return value
    
    @field_serializer('updated_at', check_fields=False)
    def serialize_updated_at(self, value):
        if value is not None:
            return value.isoformat()
        return value