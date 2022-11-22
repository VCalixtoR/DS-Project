from authF.auth import generateCID, generatePID
from socketF.clientSocket import ClientSocket
from screen.screen import screenMountReturnNextStep

cliSocket = None

def printLogMessage(message):
  print("adm app log: " + message)

def admAppStart(socketPort):
  global cliSocket

  cliSocket = ClientSocket(socketPort, 'adm cli socket log: ')
  admAppStartScr()

def admAppStartScr():

  while True:

    optN = screenMountReturnNextStep(
      'Index', 
      'Welcome administrator', 
      options=[
        'Insert Client', 
        'Modify Client',
        'recovery Client',
        'remove Client',
        'Insert Product', 
        'Modify Product',
        'recovery Product',
        'remove Product',
        'Exit'])

    if optN == 1:
      insertClientScr()

    if optN == 2:
      modifyClientScr()

    if optN == 3:
      recoveryClientScr()

    if optN == 4:
      removeClientScr()

    if optN == 5:
      insertProductScr()

    if optN == 6:
      modifyProductScr()

    if optN == 7:
      recoveryProductScr()
      
    if optN == 8:
      removeProductScr()
      
    if optN == 9:
      exit()

def insertClientScr():

  while True:

    scr_data = screenMountReturnNextStep('Client Insertion', 'Here you add a client informing their data', inputLabels=['client_cpf', 'client_name'])
    
    if(len(scr_data['client_cpf']) != 11 or not scr_data['client_cpf'].isdigit()):
      ret = screenMountReturnNextStep('Error', 'client_cpf must have 11 digits', options=['Try Again','Exit'])
      if ret == 2:
        break
    
    elif(len(scr_data['client_name']) < 5):
      ret = screenMountReturnNextStep('Error', 'client_name must have at least 5 characters', options=['Try Again','Exit'])
      if ret == 2:
        break
    
    # client insertion
    else:
      cid = generateCID(scr_data['client_cpf'])
      respType, respArgs = insertClient(cid, {'client_cpf': scr_data['client_cpf'], 'client_name' : scr_data['client_name']})
      screenMountReturnNextStep(respType, respArgs['message'])
      break

def modifyClientScr():

  while True:

    scr_data = screenMountReturnNextStep('Client Modification', 'Here you change a client informing their data', inputLabels=['cid', 'client_name'])
    
    if(len(scr_data['client_name']) < 5):
      ret = screenMountReturnNextStep('Error', 'client_name must have at least 5 characters', options=['Insert Again','Exit'])
      if ret == 2:
        break
    
    # client modification
    else:
      respType, respArgs = modifyClient(scr_data['cid'], {'client_name': scr_data['client_name']})
      screenMountReturnNextStep(respType, respArgs['message'])
      break

def recoveryClientScr():

  scr_data = screenMountReturnNextStep('Client Recovery', 'Here you recovery a client from DB', inputLabels=['cid'])
  
  # client recovery
  respType, respArgs = recoveryClient(scr_data['cid'])
  screenMountReturnNextStep(respType, respArgs['message'])

def removeClientScr():

  scr_data = screenMountReturnNextStep('Client Remotion', 'Here you remove a client informing his cid', inputLabels=['cid'])
  
  # client remotion
  respType, respArgs = removeClient(scr_data['cid'])
  screenMountReturnNextStep(respType, respArgs['message'])

def insertProductScr():

  while True:
    
    scr_data = screenMountReturnNextStep('Product Insertion', 'Here you add a product informing its data', inputLabels=['product_name', 'product_description', 'product_quantity', 'product_price'])
      
    if(len(scr_data['product_name']) < 5):
      ret = screenMountReturnNextStep('Error', 'product_name must have at least 5 characters', options=['Try Again','Exit'])
      if ret == 2:
        break
    
    elif(len(scr_data['product_description']) < 10):
      ret = screenMountReturnNextStep('Error', 'product_description must have at least 10 characters', options=['Try Again','Exit'])
      if ret == 2:
        break
     
    elif(len(scr_data['product_quantity']) > 0 and not scr_data['product_quantity'].isdigit()):
      ret = screenMountReturnNextStep('Error', 'product_quantity must be an integer', options=['Try Again','Exit'])
      if ret == 2:
        break
    
    elif( len(scr_data['product_price']) <= 0 or not isFloat(scr_data['product_price']) ):
      ret = screenMountReturnNextStep('Error', 'product_price must be an float', options=['Try Again','Exit'])
      if ret == 2:
        break
    
    # product insertion
    else:
      pid = generatePID(scr_data['product_name'])
      
      respType, respArgs = insertProduct(pid, {
        'product_name': scr_data['product_name'], 
        'product_description': scr_data['product_description'],
        'product_quantity': scr_data['product_quantity'],
        'product_price': scr_data['product_price']
      })

      screenMountReturnNextStep(respType, respArgs['message'])
      break

