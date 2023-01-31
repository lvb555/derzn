import pickle
import pickle as Cpickle

class Dictionary:
    def __init__(self, read_only=False, **params):
        self.__dict__['__children__'] = {}
        self.__dict__['__readonly__'] = read_only
        for key, value in params.iteritems():
            self.__dict__['__children__'][key] = value


    def clear(self):
        for key, value in self.__dict__['__children__'].iteritems():
            if isinstance(value, Dictionary):
                value.clear()
        self.__dict__['__children__'].clear()


    def printf(self, prefix=None):
        for key in sorted(self.__dict__['__children__'].iterkeys()):
            value = self.__dict__['__children__'][key]
            if value is None:
                continue
            if isinstance(value, Dictionary):
                if prefix:
                    value.printf('%s.%s' % (prefix, key))
                else:
                    value.printf('%s' % key)
            else:
                if prefix:
                    print('%s.%s = %s' % (prefix, key, str(value)))
                else:
                    print('%s = %s' % (key, str(value)))


    def __getattr__(self, name):
        try:
            return self.__dict__['__children__'][name]
        except KeyError:
            if not self.__dict__['__readonly__']:
                value = self.__dict__['__children__'][name] = Dictionary()
                return value
            raise


    def __delattr__(self, name):
        if self.__dict__['__readonly__']:
            raise KeyError("Read only structure.")
        del self.__dict__['__children__'][name]


    def __setattr__(self, name, value):
        children = self.__dict__['__children__']
        old_value = children.get(name)

        if name not in children:
            if self.__dict__['__readonly__']:
                raise KeyError("Read only structure.")
        elif isinstance(old_value, Dictionary):
            if old_value:
                raise AttributeError("Attribute %s has children: %s" % (repr(name), old_value))

        children[name] = value


    def __getitem__(self, name):
        return self.__getattr__(name)


    def __setitem__(self, name, value):
        self.__setattr__(name, value)


    def __delitem__(self, name):
        self.__delattr__(name)


    def __eq__(self, value):
        if isinstance(value, Dictionary):
            return repr(self) == repr(value)
        if isinstance(value, dict):
            return self.__dict__['__children__'] == value
        return value is None


    def __ne__(self, value):
        return not self.__eq__(value)


    def __nonzero__(self):
        return bool(self.__dict__['__children__'])


    def __str__(self):
        return str(repr(self))


    def __repr__(self):
        params = [('read_only=%s' % self.__dict__['__readonly__'])]
        for key in sorted(self.__dict__['__children__'].iterkeys()):
            value = self.__dict__['__children__'][key]
            params.append('%s=%s' % (key, repr(value)))
        return 'Dictionary(%s)' % ', '.join(params)


    def __len__(self):
        return len(self.__dict__['__children__'])


    def iterkeys(self):
        return self.__dict__['__children__'].iterkeys()


    def itervalues(self):
        return self.__dict__['__children__'].itervalues()


    def iteritems(self):
        return self.__dict__['__children__'].iteritems()


    def __iter__(self):
        return self.__dict__['__children__'].__iter__()


    def __setstate__(self, state):
        for key, name, value in state:
            if key == 'param':
                self.__dict__[name] = value
            elif key == 'value':
                self.__dict__['__children__'][name] = pickle.loads(value)


    def __getstate__(self):
        result = []
        result.append(('param', '__readonly__', self.__dict__['__readonly__']))

        for name, value in self.__dict__['__children__'].iteritems():
            result.append(('value', name, pickle.dumps(value)))
        return tuple(result)


    def __getinitargs__(self):
        return ()


    @staticmethod
    def parse(kwargs):
        kwargs = dict(kwargs)
        params = {}

        while kwargs:
            key, value = kwargs.popitem()
            uri = key.split(".")
            params_ptr = params

            if len(uri) == 1:
                params[key] = value
                continue

            for i in range(len(uri)):
                k = uri[i]
                if i == len(uri) - 1:
                    params_ptr[k] = value
                elif k not in params_ptr:
                    params_ptr[k] = {}
                params_ptr = params_ptr[k]

        def create(dictionary):
            result = {}
            for key, value in dictionary.iteritems():
                if isinstance(value, dict):
                    result[key] = create(value)
                else:
                    result[key] = value
            return Dictionary(read_only=True, **result)

        return create(params)
