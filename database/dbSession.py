import mysql.connector

myDB = None
myCursor = None
defUser = 'root'
defPass = '@Pass1234'
defSchemaName = 'sd_project'
sqlFolderPath = './database/sql/'

def printLogMessage(message):
  print("database log: " + message)

# starts mysql connection instance
def dbStart():
  global myDB, myCursor, defUser, defPass, defSchemaName

  if myDB is not None:
    return
  
  myDB = mysql.connector.connect(host="localhost", user=defUser, passwd=defPass)

  if not myDB:
    printLogMessage('Connection failed')
    return

  myCursor = myDB.cursor()
  myCursor.execute('show databases')

  schemaFound = False
  for db in myCursor:
    if defSchemaName == db[0]:
      schemaFound = True
      break

  if not schemaFound:
    printLogMessage('schema ' + defSchemaName + ' not found! creating schema and tables')
    create()
  else:
    myDB = mysql.connector.connect(host='localhost', user=defUser, passwd=defPass, database=defSchemaName, auth_plugin='mysql_native_password')

  myCursor = myDB.cursor()
  
  printLogMessage('Connection to ' + defSchemaName + ' successfull!')

# automatic create tables in defSchemaName schema
def create():
  global myDB, myCursor, defUser, defPass, defSchemaName

  if myDB is None:
    printLogMessage('Error, database connection not established')
    return

  myCursor = myDB.cursor()
  myCursor.execute('create schema ' + defSchemaName)

  myDB = mysql.connector.connect(host='localhost', user=defUser, passwd=defPass, database=defSchemaName)
  myCursor = myDB.cursor()

  myCursor.execute(getSqlScrypt('tbl_client'))
  myCursor.execute(getSqlScrypt('tbl_product'))
  myCursor.execute(getSqlScrypt('tbl_order'))

# get saved .sql scrypt
def getSqlScrypt(name):

  textFile = open(sqlFolderPath + name + '.sql', 'r')
  strFile = textFile.read()
  textFile.close()

  return strFile

# transaction rollback
def rollback():
  global myDB, myCursor

  if myDB is None or myCursor is None:
    printLogMessage('Error, database connection not established')
    return
  
  myDB.rollback()

# transaction commit
def commit():
  global myDB, myCursor

  if myDB is None or myCursor is None:
    printLogMessage('Error, database connection not established')
    return
  
  myDB.commit()

# execute sql scrypt, autocommit is enabled by default
def execute(sqlScrypt, values=None, commit=True):
  global myDB, myCursor

  if myDB is None or myCursor is None:
    printLogMessage('Error, database connection not established')
    return
      
  if values != None:
    myCursor.execute(sqlScrypt, values)
  else:
    myCursor.execute(sqlScrypt)
  
  if(commit):
    myDB.commit()

# get single data, use only to read
def getSingle(sqlScrypt, values=None):
  global myDB, myCursor

  if myDB is None or myCursor is None:
    printLogMessage('Error, database connection not established')
    return
  
  if values != None:
    myCursor.execute(sqlScrypt, values)
  else:
    myCursor.execute(sqlScrypt)

  return myCursor.fetchone()

# get multiple data, use only to read
def getAll(sqlScrypt, values=None):
  global myDB, myCursor

  if myDB is None or myCursor is None:
    printLogMessage('Error, database connection not established')
    return
  
  if values != None:
    myCursor.execute(sqlScrypt, values)
  else:
    myCursor.execute(sqlScrypt)

  return myCursor.fetchall()