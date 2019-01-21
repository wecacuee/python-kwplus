from inspect import signature, Parameter
from functools import wraps, partial


class xargs(partial):
    def __new__(cls, func, expect_args=()):
        self = super(xargs, cls).__new__(cls, func)
        self.expect_args = expect_args
        return self


class xlazy(partial):
    def __new__(cls, func):
        return super(xlazy, cls).__new__(cls, func)


class xmem(partial):
    def __new__(cls, func, expect_args):
        self = super(xmem, cls).__new__(cls, func)
        self.expect_args = expect_args
        return self


def iff(cond, ontrue, onfalse):
    return ontrue() if cond() else onfalse()


def loop(init, step, end):
    state = init()
    while not end(state):
        step(state)
    return state


def dict_set_default(d, k, default_fn):
    return d[k] if k in d else d.setdefault(k, default_fn())


class EvalAttr:
    def __init__(self, defaults):
        self._defaults = defaults
        self._dct = defaults.copy()
        self._cache = dict()

    def update_dct(self, *args):
        for a in args:
            self._dct.update(a)

    def __getattr__(self, key):
        return self[key]

    def __getitem__(self, key):
        v = self._dct[key]
        return (v.func(self)
                if isinstance(v, xlazy)
                else v.func(**{k: self[k] for k in v.expect_args})
                if isinstance(v, xargs)
                else dict_set_default(
                        self._cache,
                        (key, tuple(self[k] for k in v.expect_args)),
                        partial(v.func, **{k: self[k] for k in v.expect_args}))
                if isinstance(v, xmem)
                else v)


def default_kw(func):
    return {k: p.default for k, p in signature(func).parameters.items()
            if p.default is not Parameter.empty}


def need_args(func):
    return [k for k, p in signature(func).parameters.items()
            if p.kind == Parameter.POSITIONAL_OR_KEYWORD]


def kwplus(func, evaldictclass=EvalAttr):
    def_kw = default_kw(func)
    need_a = need_args(func)
    ekw = evaldictclass(def_kw)

    @wraps(func)
    def wrapper(*a, **kw):
        a2kw = dict(zip(need_a[:len(a)], a))
        ekw.update_dct(a2kw, kw)
        kwevaled = {k: ekw[k] for k in need_a}
        return func(**kwevaled)

    return wrapper
