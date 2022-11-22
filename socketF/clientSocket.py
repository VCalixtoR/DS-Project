from configparser import ConfigParser
import json
import socket
import os

config_obj = ConfigParser()
config_obj.read(os.path.abspath('config.ini'))

defIpv4 = str(config_obj['admin_socket']['ipv4'])
defBlockSize = 32

class ClientSocket:

  def __init__(self, socketPort, logStartStr=''):
    global defIpv4

    self.logStartStr = logStartStr
    
    # socket object with ipv4 hosts and tcp protocol
    self.tcpSocketCli = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    self.printLogMessage('Trying connection to server ' + defIpv4 + ':' + str(socketPort))
    try:
      self.tcpSocketCli.connect((defIpv4, socketPort))
    except:
      self.printLogMessage('Connection to server failed please make sure that server is started')
      exit()
    self.printLogMessage('Connection to server done')

  def printLogMessage(self, message):
    print(self.logStartStr + message)

  def sendRequestMessage(self, requestType, requestArgs=None):
    global defBlockSize

    message = self.createRequestMessage(requestType, requestArgs)
    
    # sends message
    self.tcpSocketCli.send(bytes(message, 'utf-8'))

  def createRequestMessage(self, requestType, requestArgs=None):

    if requestArgs:
      if not isinstance(requestArgs, dict):
        self.printLogMessage('requestArgs must be a dict with key value pairs')
        return

    # create string args
    strArgs = ''
    
    keys = list(requestArgs.keys())
    for keyIndex in range(len(keys)):

      key = keys[keyIndex]
      if type(requestArgs[key]) == dict:
        strArgs = strArgs + str(key) + '=' + json.dumps(requestArgs[key])
      else:
        strArgs = strArgs + str(key) + '=' + str(requestArgs[key])

      if keyIndex+1 < len(keys):
        strArgs = strArgs + '&'
    
    # grants that strArgs has not partial blocks
    if(len(strArgs)%defBlockSize != 0):
      strArgs = strArgs + (defBlockSize-len(strArgs)%defBlockSize) * ' '
    
    # create header
    msgLen = len(strArgs)
    header = requestType + ':' + str(msgLen)

    if(len(header)>defBlockSize):
      self.printLogMessage('Header size error')
      return

    header = header + ' ' * (defBlockSize-len(header))

    # create request message
    message = header + strArgs
    return message

  def waitServerResponse(self):

    respMsg = ''
    respMsgHeader = None
    respMsgType = None
    respMsgSize = None

    while True:

      tmp = self.tcpSocketCli.recv(defBlockSize).decode('utf-8')

      # message response receiving
      if tmp:

        # creating the response, starts by header
        if not respMsgHeader:
          respMsgHeader = tmp
          respMsgType = respMsgHeader.split(':')[0]
          respMsgSize = int(respMsgHeader.split(':')[1])
        
        # concatenates tmp in respMsg until respMsg is complete
        elif len(respMsg) < respMsgSize:
          respMsg = respMsg + tmp

        # response message received, begin response making
        if len(respMsg) == respMsgSize:

          self.printLogMessage(respMsgType + ' response received')

          # process args keys and values
          respArgs = dict()
          if len(respMsg) > 0:
            respKeyValues = respMsg.split('&')
            
            for keyValue in respKeyValues:
              splitKV = keyValue.split('=')
              respArgs[splitKV[0]] = splitKV[1].rstrip()
          
          return respMsgType, respArgs