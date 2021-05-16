from app import app, mysql
import random


class unit():
    def __init__(self,bhID=None,priceRent=None,numOfOccupants=None,genderAccommodation=None):
        self.bhID = bhID
        self.numOfOccupants = numOfOccupants
        self.priceRent = priceRent
        self.genderAccommodation = genderAccommodation
    
    def addUnit(self):
        cur =  mysql.connection.cursor()
        uniqueIndicator = False
        while uniqueIndicator == False:
            unitID = ''.join(random.choice('0123456789ABCDEF') for i in range(10))
            cur.execute("SELECT * FROM units WHERE unitID=%s", (unitID,))
            data = cur.fetchall()
            if len(data) == 0 or data == None:
                uniqueIndicator = True
                
        cur.execute("INSERT INTO units(unitID,BHID,rent,numOfOccupants,genderAccommodation) VALUES (%s,%s,%s,%s,%s)",(unitID,self.bhID,self.priceRent,self.numOfOccupants,self.genderAccommodation))
        mysql.connection.commit()
        return unitID
    
    @classmethod
    def searchOwnedUnits(self,bhID):
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM units WHERE bhID=%s ORDER BY unitNo",(bhID,))
        units = cur.fetchall()
        return units
    
    @classmethod
    def updateUnit(cls,unitID,rent,numOfOccupants,genderAccommodation):
        cur = mysql.connection.cursor()
        cur.execute("UPDATE units SET rent=%s,numOfOccupants=%s,genderAccommodation=%s WHERE unitID=%s",(rent,numOfOccupants,genderAccommodation,unitID))
        mysql.connection.commit()
        msg = "Record was successfully updated"
        return msg 
    
    @classmethod
    def deleteUnit(cls,unitID):
        cur = mysql.connection.cursor()
        cur.execute("DELETE FROM units WHERE unitID=%s",(unitID,))
        mysql.connection.commit()
        msg = "Record was successfully deleted"
        return msg 

    @classmethod
    def searchUnit(cls,bhID,searchInput):
        searchInput = '%'+searchInput+'%'
        cur = mysql.connection.cursor()
        cur.execute('''SELECT * FROM (SELECT * FROM units WHERE bhID=%s) as ownedUnits WHERE unitID LIKE %s or rent LIKE %s 
                    or numOfOccupants LIKE %s or genderAccommodation LIKE %s'''
                    ,(bhID,searchInput,searchInput,searchInput,searchInput))
        data = cur.fetchall()
        return data
    