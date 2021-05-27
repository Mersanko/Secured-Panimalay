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
        cur.close()
    
    @classmethod
    def paymentToBh(cls,bhID):
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM payments WHERE bhID=%s",(bhID,))
        data = cur.fetchall()
        if data!=None:
            cur.close()
            return data
        else:
            data = []
            cur.close()
            return data
    
    @classmethod
    def renterPayments(cls,userID):
        cur = mysql.connection.cursor()
        cur.execute('''SELECT * FROM(SELECT payments.paymentNo,payments.userID,payments.bhID,boardinghouses.boardingHouseName,payments.amount,payments.paymentDate,profiles.firstName,profiles.lastName
		    FROM payments,profiles,boardinghouses
		    WHERE payments.userID=profiles.profileID AND payments.bhID=boardinghouses.BHID) AS renterPayments
		    WHERE userID=%s''',(userID,))
        data = cur.fetchall()
        if data!=None:
            cur.close()
            return data
        else:
            data = []
            cur.close()
            return data
        