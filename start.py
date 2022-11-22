from adminF.adminApp import admAppStart
from adminF.adminPortal import admPortalStart
from clientF.clientApp import cliAppStart
from clientF.clientPortal import cliPortalStart
import sys

appChoosen = None
socketPort = None

# -app [0: adminApp, 1: adminPortal, 2: clientApp , 3: clientPortal] -socketPort [ port ] #

try:

  if(sys.argv[1] != '-app'):
    raise Exception()
  
  if(not sys.argv[2].isdigit() or int(sys.argv[2]) < 0 or int(sys.argv[2]) > 3):
    raise Exception()

  if(sys.argv[3] != '-socketPort'):
    raise Exception()
  
  if(not sys.argv[4].isdigit()):
    raise Exception()

  appChoosen = int(sys.argv[2])
  socketPort = int(sys.argv[4])

except Exception as e:
  print('Error in command line arguments: the 2 key value args must be given in this order:\n' \
    ' -app [0: adminApp, 1: adminPortal, 2: clientApp , 3: clientPortal] -socketPort port ')
  input()
  quit()

match appChoosen:
  case 0:
    admAppStart(socketPort)
  case 1:
    admPortalStart(socketPort)
  case 2:
    cliAppStart(socketPort)
  case 3:
    cliPortalStart(socketPort)