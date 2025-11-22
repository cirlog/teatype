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

# A custom property descriptor that supports class methods as properties.
# This class inherits from the built-in property type.
class classproperty(property):
    # Override the __get__ method to enable class property functionality.
    # 'obj' is the instance when accessed via an instance or None when accessed as a class attribute.
    # 'owner' is the actual class that owns the descriptor.
    def __get__(self, obj, owner=None):
        # Convert the getter function (fget) into a class method.
        # This ensures that the getter receives the class as its first argument.
        # __get__ on the class method binds it to 'owner', yielding a callable.
        # Finally, the callable is immediately invoked, passing the class to the getter.
        return classmethod(self.fget).__get__(obj, owner)()
