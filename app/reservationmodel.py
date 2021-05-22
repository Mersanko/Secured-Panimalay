from flask.globals import session
from app import app, mysql
from datetime import datetime

class reservation():
    def __init__(self, userID=None, unitID=None, reservationDate=None):
        self.userID = userID
        self.unitID = unitID
        self.reservationDate = reservationDate

    def addReservation(self):
        cur = mysql.connection.cursor(buffered=True)
        cur.execute(
            "INSERT INTO reservations(userID,unitID,reservationDate) VALUES (%s,%s,%s)",
            (self.userID, self.unitID, self.reservationDate))
        
        mysql.connection.commit()

    @classmethod
    def searchReservation(cls, userID):
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM reservations WHERE userID=%s", (userID, ))
        data = cur.fetchone()
        return data

    @classmethod
    def acceptReservation(cls, reservationNo):
        cur = mysql.connection.cursor()
        cur.execute("UPDATE reservations SET status=%s WHERE reservationNo=%s",
                    ("A", reservationNo))
        mysql.connection.commit()
        
    @classmethod
    def declineReservation(cls, userID):
        cur = mysql.connection.cursor()
        cur.execute("UPDATE reservations SET status=%s WHERE userID=%s",
                    ("D", userID))
        mysql.connection.commit()
    
         
    @classmethod
    def deleteReservation(cls, reservationNo):
        cur = mysql.connection.cursor()
        cur.execute("DELETE FROM reservations WHERE reservationNo=%s",
                    (reservationNo,))
        mysql.connection.commit()

    @classmethod
    def cancelReservation(cls, reservationNo):
        cur = mysql.connection.cursor()
        cur.execute("DELETE FROM reservations WHERE reservationNo=%s",
                    (reservationNo,))
        mysql.connection.commit()

    @classmethod
    def checkActiveReservation(cls,userID):
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM reservations WHERE userID=%s", (userID, ))
        data = cur.fetchone()
        
        return data
       
    @classmethod
    def pendingReservation(cls,userID):
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM reservations WHERE userID=%s and status=%s",(userID,"P"))
        data = cur.fetchone()
        return data 


    @classmethod
    def ownerReservationData(cls,ownersID):
        cur = mysql.connection.cursor()
        cur.execute('''SELECT * FROM (SELECT units.unitNo, units.unitID, units.BHID , units.rent,units.numOfOccupants,units.genderAccommodation,boardinghouses.ownersID,boardinghouses.boardingHouseName,reservations.reservationNo,accounts.username,reservations.userID,reservations.reservationDate,reservations.status
                        FROM units, boardinghouses,reservations,accounts
                        WHERE units.BHID = boardinghouses.BHID AND reservations.unitID=units.unitID AND accounts.userID = reservations.userID) AS unitInfo
								WHERE ownersID=%s AND status=%s''',(ownersID,"P"))
        data = cur.fetchall()
        return data
        