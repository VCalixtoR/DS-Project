from mqttF.adminMQTT import adminMQTT
import database.dbSession as db
import database.clientCRUD as dbClient
import database.productCRUD as dbProduct
import json
from screen.screen import screenCacheMount
from socketF.serverSocket import ServerSocket
from authF.auth import authenticateCID, generateCID

# In Python, the Dictionary data types represent the implementation of hash tables.
#   ref: https://www.tutorialspoint.com/python_data_structure/python_hash_table.htm

admMQTT = None
serverSocket = None
clientsCache = dict()
productsCache = dict()
ordersCache = dict()
clientOrdersCache = dict()

def admPortalStart(socketPort, debug = False):
  global admMQTT, serverSocket, clientsCache, productsCache, ordersCache, clientOrdersCache

  # mysql connection
  db.dbStart()

  # mqtt connection
  admMQTT = adminMQTT(callbackUpdateCache, debug)

  # socket connection
  serverSocket = ServerSocket(socketPort, socketAPIs, 'adm server socket log: ')
  serverSocket.processClientRequests()

def printLogMessage(message):
  print("adm portal log: " + message)

# Callback function to change local cash values when MQTT receives a message
def callbackUpdateCache(clientsCacheT = None, productsCacheT = None, ordersCacheT = None, clientOrdersCacheT = None):
  global clientsCache, productsCache, ordersCache, clientOrdersCache

  if clientsCacheT != None:
    clientsCache = clientsCacheT
    screenCacheMount('clientsCache', clientsCache)

  if productsCacheT != None:
    productsCache = productsCacheT
    screenCacheMount('productsCache', productsCache)

  if ordersCacheT != None:
    ordersCache = ordersCacheT
    screenCacheMount('ordersCache', ordersCache)
    
  if clientOrdersCacheT != None:
    clientOrdersCache = clientOrdersCacheT
    screenCacheMount('clientOrdersCache', clientOrdersCache)

### Callback function from server socket to select API request handler ###

def socketAPIs(reqMsgType, reqArgs):

  if reqMsgType == 'insertClient':
    if len(reqArgs) != 2:
      printLogMessage('Incorrect number of parameters to insertClient')
    else:
      insertClient(cid = reqArgs['cid'], client_data = reqArgs['client_data'])
  
  elif reqMsgType == 'modifyClient':
    if len(reqArgs) != 2:
      printLogMessage('Incorrect number of parameters to modifyClient')
    else:
      modifyClient(cid = reqArgs['cid'], client_data = reqArgs['client_data'])

  elif reqMsgType == 'recoveryClient':
    if len(reqArgs) != 1:
      printLogMessage('Incorrect number of parameters to recoveryClient')
    else:
      recoveryClient(cid = reqArgs['cid'])
  
  elif reqMsgType == 'removeClient':
    if len(reqArgs) != 1:
      printLogMessage('Incorrect number of parameters to removeClient')
    else:
      removeClient(cid = reqArgs['cid'])

  elif reqMsgType == 'insertProduct':
    if len(reqArgs) != 2:
      printLogMessage('Incorrect number of parameters to insertProduct')
    else:
      insertProduct(pid=reqArgs['pid'], product_data=reqArgs['product_data'])

  elif reqMsgType == 'modifyProduct':
    if len(reqArgs) != 2:
      printLogMessage('Incorrect number of parameters to modifyProduct')
    else:
      modifyProduct(pid=reqArgs['pid'], product_data=reqArgs['product_data'])

  elif reqMsgType == 'recoveryProduct':
    if len(reqArgs) != 1:
      printLogMessage('Incorrect number of parameters to recoveryProduct')
    else:
      recoveryProduct(pid=reqArgs['pid'])

  elif reqMsgType == 'removeProduct':
    if len(reqArgs) != 1:
      printLogMessage('Incorrect number of parameters to removeProduct')
    else:
      removeProduct(pid=reqArgs['pid'])

### ###

### utils ###

def isInCache(cache, key):

  for keyC in cache.keys():
    if key == keyC:
      return True

  return False
  
### ###
    
### response to APIs ###

