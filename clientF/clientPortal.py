from authF.auth import authenticateCID, generateOID
import database.dbSession as db
import database.productCRUD as dbProduct
import database.orderCRUD as dbOrder
import json
from mqttF.clientMQTT import clientMQTT
from screen.screen import screenCacheMount
from socketF.serverSocket import ServerSocket

# In Python, the Dictionary data types represent the implementation of hash tables. 
#   ref: https://www.tutorialspoint.com/python_data_structure/python_hash_table.htm

cliMQTT = None
serverSocket = None
productsCache = dict()
ordersCache = dict()
clientOrdersCache = dict()

def cliPortalStart(socketPort, debug = False):
  global cliMQTT, serverSocket, productsCache, ordersCache, clientOrdersCache

  # mysql connection
  db.dbStart()

  # mqtt connection
  cliMQTT = clientMQTT(callbackUpdateCache, debug)

  # socket connection
  serverSocket = ServerSocket(socketPort, socketAPIs, 'cli server socket log: ')
  serverSocket.processClientRequests()

def printLogMessage(message):
  print("cli portal log: " + message)

# Used a callback function to change local cash values
def callbackUpdateCache(productsCacheT = None, ordersCacheT = None, clientOrdersCacheT = None):
  global productsCache, ordersCache, clientOrdersCache

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

  if reqMsgType == 'insertOrder':
    if len(reqArgs) != 3:
      serverSocket.sendClientResponse('Failed',{ 'message': 'Incorrect number of parameters to insertOrder' })
    else:
      insertOrder(cid = reqArgs['cid'], order_datetime = reqArgs['order_datetime'], order_products = reqArgs['order_products'])

  if reqMsgType == 'modifyOrder':
    if len(reqArgs) != 3:
      serverSocket.sendClientResponse('Failed',{ 'message': 'Incorrect number of parameters to modifyOrder' })
    else:
      modifyOrder(cid = reqArgs['cid'], oid = reqArgs['oid'], order_products = reqArgs['order_products'])

  if reqMsgType == 'enumerateOrder':
    if len(reqArgs) != 2:
      serverSocket.sendClientResponse('Failed',{ 'message': 'Incorrect number of parameters to enumerateOrder' })
    else:
      enumerateOrder(cid = reqArgs['cid'], oid = reqArgs['oid'])

  if reqMsgType == 'enumerateOrders':
    if len(reqArgs) != 1:
      serverSocket.sendClientResponse('Failed',{ 'message': 'Incorrect number of parameters to enumerateOrders' })
    else:
      enumerateOrders(cid = reqArgs['cid'])

  if reqMsgType == 'cancelOrder':
    if len(reqArgs) != 2:
      serverSocket.sendClientResponse('Failed',{ 'message': 'Incorrect number of parameters to cancelOrder' })
    else:
      cancelOrder(cid = reqArgs['cid'], oid = reqArgs['oid'])

### ###

### utils ###

def isInCache(cache, key):

  for keyC in cache.keys():
    if key == keyC:
      return True

  return False

def addClientOrdersCache(cid, oid):
  global clientOrdersCache

  if not cid in clientOrdersCache:
    clientOrdersCache[cid] = [oid]

  elif not oid in clientOrdersCache[cid]:
    clientOrdersCache[cid].append(oid)
  
  screenCacheMount('clientOrdersCache', clientOrdersCache)

def removeClientOrdersCache(cid, oid):
  global clientOrdersCache

  if cid in clientOrdersCache:
    if oid in clientOrdersCache[cid]:
      clientOrdersCache[cid].remove(oid)
  
  screenCacheMount('clientOrdersCache', clientOrdersCache)
  
### ###
    
### response to APIs ###

def insertOrder(cid, order_datetime, order_products):
  global cliMQTT, clientOrdersCache, productsCache, ordersCache, serverSocket

  if not authenticateCID(cid):
    serverSocket.sendClientResponse('Failed', { 'message': 'Cannot authenticate client cid' })
    return
  
  oid = generateOID(cid, order_datetime)

  if isInCache(ordersCache, oid):
    serverSocket.sendClientResponse('Failed', { 'message': 'Order already inserted' })
  else:
    
    # get data for all order products
    order_products = json.loads(order_products)
    order_total_value = 0
    
    for product in order_products['order_products']:
      
      if not isInCache(productsCache, product['pid']):
        serverSocket.sendClientResponse('Failed', { 'message': 'Pid ' + product['pid'] + ' not exists' })
        return
      else:
        tmp = json.loads(productsCache[product['pid']])

        if int(product['product_quantity']) > int(tmp['product_quantity']):
          serverSocket.sendClientResponse('Failed', { 'message': 'Product ' + tmp['product_name'] + ' not contains quantity requested' })
          return

        product['product_name'] = tmp['product_name']
        product['product_price'] = tmp['product_price']
        order_total_value = order_total_value + float(tmp['product_price']) * int(product['product_quantity'])
    
    # iterate in products to update product cache quantity
    for product in order_products['order_products']:
      tmpP = json.loads(productsCache[product['pid']])
      tmpP['product_quantity'] = str(int(tmpP['product_quantity']) - int(product['product_quantity']))
      productsCache[product['pid']] = json.dumps(tmpP)

    ordersCache[oid] = json.dumps({
      'order_client_id' : cid,
      'order_datetime': order_datetime,
      'order_total_value': order_total_value,
      'order_products': order_products['order_products']
    })
    addClientOrdersCache(cid, oid)
    cliMQTT.publishOrders(ordersCache)
    cliMQTT.publishClientOrders(clientOrdersCache)
    cliMQTT.publishProducts(productsCache)
    dbOrder.createOrderDB(oid, ordersCache[oid])

    serverSocket.sendClientResponse('Success', { 'message': 'Order inserted' })

