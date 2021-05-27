from flask.globals import session
from app import app, mysql
from datetime import datetime


class log():
    def __init__(self,logDescription=None):
        self.logDescription = logDescription
    
    
    def addLogs(self):
        date = datetime.now()
        
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO logs(logDescription,logDate) VALUES (%s,%s)",(self.logDescription,date))
        mysql.connection.commit()
        cur.close()