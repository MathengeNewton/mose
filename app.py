from flask import Flask, render_template, url_for, session, redirect, jsonify, request, flash
from flask_sqlalchemy import SQLAlchemy
from PIL import Image
from flask_bcrypt import Bcrypt
import time
import datetime
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:mathenge,./1998@localhost/mainapp'
app.config['SECRET_KEY'] = 'some=secret+key'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
UPLOAD_FOLDER = os.getcwd() + '/static/uploads/images'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
from models import * 

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
@app.route('/', methods=['POST', 'GET'])
def main():
    allrentals = rentals.fetch_by_status_occupied()
    return render_template('dash.html', allrentals=allrentals)

# log in page is initiated here
@app.route('/gateway')
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
        elif(owners.check_email_exist(email)):
            flash('Email already in use', 'danger')
            return redirect(url_for('owner_register'))
        else:
            hashpassword = bcrypt.generate_password_hash(
                password).decode('utf-8')

            y = owners(name=name, email=email,
                       phone_number=phone, password=hashpassword)
            y.insert_record()

            flash('Account successfully created', 'success')
            return redirect(url_for('owner_login'))

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
            y = customers(name=name, email=email,
                          phone_number=phone, password=hashpassword)
            y.insert_record()
        return redirect(url_for('login'))

    else:
        flash('Try again','danger')
        return redirect(url_for('registration'))



# check wallet ballance
@app.route('/finish-booking/<int:pid>', methods=['POST'])
def finish_booking(pid):
    if 'custemail' in session:
        try:
            e = session['custemail']
            tnow = datetime.datetime.now()
            createbooking = bookings(rental_id = pid,customer_email = e,booking_date = tnow)
            createbooking.insert_record()
            updaterental = rentals.update_rental_by_id(pid)
            flash('Booking reservation made','success')
            return redirect(url_for('main'))
        except:
            flash('Booking failed','danger')
            return redirect(url_for('main'))

    else:
        return redirect(url_for('login'))





# customer login render template
@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/tenant/login', methods=['GET', 'POST'])
def tenant_login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
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
    return render_template('login.html')



@app.route('/admin')
def admin():
    if 'email' in session:
        return render_template('admindash.html')
    else:
        return redirect(url_for('owner_login'))


@app.route('/rentals/status', methods=['POST', 'GET'])
def rental_status():
    if 'email' in session:
        allr = bookings.fetch_all()
        return render_template('rentalstatus.html', allr=allr)
    else:
        return redirect(url_for('owner_login'))



@app.route('/rentals/status/clear')
def clear_status():
    if 'email' in session:
        bookings.delete_all()
        return redirect(url_for('rental_status'))
    else:
        return redirect(url_for('owner_login'))
        


@app.route('/rentals/all', methods=['GET', 'POST'])
def rentals_all():
    if 'email' in session:
        allr = rentals.fetch_all()
        print(allr)
        return render_template('allrentals.html', allr=allr)
    else:
        return redirect(url_for('owner_login'))

@app.route('/view/bookings/<int:fid>')
def view_booking(fid):
    if 'email' in session:
        details = bookings.get_booking_by_id(fid)
        if details:
            mylist = []
            mydict = {'id':details.id}         
            rid = details.rental_id
            rdets  = rentals.get_rental_by_id(rid)
            mydict['image'] = rdets.img
            owner = rdets.owner
            ownerdetails = owners.get_owner_by_id(owner)
            mydict['ownertel'] = ownerdetails.phone_number
            mydict['owner'] = ownerdetails.name
            customerdets = customers.get_customer_by_email(details.customer_email)
            mydict['customer'] = customerdets.name
            mydict['customer_phone'] = customerdets.phone_number 
            mylist.append(mydict)
            print(mydict)
            return render_template('bookingdetails.html',details = mylist)
        else:
            flash('No data available','danger')
            return render_template('bookingdetails.html')
    else:
        return redirect(url_for('owner_login'))

@app.route('/rental-details/<int:rid>')
def rental_details(rid):
    if 'email' in session:
        rentaldets = rentals.get_rental_detail_by_id(rid)
        return render_template('rentaldetail.html',allr = rentaldets)
    else:
        return redirect(url_for('owner_login'))

@app.route('/update/<int:rid>')
def rental_update_page(rid):
    if 'email' in session:
        rentaldets = rentals.get_rental_detail_by_id(rid)
        return render_template('rentalupdate.html',details = rentaldets)
    else:
        return redirect(url_for('owner_login'))



@app.route('/updaterental/<int:rid>' ,methods=['POST'])
def update_rental_details(rid):
    if 'email' in session:
        location = request.form['location']
        description = request.form['description']
        price = request.form['price']
        status = request.form['status']
        update = rentals.update_rental_details(rid,location,description,price,status)
        rentaldets = rentals.get_rental_by_id(rid)
        if update:
            rentaldets = rentals.get_rental_detail_by_id(rid)
            flash('Update complete.','success')
            return render_template('rentaldetail.html',allr = rentaldets)
        else:
            flash('Update not done. Please try again later','danger')
            return render_template('rentalupdate.html') 
    else:
        return redirect(url_for('owner_login'))
        


@app.route('/home', methods=['GET', 'POST'])
def upload_rental():
    if 'email' in session:
        if request.method == 'POST':
            print(session['email'])
            image_url = upload_file(request.files)
            location = request.form['location']
            description = request.form['description']
            price = request.form['price']
            ownerid = session['uid']           
            x = rentals(img=image_url, location=location,
                        description=description, price=price,owner = ownerid)
            x.insert_record()

            print('record successfully added')

            return render_template('admindash.html')
    else:
        return redirect(url_for('owner_login'))

    return render_template('admindash.html')

# rental booking
@app.route('/rental-book/<int:pid>', methods=['POST'])
def bid(pid):
    if 'custemail' in session:
        if request.method == 'POST':            
            email = session['custemail']   
            id = customers.get_customer_id(email)
            thisrental = rentals.get_rental_detail_by_id(pid)
            ownerid = rentals.get_rental_owner_by_id(pid)
            owner = owners.get_owner_details_by_id(ownerid)
            print(owner)
            return render_template('checkout.html', thisrental=thisrental,owners = owner)
        else:
            return redirect(url_for('main'))

    else:
        return redirect(url_for('login'))


# delete a product
@app.route('/delete/<int:id>', methods=['POST'])
def delete(id):
    deleted = rentals.delete_by_id(id)
    if deleted:
        flash("Deleted Succesfully", 'success')
        return redirect(url_for('rentals_all'))
    else:
        flash("Record not found", 'danger')
        return redirect(url_for('rentals_all'))


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
