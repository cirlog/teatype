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

# A custom property descriptor that supports static methods as properties.
# This class inherits from the built-in property type.
class staticproperty(property):
    # Override the __get__ method to enable static property functionality.
    # 'cls' is the instance when accessed via an instance or the class when accessed as a class attribute.
    # 'owner' is the actual class that owns the descriptor.
    def __get__(self, cls, owner):
        # Convert the getter function (fget) into a static method.
        # This ensures that the getter can be called without instantiating the class.
        # __get__ on the static method binds it to 'owner' with no instance (None), yielding a callable.
        # Finally, the callable is immediately invoked with self (the staticproperty instance)
        # as its argument, allowing the getter to operate in a context where it can reference the property itself.
        # Bnding the owner to the static method allows the static method to access the class it belongs to, not the 
        # function that utilizes its decorator
        return staticmethod(self.fget).__get__(None, owner)(owner)