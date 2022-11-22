from configparser import ConfigParser
import json
import paho.mqtt.client as mqtt
import os

config_obj = ConfigParser()
config_obj.read(os.path.abspath('config.ini'))

defBrokerHost = str(config_obj['mqtt']['host'])
defBrokerPort = int(config_obj['mqtt']['port'])

class adminMQTT:

    ### Constructor ###

    def __init__(self, callbackUpdateCache, logEnabled = False):
        global defBrokerHost, defBrokerPort

        self.callbackUpdateCache = callbackUpdateCache
        self.logEnabled = logEnabled
        
        # Connect an instance to broker and handle messages callbacks
        self.client = mqtt.Client()
        self.client.on_message = self.adminMessageCallback
        if self.logEnabled:
            self.client.on_log = self.adminLogCallback

        self.printLogMessage('Trying to connect to broker')
        self.client.connect(host=defBrokerHost, port=defBrokerPort)
        self.printLogMessage('Connected to ' + defBrokerHost + ':' + str(defBrokerPort))

        self.client.loop_start()

        # subscribes
        self.subscribeClients()
        self.subscribeProducts()
        self.subscribeOrders()
        self.subscribeClientOrders()

        #time.sleep(100)
        #self.client.loop_stop()
    
    ### ###

    ### callbacks and utilities ###

    def adminLogCallback(self, client, userdata, level, buf):
        self.printLogMessage(buf)
    
    def printLogMessage(self, message):
        print("adm MQTT log: " + message)

    def adminMessageCallback(self, client, userdata, message):

        if message.topic == 'tblCID':
            self.clientsCallback(message.payload.decode("utf-8"))
        
        elif message.topic == 'tblPID':
            self.productsCallback(message.payload.decode("utf-8"))

        elif message.topic == 'tblOID':
            self.ordersCallBack(message.payload.decode("utf-8"))
        
        elif message.topic == 'tblCIDOID':
            self.clientOrdersCallBack(message.payload.decode("utf-8"))
    
    ### ###

    ### sub callbacks ###

    def clientsCallback(self, strTblCID):

        tblCID = None

        try:
            tblCID = json.loads(strTblCID)
        except Exception as e:
            self.printLogMessage("Error, invalid client data type published: " + str(e))
            return
        
        self.callbackUpdateCache(clientsCacheT = tblCID)
    
    def productsCallback(self, strTblPID):

        tblPID = None

        try:
            tblPID = json.loads(strTblPID)
        except Exception as e:
            self.printLogMessage("Error, invalid table PID data type published: " + str(e))
            return
        
        self.callbackUpdateCache(productsCacheT = tblPID)
    
    def ordersCallBack(self, strTblOID):

        tblOID = None

        try:
            tblOID = json.loads(strTblOID)
        except Exception as e:
            self.printLogMessage("Error, invalid table OID data type published: " + str(e))
            return
        
        self.callbackUpdateCache(ordersCacheT = tblOID)
    
    def clientOrdersCallBack(self, strTblCIDOID):

        tblCIDOID = None

        try:
            tblCIDOID = json.loads(strTblCIDOID)
        except Exception as e:
            self.printLogMessage("Error, invalid table CIDOID data type published: " + str(e))
            return
        
        self.callbackUpdateCache(clientOrdersCacheT = tblCIDOID)
    
    ### ###

    ### publish ###

    def publishClients(self, tblCID):

        if not isinstance(tblCID, dict):
            self.printLogMessage("Error, table CID must be a dict hash table")
            return

        try:
            self.client.publish("tblCID", json.dumps(tblCID), retain=True)
        except:
            self.printLogMessage('Error trying to publish tblCID')

    def publishProducts(self, tblPID):

        if not isinstance(tblPID, dict):
            self.printLogMessage("Error, table PID must be a dict hash table")
            return
        
        try:
            self.client.publish("tblPID", json.dumps(tblPID), retain=True)
        except:
            self.printLogMessage('Error trying to publish tblPID')
    
    ### ###

    ### subscribe ###

    def subscribeClients(self):
        self.client.subscribe("tblCID")

    def subscribeProducts(self):
        self.client.subscribe("tblPID")

    def subscribeOrders(self):
        self.client.subscribe("tblOID")
    
    def subscribeClientOrders(self):
        self.client.subscribe("tblCIDOID")
    
    ### ###