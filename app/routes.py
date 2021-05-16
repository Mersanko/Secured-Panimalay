from flask import Flask, flash, render_template, redirect, request, url_for, session
from datetime import datetime
from app import app
import app.accountmodel as accounts
import app.profilemodel as profiles
import app.contactmodel as contacts
import app.boardinghousemodel as boardingHouses
import app.unitmodel as units
import app.locationmodel as locations
import app.paymentmodel as payments

@app.route('/')
@app.route('/home')
def home():
    return render_template('adminlogin.html')

@app.route('/create/account', methods=['POST'])
def createAccount():
    if request.method == "POST":
        # info needed in account table
        username = request.form.get('reg-username')
        password = request.form.get('reg-password')
        accountType = request.form.get('reg-accountType')

        # info needed in profile tables
        firstName = request.form.get('reg-fn')
        lastName = request.form.get('reg-ln')
        gender = request.form.get('reg-gender')
        birthdate = request.form.get('reg-birthdate')
        
        #info needed in contact tables
        email = request.form.get('reg-email')
        phoneNumber = request.form.get('reg-phone')

        # initialize account,profile , and contacts for a user
        userAccount = accounts.account(username, password, accountType)
        userID = userAccount.addAccount()
        
        userProfile = profiles.profile(userID, firstName, lastName, birthdate, gender)
        userProfile.addProfile()
        
        userContact = contacts.contact(userID,email,phoneNumber)
        userContact.addContacts()

        # if account type is owner add boarding house
        if accountType=="O":
            boardingHousesName = firstName + "'s " + "Boarding House"
            boardingHouse = boardingHouses.boardingHouse(userID,boardingHousesName)
            boardingHouse.addBoardingHouse()
           
        
    return '<h1>Account Already Created</h1>'


@app.route('/signin')
def signin():
    return render_template('signin.html')

@app.route('/login',methods=["POST","GET"])
def login():               
    if request.method == "POST":
        #get username/email and password
        usernameOrEmail = request.form.get('usernameOrEmail')
        password = request.form.get('password')
        
        verification = accounts.account()
        verificationResult = verification.login(usernameOrEmail,password)
        
        if verificationResult == "Invalid login credentials":
            return redirect(url_for('signin',usernameInput = usernameOrEmail,passwordInput = password))
        else:
            session['accountInfo'] = verificationResult
            return redirect(url_for('dashboard',accountInfo=session['accountInfo']))

@app.route('/dashboard')
def dashboard():
    if session['accountInfo'][3] =='O':
        return render_template('ownerdashboard.html')

@app.route('/logout')
def logout():
    session.clear()
    return '<h1>You already logout</h1>'

@app.route('/signin/OTP')
def OTP():
    return render_template('OTP.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/manage/units')
def manageUnits():
    userID = session['accountInfo'][0]
    accountType = session['accountInfo'][3]
    if accountType=="O":
        bh = boardingHouses.boardingHouse()
        bhData = bh.searchBoardingHouse(userID)
        unit = units.unit()
        session['bhID'] = bhData[0]
        ownedUnits = unit.searchOwnedUnits(bhData[0])
    
        unitsLocations = locations.location()
        unitsLocations = unitsLocations.searchAllUnitsLocation()
        
    
        return render_template('ownermanageunit.html',bhData=bhData,userID=userID,ownedUnits=ownedUnits,unitsLocations=unitsLocations)
    
@app.route('/manage/units/change/boarding/house/name',methods=["POST"])
def changeBoardingHouseName():
    if request.method == "POST":
        newBoardingHouseName  = request.form.get('bhName')
        userID = request.form.get('userID')
        bh = boardingHouses.boardingHouse()
        bh.changeBoardingHouseName(userID,newBoardingHouseName)
    return redirect(url_for('manageUnits',userID=userID))

@app.route('/add/unit',methods=["POST"])
def addUnits():
    if request.method== "POST": 
        userID = request.form.get('userID')
        bhID = session['bhID']
        numOfOccupants = request.form.get("num-occupants")
        priceRent = request.form.get("price-rent")
        genderAccommodation = request.form.get("gender-acco")
        street = request.form.get('street')
        barangay = request.form.get('barangay')
        cityOrMunicipality = request.form.get('cityOrMunicipality')
        province = request.form.get('province')
        
        #initialized unit 
        unit = units.unit(bhID,priceRent,numOfOccupants,genderAccommodation)
        locationID = unit.addUnit()
        
        #initialized unit location
        unitLocation = locations.location(locationID,street,barangay,cityOrMunicipality,province)
        unitLocation.addLocation()
        
    return redirect(url_for('manageUnits'))

        
