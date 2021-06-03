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
        cur.execute('''SELECT payments.paymentNo,payments.userID,payments.bhID,payments.amount,payments.paymentDate,accounts.username
                    FROM payments INNER JOIN accounts ON payments.userID = accounts.userID
                    WHERE bhID=%s''',(bhID,))
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
    
    @classmethod
    def searchAllPayments(cls):
        cur = mysql.connection.cursor()
        cur.execute('''SELECT payments.paymentNo,payments.userID,payments.bhID,payments.amount,payments.paymentDate,profiles.firstName,profiles.lastName,boardingHouses.boardingHouseName
                    FROM payments 
                    INNER JOIN profiles ON payments.userID=profileID
                    INNER JOIN boardinghouses ON payments.bhID=boardinghouses.BHID
                            ORDER BY paymentNo''')
        data = cur.fetchall()
        if data!=None:
            cur.close()
            return data
        else:
            data = []
            cur.close()
            return data
        
    @classmethod
    def updatePayment(cls,paymentNo,amount,paymentDate):
        cur = mysql.connection.cursor()
        cur.execute("UPDATE payments SET amount=%s,paymentDate=%s WHERE paymentNo=%s",(amount,paymentDate,paymentNo))
        mysql.connection.commit()
        cur.close()
    
    @classmethod
    def deletePayment(cls,paymentNo):
        cur = mysql.connection.cursor()
        cur.execute("DELETE FROM payments WHERE paymentNo=%s",(paymentNo,))
        mysql.connection.commit()
        cur.close()
    
    
