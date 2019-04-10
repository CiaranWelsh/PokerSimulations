"""

Copyright (c) 2010 David Schoonover

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

Original code is available here:

    * https://github.com/Infinidat/munch

Bunch is a subclass of dict with attribute-style access.

>>> b = Bunch()
>>> b.hello = 'world'
>>> b.hello
'world'
>>> b['hello'] += "!"
>>> b.hello
'world!'
>>> b.foo = Bunch(lol=True)
>>> b.foo.lol
True
>>> b.foo is b['foo']
True

It is safe to import * from this module:

    __all__ = ('Bunch', 'bunchify','unbunchify')

un/bunchify provide dictionary conversion; Munches can also be
converted via Bunch.to/fromDict().
"""

__version__ = '2.3.2'
VERSION = tuple(map(int, __version__.split('.')))

__all__ = ('Bunch', 'bunchify', 'DefaultBunch', 'DefaultFactoryBunch', 'unbunchify')

from collections import defaultdict

from six import u, iteritems, iterkeys  # pylint: disable=unused-import


class Bunch(dict):
    """ A dictionary that provides attribute-style access.

        >>> b = Bunch()
        >>> b.hello = 'world'
        >>> b.hello
        'world'
        >>> b['hello'] += "!"
        >>> b.hello
        'world!'
        >>> b.foo = Bunch(lol=True)
        >>> b.foo.lol
        True
        >>> b.foo is b['foo']
        True

        A Bunch is a subclass of dict; it supports all the methods a dict does...

        >>> sorted(b.keys())
        ['foo', 'hello']

        Including update()...

        >>> b.update({ 'ponies': 'are pretty!' }, hello=42)
        >>> print (repr(b))
        Bunch({'ponies': 'are pretty!', 'foo': Bunch({'lol': True}), 'hello': 42})

        As well as iteration...

        >>> sorted([ (k,b[k]) for k in b ])
        [('foo', Bunch({'lol': True})), ('hello', 42), ('ponies', 'are pretty!')]

        And "splats".

        >>> "The {knights} who say {ni}!".format(**Bunch(knights='lolcats', ni='can haz'))
        'The lolcats who say can haz!'

        See unbunchify/Bunch.toDict, bunchify/Bunch.fromDict for notes about conversion.
    """

    # only called if k not found in normal places
    def __getattr__(self, k):
        """ Gets key if it exists, otherwise throws AttributeError.

            nb. __getattr__ is only called if key is not found in normal places.

            >>> b = Bunch(bar='baz', lol={})
            >>> b.foo
            Traceback (most recent call last):
                ...
            AttributeError: foo

            >>> b.bar
            'baz'
            >>> getattr(b, 'bar')
            'baz'
            >>> b['bar']
            'baz'

            >>> b.lol is b['lol']
            True
            >>> b.lol is getattr(b, 'lol')
            True
        """
        try:
            # Throws exception if not in prototype chain
            return object.__getattribute__(self, k)
        except AttributeError:
            try:
                return self[k]
            except KeyError:
                raise AttributeError(f'"{k}" is not a valid attribute. '
                                     f'These are valid attributes; "{self.keys()}"')

    def __setattr__(self, k, v):
        """ Sets attribute k if it exists, otherwise sets key k. A KeyError
            raised by set-item (only likely if you subclass Bunch) will
            propagate as an AttributeError instead.

            >>> b = Bunch(foo='bar', this_is='useful when subclassing')
            >>> hasattr(b.values, '__call__')
            True
            >>> b.values = 'uh oh'
            >>> b.values
            'uh oh'
            >>> b['values']
            Traceback (most recent call last):
                ...
            KeyError: 'values'
        """
        try:
            # Throws exception if not in prototype chain
            object.__getattribute__(self, k)
        except AttributeError:
            try:
                self[k] = v
            except:
                raise AttributeError(k)
        else:
            object.__setattr__(self, k, v)

    def __delattr__(self, k):
        """ Deletes attribute k if it exists, otherwise deletes key k. A KeyError
            raised by deleting the key--such as when the key is missing--will
            propagate as an AttributeError instead.

            >>> b = Bunch(lol=42)
            >>> del b.lol
            >>> b.lol
            Traceback (most recent call last):
                ...
            AttributeError: lol
        """
        try:
            # Throws exception if not in prototype chain
            object.__getattribute__(self, k)
        except AttributeError:
            try:
                del self[k]
            except KeyError:
                raise AttributeError(k)
        else:
            object.__delattr__(self, k)

    def toDict(self):
        """ Recursively converts a munch back into a dictionary.

            >>> b = Bunch(foo=Bunch(lol=True), hello=42, ponies='are pretty!')
            >>> sorted(b.toDict().items())
            [('foo', {'lol': True}), ('hello', 42), ('ponies', 'are pretty!')]

            See unbunchify for more info.
        """
        return unbunchify(self)

    @property
    def __dict__(self):
        return self.toDict()

    def __repr__(self):
        """ Invertible* string-form of a Bunch.

            >>> b = Bunch(foo=Bunch(lol=True), hello=42, ponies='are pretty!')
            >>> print (repr(b))
            Bunch({'ponies': 'are pretty!', 'foo': Bunch({'lol': True}), 'hello': 42})
            >>> eval(repr(b))
            Bunch({'ponies': 'are pretty!', 'foo': Bunch({'lol': True}), 'hello': 42})

            >>> with_spaces = Bunch({1: 2, 'a b': 9, 'c': Bunch({'simple': 5})})
            >>> print (repr(with_spaces))
            Bunch({'a b': 9, 1: 2, 'c': Bunch({'simple': 5})})
            >>> eval(repr(with_spaces))
            Bunch({'a b': 9, 1: 2, 'c': Bunch({'simple': 5})})

            (*) Invertible so long as collection contents are each repr-invertible.
        """
        return '{0}({1})'.format(self.__class__.__name__, dict.__repr__(self))

    def __dir__(self):
        return list(iterkeys(self))

    def __getstate__(self):
        """ Implement a serializable interface used for pickling.

        See https://docs.python.org/3.6/library/pickle.html.
        """
        return {k: v for k, v in self.items()}

    def __setstate__(self, state):
        """ Implement a serializable interface used for pickling.

        See https://docs.python.org/3.6/library/pickle.html.
        """
        self.clear()
        self.update(state)

    __members__ = __dir__  # for python2.x compatibility

    @classmethod
    def fromDict(cls, d):
        """ Recursively transforms a dictionary into a Bunch via copy.

            >>> b = Bunch.fromDict({'urmom': {'sez': {'what': 'what'}}})
            >>> b.urmom.sez.what
            'what'

            See bunchify for more info.
        """
        return bunchify(d, cls)

    def copy(self):
        return type(self).fromDict(self)