def insertClient(cid, client_data):
  global admMQTT, clientsCache, serverSocket

  if isInCache(clientsCache, cid):
    serverSocket.sendClientResponse('Failed', { 'message': 'Client already inserted' })
    return

  clientsCache[cid] = client_data
  admMQTT.publishClients(clientsCache)
  dbClient.createClientDB(cid, client_data)
  serverSocket.sendClientResponse('Success', { 'message': 'Client inserted' })

def modifyClient(cid, client_data):
  global admMQTT, clientsCache, serverSocket

  if not isInCache(clientsCache, cid):
    serverSocket.sendClientResponse('Failed', { 'message': 'Client not exists' })
  else:
    client_data = json.loads(client_data)

    tmp = json.loads(clientsCache[cid])
    tmp['client_name'] = client_data['client_name']

    clientsCache[cid] = json.dumps(tmp)
    admMQTT.publishClients(clientsCache)
    dbClient.updateClientDB(cid, json.dumps(tmp))
    serverSocket.sendClientResponse('Success', { 'message': 'Client modified' })

def recoveryClient(cid):
  global admMQTT, clientsCache, serverSocket

  if isInCache(clientsCache, cid):
    serverSocket.sendClientResponse('Failed', { 'message': 'Client already exists in cache' })
  else:
    
    ok, resp = dbClient.readClientDB(cid)
    print(resp)
    if ok:
      clientsCache[resp['id']] = resp['data']
      admMQTT.publishClients(clientsCache)
      serverSocket.sendClientResponse('Success', { 'message': 'Client recovered' })
    else:
      serverSocket.sendClientResponse('Failed', { 'message': str(resp) })

def removeClient(cid):
  global admMQTT, clientsCache, serverSocket

  if not isInCache(clientsCache, cid):
    serverSocket.sendClientResponse('Failed', { 'message': 'Client not exists' })
  else:
    del clientsCache[cid]
    admMQTT.publishClients(clientsCache)
    dbClient.deleteClientDB(cid)
    serverSocket.sendClientResponse('Success', { 'message': 'Client removed' })

def insertProduct(pid, product_data):
  global admMQTT, productsCache, serverSocket

  if isInCache(productsCache, pid):
    serverSocket.sendClientResponse('Failed', { 'message': 'Product already inserted' })
  else:
    productsCache[pid] = product_data
    admMQTT.publishProducts(productsCache)
    dbProduct.createProductDB(pid, product_data)
    serverSocket.sendClientResponse('Success', { 'message': 'Product inserted' })

def modifyProduct(pid, product_data):
  global admMQTT, productsCache, serverSocket

  if not isInCache(productsCache, pid):
    serverSocket.sendClientResponse('Failed', { 'message': 'Product not exists' })
  else:
    product_data = json.loads(product_data)

    tmp = json.loads(productsCache[pid])
    tmp['product_description'] = product_data['product_description']
    tmp['product_quantity'] = product_data['product_quantity']
    tmp['product_price'] = product_data['product_price']

    productsCache[pid] = json.dumps(tmp)
    admMQTT.publishProducts(productsCache)
    dbProduct.updateProductDB(pid, json.dumps(tmp))
    serverSocket.sendClientResponse('Success', { 'message': 'Product modified' })

def recoveryProduct(pid):
  global admMQTT, productsCache, serverSocket

  if isInCache(productsCache, pid):
    serverSocket.sendClientResponse('Failed', { 'message': 'Product already exists in cache' })
  else:
    
    ok, resp = dbProduct.readProductDB(pid)
    if ok:
      productsCache[resp['id']] = resp['data']
      admMQTT.publishProducts(productsCache)
      serverSocket.sendClientResponse('Success', { 'message': 'Product recovered' })
    else:
      serverSocket.sendClientResponse('Failed', { 'message': str(resp) })

def removeProduct(pid):
  global admMQTT, productsCache, serverSocket

  if not isInCache(productsCache, pid):
    serverSocket.sendClientResponse('Failed', { 'message': 'Product not exists' })
  else:
    del productsCache[pid]
    admMQTT.publishProducts(productsCache)
    dbProduct.deleteProductDB(pid)
    serverSocket.sendClientResponse('Success', { 'message': 'Product removed' })

### ###