from flask.globals import session
from app import app, mysql


class profile():
    def __init__(self, profileID=None, firstName=None, lastName=None, birthdate=None, gender=None):
        self.profileID = profileID
        self.firstName = firstName
        self.lastName = lastName
        self.birthdate = birthdate
        self.gender = gender

    def addProfile(self):
        cur = mysql.connection.cursor() 

        cur.execute("INSERT INTO profiles(profileID,firstName,lastName,birthdate,gender) VALUES (%s,%s,%s,%s,%s)",
                    (self.profileID, self.firstName,self.lastName,self.birthdate,self.gender))
        mysql.connection.commit()
    
    @classmethod 
    def updateProfile(cls,profileID,firstName,lastName,gender,birthDate):
        cur = mysql.connection.cursor()
        cur.execute("UPDATE profiles SET firstName=%s, lastName=%s, gender=%s, birthDate=%s WHERE profileID=%s",(firstName,lastName,gender,birthDate,profileID))
        mysql.connection.commit()
        msg = "Profile successfully updated."
        return msg