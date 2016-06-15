#!/usr/bin/python -u
#encoding:utf-8
import time
import os
import psycopg2
from jsoncache import loadCache

def attempt_retries(retries=3, delay=3, IgnoreException=Exception):
    """
    Decorator for ignoring certain exception for certain number times and retrying with certain delay
    e.g.   func = @retry(connect_imap, 10, 5, SocketError) # Tries ten times
    e.g.2. retry(connect_imap)(username, password)
    """
    def wrapper(func):
        def dec(*args, **kwargs):
            for i in range(retries-1):
                try:
                    return func(*args, **kwargs)
                except IgnoreException:
                    time.sleep(delay)
            return func(*args, **kwargs)
        return dec
    return wrapper


def cache_result(cache_name, expire_days=30*12):
    if os.path.exists(cache_name) and os.stat(cache_name).st_ctime >= time.time() + expire_days*86400:
            os.remove(cache_name)
    def func_wrapper(func):
        def wrapper(*args, **kwargs):
            fname = "%s.cache" % (cache_name)
            def gen():
                return func(*args, **kwargs)
            return loadCache(fname, gen)
        return wrapper
    return func_wrapper

import hashlib
def _get_param_hash(*args, **kwargs):
    x = [str(a) for a in args]
    x += [str(k) for k in kwargs]
    x = hashlib.md5(''.join(x)).hexdigest()
    return x
    
def mem_cache_function(func):
    def wrapper(*args, **kwargs):
        param_hash = _get_param_hash(*args, **kwargs)
        if not wrapper.cached.has_key(param_hash):
            wrapper.cached[param_hash] = func(*args, **kwargs)
        return wrapper.cached[param_hash]
    wrapper.cached = {}
    return wrapper
