"""
Interface for converting objects to and from simple structures: lists, dicts,
strings, integers and combinations there of. Used for sending objects over
the communications API.
"""

REGISTERED_CLASSES = {}

def simplify(item):
    """Convert an item to a simple data structure."""
    if issubclass(type(item), Simplifiable):
        return item.simplify()
    elif type(item) is list:
        return { 'list': [simplify(x) for x in item] }
    elif type(item) is tuple:
        return { 'tuple': tuple([simplify(x) for x in item]) }
    elif item is None:
        return { 'none': '' }
    else:
        return { 'raw': item }

def unsimplify(value):
    """Reverse the simplify process."""
    if value.has_key('class'):
        cls = REGISTERED_CLASSES[value['class']]
        return cls.unsimplify(value)
    elif value.has_key('list'):
        return [unsimplify(x) for x in value['list']]
    elif value.has_key('tuple'):
        return tuple([unsimplify(x) for x in value['tuple']])
    elif value.has_key('none'):
        return None
    elif value.has_key('raw'):
        return value['raw']
    else:
        raise SimplifyError("Unknown tar type key.")

class SimplifyError(Exception):
    pass

class SimplifiableMetaclass(type):
    def __init__(cls, name, bases, dct):
        super(SimplifiableMetaclass, cls).__init__(name, bases, dct)
        REGISTERED_CLASSES[cls.__name__] = cls

class Simplifiable(object):
    """
    Object which can be simplified() and unsimplified() (i.e.
    converted to a data type which, for example, Python's XMLRPC
    or json module is capable of handling). Each subclass
    must provide SIMPLIFY (a list of strings giving the names
    of attributes which should be stored) unless a parent class
    provides the right thing.
    """
    __metaclass__ = SimplifiableMetaclass

    # List of attributes which need to be stored and restored
    SIMPLIFY = []

    def make(cls):
        """
        Create an object of this class without any attributes set.
        """
        return cls.__new__(cls)
    make = classmethod(make)

    def unsimplify(cls, value):
        """
        Create an object of this class (or a sub-class) from its
        simplification.
        """
        actual_cls = REGISTERED_CLASSES[value['class']]
        attrs = value['attributes']

        if not issubclass(actual_cls, cls):
            raise SimplifyError("Real class not a subclass of this class")

        if not len(attrs) == len(actual_cls.SIMPLIFY):
            raise SimplifyError("Wrong number of attributes for this class")

        obj = actual_cls.make()
        for attr, value in zip(actual_cls.SIMPLIFY, attrs):
            setattr(obj, attr, unsimplify(value))

        return obj
    unsimplify = classmethod(unsimplify)

    def simplify(self):
        """
        Create a simplified version (tar) of the object.
        """
        value = {}
        value['class'] = self.__class__.__name__

        attrs = []
        for attr in self.SIMPLIFY:
            o = getattr(self, attr)
            attrs.append(simplify(o))

        value['attributes'] = attrs
        return value

    def copy(self):
        """
        Return a copy of the object.
        """
        return self.__class__.unsimplify(self.simplify())
