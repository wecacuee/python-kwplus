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
>>> fibonacci(10)
89
>>> fibonacci(20)
10946

``` python-console
>> %timeit fibonacci(10)
5.41 µs ± 85.9 ns per loop (mean ± std. dev. of 7 runs, 100000 loops each)
>> %timeit fibonacci_nomem(10)
16.7 µs ± 1.11 µs per loop (mean ± std. dev. of 7 runs, 10000 loops each)
>> %timeit fibonacci_nomem(20)
16.3 µs ± 628 ns per loop (mean ± std. dev. of 7 runs, 10000 loops each)
>> %timeit fibonacci(20)
5.36 µs ± 90 ns per loop (mean ± std. dev. of 7 runs, 100000 loops each)
```

If you write a function with sufficient granularity, you will only need to
override the necessary portions of the function. For example, the following
fibonacci implementation can be easily converted into a factorial computation
later.

``` python
from functools import partial
@kwplus
def fibonacci(n=1, 
              isterminal=xlazy(lambda s: s.n <= 1),
              onterminal=1,
              recurse=lambda n: fibonacci(n=n-1) + fibonacci(n=n-2),
              ret=xmem(lambda n, onterminal, isterminal, recurse: 
              onterminal if isterminal else recurse(n), "n onterminal isterminal recurse".split())):
    return ret

factorial = partial(fibonacci,
    recurse=lambda n: n*factorial(n-1))

```


Coming back to `foo`.

``` python-console
>>> from kwplus import kwplus, xlazy, xargs, recpartial
>>> @kwplus
... def foo(a=1, b=2, d=xargs(lambda a=None, b=None, offset=5:a+b+offset, expect_args="a b".split()), c=xargs(lambda a=None, b=None, d=None, offset=3: a + b + d+offset, expect_args="a b d".split())):
...     print(a, b, c, d)
...
>>> foo()
1 2 14 8
>>> recpartial(foo, {'d.offset': 3})()
1 2 12 6
>>> recpartial(foo, {'d.offset': 3, 'c.offset': 5})()
1 2 14 6

```

We can be ambitious and serialize python programs as a single dictionary:

``` python-console
>>> from kwplus import kwplus, xlazy, xargs, recpartial
>>> from kwrepr import flattened_kwrepr
>>> from pprint import pprint
>>> from functools import partial
>>> def sum_three(a=0, b=0, d=0, offset=5): return a+b+d+offset
>>> @kwplus
... def foo(a=1, b=2, d=xargs(sum_three, expect_args="a b".split()), c=xargs(sum_three, expect_args="a b d".split())):
...     print(a, b, c, d)
...
>>> pprint(flattened_kwrepr(foo))
{'__class__': 'foo'}
>>> pprint(flattened_kwrepr(recpartial(foo, {'d.offset': 3, 'c.offset': 5})))
{'__class__': 'functools:partial',
 'c.__class__': 'kwplus:xargs',
 'c.expect_args': ['a', 'b', 'd'],
 'c.func.__class__': 'functools:partial',
 'c.func.func.__class__': 'sum_three',
 'c.func.offset': 5,
 'd.__class__': 'kwplus:xargs',
 'd.expect_args': ['a', 'b'],
 'd.func.__class__': 'functools:partial',
 'd.func.func.__class__': 'sum_three',
 'd.func.offset': 3,
 'func.__class__': 'foo'}
>>> @kwplus
... def fibonacci(n=1, 
...               isterminal=xlazy(lambda s: s.n <= 1),
...               onterminal=1,
...               recurse=lambda n: fibonacci(n=n-1) + fibonacci(n=n-2),
...               ret=xmem(lambda n, onterminal, isterminal, recurse: 
...               onterminal if isterminal else recurse(n), "n onterminal isterminal recurse".split())):
...     return ret
... 
>>> def factorial_recurse(n): return n*factorial(n-1)
>>> factorial = partial(fibonacci, recurse=factorial_recurse)
>>> pprint(flattened_kwrepr(fibonacci))
{'__class__': 'fibonacci'}
>>> pprint(flattened_kwrepr(factorial))
{'__class__': 'functools:partial',
 'func.__class__': 'fibonacci',
 'recurse.__class__': 'factorial_recurse'}

```

You can include more detailed recursive configuration if you include function defaults.

``` python-console
>>> import kwrepr
>>> kwrepr.include_function_defaults()
>>> from kwplus import kwplus, xlazy, xargs, recpartial
>>> from kwrepr import flattened_kwrepr
>>> from pprint import pprint
>>> def sum_three(a=0, b=0, d=0, offset=5): return a+b+d+offset
>>> @kwplus
... def foo(a=1, b=2, d=xargs(sum_three, expect_args="a b".split()), c=xargs(sum_three, expect_args="a b d".split())):
...     print(a, b, c, d)
...
>>> pprint(flattened_kwrepr(foo))
{'__class__': 'foo',
 'a': 1,
 'b': 2,
 'c.__class__': 'kwplus:xargs',
 'c.expect_args': ['a', 'b', 'd'],
 'c.func.__class__': 'sum_three',
 'c.func.a': 0,
 'c.func.b': 0,
 'c.func.d': 0,
 'c.func.offset': 5,
 'd.__class__': 'kwplus:xargs',
 'd.expect_args': ['a', 'b'],
 'd.func.__class__': 'sum_three',
 'd.func.a': 0,
 'd.func.b': 0,
 'd.func.d': 0,
 'd.func.offset': 5}
>>> pprint(flattened_kwrepr(recpartial(foo, {'d.offset': 3, 'c.offset': 5})))
{'__class__': 'functools:partial',
 'c.__class__': 'kwplus:xargs',
 'c.expect_args': ['a', 'b', 'd'],
 'c.func.__class__': 'functools:partial',
 'c.func.func.__class__': 'sum_three',
 'c.func.func.a': 0,
 'c.func.func.b': 0,
 'c.func.func.d': 0,
 'c.func.func.offset': 5,
 'c.func.offset': 5,
 'd.__class__': 'kwplus:xargs',
 'd.expect_args': ['a', 'b'],
 'd.func.__class__': 'functools:partial',
 'd.func.func.__class__': 'sum_three',
 'd.func.func.a': 0,
 'd.func.func.b': 0,
 'd.func.func.d': 0,
 'd.func.func.offset': 5,
 'd.func.offset': 3,
 'func.__class__': 'foo',
 'func.a': 1,
 'func.b': 2,
 'func.c.__class__': 'kwplus:xargs',
 'func.c.expect_args': ['a', 'b', 'd'],
 'func.c.func.__class__': 'sum_three',
 'func.c.func.a': 0,
 'func.c.func.b': 0,
 'func.c.func.d': 0,
 'func.c.func.offset': 5,
 'func.d.__class__': 'kwplus:xargs',
 'func.d.expect_args': ['a', 'b'],
 'func.d.func.__class__': 'sum_three',
 'func.d.func.a': 0,
 'func.d.func.b': 0,
 'func.d.func.d': 0,
 'func.d.func.offset': 5}

```
