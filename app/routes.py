from config import ADMIN_CODES
from logging import log
from flask import Flask, flash, json, render_template, redirect, request, url_for, session, jsonify,abort,make_response
from datetime import datetime
import random
from flask_ipban.ip_ban import IpBan

from werkzeug.utils import html
from app import app
import secrets
import app.accountmodel as accounts
import app.profilemodel as profiles
import app.contactmodel as contacts
import app.boardinghousemodel as boardingHouses
import app.unitmodel as units
import app.locationmodel as locations
import app.paymentmodel as payments
import app.reservationmodel as reservations
import app.rentermodel as renters
import app.logsmodel as logs    


def loginRequired():
    if "accountInfo" in session:
        return True
    else:
        return False
            
 


@app.route('/create/account', methods=['POST'])
def createAccount():
    if request.method == "POST":
        # info needed in account table
        username = request.form.get('username')
        password = request.form.get('reg-password')
        accountType = request.form.get('reg-accountType')

        # info needed in profile tables
        firstName = request.form.get('reg-fn')
        lastName = request.form.get('reg-ln')
        gender = request.form.get('reg-gender')
        birthdate = request.form.get('reg-birthdate')

        #info needed in contact tables
        email = request.form.get('email')
        phoneNumber = request.form.get('phoneNumber')

        # initialize account,profile , and contacts for a user
        userAccount = accounts.account(username, password, accountType)
        userID = userAccount.addAccount()

        userProfile = profiles.profile(userID, firstName, lastName, birthdate,
                                    gender)
        userProfile.addProfile()

        userContact = contacts.contact(userID, email, phoneNumber)
        userContact.addContacts()

        # if account type is owner add boarding house
        if accountType == "O":
            boardingHousesName = firstName + "'s " + "Boarding House"
            boardingHouse = boardingHouses.boardingHouse(
                userID, boardingHousesName)
            boardingHouse.addBoardingHouse()

        verification = accounts.account()
        verificationResult = verification.login(username, password)

        if verificationResult == "Invalid login credentials":
            return redirect(
                url_for('signin',
                        usernameInput=username,
                        passwordInput=password))

        else:
            session['accountInfo'] = verificationResult
            flash("Welcome! You've successfuly created an account", 'success')
            return redirect(
                url_for('dashboard', accountInfo=session['accountInfo']))



@app.route('/signin')
def signin():
    return render_template('signin.html')

@app.route('/forgot/password')
def forgotPassword():
    return render_template('forgotpassword.html')


@app.route('/forgot/password/send/code',methods=["POST"])
def forgotPasswordSendCode():
    if request.method=="POST":
        contactType =  request.form.get('emailOrPhoneNumber') 
        contact = request.form.get('contact') 
        code = contacts.contact()
        checker = code.checkIfExist(contact,contact)
        if checker!=None or len(checker)!=0 :
            if contactType=="email":
                code = code.sendEmailVerificationCodeForgotPassword(contact)
                return render_template('forgotpasswordverification.html',code=code,contact=contact)

            else:
                code = code.smsAlertForgotPassword(contact)
                return render_template('forgotpasswordverification.html',code=code,contact=contact)

        else:
            return '<h1>NO ACCOUNT IS DETECTED</h1>'
            

@app.route('/set/new/password/<string:contact>')
def setNewPassword(contact):
    return render_template('setnewpassword.html',contact=contact)

@app.route('/change/password/force/<string:contact>',methods=['POST'])
def changePasswordForce(contact):
    if request.method == "POST":
        password = request.form.get("newPassword") 
        checkContact= contacts.contact()
        checkContact = checkContact.checkIfExist(contact,contact)
        account = accounts.account()
        data = account.forceChangePassword(checkContact[0][0],password)
        
        verificationResult = account.login(data[0][1], password)
        
        session['accountInfo'] = verificationResult
        description = "{} signed in".format(session['accountInfo'][1])
        log = logs.log(description)
        log.addLogs()
        flash("Welcome! You've successfully login.","success")
        return redirect(url_for('dashboard'))
  
@app.route('/login', methods=["POST", "GET"])
def login():
    if request.method == "POST":
        #get username/email and password
        usernameOrEmail = request.form.get('usernameOrEmail')
        password = request.form.get('password')

        verification = accounts.account()
        verificationResult = verification.login(usernameOrEmail, password)
        if verificationResult == "Invalid login credentials":
            return redirect(
                url_for('signin',
                        usernameInput=usernameOrEmail,
                        passwordInput=password))
        elif verificationResult==None:
              return redirect(
                url_for('signin'))
        else:
            session['accountInfo'] = verificationResult
            description = "{} signed in".format(session['accountInfo'][1])
            log = logs.log(description)
            log.addLogs()
            flash("Welcome! You've successfully login.","success")
            return redirect(url_for('dashboard'))
   
