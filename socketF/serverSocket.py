from configparser import ConfigParser
import socket
import os

config_obj = ConfigParser()
config_obj.read(os.path.abspath('config.ini'))

defIpv4 = str(config_obj['admin_socket']['ipv4'])
defBlockSize = 32

class ServerSocket:

  ### socket configuration ###

  def __init__(self, socketPort, socketAPICallback, logStartStr=''):
    global defIpv4, defBlockSize

    self.logStartStr = str(logStartStr)
    self.socketAPICallback = socketAPICallback
    
    # socket object with ipv4 hosts and tcp protocol
    tcpSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcpSocket.bind((defIpv4, socketPort))
    self.printLogMessage('TCP Socket ' + defIpv4 + ':' + str(socketPort) + ' created')
    # 1 to 1 communication
    tcpSocket.listen(1)

    self.printLogMessage('Trying connection to client')
    self.appSocket, self.appAdress = tcpSocket.accept()
    self.printLogMessage('Connection with ' + str(self.appAdress) + ' done')

  def printLogMessage(self, message):
    print(self.logStartStr + message)

  def processClientRequests(self):

    reqMsg = ''
    reqMsgHeader = None
    reqMsgType = None
    reqMsgSize = None

    self.printLogMessage('listening to client requests')

    while True:
      
      tmp = self.appSocket.recv(defBlockSize).decode('utf-8')

      # message request receiving
      if tmp:

        # starting new request, starts by header
        if not reqMsgHeader:
          reqMsgHeader = tmp
          reqMsgType = reqMsgHeader.split(':')[0]
          reqMsgSize = int(reqMsgHeader.split(':')[1])
        
        # concatenates tmp in reqMsg until reqMsg is complete
        elif len(reqMsg) < reqMsgSize:
          reqMsg = reqMsg + tmp

        # request message received, begin response making
        if len(reqMsg) == reqMsgSize:

          self.printLogMessage(reqMsgType + ' request received')

          # process args keys and values
          reqArgs = dict()
          if len(reqMsg) > 0:
            reqKeyValues = reqMsg.split('&')
            
            for keyValue in reqKeyValues:
              splitKV = keyValue.split('=')
              reqArgs[splitKV[0]] = splitKV[1].rstrip()
          
          self.socketAPICallback(reqMsgType, reqArgs)

          reqMsg = ''
          reqMsgHeader = None
          reqMsgType = None
          reqMsgSize = None

  def sendClientResponse(self, responseStatus, responseArgs=None):
    global defBlockSize

    if responseArgs:
      if not isinstance(responseArgs, dict):
        self.printLogMessage('responseArgs must be a dict with key value pairs')
        return

    # create string args
    strArgs = ''
    
    keys = list(responseArgs.keys())
    for keyIndex in range(len(keys)):

      key = keys[keyIndex]
      strArgs = strArgs + str(key) + '=' + responseArgs[key]

      if keyIndex+1 < len(keys):
        strArgs = strArgs + '&'

    # grants that strArgs has no partial blocks
    strArgs = strArgs + (' ' * (defBlockSize-len(strArgs)%defBlockSize))

    # create header
    respLen = len(strArgs)
    header = str(responseStatus) + ':' + str(respLen)

    if(len(header)>defBlockSize):
      self.printLogMessage('Header size error')
      return
    
    # set header to one block size
    header = header + ' ' * (defBlockSize-len(header))

    # creates message
    response = header + strArgs
    
    self.appSocket.send(bytes(response, 'utf-8'))

### ###