def modifyProductScr():

  while True:
    
    scr_data = screenMountReturnNextStep('Product Modification', 'Here you modify a product informing its data', inputLabels=['pid', 'product_description', 'product_quantity', 'product_price'])

    if(len(scr_data['product_description']) < 10):
      ret = screenMountReturnNextStep('Error', 'product_description must have at least 10 characters', options=['Try Again','Exit'])
      if ret == 2:
        break
     
    elif(len(scr_data['product_quantity']) > 0 and not scr_data['product_quantity'].isdigit()):
      ret = screenMountReturnNextStep('Error', 'product_quantity must be an integer', options=['Try Again','Exit'])
      if ret == 2:
        break
    
    elif( len(scr_data['product_price']) <= 0 or not isFloat(scr_data['product_price']) ):
      ret = screenMountReturnNextStep('Error', 'product_price must be an float', options=['Try Again','Exit'])
      if ret == 2:
        break
    
    # product modification
    else:
      pid = scr_data['pid']
      
      respType, respArgs = modifyProduct(pid, {
        'product_description': scr_data['product_description'],
        'product_quantity': scr_data['product_quantity'],
        'product_price': scr_data['product_price']
      })

      screenMountReturnNextStep(respType, respArgs['message'])
      break

def recoveryProductScr():

  scr_data = screenMountReturnNextStep('Product Recovery', 'Here you recovery a product from DB', inputLabels=['pid'])
  
  # product recovery
  respType, respArgs = recoveryProduct(scr_data['pid'])
  screenMountReturnNextStep(respType, respArgs['message'])

def removeProductScr():

  scr_data = screenMountReturnNextStep('Product Remotion', 'Here you remove a product informing his pid', inputLabels=['pid'])
  
  # client remotion
  respType, respArgs = removeProduct(scr_data['pid'])
  screenMountReturnNextStep(respType, respArgs['message'])

### request to APIs ###

def insertClient(cid, client_data):
  global cliSocket

  cliSocket.sendRequestMessage(requestType='insertClient', requestArgs={'cid': cid, 'client_data': client_data })
  return cliSocket.waitServerResponse()

def modifyClient(cid, client_data):
  global cliSocket

  cliSocket.sendRequestMessage(requestType='modifyClient', requestArgs={'cid': cid, 'client_data': client_data })
  return cliSocket.waitServerResponse()

def recoveryClient(cid):
  global cliSocket

  cliSocket.sendRequestMessage(requestType='recoveryClient', requestArgs={'cid': cid })
  return cliSocket.waitServerResponse()

def removeClient(cid):
  global cliSocket

  cliSocket.sendRequestMessage(requestType='removeClient', requestArgs={'cid': cid})
  return cliSocket.waitServerResponse()

def insertProduct(pid, product_data):
  global cliSocket

  cliSocket.sendRequestMessage(requestType='insertProduct', requestArgs={'pid': pid, 'product_data': product_data})
  return cliSocket.waitServerResponse()

def modifyProduct(pid, product_data):
  global cliSocket

  cliSocket.sendRequestMessage(requestType='modifyProduct', requestArgs={'pid': pid, 'product_data': product_data})
  return cliSocket.waitServerResponse()

def recoveryProduct(pid):
  global cliSocket

  cliSocket.sendRequestMessage(requestType='recoveryProduct', requestArgs={'pid': pid})
  return cliSocket.waitServerResponse()

def removeProduct(pid):
  global cliSocket

  cliSocket.sendRequestMessage(requestType='removeProduct', requestArgs={'pid': pid})
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