@app.route('/dashboard')
def dashboard():
    sessionChecker = loginRequired()
    if sessionChecker==True:
        if session['accountInfo'][3] == 'O':
            return render_template('ownerdashboard.html',
                               accountInfo=session['accountInfo'])
        else:
            return render_template('renterdashboard.html',
                               accountInfo=session['accountInfo'])
    else:
        return redirect(url_for("signin"))
    
@app.route('/logout')
def logout():
    description = "{} signed out".format(session['accountInfo'][1]) 
    log = logs.log(description)
    log.addLogs()
    session.clear()
    return redirect(url_for("signin"))


@app.route('/signin/OTP')
def OTP():
    return render_template('OTP.html')


@app.route('/signup')
def signup():
    if loginRequired==True:
        return redirect(url_for('dashboard'))
    else:
        return render_template('signup.html')


@app.route('/manage/units')
def manageUnits():
    sessionChecker = loginRequired()
    if sessionChecker==True:
        userID = session['accountInfo'][0]
        accountType = session['accountInfo'][3]
        if accountType == "O":
            bh = boardingHouses.boardingHouse()
            bhData = bh.searchBoardingHouse(userID)
            unit = units.unit()
            session['bhID'] = bhData[0]
            ownedUnits = unit.searchOwnedUnits(bhData[0])

            unitsLocations = locations.location()
            unitsLocations = unitsLocations.searchAllUnitsLocation()

            return render_template('ownermanageunit.html',
                                bhData=bhData,
                                userID=userID,
                                ownedUnits=ownedUnits,
                                unitsLocations=unitsLocations)
    else:
        return redirect(url_for("signin"))


@app.route('/manage/units/change/boarding/house/name', methods=["POST"])
def changeBoardingHouseName():
    sessionChecker = loginRequired()
    if sessionChecker==True:
        if request.method == "POST":
            newBoardingHouseName = request.form.get('bhName')
            userID = request.form.get('userID')
            bh = boardingHouses.boardingHouse()
            bh.changeBoardingHouseName(userID, newBoardingHouseName)
            description = "{} changes its boarding house name to {}".format(session['accountInfo'][1],newBoardingHouseName)
            log = logs.log(description)
            log.addLogs()
        return redirect(url_for('manageUnits', userID=userID))
    else:
        return redirect(url_for("signin"))

@app.route('/add/unit', methods=["POST"])
def addUnits():
    sessionChecker = loginRequired()
    if sessionChecker==True:
        if request.method == "POST":
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
            unit = units.unit(bhID, priceRent, numOfOccupants, genderAccommodation)
            locationID = unit.addUnit()

            #initialized unit location
            unitLocation = locations.location(locationID, street, barangay,
                                            cityOrMunicipality, province)
            unitLocation.addLocation()

            description = "{} added a new unit to its boarding house".format(session['accountInfo'][1])
            log = logs.log(description)
            log.addLogs()
            msg = flash("Well Done! You've successfully added a new unit.","success")
        return redirect(url_for('manageUnits',msg=msg))
    else:
        return redirect(url_for("signin"))


@app.route('/update/unit/<string:unitID>', methods=["POST"])
def updateUnits(unitID):
    sessionChecker= loginRequired()
    if sessionChecker==True:
        if request.method == "POST":
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
            unitLocation.updateLocation(unitID, street, barangay,
                                        cityOrMunicipality, province)
            
            description = "{} updated one of its unit {} info".format(session['accountInfo'][1],unitID)
            log = logs.log(description)
            log.addLogs()
            
        return redirect(url_for('manageUnits', userID=userID))
    else:
        return redirect(url_for("signin"))


@app.route('/delete/unit/<string:unitID>', methods=["POST"])
def deleteUnit(unitID):
    sessionChecker = loginRequired()
    if sessionChecker==True:
        if request.method == "POST":
            userID = request.form.get('userID')
            unit = units.unit()
            unit.deleteUnit(unitID)
            description = "{} deleted unit {}".format(session['accountInfo'][1],unitID)
            log = logs.log(description)
            log.addLogs()
        return redirect(url_for('manageUnits', userID=userID))
    else:
        return redirect(url_for("signin"))