@app.route('/update/unit/<string:unitID>',methods=["POST"])
def updateUnits(unitID):
    if request.method=="POST":
        userID = request.form.get('userID')
        numOfOccupants = request.form.get("num-occupants")
        rent = request.form.get("price-rent")
        genderAccommodation = request.form.get("gender-acco")
        
        street = request.form.get("street")
        barangay = request.form.get("barangay")
        cityOrMunicipality = request.form.get("cityOrMunicipality")
        province = request.form.get("province")
        #update unit info
        unit = units.unit()
        unit.updateUnit(unitID, rent, numOfOccupants, genderAccommodation)
        
        #update unit location 
        unitLocation = locations.location()
        unitLocation.updateLocation(unitID, street, barangay, cityOrMunicipality, province)
        
        
    return redirect(url_for('manageUnits',userID=userID))

@app.route('/delete/unit/<string:unitID>',methods =["POST"])
def deleteUnit(unitID):
    if request.method =="POST":
        userID = request.form.get('userID')
        unit = units.unit()
        unit.deleteUnit(unitID)
    return redirect(url_for('manageUnits',userID=userID))
    
@app.route('/manage/unit/search/<string:bhID>',methods=["POST"])
def ownerSearchUnits(bhID):
    if request.method == "POST":
        inputForSearch = request.form.get('search')
        userID = request.form.get('userID')
        
        bh = boardingHouses.boardingHouse()
        bhData = bh.searchBoardingHouse(userID)
        searchedUnits = units.unit()
        searchedUnits = searchedUnits.searchUnit(bhID,inputForSearch)
        
    return render_template('ownermanageunit.html',bhData=bhData,userID=userID,ownedUnits=searchedUnits)

@app.route('/account/info')
def accountInfo():
    return render_template('owneraccount.html',data=session['accountInfo'])

@app.route('/account/info/update/profile/and/contact',methods=['POST'])
def updateProfileAndContact():
    if request.method == 'POST':
        firstName = request.form.get('firstName')
        lastName = request.form.get('lastName')
        gender = request.form.get('gender')
        birthDate =request.form.get('birthDate')
        phoneNo = request.form.get('phoneNo')
        email = request.form.get('email')
        
        profile = profiles.profile()
        profile.updateProfile(session['accountInfo'][0],firstName,lastName,gender,birthDate)
        
        contact = contacts.contact()
        contact.updateContact(session['accountInfo'][0],phoneNo,email)
        
        account = accounts.account()
        username = session['accountInfo'][1]
        password = session['accountInfo'][2]
        session.clear()
        accountInfo = account.login(username,password)
        session['accountInfo'] = accountInfo
        return redirect(url_for('accountInfo'))
    
@app.route('/account/info/change/password',methods=['POST'])
def changePassword():
    if request.method == 'POST':
        oldPassword = request.form.get('oldPass')
        newPassword = request.form.get('newPass')
        account = accounts.account()
        account.changePassword(oldPassword,newPassword)
    return redirect(url_for('accountInfo'))

@app.route('/manage/payment')
def managePayment():
    bh = boardingHouses.boardingHouse()
    bh = bh.searchBoardingHouse(session['accountInfo'][0])
    bhID = bh[0]
    session['bhID'] = bhID
    paymentRecord = payments.payment()
    paymentRecord = paymentRecord.paymentToBh(bhID)
    
    accs = accounts.account()
    accs = accs.searchAllAccounts()
    
    ownedUnits = units.unit()
    ownedUnits = ownedUnits.searchOwnedUnits(bhID)
    return render_template('ownermanagepayments.html',paymentRecord = paymentRecord,accs=accs,ownedUnits=ownedUnits,accountInfo=session['accountInfo'],bhID=session['bhID'])

@app.route('/add/payment',methods=['POST'])
def addPayment():
    if request.method=='POST':
        renter = request.form.get('renterID')
        bhID = request.form.get('bhID')
        amount = request.form.get('amount')
        paymentDate = request.form.get('paidDate')
        
        payment = payments.payment(renter,bhID,amount,paymentDate)
        payment.addPayment()
    return redirect(url_for('managePayment'))
        