"""Tools to git deboogie on."""
from pprint import pformat
from sys import stdout
from StringIO import StringIO

def get_debug_logger(name, strm=None):
    """Creates a basic debug log function with prettyprint capabilities.

    A basic logger is created.
    The logger's ``debug`` method is returned.
    The logger itself is returned as ``return.logger``.
    The handler is returned as ``return.handler``.
    A pretty-printing version of the log function is returned as ``return.pp``.

    >>> from sys import stdout
    >>> debug = get_debug_logger('boogie', strm=stdout)
    >>> debug('Git yer gittin it on on and boogie!')
    Git yer gittin it on on and boogie!
    >>> debug.pp(debug.__dict__)  # doctest: +ELLIPSIS
    { 'handler': <logging.StreamHandler instance at 0x...>,
      'pp': <function <lambda> at 0x...>}

    Subsequent loggers do not issue duplicate output.
    >>> debug_two = get_debug_logger('boogie', strm=stdout)
    >>> debug('Hit me one time!  OW!')
    Hit me one time!  OW!

    How does that work?
    >>> debug.logger is debug_two.logger
    False

    So logging.Logger(name) doesn't always return the same object.
    """
    from logging import Logger, StreamHandler, DEBUG
    logger = Logger(name)
    debug = lambda *args, **kwargs: logger.debug(*args, **kwargs)
    debug.logger = logger

    handler = StreamHandler(strm=strm)
    logger.addHandler(handler)
    debug.handler = handler

    from pprint import PrettyPrinter
    pformat = PrettyPrinter(indent=2).pformat
    debug.pp = lambda *args, **kwargs: debug(pformat(*args, **kwargs))
    return debug


class NullStream(StringIO):
    def write(*args):
        pass
null_stream = NullStream()

def get_null_logger(name):
    from StringIO import StringIO
    return get_debug_logger(name, null_stream)
null_log = get_null_logger('null')


# expanded version of iterrabble.iterlog
def iterdebug(name, it, stringifier=str, strm=None):
    """Log iterable elements to `strm` as they pass through this node.

    >>> from sys import stdout
    >>> jives = (1, 2, 3)
    >>> dejives = iterdebug('jives', jives, stringifier='jive {0}'.format,
    ...                     strm=stdout)
    >>> list(dejives)
    jive 1
    jive 2
    jive 3
    [1, 2, 3]
    """
    debug = get_debug_logger(name, strm=strm)
    for i in iter(it):
        debug(stringifier(i))
        yield i

def tuplabel(name, f=None):
    """The produced function wraps a tuple with a label and a function call."""
    def label(tup):
        if f:
            tup = f(tup)
        return (name, tup)
    return label

# The default logger for tracewrap-produced decorators.
tracewrap_log = get_debug_logger('tracewrap')
null_fmt = lambda *a, **k: None

def tracewrap(infmt=lambda a: pformat(tuplabel('->')(a)),
              outfmt=lambda a: pformat(tuplabel('<-')(a)),
              inlog=tracewrap_log, outlog=tracewrap_log):
    """Decorator factory to log function inputs and outputs.

    First we have to do some setup to break doctest's fourth wall.
        >>> # We want to catch the default output of this function,
        >>> # which is directed to standard error.
        >>> import sys
        >>> sys.stderr = sys.stdout

        >>> # Since this function has a reference to the real standard error,
        >>> # we need to reload the module and re-import its names.
        >>> # This will allow doctest to catch its output.
        >>> import deboogie
        >>> reload(deboogie) # doctest: +ELLIPSIS
        <module 'deboogie'...>
        >>> from deboogie import *

    This is how tracewrap works with its default settings:
        >>> from pprint import pprint
        >>> @tracewrap()
        ... def simply_wrapped_func(*wa, **wk):
        ...     return ('simply_wrapped_func returning (wa, wk)', wa, wk)
        >>> ret = simply_wrapped_func('simply_wrapped_func arg 1',
        ...                           'simply_wrapped_func arg 2',
        ...                           wfkw1='wrapped_func kwarg 1')
        ... # doctest: +ELLIPSIS
        ('->',
         (('function', <function simply_wrapped_func at 0x...>),
          ('args', ('simply_wrapped_func arg 1', 'simply_wrapped_func arg 2')),
          ('kwargs', {'wfkw1': 'wrapped_func kwarg 1'})))
        ('<-',
         ('simply_wrapped_func returning (wa, wk)',
          ('simply_wrapped_func arg 1', 'simply_wrapped_func arg 2'),
          {'wfkw1': 'wrapped_func kwarg 1'}))
        >>> pprint(ret)
        ('simply_wrapped_func returning (wa, wk)',
         ('simply_wrapped_func arg 1', 'simply_wrapped_func arg 2'),
         {'wfkw1': 'wrapped_func kwarg 1'})

    To show how the format functions can be used to process the data,
    we set things up to log the first positional argument
    and to ignore return values:
        >>> #fmt=lambda data: pformat(('lambda-formatted', data))
        >>> infmt=lambda data: ('first positional argument', data[1][0])

        >>> def printlog(*args, **kwargs):
        ...     if args[0]:
        ...         print 'Example call trace: ', args[0]

        >>> @tracewrap(infmt=infmt, outfmt=null_fmt,
        ...            inlog=printlog, outlog=null_log)
        ... def wrapped_func(*wa, **wk):
        ...     return ('wrapped_func returning (wa, wk)', wa, wk)
        >>> ret = wrapped_func('wrapped_func arg 1', 'wrapped_func arg 2',
        ...                    wfkw1='wrapped_func kwarg 1')
        ... # doctest: +ELLIPSIS
        Example call trace:  ('first positional argument', 'args')
        >>> pprint(ret)
        ('wrapped_func returning (wa, wk)',
         ('wrapped_func arg 1', 'wrapped_func arg 2'),
         {'wfkw1': 'wrapped_func kwarg 1'})
    """
    def tracer(f):
        def trace(*args, **kwargs):
            """Trace output function.

            Inputs and outputs are passed as a single tuple to
            ``{0}`` and ``{1}`` respectively.
            """.format(infmt, outfmt)

            inlog(infmt((('function', f),
                       ('args', args), ('kwargs', kwargs))))
            ret = f(*args, **kwargs)
            outlog(outfmt(ret))
            return ret
        return trace
    return tracer
