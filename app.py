from flask import Flask, render_template, url_for, session, redirect, jsonify, request, flash
from flask_sqlalchemy import SQLAlchemy
from PIL import Image
from flask_bcrypt import Bcrypt
import time
import datetime
import os
import random
import string

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://postgres:mathenge,./1998@localhost/mainapp'
app.config['SECRET_KEY'] = 'some=secret+key'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
UPLOAD_FOLDER = os.getcwd() + '/static/uploads/images'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

# db models
# customer db model class


class customers(db.Model):
    id = db.Column(db.Integer, nullable=False,
                   primary_key=True, autoincrement=True)
    name = db.Column(db.String(15), nullable=False)
    email = db.Column(db.String(20), nullable=False, unique=True)
    phone_number = db.Column(db.String(30), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)

    # insert new user class

    def insert_record(self):
        db.session.add(self)
        db.session.commit()

    # check if email is in use
    @classmethod
    def check_email_exist(cls, email):
        customer = cls.query.filter_by(email=email).first()
        if customer:
            return True
        else:
            return False

    # validate password
    @classmethod
    def validate_password(cls, email, password):
        customer = cls.query.filter_by(email=email).first()

        if customer and bcrypt.check_password_hash(customer.password, password):
            return True
        else:
            return False

    # get customer id
    @classmethod
    def get_customer_id(cls, email):
        return cls.query.filter_by(email=email).first().id

# db owner relation class


class owners(db.Model):
    id = db.Column(db.Integer, nullable=False,
                   primary_key=True, autoincrement=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(200), nullable=False, unique=True)
    phone_number = db.Column(db.String(30), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)

    # insert new user class

    def insert_record(self):
        db.session.add(self)
        db.session.commit()

    # check if email exists
    @classmethod
    def check_email_exist(cls, email):
        owners = cls.query.filter_by(email=email).first()
        print(owners)
        if owners:
            return True
        else:
            return False

    # validate password
    @classmethod
    def validate_password(cls, email, password):
        owners = cls.query.filter_by(email=email).first()
        if owners and bcrypt.check_password_hash(owners.password, password):
            return True
        else:
            return False

    # get customer id
    @classmethod
    def get_owners_id(cls, email):
        return cls.query.filter_by(email=email).first().id


class property(db.Model):
    id = db.Column(db.Integer, nullable=False,
                   primary_key=True, autoincrement=True)
    img = db.Column(db.String(), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(1000), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(), nullable=False, default='vacant')

    # insert property

    def insert_record(self):
        db.session.add(self)
        db.session.commit()

    # fetch all property
    @classmethod
    def fetch_all(cls):
        return cls.query.all()

    # fetch where status is 1
    @classmethod
    def fetch_by_status_occupied(cls):
        return cls.query.filter_by(status=u'vacant')

    # get property by id
    @classmethod
    def get_property_by_id(cls, id):
        return cls.query.filter_by(id=id)

    @classmethod
    def get_property_price(cls, id):
        return cls.query.filter_by(id=id).first().price
    # update status
        # update property

    @classmethod
    def update_property_by_id(cls, id):
        property = cls.query.filter_by(id=id).first()
        if property:
            status = property.status            
            if status == 'booked':
                newstatus = 'vacant'
                property.status = newstatus
                db.session.commit()
                return True
            else:
                newstatus = 'booked'
                property.status = newstatus
                db.session.commit()
                return True
        else:
            return False

    # delete property by id
    @classmethod
    def delete_by_id(cls, id):
        property = cls.query.filter_by(id=id).first()
        if property:
            property.delete()
            db.session.commit()
            return True
        else:
            return False


class bookings(db.Model):
    id = db.Column(db.Integer, nullable=False,
                   primary_key=True, autoincrement=True)
    property_id = db.Column(db.Integer)
    movein_date = db.Column(db.Date)
    customer_email = db.Column(db.String)

 # create

    def insert_record(self):
        db.session.add(self)
        db.session.commit()

    # fetch all
    @classmethod
    def fetch_all(cls):
        return cls.query.all()

    # fetch booking id
    @classmethod
    def get_booking_id_by_property_id(cls, id):
        return cls.query.filter_by(property_id=id).first().id