class AutoMunch(Bunch):
    def __setattr__(self, k, v):
        """ Works the same as Bunch.__setattr__ but if you supply
            a dictionary as value it will convert it to another Bunch.
        """
        if isinstance(v, dict) and not isinstance(v, (AutoMunch, Bunch)):
            v = bunchify(v, AutoMunch)
        super(AutoMunch, self).__setattr__(k, v)


class DefaultBunch(Bunch):
    """
    A Bunch that returns a user-specified value for missing keys.
    """

    def __init__(self, *args, **kwargs):
        """ Construct a new DefaultBunch. Like collections.defaultdict, the
            first argument is the default value; subsequent arguments are the
            same as those for dict.
        """
        # Mimic collections.defaultdict constructor
        if args:
            default = args[0]
            args = args[1:]
        else:
            default = None
        super(DefaultBunch, self).__init__(*args, **kwargs)
        self.__default__ = default

    def __getattr__(self, k):
        """ Gets key if it exists, otherwise returns the default value."""
        try:
            return super(DefaultBunch, self).__getattr__(k)
        except AttributeError:
            return self.__default__

    def __setattr__(self, k, v):
        if k == '__default__':
            object.__setattr__(self, k, v)
        else:
            return super(DefaultBunch, self).__setattr__(k, v)

    def __getitem__(self, k):
        """ Gets key if it exists, otherwise returns the default value."""
        try:
            return super(DefaultBunch, self).__getitem__(k)
        except KeyError:
            return self.__default__

    def __getstate__(self):
        """ Implement a serializable interface used for pickling.

        See https://docs.python.org/3.6/library/pickle.html.
        """
        return (self.__default__, {k: v for k, v in self.items()})

    def __setstate__(self, state):
        """ Implement a serializable interface used for pickling.

        See https://docs.python.org/3.6/library/pickle.html.
        """
        self.clear()
        default, state_dict = state
        self.update(state_dict)
        self.__default__ = default

    @classmethod
    def fromDict(cls, d, default=None):
        # pylint: disable=arguments-differ
        return bunchify(d, factory=lambda d_: cls(default, d_))

    def copy(self):
        return type(self).fromDict(self, default=self.__default__)

    def __repr__(self):
        return '{0}({1!r}, {2})'.format(
            type(self).__name__, self.__undefined__, dict.__repr__(self))


