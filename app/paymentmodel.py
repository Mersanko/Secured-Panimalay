from app import app, mysql

class payment():
    def __init__(self,userID=None,bhID=None,amount=None,paymentDate=None):
        self.userID = userID    
        self.bhID = bhID 
        self.amount = amount
        self.paymentDate = paymentDate

    def addPayment(self):
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO payments(userID,bhID,amount,paymentDate) VALUES (%s,%s,%s,%s)",(self.userID,self.bhID,self.amount,self.paymentDate))
        mysql.connection.commit()
    
    @classmethod
    def paymentToBh(cls,bhID):
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM payments WHERE bhID=%s",(bhID,))
        data = cur.fetchall()
        if data!=None:
            return data
        else:
            data = []
            return data