@app.route('/manage/unit/search/<string:bhID>', methods=["POST"])
def ownerSearchUnits(bhID):
    sessionChecker = loginRequired()
    if sessionChecker==True:
        if request.method == "POST":
            inputForSearch = request.form.get('search')
            userID = request.form.get('userID')

            bh = boardingHouses.boardingHouse()
            bhData = bh.searchBoardingHouse(userID)
            searchedUnits = units.unit()
            searchedUnits = searchedUnits.searchUnit(bhID, inputForSearch)

        return render_template('ownermanageunit.html',
                            bhData=bhData,
                            userID=userID,
                            ownedUnits=searchedUnits)
    else:
        return redirect(url_for("signin"))



@app.route('/account/info')
def accountInfo():
    sessionChecker = loginRequired()
    if sessionChecker==True:
        if session['accountInfo'][3] == "O":
            return render_template('owneraccount.html',
                                data=session['accountInfo'])
        else:
            return render_template('renteraccount.html',
                                data=session['accountInfo'])
    return redirect(url_for("signin"))


@app.route('/account/info/update/profile/and/contact', methods=['POST'])
def updateProfileAndContact():
    sessionChecker = loginRequired()
    if sessionChecker==True:
        if request.method == 'POST':
            firstName = request.form.get('firstName')
            lastName = request.form.get('lastName')
            gender = request.form.get('gender')
            birthDate = request.form.get('birthDate')
            phoneNo = request.form.get('phoneNo')
            email = request.form.get('email')

            profile = profiles.profile()
            profile.updateProfile(session['accountInfo'][0], firstName, lastName,
                                gender, birthDate)

            contact = contacts.contact()
            contact.updateContact(session['accountInfo'][0], phoneNo, email)

            account = accounts.account()
            username = session['accountInfo'][1]
            password = session['accountInfo'][2]
            session.clear()
            accountInfo = account.login(username, password)
            session['accountInfo'] = accountInfo
            description = "{} update its account info".format(session['accountInfo'][1])
            log = logs.log(description)
            log.addLogs()
            msg = flash("Well Done! You've successfully updated your profile information.","success")
            return redirect(url_for('accountInfo',msg=msg ))
    else:
        return redirect(url_for("signin"))



@app.route('/account/info/change/password', methods=['POST'])
def changePassword():
    sessionChecker = loginRequired()
    if sessionChecker==True:
        if request.method == 'POST':
            oldPassword = request.form.get('oldPass')
            newPassword = request.form.get('newPass')
            account = accounts.account()
            account.changePassword(session['accountInfo'][0],oldPassword, newPassword)
            description = "{} update its password".format(session['accountInfo'][1])
            log = logs.log(description)
            log.addLogs()
            msg = flash("Well Done! You've successfully updated your profile information.","success")
        return redirect(url_for('accountInfo',msg=msg))
    return redirect(url_for("signin"))


@app.route('/manage/payment')
def managePayment():
    sessionChecker = loginRequired()
    if sessionChecker==True:
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
        return render_template('ownermanagepayments.html',
                            paymentRecord=paymentRecord,
                            accs=accs,
                            ownedUnits=ownedUnits,
                            accountInfo=session['accountInfo'],
                            bhID=session['bhID'])
    else:
        return redirect(url_for("signin"))



@app.route('/add/payment', methods=['POST'])
def addPayment():
    sessionChecker = loginRequired()
    if sessionChecker==True:
        if request.method == 'POST':
            renter = request.form.get('renterID')
            bhID = request.form.get('bhID')
            amount = request.form.get('amount')
            paymentDate = request.form.get('paidDate')
            payment = payments.payment(renter, bhID, amount, paymentDate)
            payment.addPayment()
            description = "{} pays P{} to {} ".format(renter,amount,bhID)
            log= logs.log(description)
            log.addLogs()
            msg = flash("Well Done! You've successfully added a payment.","success")
        return redirect(url_for('managePayment',msg=msg))
    else:
        return redirect(url_for("signin"))



@app.route('/manage/tenants')
def manageTenants():
    sessionChecker = loginRequired()
    if sessionChecker==True:
        reservationList = reservations.reservation()
        reservationList = reservationList.ownerReservationData(session['accountInfo'][0])
        renterList = renters.renter()
        activeRenterList = renterList.tenantsList()
        renterRequestLeaveList = renterList.leaveRequestList()
        
        return render_template('ownermanagetenants.html',reservationList=reservationList,activeRenterList=activeRenterList,renterRequestLeaveList=renterRequestLeaveList,accountInfo=session['accountInfo'])
    else:
        return redirect(url_for("signin"))



@app.route('/search/units')
def searchUnits():
    sessionChecker = loginRequired()
    if sessionChecker==True:
        location = request.args.get('location', 0, type=str)
        rent = request.args.get('rent', 0, type=int)
        capacity = request.args.get('capacity', 0, type=int)
        genderAccommodation = request.args.get('genderAccommodation', 0, type=str)

        allUnits = units.unit()
        allUnits = allUnits.searchResult(location, rent, capacity,
                                        genderAccommodation)
        if allUnits != None:
            return jsonify(result=allUnits)
        else:
            return jsonify(result=[])
    else:
        return redirect(url_for("signin"))



