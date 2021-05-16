from app import app, mysql


class location():
    def __init__(self,locationID=None,street=None,barangay=None,cityOrMunicipality=None,province=None):
        self.locationID = locationID
        self.street = street
        self.barangay = barangay 
        self.cityOrMunicipality = cityOrMunicipality
        self.province = province
    
    def addLocation(self):
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO locations(locationID,street,barangay,cityOrMunicipality,province) VALUES (%s,%s,%s,%s,%s)",(self.locationID,self.street,self.barangay,self.cityOrMunicipality,self.province))
        mysql.connection.commit()
    
    
    @classmethod
    def searchAllUnitsLocation(cls):
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM locations")
        data = cur.fetchall()
        return data
        
    @classmethod
    def updateLocation(cls,locationID,street,barangay,cityOrMunicipality,province):
        cur = mysql.connection.cursor()
        cur.execute("UPDATE locations SET street=%s,barangay=%s,cityOrMunicipality=%s,province=%s WHERE locationID=%s ",(street,barangay,cityOrMunicipality,province,locationID))
        mysql.connection.commit()
        
    @classmethod
    def deleteLocation(cls,locationID):
        cur = mysql.connection.cursor()
        cur.execute("DELETE FROM locations WHERE locationID=%s",(locationID))
        mysql.connection.commit()
        
        
    