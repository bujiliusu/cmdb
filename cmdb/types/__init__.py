import ipaddress
# import importlib

classes_cache = {}
instances_cache = {}
def get_class(type:str):
    cls = classes_cache.get(type)
    if cls:
        return cls
    # m, c = type.rsplit('.', maxsplit=1)
    # mod = importlib.import_module(m)
    # cls = getattr(mod, c)
    # classes_cache[type] = cls
    # if issubclass(cls, BaseType):
    #     return cls
    raise TypeError('Wrong Type!')
def get_instance(type:str, **option):
    key = ",".join("{}={}".format(k,v) for k,v in sorted(option.items()))
    key = "{}|{}".format(type, key)
    obj = instances_cache.get(key)
    if obj:
        return obj
    obj = get_class(type)(**option)
    instances_cache[key] = obj
    # print(obj.stringify(2000))
    return obj
def inject():
    for k,v in globals().items():
        if type(v) == type and k != 'BaseType':
            classes_cache[k] = v
            classes_cache["{}.{}".format(__name__, k)]=v
class BaseType:
    def __init__(self, **option):
        self.option = option
    def __getattr__(self, item):
        return self.option.get(item)
    def stringify(self, value):
        raise NotImplementedError()
    def destringify(self, value):
        raise NotImplementedError()
class Int(BaseType):
    def stringify(self, value):
        val = int(value)
        max = self.max
        if max and val > max:
            raise TypeError('too big')
        min = self.min
        if min and val < min:
            raise TypeError('too small')
        return str(val)

    def destringify(self, value):
        return value
class IP(BaseType):
    def stringify(self, value):
        val = ipaddress.ip_address(value)
        prefix = self.prefix
        if prefix and not str(val).startswith(prefix):
            raise TypeError('prefix wrong')
        return str(val)

    def destringify(self, value):
        return value

inject()