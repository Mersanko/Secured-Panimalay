from app import app, mysql
import random


class contact():
    def __init__(self,contactID=None,email=None,phoneNumber=None):
        self.contactID= contactID
        self.email = email
        self.phoneNumber = phoneNumber
        
    def addContacts(self):
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO contacts(contactID,email,phoneNumber) VALUES (%s,%s,%s)",(self.contactID,self.email,self.phoneNumber))
        mysql.connection.commit()
    
    @classmethod
    def updateContact(cls,contactID,phoneNo,email):
        cur = mysql.connection.cursor()
        cur.execute('UPDATE contacts SET phoneNumber=%s,email=%s WHERE contactID=%s',(phoneNo,email,contactID))
        mysql.connection.commit()
        msg = 'Contact successfully updated'
        return msg