@app.route('/rent/request/<string:unitID>')
def addRentRequest(unitID):
    sessionChecker = loginRequired()
    if sessionChecker==True:
        reserve = reservations.reservation()
        reservationChecker = reserve.checkActiveReservation(session['accountInfo'][0])
        info = units.unit()
        info = info.unitsInfo(unitID)
        today = datetime.today()
        date = today.strftime("%B %d, %Y")
        flash("Awesome! You've successfuly sent a request for a reservation.", 'success')
        return render_template("renterreservation.html",
                            accountInfo=session['accountInfo'],
                            unitID=unitID,
                            unitInfo=info,
                            date=date,reservationChecker=reservationChecker)
    else:
        return redirect(url_for("signin"))
    
@app.route('/renter/pending/reservation')
def renterPendingReservation():
    sessionChecker = loginRequired()
    if sessionChecker==True:
        reserve = reservations.reservation()
        reservationChecker = reserve.checkActiveReservation(session['accountInfo'][0])
        reservationData = reserve.pendingReservation(session['accountInfo'][0])
        if reservationChecker!=None:
            reservationChecker=reservationChecker[4]
            
        else:
            reservationChecker="N"
        info = units.unit()
        if reservationData==None or len(reservationData)==0:
            info = []
            reservationData= []
     
            
            today = datetime.today()
            date = today.strftime("%B %d, %Y")
            return render_template("pendingreservation.html",
                                accountInfo=[],
                                unitInfo=info,
                                date=date,reservationChecker=reservationChecker,reservationData=reservationData)
        else:
            info = info.unitsInfo(reservationData[2])
            today = datetime.today()
            date = today.strftime("%B %d, %Y")
            return render_template("pendingreservation.html",
                                accountInfo=session['accountInfo'],
                                unitInfo=info,
                                date=date,reservationChecker=reservationChecker,reservationData=reservationData)
    else:
        return redirect(url_for("signin"))
    
@app.route('/renter/cancel/reservation/<int:reservationNo>')
def cancelReservation(reservationNo):
    sessionChecker = loginRequired()
    if sessionChecker==True:
        reserve = reservations.reservation()
        reserve.cancelReservation(reservationNo) 
        description = "{} cancels reservation no.{}".format(session['accountInfo'][1],reservationNo)
        log = logs.log(description)
        log.addLogs()
        return redirect(url_for('renterPendingReservation'))
    else:
         return redirect(url_for("signin"))


    
@app.route('/renter/delete/reservation/<int:reservationNo>')
def deleteReservation(reservationNo):
    sessionChecker = loginRequired()
    if sessionChecker==True:
        reserve = reservations.reservation()
        reserve.deleteReservation(reservationNo) 
        description = "{} deleted reservation no.{} ".format(session['accountInfo'][1],reservationNo)
        log = logs.log(description)
        log.addLogs()
        return redirect(url_for('renterPendingReservation'))
    else:
        return redirect(url_for("signin"))


@app.route('/confirm/leave/request/<string:userID>',methods=["POST"])
def confirmLeaveRequest(userID):
    sessionChecker = loginRequired()
    if sessionChecker==True:
        leaveRequest = renters.renter()
        leaveRequest.confirmLeaveRequest(userID)
        description = "Leave request of {} was approved by the boarding house owner ".format(session['accountInfo'][1])
        log = logs.log(description)
        log.addLogs()
        return redirect(url_for('manageTenants'))
    else:
        return redirect(url_for("signin"))

@app.route('/decline/leave/request/<string:userID>')
def declineLeaveRequest(userID):
    sessionChecker = loginRequired()
    if sessionChecker==True:
        leaveRequest = renters.renter()
        leaveRequest.declineLeaveRequest(userID)
        description = "Leave request of {} was declined by the boarding house owner ".format(session['accountInfo'][1])
        log = logs.log(description)
        log.addLogs()
        return redirect(url_for('manageTenants'))
    else:
        return redirect(url_for("signin"))
        
            

@app.route('/renter/payments/list')
def renterPaymentsList():
    sessionChecker = loginRequired()
    if sessionChecker==True:
        myPayments = payments.payment()
        myPayments = myPayments.renterPayments(session['accountInfo'][0])
        return render_template("renterpayments.html",
                            accountInfo=session['accountInfo'],myPayments=myPayments)
    else:
        return redirect(url_for("signin"))
    