def modifyOrder(cid, oid, order_products):
  global cliMQTT, ordersCache, serverSocket

  if not authenticateCID(cid):
    serverSocket.sendClientResponse('Failed', { 'message': 'Cannot authenticate client cid' })
    return
  
  if not isInCache(ordersCache, oid):
    serverSocket.sendClientResponse('Failed', { 'message': 'Order  not exists' })
    return

  oldOrder = json.loads(ordersCache[oid])

  if cid != oldOrder['order_client_id']:
    serverSocket.sendClientResponse('Failed', { 'message': 'Order does not belongs to this client' })
    return

  # keep out datetime
  order_datetime = oldOrder['order_datetime']

  order_products = json.loads(order_products)

  order_total_value = 0
  # get data for all order products
  for product in order_products['order_products']:
    
    if not isInCache(productsCache, product['pid']):
      serverSocket.sendClientResponse('Failed', { 'message': 'Pid ' + product['pid'] + ' not exists' })
      return
    else:
      tmp = json.loads(productsCache[product['pid']])

      if int(product['product_quantity']) > int(tmp['product_quantity']):
        serverSocket.sendClientResponse('Failed', { 'message': 'Product ' + tmp['product_name'] + ' not contains quantity requested' })
        return

      product['product_name'] = tmp['product_name']
      product['product_price'] = tmp['product_price']
      order_total_value = order_total_value + float(tmp['product_price']) * int(product['product_quantity'])

  # iterate in products to update product cache quantity sum olders
  for oldProduct in oldOrder['order_products']:
    print('sum ' + str(oldProduct['product_quantity']))
    tmpP = json.loads(productsCache[oldProduct['pid']])
    tmpP['product_quantity'] = str(int(tmpP['product_quantity']) + (int(oldProduct['product_quantity']) ))
    productsCache[oldProduct['pid']] = json.dumps(tmpP)

  # iterate in products to update product cache quantity subtract new ones
  for newProduct in order_products['order_products']:
    print('sub ' + str(newProduct['product_quantity']))
    tmpP = json.loads(productsCache[newProduct['pid']])
    tmpP['product_quantity'] = str(int(tmpP['product_quantity']) - (int(newProduct['product_quantity']) ))
    productsCache[newProduct['pid']] = json.dumps(tmpP)
  
  ordersCache[oid] = json.dumps({
    'order_client_id' : cid,
    'order_datetime': order_datetime,
    'order_total_value': order_total_value,
    'order_products': order_products['order_products']
  })
  cliMQTT.publishOrders(ordersCache)
  cliMQTT.publishProducts(productsCache)
  dbOrder.updateOrderDB(oid, ordersCache[oid])

  serverSocket.sendClientResponse('Success', { 'message': 'Order modified' })
  
def enumerateOrder(cid, oid):
  global cliMQTT, ordersCache, serverSocket

  if not authenticateCID(cid):
    serverSocket.sendClientResponse('Failed', { 'message': 'Cannot authenticate client cid' })
    return
  
  if not isInCache(ordersCache, oid):
    serverSocket.sendClientResponse('Failed', { 'message': 'Order not exists' })
    return
  
  if cid not in ordersCache[oid]:
    serverSocket.sendClientResponse('Failed', { 'message': 'Order does not belongs to this client' })
    return
  
  tmp = json.loads(ordersCache[oid])
  resp = { 'message': 'Order enumered', 'oid' : oid, 'str_order_products' : json.dumps({'order_products' : tmp['order_products']}) }
  serverSocket.sendClientResponse('Success', resp)

def enumerateOrders(cid):
  global cliMQTT, ordersCache, serverSocket

  if not authenticateCID(cid):
    serverSocket.sendClientResponse('Failed', { 'message': 'Cannot authenticate client cid' })
    return
  
  ret = []
  for oid in clientOrdersCache[cid]:
    tmp = json.loads(ordersCache[oid])
    ret.append({oid : tmp['order_total_value']})

  resp = { 'message': 'Orders enumered', 'str_orders_enum' : json.dumps({'orders_enum' : ret}) }
  serverSocket.sendClientResponse('Success', resp)

def cancelOrder(cid, oid):
  global cliMQTT, ordersCache, serverSocket

  if not authenticateCID(cid):
    serverSocket.sendClientResponse('Failed', { 'message': 'Cannot authenticate client cid' })
    return
  
  if not isInCache(ordersCache, oid):
    serverSocket.sendClientResponse('Failed', { 'message': 'Order not exists' })
    return
  
  if cid not in ordersCache[oid]:
    serverSocket.sendClientResponse('Failed', { 'message': 'Order does not belongs to this client' })
    return
  
  # iterate in products to update product cache quantity
  tmpO = json.loads(ordersCache[oid])
  for product in tmpO['order_products']:
    tmpP = json.loads(productsCache[product['pid']])
    tmpP['product_quantity'] = str(int(tmpP['product_quantity']) + int(product['product_quantity']))
    productsCache[product['pid']] = json.dumps(tmpP)
  
  del ordersCache[oid]
  removeClientOrdersCache(cid, oid)
  cliMQTT.publishOrders(ordersCache)
  cliMQTT.publishClientOrders(clientOrdersCache)
  cliMQTT.publishProducts(productsCache)
  dbOrder.deleteOrderDB(oid)

  serverSocket.sendClientResponse('Success', { 'message': 'Order cancelled' })

### ###