# clear rcords
    @classmethod
    def delete_all(cls):
        booked = cls.query.delete()
        db.session.commit()
        return True

    @classmethod
    def delete_by_id(cls, id):
        booking = cls.query.filter_by(id=id)
        if booking.first():
            booking.delete()
            db.session.commit()
            return True
        else:
            return False
# wallet class


class wallet(db.Model):
    id = db.Column(db.Integer, primary_key=True,
                   nullable=False, autoincrement=True)
    owner = db.Column(db.Integer)
    phone = db.Column(db.Integer)
    amount = db.Column(db.Integer, default=0)

# create new wallet
    def create_wallet(self):
        db.session.add(self)
        db.session.commit()
# view wallet
    @classmethod
    def view_curacquire_amount(cls, id):
        return cls.query.filter_by(owner=id).first().amount
# update wallet
    @classmethod
    def update_wallet_by_id(cls, id, newentry):
        ownerid = cls.query.filter_by(owner=id).first()
        if ownerid:
            ownerid.amount = newentry
            db.session.commit()
            return True
        return False

#random character generator 
def randomgenerator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

#  function that check if an extension is valid, uploads a file and redirect user to url for image
def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def upload_file(imageFile):
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in imageFile:
            print('No file part')
            return None

        file = imageFile['file']

        # if user does not select file, browser also submits an empty part without filename
        if file.filename == '':
            return None
        if file and allowed_file(file.filename):
            img = Image.open(file)
            new_width = 150
            new_height = 150
            size = (new_height, new_width)
            img = img.resize(size)
            stamped = int(time.time())
            print('all good')
            img.save(os.path.join(UPLOAD_FOLDER, str(stamped) + file.filename))
            print(os.path.join(UPLOAD_FOLDER, str(stamped) + file.filename))
            return '/static/uploads/images/' + str(stamped) + file.filename
        else:
            return None

# customer landing page
@app.route('/main', methods=['POST', 'GET'])
def main():
    if 'custemail' in session:
        allproperty = property.fetch_by_status_occupied()
        return render_template('dash.html', allproperty=allproperty)
    else:
        return redirect(url_for('login'))

# log in page is initiated here
@app.route('/')
def start():
    return render_template('index.html')

# owner register and login
@app.route('/owner/register')
def owner_register():
    return render_template('adminreg.html')


# owner registration occurs
@app.route('/owner_reg', methods=['POST', 'GET'])
def owner_reg():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        password = request.form['password']
        confirmpass = request.form['confirmpass']

        if password != confirmpass:
            flash('Passwords dont match', 'danger')
            return redirect(url_for('owner_register'))
        elif owners.check_email_exist(email):

            flash('Email already in use', 'danger')
            return redirect(url_for('owner_register'))
        else:
            hashpassword = bcrypt.generate_password_hash(
                password).decode('utf-8')
            try:
                y = owners(name=name, email=email,
                       phone_number=phone, password=hashpassword)
                y.insert_record()

                flash('Account successfully created', 'success')
                return redirect(url_for('owner_login'))
            except :
                flash('Account creation failed. check your credentials and try again', 'danger')
                return redirect(url_for('owner_register'))

    return redirect(url_for('owner_register'))

# owner login
@app.route('/owner/login')
def owner_login():
    return render_template('adminlogin.html')


@app.route('/owner/log_in', methods=['GET', 'POST'])
def owners_login():
    if request.method == 'POST':
        # try:
        email = request.form['email']
        password = request.form['password']

        # check if email exist
        if owners.check_email_exist(email):
            if owners.validate_password(email=email, password=password):
                session['email'] = email
                session['uid'] = owners.get_owners_id(email)
                return redirect(url_for('admin'))
            else:
                flash('Invalid login credentials', 'danger')
                return redirect(url_for('owner_login'))
        else:
            flash('Invalid login credentials', 'danger')
            return redirect(url_for('owner_login'))
    # except Exception as e:
        # print(e)
    return render_template('owner_login.html')
# customer registration render page
@app.route('/registration')
def registration():
    return render_template('register.html')

