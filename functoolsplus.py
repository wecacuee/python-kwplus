from functools import partial, reduce


def call(f, *a, **kw):
    return f(*a, **kw)


def compose(fs):
    """
    Composes functions together

    If the input is [f, g, h], the function returns r such that
    r(x) = f(g(h(x)))

    or r = (f · g · h)
    """
    return partial(reduce, lambda acc, f: f(acc), reversed(fs))


def kwcompose(fs):
    """
    Composes keyword functions together

    If the input is [f, g, h], the function returns r such that
    r(**kw) = f(**g(**h(**kw)))

    or r = (f · g · h)
    """
    return partial(reduce, lambda acc, f: f(**acc), reversed(fs))


def argcompose(fs):
    """
    Composes keyword functions together

    If the input is [f, g, h], the function returns r such that
    r(*a) = f(*g(*h(*a)))

    or r = (f · g · h)
    """
    return partial(reduce, lambda acc, f: f(*acc), reversed(fs))
