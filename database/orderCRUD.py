import database.dbSession as dbSession

class Order:
    def __init__(self, id, data):
        self.id = id
        self.data = data

def createOrderDB(id, data):

    order = Order(id, data)

    sqlScrypt = 'INSERT INTO tbl_order (order_id, order_data) VALUES ' \
        ' (%s, %s); '
    
    try:
        dbSession.execute(sqlScrypt, (order.id, order.data))
        return True, 'Order created'
    
    except Exception as e:
        return False, 'Error ' + str(e)

def readOrderDB(orderId):

    sqlScrypt = ' SELECT order_id, order_data FROM tbl_order ' \
        ' WHERE order_id = %s; '

    try:
        sqlRes = dbSession.getSingle(sqlScrypt, [(orderId)])

        if sqlRes == None or len(sqlRes) != 2:
            return False, 'Order not found'

        return True, Order(sqlRes[0], sqlRes[2])
    
    except Exception as e:
        return False, 'Error ' + str(e)

def updateOrderDB(id, data):

    order = Order(id, data)

    # not allows changing order_client_id
    sqlScrypt = ' UPDATE tbl_order SET ' \
        ' order_data = %s ' \
        ' WHERE order_id = %s; '
    
    try:
        dbSession.execute(sqlScrypt, (order.data, order.id))
        return True, 'Order updated'
    
    except Exception as e:
        return False, 'Error ' + str(e)

def deleteOrderDB(orderId):

    sqlScrypt = ' DELETE FROM tbl_order ' \
        ' WHERE order_id = %s; '

    try:
        dbSession.execute(sqlScrypt, [(orderId)])
        return True, 'Order deleted'
    
    except Exception as e:
        return False, 'Error ' + str(e)