@app.route('/owner/reservation')
def ownerReservation():
    sessionChecker = loginRequired()
    if sessionChecker==True:
        return render_template('ownerreservations.html')
    else:
        return redirect(url_for("signin"))


@app.route('/profile')
def profile():
    sessionChecker = loginRequired()
    if sessionChecker==True:
        return render_template('renterownerprofiles.html')
    else:
        return redirect(url_for("signin"))


@app.route('/sent/rent/request', methods=["POST"])
def sendRentRequest():
    sessionChecker = loginRequired()
    if sessionChecker==True:
        if request.method == "POST":
            unitID = request.form.get('unitID')
            userID = request.form.get('userID')
            today = datetime.today()
            date = today.strftime("%Y-%m-%d")
            reserve = reservations.reservation(userID, unitID, date)
            reserve.addReservation()
            description = "{} send reservation for unit: {}".format(session['accountInfo'][0],unitID)
            log= logs.log(description)
            log.addLogs()
            return redirect(url_for('renterPendingReservation'))
    else:
        return redirect(url_for("signin"))

@app.route('/accept/rent/request/<int:reservationNo>/<string:userID>/<string:unitID>',methods=["POST"])
def acceptRentRequest(reservationNo,userID,unitID):
    sessionChecker = loginRequired()
    if sessionChecker==True:
        today = datetime.today()
        date = today.strftime("%Y-%m-%d")
        renter = renters.renter(userID,unitID,date)
        reservation = reservations.reservation()
        reservation.acceptReservation(reservationNo)
        renter.addRenter()
        
        description = "Rent request of {} was approved by the boarding house owner".format(session['accountInfo'][0])
        log= logs.log(description)
        log.addLogs()
        
        description = "{} started renting for unit: {}".format(session['accountInfo'][0],unitID)
        log= logs.log(description)
        log.addLogs()
        return redirect(url_for('manageTenants'))
    else:
        return redirect(url_for("signin"))

@app.route('/decline/rent/request/<int:reservationNo>')
def declineRentRequest(reservationNo):
    sessionChecker = loginRequired()
    if sessionChecker==True:
        reservation = reservations.reservation()
        reservation.declineReservation(reservationNo)
        
        description = "Rent request no.{} was declined by the boarding house owner".format(reservationNo)
        log= logs.log(description)
        log.addLogs()
        
        return redirect(url_for('manageTenants'))
    else:
        return redirect(url_for("signin"))



@app.route('/renter/rented/unit')
def rentedUnit():
    sessionChecker = loginRequired()
    if sessionChecker==True:
        unitInfo = units.unit()
        info = unitInfo.rentedUnit(session['accountInfo'][0])
        if info==None or len(info)==0:    
            return render_template('renterrentedunit.html',info=[],unit=[],date=[],accountInfo=session['accountInfo'])
        else:
            unit = unitInfo.rentedUnitInfo(info[0][1])
            return render_template('renterrentedunit.html',info=info,unit=unit,date=str(info[0][2]),accountInfo=session['accountInfo'])
    else:
        return redirect(url_for("signin"))

@app.route('/unit')
def unit():
    sessionChecker = loginRequired()
    if sessionChecker==True:
        return render_template('unit.html')
    else:
        return redirect(url_for("signin"))


@app.route('/renter/rented/unit/request/to/leave/<string:userID>/<string:unitID>',methods=['POST'])
def requestToLeave(userID,unitID):
    sessionChecker = loginRequired()
    if sessionChecker==True:
        renter = renters.renter()
        renter.requestRenterLeave(userID,unitID)
        description = "{} sents a leave request for the boarding house owner".format(session['accountInfo'][1])
        log= logs.log(description)
        log.addLogs()
        return redirect(url_for('rentedUnit'))
    else:
        return redirect(url_for("signin"))



@app.route('/cancel/request/to/leave/<string:userID>/<string:unitID>')
def cancelRequestToLeave(userID,unitID):
    sessionChecker = loginRequired()
    if sessionChecker==True:
        renter = renters.renter()
        renter.cancelOrDeclineRenterLeave(userID,unitID)
        
        description = "{} cancel its leave request".format(session['accountInfo'][1])
        log= logs.log(description)
        log.addLogs()
        return redirect(url_for('rentedUnit'))
    else:
        return redirect(url_for("signin"))



    
@app.route('/renter/privacy')
def renterPrivacy():
    sessionChecker = loginRequired()
    if sessionChecker==True:
        if session['accountInfo'][3]=="R":
            return render_template('renterprivacy.html',jsonifyAccountInfo=jsonify(session['accountInfo']),accountInfo=session['accountInfo'])
        else:
            return redirect(url_for("dashboard"))
    else:
        return redirect(url_for("signin"))


    
