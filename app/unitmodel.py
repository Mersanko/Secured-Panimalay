from app import app, mysql
import random


class unit():
    def __init__(self,
                 bhID=None,
                 priceRent=None,
                 numOfOccupants=None,
                 genderAccommodation=None):
        self.bhID = bhID
        self.numOfOccupants = numOfOccupants
        self.priceRent = priceRent
        self.genderAccommodation = genderAccommodation

    def addUnit(self):
        cur = mysql.connection.cursor()
        uniqueIndicator = False
        while uniqueIndicator == False:
            unitID = ''.join(
                random.choice('0123456789ABCDEF') for i in range(10))
            cur.execute("SELECT * FROM units WHERE unitID=%s", (unitID, ))
            data = cur.fetchall()
            if len(data) == 0 or data == None:
                uniqueIndicator = True

        cur.execute(
            "INSERT INTO units(unitID,BHID,rent,numOfOccupants,genderAccommodation) VALUES (%s,%s,%s,%s,%s)",
            (unitID, self.bhID, self.priceRent, self.numOfOccupants,
             self.genderAccommodation))
        mysql.connection.commit()
        cur.close()
        return unitID

    @classmethod
    def searchOwnedUnits(self, bhID):
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM units WHERE bhID=%s ORDER BY unitNo",
                    (bhID, ))
        units = cur.fetchall()
        cur.close()
        return units

    @classmethod
    def updateUnit(cls, unitID, rent, numOfOccupants, genderAccommodation):
        cur = mysql.connection.cursor()
        cur.execute(
            "UPDATE units SET rent=%s,numOfOccupants=%s,genderAccommodation=%s WHERE unitID=%s",
            (rent, numOfOccupants, genderAccommodation, unitID))
        mysql.connection.commit()
        msg = "Record was successfully updated"
        cur.close()
        return msg

    @classmethod
    def deleteUnit(cls, unitID):
        cur = mysql.connection.cursor()
        cur.execute("DELETE FROM units WHERE unitID=%s", (unitID, ))
        mysql.connection.commit()
        msg = "Record was successfully deleted"
        cur.close()
        return msg

    @classmethod
    def searchUnit(cls, bhID, searchInput):
        searchInput = '%' + searchInput + '%'
        cur = mysql.connection.cursor()
        cur.execute(
            '''SELECT * FROM (SELECT * FROM units WHERE bhID=%s) as ownedUnits WHERE unitID LIKE %s or rent LIKE %s 
                    or numOfOccupants LIKE %s or genderAccommodation LIKE %s''',
            (bhID, searchInput, searchInput, searchInput, searchInput))
        data = cur.fetchall()
        cur.close()
        return data

    @classmethod
    def searchResult(cls, location, rent, capacity, genderAccommodation):
        inputLocation = '%' + location + '%'

        cur = mysql.connection.cursor()

        cur.execute(
            '''SELECT * FROM (SELECT units.unitNo, units.unitID, units.BHID , units.rent,units.numOfOccupants,units.genderAccommodation,boardinghouses.ownersID,boardinghouses.boardingHouseName,locations.street,locations.barangay,locations.cityOrMunicipality,locations.province
                        FROM units, locations, boardingHouses
                        WHERE units.unitID = locations.locationID AND units.BHID = boardinghouses.BHID) AS unitsInfo 
                        WHERE (street LIKE %s or barangay LIKE %s or cityOrMunicipality  LIKE %s or province LIKE %s) or rent=%s and numOfOccupants=%s and genderAccommodation=%s''',
            (inputLocation, inputLocation, inputLocation, inputLocation, rent,
             capacity, genderAccommodation))
        data = cur.fetchall()
        cur.close()
        return data

    @classmethod
    def searchAllUnits(cls):
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM units")
        data = cur.fetchall()
        cur.close()
        return data

    @classmethod
    def unitsInfo(cls, unitID):
        cur = mysql.connection.cursor()
        cur.execute(
            '''SELECT units.unitNo, units.unitID, units.BHID , units.rent,units.numOfOccupants,units.genderAccommodation,boardinghouses.ownersID,boardinghouses.boardingHouseName,locations.street,locations.barangay,locations.cityOrMunicipality,locations.province,accounts.username,profiles.firstName,profiles.lastName,contacts.email,contacts.phoneNumber
                        FROM (((((units
                        INNER JOIN locations ON units.unitID = locations.locationID)
                        INNER JOIN boardinghouses ON units.BHID = boardinghouses.BHID)
                        INNER JOIN accounts ON boardinghouses.ownersID = accounts.userID)
                        INNER JOIN profiles ON profiles.profileID = accounts.userID)
                        INNER JOIN contacts ON contacts.contactID = profiles.profileID)
								WHERE units.unitID = %s''', (unitID, ))
        data = cur.fetchone()
        cur.close()
        return data
    
    @classmethod
    def rentedUnitInfo(cls, unitID):
        cur = mysql.connection.cursor()
        cur.execute('''SELECT units.unitNo, units.unitID, units.BHID , units.rent,units.numOfOccupants,units.genderAccommodation,boardinghouses.ownersID,boardinghouses.boardingHouseName,locations.street,locations.barangay,locations.cityOrMunicipality,locations.province,accounts.username,profiles.firstName,profiles.lastName,contacts.email,contacts.phoneNumber
                        FROM (((((units
                        INNER JOIN locations ON units.unitID = locations.locationID)
                        INNER JOIN boardinghouses ON units.BHID = boardinghouses.BHID)
                        INNER JOIN accounts ON boardinghouses.ownersID = accounts.userID)
                        INNER JOIN profiles ON profiles.profileID = accounts.userID)
                        INNER JOIN contacts ON contacts.contactID = profiles.profileID)
								WHERE units.unitID =%s''', (unitID,))
        data = cur.fetchone()
        cur.close()
        return data
    
    @classmethod
    def rentedUnit(cls,userID):
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM renter WHERE userID=%s AND status!=%s",(userID,"L"))
        data = cur.fetchall()
        cur.close()
        return data