class DefaultFactoryBunch(defaultdict, Bunch):
    """ A Bunch that calls a user-specified function to generate values for
        missing keys like collections.defaultdict.

        >>> b = DefaultFactoryBunch(list, {'hello': 'world!'})
        >>> b.hello
        'world!'
        >>> b.foo
        []
        >>> b.bar.append('hello')
        >>> b.bar
        ['hello']
    """

    def __init__(self, default_factory, *args, **kwargs):
        # pylint: disable=useless-super-delegation
        super(DefaultFactoryBunch, self).__init__(default_factory, *args, **kwargs)

    @classmethod
    def fromDict(cls, d, default_factory):
        # pylint: disable=arguments-differ
        return bunchify(d, factory=lambda d_: cls(default_factory, d_))

    def copy(self):
        return type(self).fromDict(self, default_factory=self.default_factory)

    def __repr__(self):
        factory = self.default_factory.__name__
        return '{0}({1}, {2})'.format(
            type(self).__name__, factory, dict.__repr__(self))


# While we could convert abstract types like Mapping or Iterable, I think
# bunchify is more likely to "do what you mean" if it is conservative about
# casting (ex: isinstance(str,Iterable) == True ).
#
# Should you disagree, it is not difficult to duplicate this function with
# more aggressive coercion to suit your own purposes.

def bunchify(x, factory=Bunch):
    """ Recursively transforms a dictionary into a Bunch via copy.

        >>> b = bunchify({'urmom': {'sez': {'what': 'what'}}})
        >>> b.urmom.sez.what
        'what'

        bunchify can handle intermediary dicts, lists and tuples (as well as
        their subclasses), but ymmv on custom datatypes.

        >>> b = bunchify({ 'lol': ('cats', {'hah':'i win again'}),
        ...         'hello': [{'french':'salut', 'german':'hallo'}] })
        >>> b.hello[0].french
        'salut'
        >>> b.lol[1].hah
        'i win again'

        nb. As dicts are not hashable, they cannot be nested in sets/frozensets.
    """
    if isinstance(x, dict):
        return factory((k, bunchify(v, factory)) for k, v in iteritems(x))
    elif isinstance(x, (list, tuple)):
        return type(x)(bunchify(v, factory) for v in x)
    else:
        return x


def unbunchify(x):
    """ Recursively converts a Bunch into a dictionary.

        >>> b = Bunch(foo=Bunch(lol=True), hello=42, ponies='are pretty!')
        >>> sorted(unbunchify(b).items())
        [('foo', {'lol': True}), ('hello', 42), ('ponies', 'are pretty!')]

        unbunchify will handle intermediary dicts, lists and tuples (as well as
        their subclasses), but ymmv on custom datatypes.

        >>> b = Bunch(foo=['bar', Bunch(lol=True)], hello=42,
        ...         ponies=('are pretty!', Bunch(lies='are trouble!')))
        >>> sorted(unbunchify(b).items()) #doctest: +NORMALIZE_WHITESPACE
        [('foo', ['bar', {'lol': True}]), ('hello', 42), ('ponies', ('are pretty!', {'lies': 'are trouble!'}))]

        nb. As dicts are not hashable, they cannot be nested in sets/frozensets.
    """
    if isinstance(x, dict):
        return dict((k, unbunchify(v)) for k, v in iteritems(x))
    elif isinstance(x, (list, tuple)):
        return type(x)(unbunchify(v) for v in x)
    else:
        return x


# Serialization