@app.route('/owner/privacy')
def ownerPrivacy():
    sessionChecker = loginRequired()
    if sessionChecker==True:
        if session['accountInfo'][3]=="O":
            return render_template('ownerprivacy.html',jsonifyAccountInfo=jsonify(session['accountInfo']),accountInfo=session['accountInfo'])
        else:
            return redirect(url_for("dashboard"))
    else:
        return redirect(url_for("signin"))


@app.route('/send/email/verification/code')
def sendEmailVerification():
    sessionChecker = loginRequired()
    if sessionChecker==True:
        code = secrets.token_hex(16)
        msg = "Code: {}".format(code)
        emailVerification = contacts.contact()
        emailVerification.emailAlert("Panimalay Email Verification",msg,session['accountInfo'][8])
        
        description = "Panimalay sents an email verification code to {} r".format(session['accountInfo'][8])
        log= logs.log(description)
        log.addLogs()
        return jsonify(result=code)
        
    return redirect(url_for("signin"))
    
@app.route('/verify/email',methods=["POST"])
def verifyEmail():
    sessionChecker = loginRequired()
    if sessionChecker==True:
        email = contacts.contact()
        email.verifyEmail(session["accountInfo"][0])
        username = session["accountInfo"][1]
        password = session["accountInfo"][2]
        verification = accounts.account()
        verificationResult = verification.login(username, password)
        session['accountInfo'] = verificationResult
        return redirect(url_for('renterPrivacy'))
    else:
        return redirect(url_for("signin"))
    

@app.route('/send/phone/number/verification/code')
def sendPhoneNumberVerification():
    sessionChecker = loginRequired()
    if sessionChecker==True:
        code = ''.join(random.choice('0123456789') for _ in range(6))
        emailVerification = contacts.contact()
        emailVerification.smsAlert(code,session['accountInfo'][9])
        
        
        description = "Panimalay sents an sms verification code to {} r".format(session['accountInfo'][9])
        log= logs.log(description)
        log.addLogs()
        
        return jsonify(result=code)
        
    return redirect(url_for("signin"))

@app.route('/verify/phone/number',methods=["POST"])
def verifyPhoneNumber():
    sessionChecker = loginRequired()
    if sessionChecker==True:
        email = contacts.contact()
        email.verifyPhoneNumber(session["accountInfo"][0])
        username = session["accountInfo"][1]
        password = session["accountInfo"][2]
        verification = accounts.account()
        verificationResult = verification.login(username, password)
        session['accountInfo'] = verificationResult
        return redirect(url_for('renterPrivacy'))
    else:
        return redirect(url_for("signin"))

@app.route('/update/2FA')
def update2FA():
    sessionChecker = loginRequired()
    if sessionChecker==True:
        update2fa = contacts.contact()
        update2fa.update2FA(session['accountInfo'][0])
        username = session["accountInfo"][1]
        password = session["accountInfo"][2]
        verification = accounts.account()
        verificationResult = verification.login(username, password)
        session['accountInfo'] = verificationResult
        if  session["accountInfo"][3]=="R":
            return redirect(url_for('renterPrivacy'))
        else:
              return redirect(url_for('ownerPrivacy'))
    else:
        return redirect(url_for("signin"))

@app.route('/email/OTP')
def emailOTP():
    return render_template("emailotp.html")


@app.route('/sms/OTP')
def smsOTP():
    return render_template("smsotp.html")
    
@app.route('/username/credentials/uniqueness/test')
def usernameCredentialUniquenessTest():
    username = request.args.get('username', 0, type=str)
    uniquenessTest = accounts.account()
    uniquenessTest = uniquenessTest.usernameUniquenessTest(username)
    
    return jsonify(result=uniquenessTest)
        
    

@app.route('/email/credentials/uniqueness/test')
def emailCredentialUuniquenessTest():

    email = request.args.get('email', 0, type=str)
    uniquenessTest = contacts.contact()
    uniquenessTest= uniquenessTest.emailUniquenessTest(email)

    return jsonify(result=uniquenessTest)
    

@app.route('/phoneNumber/credentials/uniqueness/test')
def phoneNumberCredentialUniquenessTest():
    phoneNumber = request.args.get('phoneNumber', 0, type=str)
    uniquenessTest = contacts.contact()
    uniquenessTest = uniquenessTest.phoneNumberUniquenessTest(phoneNumber)
    
    return jsonify(result=uniquenessTest)
    

@app.route('/admin/dashboard')
def adminDashboard():
    if 'adminLogin' in session:
        trusted_proxies_and_IP = ['127.0.0.1']
        if request.remote_addr not in trusted_proxies_and_IP:
            abort(403)  # Forbidden
        else:
            return render_template('admindashboard.html')
    else:
        return render_template('errorpage.html')

