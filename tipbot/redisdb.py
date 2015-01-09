#!/bin/python
#
# Cryptonote tipbot
# Copyright 2014 moneromooo
# Inspired by "Simple Python IRC bot" by berend
#
# The Cryptonote tipbot is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation; either version 2, or (at your option)
# any later version.
#

import redis
from tipbot.log import log_error, log_warn, log_info, log_log

redisdb = None

def connect_to_redis(host,port):
  log_info('Connecting to Redis at %s:%u' % (host, port))
  try:
    global redisdb
    redisdb = redis.Redis(host=host,port=port)
    return redisdb
  except Exception, e:
    log_error( 'Error initializing redis: %s' % str(e))
    exit()

def redis_pipeline():
  return redisdb.pipeline()

def redis_get(k):
  return redisdb.get(k)

def redis_set(k,v):
  return redisdb.set(k,v)

def redis_hexists(t,k):
  return redisdb.hexists(t,k)

def redis_hget(t,k):
  return redisdb.hget(t,k)

def redis_hgetall(t):
  return redisdb.hgetall(t)

def redis_hset(t,k,v):
  return redisdb.hset(t,k,v)

def redis_hincrby(t,k,v):
  return redisdb.hincrby(t,k,v)

def redis_incrby(k,v):
  return redisdb.incrby(k,v)


def CompatibilityCheck():
  try:
    r = redis.Redis()
    if not r.pipeline: raise RuntimeError('pipeline call not found')
    p = r.pipeline()
    if not p.get: raise RuntimeError('get call not found')
    if not p.set: raise RuntimeError('set call not found')
    if not p.hexists: raise RuntimeError('hexists call not found')
    if not p.hget: raise RuntimeError('hget call not found')
    if not p.hgetall: raise RuntimeError('hgetall call not found')
    if not p.hset: raise RuntimeError('hset call not found')
    if not p.hincrby: raise RuntimeError('hincrby call not found')
    if not p.incrby: raise RuntimeError('incrby call not found')
    if not p.execute: raise RuntimeError('execute call not found')
  except Exception,e:
    log_error('Error checking redis compatibility: %s' % str(e))
    exit(1)

CompatibilityCheck()

