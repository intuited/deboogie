"""Tools to git deboogie on."""

def get_debug_logger(name, strm=None):
    """Creates a basic debug logger with prettyprint capabilities.

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