@app.route('/admin/login')
def adminLogin():
    trusted_proxies_and_IP = ['127.0.0.1']
    if request.remote_addr not in trusted_proxies_and_IP:
        abort(403)  # Forbidden
    else:
        return render_template('adminlogin.html')

@app.route('/admin/random/code/generator')
def adminRandomCodeGenarator():
    trusted_proxies_and_IP = ['127.0.0.1']
    if request.remote_addr not in trusted_proxies_and_IP:
        abort(403)  # Forbidden
    else:
        return render_template('adminrandomcodegenerator.html',codes=ADMIN_CODES)

@app.route('/admin/login/check/credentials',methods=["POST"])
def adminLoginCheckCredentials():
    trusted_proxies_and_IP = ['127.0.0.1']
    if request.remote_addr not in trusted_proxies_and_IP:
        abort(403)  # Forbidden
    else:
        if request.method=="POST":
            password = request.form.get("password",0,str)
            password = [password]
            if password in ADMIN_CODES:
                msg = flash("Awesome! You've successfully login.","success")
                session['adminLogin'] = 1
                return redirect(url_for('adminDashboard',msg=msg))
            else:
                return redirect(url_for('adminLogin'))
            
@app.route('/admin/account')
def adminAccount():
    if 'adminLogin' in session:
        trusted_proxies_and_IP = ['127.0.0.1']
        if request.remote_addr not in trusted_proxies_and_IP:
            abort(403)  # Forbidden
        else:
            return render_template("adminaccount.html")
    else:
        return render_template('errorpage.html')

"""
@app.route('/admin/account/manage/password', methods=['POST'])
def updateAdminAccount():
    if 'adminLogin' in session:
        if request.method == 'POST':
            trusted_proxies_and_IP = ['127.0.0.1']
            if request.remote_addr not in trusted_proxies_and_IP:
            abort(403)  # Forbidden
        else:
            currentPass = request.form.get('currentPass')
            newPass = request.form.get('newPass')
            secretAnswer = request.form.get('secretAnswer')
            if secretQuestion==ADMIN_SECRET_QUESTION:
                return redirect(url_for('adminAccount'))
    else:
        return render_template('errorpage.html') 
"""
    
@app.route('/admin/logs')
def adminLogs():
    if 'adminLogin' in session:
        trusted_proxies_and_IP = ['127.0.0.1']
        if request.remote_addr not in trusted_proxies_and_IP:
            abort(403)  # Forbidden
        else:
            return render_template("adminlogs.html")
    else:
        return render_template('errorpage.html')  
    
@app.route('/fetch/logs')
def fetchLogs():
    if 'adminLogin' in session:
        trusted_proxies_and_IP = ['127.0.0.1']
        if request.remote_addr not in trusted_proxies_and_IP:
            abort(403)  # Forbidden
        else:
            searchAllLogs = logs.log()
            data = searchAllLogs.searchAllLogs()
            return jsonify(result=data)
    else:
        return render_template('errorpage.html')  
       
@app.route('/admin/manage/passwords')
def adminManagePasswords():
    if 'adminLogin' in session:
        trusted_proxies_and_IP = ['127.0.0.1']
        if request.remote_addr not in trusted_proxies_and_IP:
            abort(403)  # Forbidden
        else:
            return render_template("adminmanagepasswords.html")
    else:
        return render_template('errorpage.html')  

"""
@app.route('/manage/passwords', methods=["POST"])
def managePasswords():
    if 'adminLogin' in session:
        if request.method == 'POST':
            trusted_proxies_and_IP = ['127.0.0.1']
            if request.remote_addr not in trusted_proxies_and_IP:
            abort(403)  # Forbidden
        else:


"""

@app.route('/admin/manage/payments')
def adminManagePayments():
    if 'adminLogin' in session:
        trusted_proxies_and_IP = ['127.0.0.1']
        if request.remote_addr not in trusted_proxies_and_IP:
            abort(403)  # Forbidden
        else:
            paymentRecord = payments.payment()
            paymentRecord = paymentRecord.searchAllPayments()
            return render_template("adminmanagepayments.html",payments=paymentRecord)
    else:
        return render_template('errorpage.html')  
    

@app.errorhandler(404)
def not_found(error):
    resp = make_response(render_template('errorpage.html'), 404)
    resp.headers['header'] = 'ERROR'
    return resp