try:
    try:
        import json
    except ImportError:
        import simplejson as json


    def toJSON(self, **options):
        """ Serializes this Bunch to JSON. Accepts the same keyword options as `json.dumps()`.

            >>> b = Bunch(foo=Bunch(lol=True), hello=42, ponies='are pretty!')
            >>> json.dumps(b) == b.toJSON()
            True
        """
        return json.dumps(self, **options)


    Bunch.toJSON = toJSON

except ImportError:
    pass

try:
    # Attempt to register ourself with PyYAML as a representer
    import yaml
    from yaml.representer import Representer, SafeRepresenter


    def from_yaml(loader, node):
        """ PyYAML support for Munches using the tag `!bunch` and `!bunch.Bunch`.

            >>> import yaml
            >>> yaml.load('''
            ... Flow style: !bunch.Bunch { Clark: Evans, Brian: Ingerson, Oren: Ben-Kiki }
            ... Block style: !bunch
            ...   Clark : Evans
            ...   Brian : Ingerson
            ...   Oren  : Ben-Kiki
            ... ''') #doctest: +NORMALIZE_WHITESPACE
            {'Flow style': Bunch(Brian='Ingerson', Clark='Evans', Oren='Ben-Kiki'),
             'Block style': Bunch(Brian='Ingerson', Clark='Evans', Oren='Ben-Kiki')}

            This module registers itself automatically to cover both Bunch and any
            subclasses. Should you want to customize the representation of a subclass,
            simply register it with PyYAML yourself.
        """
        data = Bunch()
        yield data
        value = loader.construct_mapping(node)
        data.update(value)


    def to_yaml_safe(dumper, data):
        """ Converts Bunch to a normal mapping node, making it appear as a
            dict in the YAML output.

            >>> b = Bunch(foo=['bar', Bunch(lol=True)], hello=42)
            >>> import yaml
            >>> yaml.safe_dump(b, default_flow_style=True)
            '{foo: [bar, {lol: true}], hello: 42}\\n'
        """
        return dumper.represent_dict(data)


    def to_yaml(dumper, data):
        """ Converts Bunch to a representation node.

            >>> b = Bunch(foo=['bar', Bunch(lol=True)], hello=42)
            >>> import yaml
            >>> yaml.dump(b, default_flow_style=True)
            '!bunch.Bunch {foo: [bar, !bunch.Bunch {lol: true}], hello: 42}\\n'
        """
        return dumper.represent_mapping(u('!bunch.Bunch'), data)


    yaml.add_constructor(u('!bunch'), from_yaml)
    yaml.add_constructor(u('!bunch.Bunch'), from_yaml)

    SafeRepresenter.add_representer(Bunch, to_yaml_safe)
    SafeRepresenter.add_multi_representer(Bunch, to_yaml_safe)

    Representer.add_representer(Bunch, to_yaml)
    Representer.add_multi_representer(Bunch, to_yaml)


    # Instance methods for YAML conversion
    def toYAML(self, **options):
        """ Serializes this Bunch to YAML, using `yaml.safe_dump()` if
            no `Dumper` is provided. See the PyYAML documentation for more info.

            >>> b = Bunch(foo=['bar', Bunch(lol=True)], hello=42)
            >>> import yaml
            >>> yaml.safe_dump(b, default_flow_style=True)
            '{foo: [bar, {lol: true}], hello: 42}\\n'
            >>> b.toYAML(default_flow_style=True)
            '{foo: [bar, {lol: true}], hello: 42}\\n'
            >>> yaml.dump(b, default_flow_style=True)
            '!bunch.Bunch {foo: [bar, !bunch.Bunch {lol: true}], hello: 42}\\n'
            >>> b.toYAML(Dumper=yaml.Dumper, default_flow_style=True)
            '!bunch.Bunch {foo: [bar, !bunch.Bunch {lol: true}], hello: 42}\\n'

        """
        opts = dict(indent=4, default_flow_style=False)
        opts.update(options)
        if 'Dumper' not in opts:
            return yaml.safe_dump(self, **opts)
        else:
            return yaml.dump(self, **opts)


    def fromYAML(*args, **kwargs):
        return bunchify(yaml.load(*args, **kwargs))


    Bunch.toYAML = toYAML
    Bunch.fromYAML = staticmethod(fromYAML)

except ImportError:
    pass
