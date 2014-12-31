#!/bin/python
#
# Cryptonote tipbot - utility functions
# Copyright 2014 moneromooo
#
# The Cryptonote tipbot is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation; either version 2, or (at your option)
# any later version.
#

import redis
import hashlib
import json
import httplib
import tipbot.config as config
import tipbot.coinspecs as coinspecs
from tipbot.log import log_error, log_warn, log_info, log_log
from tipbot.irc import *
from tipbot.redisdb import *


def GetPassword():
  try:
    f = open('tipbot-password.txt', 'r')
    for p in f:
      p = p.strip("\r\n")
      f.close()
      return p
  except Exception,e:
    log_error('could not fetch password: %s' % str(e))
    raise
    return "xxx"

def IsParamPresent(parms,idx):
  return len(parms) > idx

def GetParam(parms,idx):
  if IsParamPresent(parms,idx):
    return parms[idx]
  return None

def GetPaymentID(nick):
  salt="2u3g55bkwrui32fi3g4bGR$j5g4ugnujb-"+coinspecs.name+"-";
  p = hashlib.sha256(salt+nick).hexdigest();
  try:
    redis_hset("paymentid",p,nick)
  except Exception,e:
    log_error('GetPaymentID: failed to set payment ID for %s to redis: %s' % (nick,str(e)))
  return p

def GetNickFromPaymendID(p):
  nick = redis_hget("paymentid",p)
  log_log('PaymendID %s => %s' % (p, str(nick)))
  return nick

def AmountToString(amount):
  if amount == None:
    amount = 0
  lamount=long(amount)
  samount = None
  if lamount == 0:
    samount = "0 %s" % coinspecs.name
  else:
    for den in coinspecs.denominations:
      if lamount < den[0]:
        samount = "%.16g %s" % (float(lamount) / den[1], den[2])
        break
  if not samount:
      samount = "%.16g %s" % (float(lamount) / coinspecs.atomic_units, coinspecs.name)
  log_log("AmountToString: %s -> %s" % (str(amount),samount))
  return samount

def SendJSONRPCCommand(host,port,method,params):
  try:
    http = httplib.HTTPConnection(host,port)
  except Exception,e:
    log_error('SendJSONRPCCommand: Error connecting to %s:%u: %s' % (host, port, str(e)))
    raise
  d = dict(id="0",jsonrpc="2.0",method=method,params=params)
  try:
    j = json.dumps(d).encode()
  except Exception,e:
    log_error('SendJSONRPCCommand: Failed to encode JSON: %s' % str(e))
    http.close()
    raise
  log_log('SendJSONRPCCommand: Sending json as body: %s' % j)
  headers = None
  try:
    http.request("POST","/json_rpc",body=j)
  except Exception,e:
    log_error('SendJSONRPCCommand: Failed to post request: %s' % str(e))
    http.close()
    raise
  response = http.getresponse()
  log_log('SendJSONRPCCommand: Received reply status: %s' % response.status)
  if response.status != 200:
    log_error('SendJSONRPCCommand: Error, not 200: %s' % str(response.status))
    http.close()
    raise RuntimeError("Error "+response.status)
  s = response.read()
  log_log('SendJSONRPCCommand: Received reply: %s' % str(s))
  try:
    j = json.loads(s)
  except Exception,e:
    log_error('SendJSONRPCCommand: Failed to decode JSON: %s' % str(e))
    http.close()
    raise
  http.close()
  return j

def SendHTMLCommand(host,port,method):
  try:
    http = httplib.HTTPConnection(host,port)
  except Exception,e:
    log_error('SendHTMLCommand: Error connecting to %s:%u: %s' % (host, port, str(e)))
    raise
  headers = None
  try:
    http.request("POST","/"+method)
  except Exception,e:
    log_error('SendHTMLCommand: Failed to post request: %s' % str(e))
    http.close()
    raise
  response = http.getresponse()
  log_log('SendHTMLCommand: Received reply status: %s' % response.status)
  if response.status != 200:
    log_error('SendHTMLCommand: Error, not 200: %s' % str(response.status))
    http.close()
    raise RuntimeError("Error "+response.status)
  s = response.read()
  log_log('SendHTMLCommand: Received reply: %s' % s)
  try:
    j = json.loads(s)
  except Exception,e:
    log_error('SendHTMLCommand: Failed to decode JSON: %s' % str(e))
    http.close()
    raise
  http.close()
  return j

def SendWalletJSONRPCCommand(method,params):
  return SendJSONRPCCommand(config.wallet_host,config.wallet_port,method,params)

def SendDaemonJSONRPCCommand(method,params):
  return SendJSONRPCCommand(config.daemon_host,config.daemon_port,method,params)

def SendDaemonHTMLCommand(method):
  return SendHTMLCommand(config.daemon_host,config.daemon_port,method)
