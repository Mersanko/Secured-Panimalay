from app import app, mysql
import random

class boardingHouse():
    def __init__(self,ownersID=None, boardingHouseName=None):
        self.ownersID = ownersID
        self.boardingHouseName = boardingHouseName
    
    def addBoardingHouse(self):
        cur =  mysql.connection.cursor()
        uniqueIndicator = False
        while uniqueIndicator == False:
            bhID = ''.join(random.choice('0123456789ABCDEF') for i in range(8))
            cur.execute("SELECT * FROM boardingHouses WHERE BHID=%s", (bhID,))
            data = cur.fetchall()
            if len(data) == 0 or data == None:
                uniqueIndicator = True
                
        cur.execute("INSERT INTO boardinghouses(BHID,ownersID,boardingHouseName) VALUES (%s,%s,%s)",(bhID,self.ownersID,self.boardingHouseName))
        mysql.connection.commit()
        cur.close()

    @classmethod
    def searchBoardingHouse(cls,userID):
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM boardingHouses WHERE ownersID=%s",(userID,))
        bh = cur.fetchone()
        cur.close()
        return bh
    
    @classmethod
    def changeBoardingHouseName(cls,userID,bhName):
        cur = mysql.connection.cursor()
        cur.execute("UPDATE boardingHouses SET boardingHouseName=%s WHERE ownersID=%s",(bhName,userID))
        mysql.connection.commit()
        cur.close()
   
   
        