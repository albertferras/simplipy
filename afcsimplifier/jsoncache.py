#!/usr/bin/python -u
#encoding:utf-8

import os;
import ujson

def loadCache(fname, func_gen_data=None):
    if (os.path.exists(fname)):
        #print 'Loading cache:', fname;
        fd = open(fname, 'r');
        data = fd.read();
        fd.close();
        return ujson.loads(data);
    elif func_gen_data is not None:
        data = func_gen_data()
        saveCache(fname, data)
        return data
    return None

def saveCache(fname, data):
    fd = open(fname, 'w');
    fd.write(ujson.dumps(data));
    fd.close();
