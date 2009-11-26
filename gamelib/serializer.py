"""
Interface for converting objects to and from simple structures: lists, dicts,
strings, integers and combinations there of. Used for sending objects over
the communications API.
"""

REGISTERED_CLASSES = {}

def simplify(item, refs=None):
    """Convert an item to a simple data structure."""
    if refs is None:
        refs = set()

    refid = str(id(item))

    if refid in refs:
        return { 'byref': refid }

    if issubclass(type(item), Simplifiable):
        refs.add(refid)
        value = item.simplify(refs)
        value['refid'] = refid
    elif type(item) is list:
        refs.add(refid)
        value = { 'list': [simplify(x, refs) for x in item] }
        value['refid'] = refid
    elif type(item) is set:
        refs.add(refid)
        value = { 'set': [simplify(x, refs) for x in item] }
        value['refid'] = refid
    elif type(item) is tuple:
        refs.add(refid)
        value = { 'tuple': tuple([simplify(x, refs) for x in item]) }
        value['refid'] = refid
    elif item is None:
        value = { 'none': '' }
    else:
        value = { 'raw': item }

    return value

def unsimplify(value, refs=None):
    """Reverse the simplify process."""
    if refs is None:
        refs = {}

    if 'refid' in value:
        refid = value['refid']

    if value.has_key('class'):
        cls = REGISTERED_CLASSES[value['class']]
        item = cls.unsimplify(value, refs)
    elif value.has_key('list'):
        item = []
        refs[refid] = item
        item.extend(unsimplify(x, refs) for x in value['list'])
    elif value.has_key('set'):
        item = set()
        refs[refid] = item
        item.update(unsimplify(x, refs) for x in value['set'])
    elif value.has_key('tuple'):
        item = tuple([unsimplify(x, refs) for x in value['tuple']])
    elif value.has_key('none'):
        item = None
    elif value.has_key('raw'):
        item = value['raw']
    elif value.has_key('byref'):
        refid = value['byref']
        if refid in refs:
            item = refs[refid]
        else:
            raise SimplifyError("Unknown refid %r in byref." % (refid,))
    else:
        raise SimplifyError("Unknown unsimplify type key.")

    if 'refid' in value:
        refs[value['refid']] = item

    return item

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

    @classmethod
    def make(cls):
        """
        Create an object of this class without any attributes set.
        """
        return cls.__new__(cls)

    @classmethod
    def unsimplify(cls, value, refs=None):
        """
        Create an object of this class (or a sub-class) from its
        simplification.
        """
        actual_cls = REGISTERED_CLASSES[value['class']]
        attrs = value['attributes']

        if not issubclass(actual_cls, cls):
            raise SimplifyError("Actual class (%r) not a subclass of"
                " this class (%r)" % (actual_cls, cls))

        if not len(attrs) == len(actual_cls.SIMPLIFY):
            raise SimplifyError("Wrong number of attributes for this"
                " class (%r)" % (actual_cls,))

        obj = actual_cls.make()
        refs[value['refid']] = obj

        for attr, value in zip(actual_cls.SIMPLIFY, attrs):
            setattr(obj, attr, unsimplify(value, refs))

        return obj

    def simplify(self, refs=None):
        """
        Create a simplified version (tar) of the object.
        """
        value = {}
        value['class'] = self.__class__.__name__

        attrs = []
        for attr in self.SIMPLIFY:
            o = getattr(self, attr)
            attrs.append(simplify(o, refs))

        value['attributes'] = attrs
        return value

    def copy(self):
        """
        Return a copy of the object.
        """
        return self.__class__.unsimplify(self.simplify())
