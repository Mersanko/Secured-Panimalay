from app import app, mysql
import random

class account():
    def __init__(self, username=None, password=None, accountType=None):
        self.username = username
        self.password = password
        self.accountType = accountType

  
    def addAccount(self):
        
        cur = mysql.connection.cursor()
        # generate unique userID
        uniqueIndicator = False
        while uniqueIndicator == False:
            userID = ''.join(random.choice('0123456789ABCDEF') for i in range(16))
            cur.execute("SELECT * FROM accounts WHERE userID=%s", (userID,))
            data = cur.fetchall()
            if len(data) == 0 or data == None:
                uniqueIndicator = True

        cur.execute("INSERT INTO accounts(userID,username,password,accountType) VALUES (%s,%s,AES_ENCRYPT(%s,UNHEX(SHA2('kumsainibai',512))),%s)",
                    (userID,self.username,self.password,self.accountType))
        mysql.connection.commit()
        return userID
    
    @classmethod 
    def login(cls,usernameOrEmail,password):
        cur = mysql.connection.cursor()
        cur.execute('''SELECT * FROM (SELECT accounts.userID,accounts.username,AES_DECRYPT(accounts.password,UNHEX(SHA2('kumsainibai',512))),accounts.accountType,profiles.firstName,profiles.lastName,profiles.birthdate,profiles.gender,contacts.email,contacts.phoneNumber,contacts.emailVerification,contacts.phoneNumberVerification,contacts.2FA
                        FROM accounts, profiles, contacts
                        WHERE accounts.userID = profiles.profileID AND profiles.profileID = contacts.contactID) AS accountInfo WHERE username=%s or email=%s''',(usernameOrEmail,usernameOrEmail))
        data = cur.fetchall()
        #validate login credentials
        for i in data:
            x = i[2]
            x = x.decode('utf8')
            if (i[1]==usernameOrEmail and x==password) or (i[-1]==usernameOrEmail and x==password):
                n = len(i)
                m = 0
                accountInfo = []
                while m<n:
                    if m!=2 and m!=6:
                        accountInfo.append(i[m])
                        m+=1
                    elif m==6:
                        splitDate = str(i[6])
                        accountInfo.append(splitDate)
                        m+=1
                    else:

                        accountInfo.append(x)
                        m+=1
                return accountInfo
            else:
                msg = "Invalid login credentials"
                return msg
        cur.close()
        
    @classmethod
    def changePassword(cls,userID,oldPassword,newPassword):
        cur = mysql.connection.cursor()
        cur.execute("UPDATE accounts SET password=AES_ENCRYPT(%s,UNHEX(SHA2('kumsainibai',512))) WHERE password=AES_ENCRYPT(%s,UNHEX(SHA2('kumsainibai',512))) AND userID=%s",(newPassword,oldPassword,userID))
        mysql.connection.commit()
        cur.close()
        
    @classmethod
    def searchAllAccounts(cls):
        cur = mysql.connection.cursor()
        cur.execute("SELECT userID,username FROM accounts")
        data = cur.fetchall()
        if data!=None:
            cur.close()
            return data
        else:
            data = []
            cur.close()
            return data
        
    @classmethod
    def searchAllAccountsForAdmin(cls):
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM accounts")
        data = cur.fetchall()
        if data!=None:
            cur.close()
            return data
        else:
            data = []
            cur.close()
            return data
        
    
    @classmethod
    def usernameUniquenessTest(cls,providedUsername):
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM accounts WHERE username=%s",(providedUsername,))
        data = cur.fetchall()
       
        if data==None or data==[]:
            cur.close()
            return "Available"
        else:
            cur.close()
            return "Taken"
    
    @classmethod
    def forceChangePassword(cls,userID,password):
        cur = mysql.connection.cursor()
        cur.execute("UPDATE accounts SET  password=AES_ENCRYPT(%s,UNHEX(SHA2('kumsainibai',512))) WHERE userID=%s",(password,userID))
        mysql.connection.commit()
        
        cur.execute("SELECT * FROM accounts WHERE userID=%s",(userID,))
        data = cur.fetchall()
        cur.close()
        return data