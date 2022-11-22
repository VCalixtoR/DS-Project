import database.dbSession as dbSession

class Product:
    def __init__(self, id, data):
        self.id = id
        self.data = data

def createProductDB(id, data):

    prod = Product(id, data)

    sqlScrypt = 'INSERT INTO tbl_product (product_id, product_data) VALUES ' \
        ' (%s, %s); '
    
    try:
        dbSession.execute(sqlScrypt, (prod.id, prod.data))
        return True, 'Product created'
    
    except Exception as e:
        return False, 'Error ' + str(e)

def readProductDB(prodId):

    sqlScrypt = ' SELECT product_id, product_data FROM tbl_product ' \
        ' WHERE product_id = %s; '

    try:
        sqlRes = dbSession.getSingle(sqlScrypt, [(prodId)])

        if sqlRes == None or len(sqlRes) != 2:
            return False, 'Product not found'

        return True, Product(sqlRes[0], sqlRes[1]).__dict__
    
    except Exception as e:
        return False, 'Error ' + str(e)

def updateProductDB(id, data):

    prod = Product(id, data)

    sqlScrypt = ' UPDATE tbl_product SET ' \
        ' product_data = %s ' \
        ' WHERE product_id = %s; '
    
    try:
        dbSession.execute(sqlScrypt, (prod.data, prod.id))
        return True, 'Product updated'
    
    except Exception as e:
        return False, 'Error ' + str(e)

def deleteProductDB(prodId):

    sqlScrypt = ' DELETE FROM tbl_product ' \
        ' WHERE product_id = %s; '

    try:
        dbSession.execute(sqlScrypt, [(prodId)])
        return True, 'Product deleted'
    
    except Exception as e:
        return False, 'Error ' + str(e)