@app.route('/update/payment/record',methods=["POST"])
def updatePaymentRecord():
    if 'adminLogin' in session:
        if request.method == "POST":
            trusted_proxies_and_IP = ['127.0.0.1']
            if request.remote_addr not in trusted_proxies_and_IP:
                abort(403)  # Forbidden
            else:
                paymentNo = request.form.get("paymentNo")
                amount = request.form.get("paymentAmount")
                date = request.form.get("paymentDate")
                paymentRecord = payments.payment()
                paymentRecord.updatePayment(paymentNo,amount,date)
                return redirect(url_for("adminManagePayments")) 
    else:
        return render_template('errorpage.html')  

@app.route('/update/payment/record/email/verification/<string:userID>/<string:bhID>')
def updatePaymentRecordEmailVerication(userID,bhID):
    if 'adminLogin' in session:
        trusted_proxies_and_IP = ['127.0.0.1']
        if request.remote_addr not in trusted_proxies_and_IP:
            abort(403)  # Forbidden
        else:
            #code for renter
            renterCode = contacts.contact()
            renterEmail = renterCode.findEmailUsingUserID(userID)
            renterCode = renterCode.sendEmailVerificationCodeForPaymentUpdate(renterEmail[0][1])
            
            #code for owner
            ownerCode =  contacts.contact()
            ownerEmail = ownerCode.findEmailUsingbhID(bhID)
            ownerCode =  ownerCode.sendEmailVerificationCodeForPaymentUpdate(ownerEmail[1])
            return jsonify(result=[renterCode,ownerCode]) 
    else:
        return render_template('errorpage.html')


@app.route('/admin/logout')
def adminLogout():
    session.pop('adminLogin')
    return redirect(url_for('adminLogin'))
    

@app.route('/edit/payments/<int:paymentNo>',methods=['POST'])
def editPayments(paymentNo):
    trusted_proxies_and_IP = ['127.0.0.1']
    if 'adminLogin' in session:
        if request.remote_addr not in trusted_proxies_and_IP:
            abort(403)  # Forbidden
        else:
            if request.method == "POST":
                amount = request.form.get('amount')
                date =  request.form.get('paymentDate')
                payment = payments.payment()
                payment.updatePayment(paymentNo,amount,date)
                msg = flash("Well Done! You've successfully updated the payment.","success")
                return redirect(url_for('adminManagePayments',msg=msg))
    else:
        return render_template('errorpage.html')


@app.route('/delete/payments/record/email/verification/<string:userID>/<string:bhID>')
def deletePaymentRecordEmailVerication(userID,bhID):
    trusted_proxies_and_IP = ['127.0.0.1']
    if 'adminLogin' in session:
        if request.remote_addr not in trusted_proxies_and_IP:
            abort(403)  # Forbidden
        else:
            #code for renter
            renterCode = contacts.contact()
            renterEmail = renterCode.findEmailUsingUserID(userID)
            renterCode = renterCode.sendEmailVerificationCodeForPaymentUpdate(renterEmail[0][1])
            
            #code for owner
            ownerCode =  contacts.contact()
            ownerEmail = ownerCode.findEmailUsingbhID(bhID)
            ownerCode =  ownerCode.sendEmailVerificationCodeForPaymentUpdate(ownerEmail[1])
            return jsonify(result=[renterCode,ownerCode]) 
            
    else:
        return render_template('errorpage.html')
    
@app.route('/delete/payments/<int:paymentNo>',methods=['POST'])
def deletePayments(paymentNo):
    trusted_proxies_and_IP = ['127.0.0.1']
    if 'adminLogin' in session:
        if request.remote_addr not in trusted_proxies_and_IP:
            abort(403)  # Forbidden
        else:
            payment = payments.payment()
            payment.deletePayment(paymentNo)
            return redirect(url_for('adminManagePayments'))
            
    else:
        return render_template('errorpage.html')


@app.route('/admin/list/of/bh')
def adminListOfBh():
    if 'adminLogin' in session:
        trusted_proxies_and_IP = ['127.0.0.1']
        if request.remote_addr not in trusted_proxies_and_IP:
            abort(403)  # Forbidden
        else:

            return render_template("adminlistofbh.html")
    else:
        return render_template('errorpage.html')

@app.route('/admin/list/of/users')
def adminListOfUsers():
    if 'adminLogin' in session:
        trusted_proxies_and_IP = ['127.0.0.1']
        if request.remote_addr not in trusted_proxies_and_IP:
            abort(403)  # Forbidden
        else:
            myListOfUsers = accounts.account()
            myListOfUsers = myListOfUsers.searchAllAccountsForAdmin()
            return render_template("adminlistofusers.html",myListOfUsers=myListOfUsers)
    else:
        return render_template('errorpage.html')


'''
    
@app.errorhandler(404)
def page_not_found(e):
 return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
 return render_template('500.html'), 500

'''
