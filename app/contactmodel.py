from app import app, mysql
import random
import smtplib
from email.message import EmailMessage
import secrets
from twilio.rest import Client



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
    
    @classmethod
    def verifyEmail(cls,userID):
        cur = mysql.connection.cursor()
        cur.execute('UPDATE contacts SET emailVerification=%s WHERE contactID=%s',("Y",userID))
        mysql.connection.commit()
        msg = 'Email successfully verified'
        return msg
    
    @classmethod
    def verifyPhoneNumber(cls,userID):
        cur = mysql.connection.cursor()
        cur.execute('UPDATE contacts SET phoneNumberVerification=%s WHERE contactID=%s',("Y",userID))
        mysql.connection.commit()
        msg = 'Phone number successfully verified'
        return msg


    @classmethod
    def emailAlert(cls,subject, body, to):
        msg = EmailMessage()
        msg.set_content(body)

        msg['subject'] = subject
        msg['to'] = to

        user = "mersanko1@gmail.com"
        msg['from'] = user
        password = "nbihpgiycoerznfg"

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(user, password)
        server.send_message(msg)
        server.quit()
        


    @classmethod
    def smsAlert(cls,msg,phoneNumber):
        locationBasesPhoneNumber = '+63'+phoneNumber[1:]
        ACCOUNT_SSID = 'AC816585e01c8d623ad0f35ebe31e6825f'
        AUTH_TOKEN = '4d0b227819cc746c0f7af999d31bb713'

        client = Client(ACCOUNT_SSID,AUTH_TOKEN )

        message = client.messages.create(
            messaging_service_sid='MG76b374860c5a03f5726a8396f7040b8d',
            body=msg,
            to=locationBasesPhoneNumber

        )
        
    @classmethod
    def emailUniquenessTest(cls,providedEmail):
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM contacts WHERE email=%s",(providedEmail,))
        data = cur.fetchall()
       
        if data==None or data==[]:
            return "Available"
        else:
            return "Taken"
    
    @classmethod
    def phoneNumberUniquenessTest(cls,providedPhoneNumber):
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM contacts WHERE phoneNumber=%s",(providedPhoneNumber,))
        data = cur.fetchall()
        if data==None or data==[]:
            return "Available"
        else:
            return "Taken"

    @classmethod
    def update2FA(cls,contactID):
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM contacts WHERE contactID=%s",(contactID,))
        data = cur.fetchone()
        if data[5]=="N":
            cur.execute("UPDATE contacts SET 2FA=%s WHERE contactID=%s",("Y",contactID))
        else:
            cur.execute("UPDATE contacts SET 2FA=%s WHERE contactID=%s",("N",contactID))
        