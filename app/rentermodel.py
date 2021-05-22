from flask.globals import session
from mysql.connector import connect
from app import app, mysql

class renter():
    def __init__(self,userID=None,unitID=None,dateStarted=None):
        self.userID = userID
        self.unitID = unitID
        self.dateStarted = dateStarted
    
    
    
    def addRenter(self):
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO renter(userID,unitID,dateStarted) VALUES (%s,%s,%s)",(self.userID,self.unitID,self.dateStarted))
        mysql.connection.commit()
    
    @classmethod
    def requestRenterLeave(cls,userID,unitID):
        cur = mysql.connection.cursor()
        cur.execute("UPDATE renter SET status=%s WHERE userID=%s AND unitID=%s AND status=%s",("RL",userID,unitID,"S"))
        mysql.connection.commit()
    
    @classmethod
    def cancelOrDeclineRenterLeave(cls,userID,unitID):
        cur = mysql.connection.cursor()
        cur.execute("UPDATE renter SET status=%s WHERE userID=%s and unitID=%s",("S",userID,unitID))
        mysql.connection.commit()
        
    @classmethod
    def confirmRenterLeave(cls,userID):
        cur = mysql.connection.cursor()
        cur.execute("UPDATE renter SET status=%s WHERE userID=%s",("L",userID))
        mysql.connection.commit()
        
    
    @classmethod
    def tenantsList(cls):
        userID = session['accountInfo'][0]
        cur = mysql.connection.cursor()
        cur.execute('''SELECT * FROM (SELECT units.unitNo, units.unitID, units.BHID , units.rent,units.numOfOccupants,units.genderAccommodation,boardinghouses.ownersID,boardinghouses.boardingHouseName,renter.userID,renter.dateStarted,renter.dateEnded,renter.status,accounts.username,profiles.firstName,profiles.lastName,profiles.gender,contacts.email,contacts.phoneNumber
                        FROM units,boardinghouses,renter,accounts,profiles,contacts
                        WHERE units.BHID = boardinghouses.BHID AND renter.unitID=units.unitID AND renter.userID=accounts.userID AND accounts.userID=profiles.profileID AND contacts.contactID=profiles.profileID) AS unitInfo
								WHERE ownersID=%s AND (status=%s OR status=%s)''',(userID,"S","RL"))
        data = cur.fetchall()
        return data
    
    @classmethod
    def leaveRequestList(cls):
        userID = session['accountInfo'][0]
        cur = mysql.connection.cursor()
        cur.execute('''SELECT * FROM (SELECT units.unitNo, units.unitID, units.BHID , units.rent,units.numOfOccupants,units.genderAccommodation,boardinghouses.ownersID,boardinghouses.boardingHouseName,renter.userID,renter.dateStarted,renter.dateEnded,renter.status
                        FROM units, boardinghouses,renter
                        WHERE units.BHID = boardinghouses.BHID AND renter.unitID=units.unitID ) AS unitInfo
								WHERE ownersID=%s AND status=%s''',(userID,"RL"))
        data = cur.fetchall()
        return data