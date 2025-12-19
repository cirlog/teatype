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

# System-library imports
import json
from abc import abstractmethod
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Literal, Optional, Type, TypeVar, Union

# Third-party imports
from pydantic import BaseModel as PydanticBaseModel
from teatype.forma.base_forma import BaseForma

TForma = TypeVar('TForma', bound=PydanticBaseModel)

@dataclass
class PathRule:
    """
    One rule describing how a field in forma_a maps to a field in forma_b.

    a_path: JSON-like path in forma_a
    b_path: JSON-like path in forma_b
    a_to_b: optional converter when going a → b
    b_to_a: optional converter when going b → a
    """
    a_path:str
    b_path:str
    a_to_b:Optional[Callable[[Any],Any]]=None
    b_to_a:Optional[Callable[[Any],Any]]=None

class PathUtils:
    @staticmethod
    def get_by_path(data:Dict[str,Any], path:str) -> Any:
        current = data
        for part in path.split('.'):
            if current is None or not isinstance(current, dict):
                return None
            current = current.get(part)
        return current

    @staticmethod
    def set_by_path(data:Dict[str,Any], path:str, value:Any) -> None:
        parts = path.split('.')
        current = data
        for part in parts[:-1]:
            if part not in current or not isinstance(current[part], dict):
                current[part] = {}
            current = current[part]
        current[parts[-1]] = value

