from datetime import datetime
import json
from socketF.clientSocket import ClientSocket
from screen.screen import screenMountReturnNextStep

cliSocket = None

def printLogMessage(message):
  print("cli app log: " + message)

def cliAppStart(socketPort):
  global cliSocket

  cliSocket = ClientSocket(socketPort, 'cli cli socket log: ')
  cliAppStartScr()

def cliAppStartScr():

  while True:

    optN = screenMountReturnNextStep(
      'Index',
      'Welcome client',
      options=[
        'Insert Order',
        'Modify Order',
        'Enumerate Order',
        'Enumerate Orders',
        'Cancel Order',
        'Exit'])

    if optN == 1:
      insertOrderScr()

    if optN == 2:
      modifyOrderScr()

    if optN == 3:
      enumerateOrderScr()

    if optN == 4:
      enumerateOrdersScr()

    if optN == 5:
      cancelOrderScr()

    if optN == 6:
      exit()

def insertOrderScr():
  
  orderProducts = []

  scr_data = screenMountReturnNextStep('Order Insertion', 'First you must input your cid', inputLabels=['cid'])
  cid = scr_data['cid']

  while True:

    scr_data = screenMountReturnNextStep('Order Insertion', 'Here you create an order by informing its products data', inputLabels=['pid', 'product_quantity'] ,arrayDictData=orderProducts)
    
    if(len(scr_data['product_quantity']) <= 0 or not scr_data['product_quantity'].isdigit()):
      ret = screenMountReturnNextStep('Error', 'product_quantity must be a digit', options=['Input product again', 'Restart order', 'Exit'])
      
      if ret == 2:
        orderProducts = []
      
      if ret == 3:
        break
    
    else:
      orderProducts.append({'pid': scr_data['pid'], 'product_quantity': scr_data['product_quantity']})

      ret = screenMountReturnNextStep('Order product added', 'Continue to add more products?', options=['Yes', 'No'])
      if ret == 2:
        respType, respArgs = insertOrder(cid, str(datetime.now()),{ 'order_products': orderProducts })
        screenMountReturnNextStep(respType, respArgs['message'])
        break

def modifyOrderScr():

  orderProducts = []

  scr_data = screenMountReturnNextStep('Order Modification', 'First you must input your cid and the orders id', inputLabels=['cid', 'oid'])
  cid = scr_data['cid']
  oid = scr_data['oid']

  while True:

    scr_data = screenMountReturnNextStep('Order Modification', 'Here you modify an order by informing its products data', inputLabels=['pid', 'product_quantity'] ,arrayDictData=orderProducts)
    
    if(len(scr_data['product_quantity']) <= 0 or not scr_data['product_quantity'].isdigit()):
      ret = screenMountReturnNextStep('Error', 'product_quantity must be a digit', options=['Input product again', 'Restart order', 'Exit'])
      
      if ret == 2:
        orderProducts = []
      
      if ret == 3:
        break
    
    else:
      orderProducts.append({'pid': scr_data['pid'], 'product_quantity': scr_data['product_quantity']})

      ret = screenMountReturnNextStep('Order product added', 'Continue to add more products?', options=['Yes', 'No'])
      if ret == 2:
        respType, respArgs = modifyOrder(cid, oid, { 'order_products': orderProducts })
        screenMountReturnNextStep(respType, respArgs['message'])
        break

def enumerateOrderScr():

  scr_data = screenMountReturnNextStep('Order Enumeration', 'Here you can read data from a single order by giving cid and oid', inputLabels=['cid', 'oid'])
  cid = scr_data['cid']
  oid = scr_data['oid']

  # order enumeration
  respType, respArgs = enumerateOrder(cid, oid)

  if respType == 'Success':
    orderProductsAr = (json.loads(respArgs['str_order_products']))['order_products']
    screenMountReturnNextStep(respType, 'OID: ' + respArgs['oid'], arrayDictData=orderProductsAr )
  else:
    screenMountReturnNextStep(respType, respArgs['message'])

def enumerateOrdersScr():

  scr_data = screenMountReturnNextStep('Orders Enumeration', 'Here you can read data from a multiple orders by giving your cid', inputLabels=['cid'])
  cid = scr_data['cid']

  # orders enumeration
  respType, respArgs = enumerateOrders(cid)

  if respType == 'Success':
    orderProductsAr = json.loads(respArgs['str_orders_enum'])
    orderProductsAr = orderProductsAr['orders_enum']
    
    screenMountReturnNextStep(respType, respArgs['message'], arrayDictData=orderProductsAr )
  else:
    screenMountReturnNextStep(respType, respArgs['message'])

def cancelOrderScr():

  scr_data = screenMountReturnNextStep('Order Cancelation', 'Here you cancel an order by giving your cid and oid', inputLabels=['cid', 'oid'])
  cid = scr_data['cid']
  oid = scr_data['oid']

  # order cancelation
  respType, respArgs = cancelOrder(cid, oid)
  screenMountReturnNextStep(respType, respArgs['message'])

### request to APIs ###

def insertOrder(cid, order_datetime, order_products):
  global cliSocket

  cliSocket.sendRequestMessage(requestType='insertOrder', requestArgs={'cid': cid, 'order_datetime': order_datetime, 'order_products': order_products })
  return cliSocket.waitServerResponse()

# because datetime is used as a part of the key to generate oid, its not modificable
def modifyOrder(cid, oid, order_products):
  global cliSocket

  cliSocket.sendRequestMessage(requestType='modifyOrder', requestArgs={'cid': cid, 'oid': oid, 'order_products': order_products })
  return cliSocket.waitServerResponse()

def enumerateOrder(cid, oid):
  global cliSocket

  cliSocket.sendRequestMessage(requestType='enumerateOrder', requestArgs={'cid': cid, 'oid': oid})
  return cliSocket.waitServerResponse()

def enumerateOrders(cid):
  global cliSocket

  cliSocket.sendRequestMessage(requestType='enumerateOrders', requestArgs={'cid': cid})
  return cliSocket.waitServerResponse()

def cancelOrder(cid, oid):
  global cliSocket

  cliSocket.sendRequestMessage(requestType='cancelOrder', requestArgs={'cid': cid, 'oid': oid})
  return cliSocket.waitServerResponse()

### ###

### utils ###

def isFloat(n):

  if not n:
    return False
  try:
    float(n)
    return True
  except:
    return False

### ###