# customer registration
@app.route('/cust_reg', methods=['POST', 'GET'])
def cust_reg():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        password = request.form['password']
        confirmpass = request.form['confirmpass']

        if password != confirmpass:
            flash('Passwords dont match', 'danger')
            return redirect(url_for('registration'))
        elif(customers.check_email_exist(email)):
            flash('Email already in use', 'danger')
            return redirect(url_for('regisration'))
        else:
            hashpassword = bcrypt.generate_password_hash(
                password).decode('utf-8')
            session['myemail'] = email
            session['phone'] = phone
            try:
                y = customers(name=name, email=email,
                          phone_number=phone, password=hashpassword)
                y.insert_record()
                return redirect(url_for('wallet_create'))
            except:
                flash('error creating account','danger')
                return redirect(url_for('registration'))            

    return redirect(url_for('registrtion'))

    return redirect(url_for('registration'))


# create wallet
@app.route('/wallet/create')
def wallet_create():
    walletemail = session['myemail']
    owner_id = customers.get_customer_id(walletemail)
    phone = session['phone']
    w = wallet(owner=owner_id, phone=phone)
    w.create_wallet()
    session.pop('myemail')
    session.pop('phone')
    flash('Account successfully created', 'success')
    return redirect(url_for('login'))

# check wallet ballance
@app.route('/wallet/balance', methods=['POST', 'GET'])
def wallet_ballance():
    id = session['custid']
    myamount = wallet.view_curacquire_amount(id)
    print(myamount)
    property = session['thisid']
    pricetag = property.get_property_price(property)
    if myamount >= pricetag:
        newbal = myamount - pricetag
        id = session['custid']
        updatebal = wallet.update_wallet_by_id(id, newbal)
        return redirect(url_for('finish'))
    else:
        return redirect(url_for('broke_wallet'))


# succesiful wallet
@app.route('/checkout/finish')
def finish():
    if 'custemail' in session:        
        return redirect(url_for('main'))
    else:
        return redirect(url_for('login'))

@app.route('/booked')
def booked():
    allproperty = property.fetch_by_status_occupied()
    flash('booking was made succesifully.', 'success')
    return render_template('dash.html', allproperty=allproperty)


# no money in wallet
@app.route('/wallet/broke', methods=['POST', 'GET'])
def broke_wallet():
    id = session['thisid']
    booking_id = bookings.get_booking_id_by_property_id(id)
    delete = bookings.delete_by_id(booking_id)
    update_status = property.update_property_by_id(id)
    flash('You don not have enough funds.Please recharge and try again later', 'danger')
    return render_template('recharge.html')

# customer login render template
@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/buyer/login', methods=['GET', 'POST'])
def buyer_login():
    if request.method == 'POST':
        # try:
        email = request.form['email']
        password = request.form['password']

        # check if email exist
        if customers.check_email_exist(email):
            if customers.validate_password(email=email, password=password):
                session['custemail'] = email
                session['custid'] = customers.get_customer_id(email)
                return redirect(url_for('main'))
            else:
                flash('Invalid login credentials', 'danger')
                return redirect(url_for('login'))
        else:
            flash('Invalid login credentials', 'danger')
            return redirect(url_for('login'))
    # except Exception as e:
        # print(e)

    return render_template('login.html')

# start page loader
@app.route('/admin')
def admin():
    if 'email' in session:
        return render_template('admindash.html')
    else:
        return redirect('/owner/login')

# check booked property
@app.route('/property/status', methods=['POST', 'GET'])
def property_status():
    if 'email' in session:
        allr = bookings.fetch_all()
        return render_template('propertytatus.html', allr=allr)
    else:
        return redirect(url_for('owner_login'))


@app.route('/property/status/clear')
def clear_status():
    if session:
        bookings.delete_all()
        return redirect(url_for('property_status'))
    else:
        return redirect('/owner/login')
# view property
@app.route('/property/all', methods=['GET', 'POST'])
def property_all():
    if 'email' in session:
        allr = property.fetch_all()
        return render_template('allproperty.html', allr=allr)
    else:
        return redirect(url_for('owner_login'))

# landlord upload new property is processed here
@app.route('/home', methods=['GET', 'POST'])
def upload_property():
    if 'email' in session:
        if request.method == 'POST':
            print(session['email'])
            image_url = upload_file(request.files)
            location = request.form['location']
            description = request.form['description']
            price = request.form['price']
            x = property(img=image_url, location=location,
                        description=description, price=price)
            x.insert_record()

            print('record successfully added')

            return render_template('admindash.html')
    else:
        return redirect(url_for('owner_login'))

    return render_template('admindash.html')

