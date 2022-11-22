import database.dbSession as dbSession

class Client:
    def __init__(self, id, data):
        self.id = id
        self.data = data

def createClientDB(id, data):

    client = Client(id, data)

    sqlScrypt = 'INSERT INTO tbl_client (client_id, client_data) VALUES ' \
        ' (%s, %s); '
    
    try:
        dbSession.execute(sqlScrypt, (client.id, client.data))
        return True, 'Client created'
    
    except Exception as e:
        print(e)
        return False, 'Error ' + str(e)

def readClientDB(clientId):

    sqlScrypt = ' SELECT client_id, client_data FROM tbl_client ' \
        ' WHERE client_id = %s; '

    try:
        sqlRes = dbSession.getSingle(sqlScrypt, [(clientId)])

        if sqlRes == None or len(sqlRes) != 2:
            return False, 'Client not found'

        return True, (Client(sqlRes[0], sqlRes[1])).__dict__
    
    except Exception as e:
        return False, 'Error ' + str(e)

def updateClientDB(id, data):

    client = Client(id, data)

    sqlScrypt = ' UPDATE tbl_client SET ' \
        ' client_data = %s ' \
        ' WHERE client_id = %s; '
    
    try:
        dbSession.execute(sqlScrypt, (client.data, client.id))
        return True, 'Client updated'
    
    except Exception as e:
        return False, 'Error ' + str(e)

def deleteClientDB(clientId):

    sqlScrypt = ' DELETE FROM tbl_client ' \
        ' WHERE client_id = %s; '

    try:
        dbSession.execute(sqlScrypt, [(clientId)])
        return True, 'Client deleted'
    
    except Exception as e:
        return False, 'Error ' + str(e)