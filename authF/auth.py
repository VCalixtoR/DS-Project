from hashlib import md5
import os

secretKey = open(os.path.abspath("authF/secretKey.key"), "r").read()

def printLogMessage(message):
  print("adm auth log: " + message)

def generateOID(cid, order_datetime):

  if type(cid) != str or type(order_datetime) != str or not ':' in cid:
    printLogMessage('invalid cid or order_datetime data type')
    return False
  
  oidKey = cid.split(':')[1] + order_datetime.replace(' ', '')
  oid = md5((oidKey+secretKey).encode('utf-8')).hexdigest() + ':' + oidKey

  return oid

def generatePID(productName):

  if type(productName) != str:
    printLogMessage('invalid productName data type')
    return False

  pid = md5((productName+secretKey).encode('utf-8')).hexdigest() + ':' + productName

  return pid

def generateCID(clientCPF):

  if type(clientCPF) != str:
    printLogMessage('invalid clientCPF data type')
    return False

  cid = md5((clientCPF+secretKey).encode('utf-8')).hexdigest() + ':' + clientCPF

  return cid

def authenticateCID(cid):

  if type(cid)!= str:
    printLogMessage('invalid cid data type')
    return False

  if len(cid)-(cid.rfind(':')+1) != 11:
    printLogMessage('invalid cid structure')
    return False
  
  cpf = cid[cid.rfind(':')+1:len(cid)]
  
  return generateCID(cpf) == cid