class BaseTransformer:
    """
    Generic bidirectional path-based transformer between two Pydantic models.

    Subclasses must define:
      - forma_a: Type[BaseForma]
      - forma_b: Type[BaseForma]
      - rules: List[PathRule]

    At runtime you construct with:
      transformer = Transformer(to_forma='ModelA')

    Then call:
      transformer.transform(data)

    `data` can be:
      - dict that matches source forma schema
      - instance of source forma
      - instance of target forma (for reverse transformation)
    """
    # to be overridden by subclass
    forma_a=None
    forma_b=None
    rules:List[PathRule]=[]
    
    # Class-level registry for forma lookup by name
    _forma_registry: Dict[str, Type[BaseForma]] = {}

    def __init__(self, to_forma:Optional[Union[str,Type[BaseForma]]]=None,
                 from_forma:Optional[Union[str,Type[BaseForma]]]=None) -> None:
        self.lazy_load()
        
        if self.forma_a is None or self.forma_b is None:
            raise TypeError('Subclass must define forma_a and forma_b')
        if not self.rules:
            raise TypeError('Subclass must define non-empty rules')
        
        # Register formas in the class registry by their names
        self._register_forma(self.forma_a)
        self._register_forma(self.forma_b)
        
        # Resolve string forma names to actual forma classes if provided
        to_forma_resolved = self._resolve_forma(to_forma) if to_forma else None
        from_forma_resolved = self._resolve_forma(from_forma) if from_forma else None
        
        # If both are provided, validate they match the allowed pair
        if to_forma_resolved and from_forma_resolved:
            allowed = {self.forma_a, self.forma_b}
            requested = {from_forma_resolved, to_forma_resolved}
            if allowed != requested:
                raise ValueError(
                    f'{self.__class__.__name__} only supports formas '
                    f'{self.forma_a.__name__} and {self.forma_b.__name__}, '
                    f'but got {from_forma_resolved.__name__} and {to_forma_resolved.__name__}'
                )
        
        # If only to_forma is provided, infer from_forma
        if to_forma_resolved and not from_forma_resolved:
            if to_forma_resolved == self.forma_a:
                from_forma_resolved = self.forma_b
            elif to_forma_resolved == self.forma_b:
                from_forma_resolved = self.forma_a
            else:
                raise ValueError(f'{self.__class__.__name__} does not support forma {to_forma}')

        # Store for dict handling (optional, will be inferred from data if not set)
        self.from_forma = from_forma_resolved
        self.to_forma = to_forma_resolved
        
    #################
    # Class methods #
    #################
    
    @classmethod
    def _register_forma(cls, forma:Type[BaseForma]) -> None:
        """
        Register a forma in the class registry by its name.
        """
        if forma and forma.__name__ not in cls._forma_registry:
            cls._forma_registry[forma.__name__] = forma
    
    @classmethod
    def _resolve_forma(cls, forma:Optional[Union[str,Type[BaseForma]]]) -> Optional[Type[BaseForma]]:
        """
        Resolve a forma from string name or return the forma class itself.
        
        Args:
            forma: String forma name or forma class
            
        Returns:
            Resolved forma class or None
            
        Raises:
            ValueError: If string forma name is not found in registry
        """
        if forma is None:
            return None
        if isinstance(forma, str):
            if forma not in cls._forma_registry:
                raise ValueError(
                    f'forma "{forma}" not found in registry. '
                    f'Available formas: {list(cls._forma_registry.keys())}'
                )
            return cls._forma_registry[forma]
        return forma

    @classmethod
    def _deep_update(cls, target:Dict[str,Any], supplement:Dict[str,Any]) -> None:
        """
        Recursively merge supplement into target, overriding existing values.
        """
        for key, value in supplement.items():
            if isinstance(value, dict):
                target_value = target.get(key)
                if not isinstance(target_value, dict):
                    target[key] = {}
                BaseTransformer._deep_update(target[key], value)
            else:
                target[key] = value
                
    ##############
    # Public API #
    ##############

    def transform(self,
                  data:Union[BaseForma,Dict[str,Any]],
                  return_dict:bool=True,
                  hydrate:Optional[Dict[str,Any]]=None,
                  dict_mode:Literal['python','json']='json') -> BaseForma|Dict[str,Any]:
        """
        Automatically determines transformation direction based on data type.

        - If data is an instance of forma_a -> transforms to forma_b
        - If data is an instance of forma_b -> transforms to forma_a
        - If data is a dict and from_forma/to_forma were set -> uses those
        - If data is a dict and no hint -> defaults to forma_a -> forma_b

        The lambda functions in rules receive the full source object, not just field values.

        Args:
            data: Source payload, dict or Pydantic instance of either forma.
            return_dict: When True (default) return the validated destination dict.
            hydrate: Optional nested dict merged over the mapped data before
                     validation (e.g., provide default values that source lacks).
            dict_mode: When returning dicts choose `python` for raw Python types
                       (default) or `json` to coerce JSON-friendly primitives
                       using Pydantic's encoder (e.g., datetimes → ISO strings).
        """
        A = self.forma_a
        B = self.forma_b

        # Auto-detect source and destination formas
        if isinstance(data, dict):
            # Use hints if available, otherwise default to A -> B
            if self.from_forma and self.to_forma:
                src_forma, dst_forma = self.from_forma, self.to_forma
            else:
                src_forma, dst_forma = A, B
        elif isinstance(data, A):
            src_forma, dst_forma = A, B
        elif isinstance(data, B):
            src_forma, dst_forma = B, A
        else:
            raise TypeError(f'Data must be dict or instance of {A.__name__}/{B.__name__}, not {type(data)}')

        # Normalize to a *validated* Pydantic instance of src_forma
        if isinstance(data, dict):
            src_instance = src_forma.parse_obj(data)
        else:
            # data is BaseForma here
            src_instance = src_forma.parse_obj(data.dict())

        src_dict = src_instance.dict()
        
        # Determine rule direction
        if src_forma is A and dst_forma is B:
            direction = 'a_to_b'
        elif src_forma is B and dst_forma is A:
            direction = 'b_to_a'
        else:
            raise RuntimeError(f'Inconsistent transformer configuration: src={src_forma}, dst={dst_forma}, canonical A={A}, B={B}')

        # Apply rules - pass full source object to lambdas
        dest: Dict[str, Any] = {}
        for rule in self.rules:
            if direction == 'a_to_b':
                value = PathUtils.get_by_path(src_dict, rule.a_path)
                if value is None:
                    continue
                if rule.a_to_b:
                    # Pass the full source object to the lambda
                    value = rule.a_to_b(src_instance)
                PathUtils.set_by_path(dest, rule.b_path, value)
            else:  # b_to_a
                value = PathUtils.get_by_path(src_dict, rule.b_path)
                if value is None:
                    continue
                if rule.b_to_a:
                    # Pass the full source object to the lambda
                    value = rule.b_to_a(src_instance)
                PathUtils.set_by_path(dest, rule.a_path, value)

        # Hydrate with supplemental data before validation if requested
        if hydrate:
            self._deep_update(dest, hydrate)

        # Build *validated* destination forma
        forma_instance = dst_forma.parse_obj(dest)
        if not return_dict:
            return forma_instance

        if dict_mode == 'json':
            return json.loads(forma_instance.json())
        return forma_instance.dict()
    
    ####################
    # Abstract methods #
    ####################
    
    @abstractmethod
    def lazy_load(self, *args, **kwargs):
        raise NotImplementedError('''Subclasses must implement lazy_load method like this:\n
def lazy_load(self, *args, **kwargs):
    # Lazy-load models only when transformer is instantiated
    import MyFormaA, MyFormaB
    if MyTransformer.forma_a is None:
        MyTransformer.forma_a = MyFormaA
        MyTransformer.forma_b = MyFormaB''')