# property booking
@app.route('/property/book', methods=['GET', 'POST'])
def bid():
    if 'custemail' in session:
        if request.method == 'POST':
            property_id = request.form['id']
            email = session['custemail']
            mdate = request.form['date']
            session['thisid'] = property_id
            b = bookings(property_id=property_id,
                         customer_email=email, movein_date=mdate)
            b.insert_record()
            print('booking successfull')
            up = property.update_property_by_id(id=property_id)
            print('update succesiful')
            return redirect(url_for('check_out'))
        else:
            return redirect(url_for('main'))

    else:
        return redirect(url_for('login'))


@app.route('/property/checkout')
def check_out():
    if 'custemail' in session:
        email = session['custemail']
        id = customers.get_customer_id(email)
        rid = session['thisid']
        thisproperty = property.get_property_by_id(rid)
        return render_template('checkout.html', thisproperty=thisproperty)
    else:
        return redirect(url_for('main'))

@app.route('/wallet/status')
def WalletStatus():
    id = session['custid']
    CuracquireAmount = wallet.view_curacquire_amount(id)
    date = datetime.date.today()
    return render_template('mywallet.html',amount = CuracquireAmount,date = date)


# update wallet
@app.route('/wallet/recharge', methods=['POST', 'GET'])
def recharge_wallet():
    if 'custemail' in session:
        return render_template('rechargewallet.html')
    else:
        return redirect(url_for('login'))

# walletrecharge
@app.route('/walletupdate', methods=['POST', 'GET'])
def walletrecharge():
    entry = request.form['amount']
    id = session['custid']
    new = entry
    newentry = int(new)
    Curacquire = wallet.view_curacquire_amount(id)
    CuracquireAmount = int(Curacquire) 
    newamount = newentry + CuracquireAmount
    update = wallet.update_wallet_by_id(id, newamount)
    return redirect(url_for('WalletStatus'))

# update  status
@app.route('/status/update/<int:id>', methods=['GET', 'POST'])
def update_status(id):
    if request.method == 'POST':
        print(id)
        up = property.update_property_by_id(id=id)
        if up:
            flash('update successful', 'success')
            return redirect(url_for('property_all'))
        else:
            flash('record not found', 'danger')
            return redirect(url_for('property_all'))
    else:
        return redirect(url_for('property_all'))

# @app.route('/status/update/error-outcome')
# def status_error():
#     allr = property.fetch_all()
#     flash("An error occured","danger")
#     return render_template('allproperty.html', allr=allr)

# delete a product
@app.route('/delete/<int:id>', methods=['POST'])
def delete(id):
    deleted = property.delete_by_id(id)
    if deleted:
        flash("Deleted Succesfully", 'success')
        return redirect(url_for('property_all'))
    else:
        flash("Record not found", 'danger')
        return redirect(url_for('property_all'))

# @app.route('/reset')
# def buyer_reset_password():
#     return render_template('reset.html')

# @app.route('/buyereset',methods=['POST'])
# def buyer_reset():
#     return 'done'

@app.route('/owner/reset')
def owner_reset_password():
    return render_template('admingetcode.html')


@app.route('/owner/resetpass',methods = ['POST','GET'])
def owner_reset():
    if request.method == 'POST':
        email = request.form['email']        
        if owners.check_email_exist(email):
            t = randomgenerator()
            print(t)
            return f'true'
        else:
            flash('email doesn not exist','danger')
            return redirect(url_for('owner_reset_password'))
    else:
        flash('Incorrect method','danger')
        return redirect(url_for('owner_reset_password'))

    return render_template('adminreset.html')



@app.route('/owner/api/reset',methods=['POST'])
def api_reset():
    password = request.form['password']
    confirmpass = request.form['confirmpassword']
    if password != confirmpass:
            flash('Passwords dont match', 'danger')
            return redirect(url_for('owner_reset'))
    else:
        flash('Password reset', 'success')
        return redirect(url_for('admin'))
    return redirect(url_for('owner_reset_password'))


@app.route('/owner/logout', methods=['POST'])
def logout_owner():
    session.clear()
    return redirect(url_for('admin'))


@app.route('/customer/logout', methods=['POST'])
def logout_customer():
    session.clear()
    return redirect(url_for('main'))


# debug mode
if __name__ == "__main__":
    app.run(debug=True)
