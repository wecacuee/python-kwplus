# python-kwplus
Python keywords on steroids

## Design requirements

Consider defining a function that takes in three parameters `a,b,c`
``` python
def foo(a, b, c):
    ...
```

To make the usage of function easier we want to provide defaults for the parameters.

``` python
def foo(a=1, b=2, c=3):
    ...
```

Sometimes, some of the reasonable initializations of the parameters depends on other inputs.

``` python
def foo(a=1, b=2):
    c = a + b
    ...
```

What if, we also want c as a parameter.

``` python
def foo(a=1, b=2, c=None):
    c = (a + b if c is None else c)
    ...
```

What if, we want to let the user define `c` in terms of `a` and `b`.


``` python
def foo(a=1, b=2, c_=lambda a, b: a + b):
    c = c_(a, b)
    ...
```

What if, we add another parameter `d` and we want `c` to depend upon `a`, `b`, and `d`.

``` python
def foo(a=1, b=2, d=3, c_=lambda a, b, d: a + b + d):
    c = c_(a, b, d)
    ...
```

However, this breaks backward compatibility with previous signature of `c_`
which only takes two arguments. What if you could do this:

``` python
from kwplus import kwplus, xlazy

@kwplus
def foo(a=1, b=2, d=3, c=xlazy(lambda s: s.a + s.b + s.d)):
    print(a, b, c, d)
```

What if `d` could be a function of `a` and `b`:

``` python
@kwplus
def foo(a=1, b=2, d=xlazy(lambda s:s.a+s.b), c=xlazy(lambda s: s.a + s.b + s.d)):
    print(a, b, c, d)
```

This is enough to make a new programming language.

``` python
@kwplus
def fibonacci(n=1, 
              ret=xlazy(lambda s: 1 if s.n <= 1 else fibonacci(n=s.n-1) + fibonacci(n=s.n-2))):
    return ret
```

To convert this to dynamic programming one can use `xmem`.

``` python-console
>>> from kwplus import kwplus, xmem, xargs
>>> @kwplus
... def fibonacci(n=1, 
...               ret=xmem(lambda n: 1 if n <= 1 else fibonacci(n=n-1) + fibonacci(n=n-2), ["n"])):
...     return ret
>>> @kwplus
... def fibonacci_nomem(n=1, 
...               ret=xargs(lambda n: 1 if n <= 1 else fibonacci(n=n-1) + fibonacci(n=n-2), ["n"])):
...     return ret
>>> %timeit fibonacci(10)
5.41 µs ± 85.9 ns per loop (mean ± std. dev. of 7 runs, 100000 loops each)
>>> %timeit fibonacci_nomem(10)
16.7 µs ± 1.11 µs per loop (mean ± std. dev. of 7 runs, 10000 loops each)
>>> %timeit fibonacci_nomem(20)
16.3 µs ± 628 ns per loop (mean ± std. dev. of 7 runs, 10000 loops each)
>>> %timeit fibonacci(20)
5.36 µs ± 90 ns per loop (mean ± std. dev. of 7 runs, 100000 loops each)

```

