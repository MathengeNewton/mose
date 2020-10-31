from app import db,bcrypt


class customers(db.Model):
    id = db.Column(db.Integer, nullable=False,
                   primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), nullable=False, unique=True)
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

    @classmethod
    def get_customer_by_email(cls, email):
        return cls.query.filter_by(email=email).first()

# db owner relation class


class owners(db.Model):
    id = db.Column(db.Integer, nullable=False,
                   primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), nullable=False, unique=True)
    phone_number = db.Column(db.String(30), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)

    # insert new user class

    def insert_record(self):
        db.session.add(self)
        db.session.commit()

    # check if email is in use
    @classmethod
    def check_email_exist(cls, email):
        owners = cls.query.filter_by(email=email).first()
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

    @classmethod
    def get_owner_by_id(cls, id):
        return cls.query.filter_by(id = id).first()

    @classmethod
    def get_owner_details_by_id(cls, id):
        return cls.query.filter_by(id = id)


class rentals(db.Model):
    id = db.Column(db.Integer, nullable=False,
                   primary_key=True, autoincrement=True)
    img = db.Column(db.String(), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(1000), nullable=False)
    price = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(), nullable=False, default='vacant')
    owner = db.Column(db.Integer,nullable = False)

    # insert rental

    def insert_record(self):
        db.session.add(self)
        db.session.commit()

    # fetch all rentals
    @classmethod
    def fetch_all(cls):
        return cls.query.all()

    # fetch where status is 1
    @classmethod
    def fetch_by_status_occupied(cls):
        return cls.query.filter_by(status=u'vacant')

    # get rental by id
    @classmethod
    def get_rental_by_id(cls, id):
        return cls.query.filter_by(id=id).first()
    @classmethod
    def get_rental_detail_by_id(cls, id):
        return cls.query.filter_by(id=id)

    @classmethod
    def get_rental_owner_by_id(cls, id):
        return cls.query.filter_by(id=id).first().owner

    @classmethod
    def get_rental_price(cls, id):
        return cls.query.filter_by(id=id).first().price
    # update status
        # update rental

    @classmethod
    def update_rental_details(cls,id,location,description,price,status):
        rental = cls.query.filter_by(id = id).first()
        if rental:
            try:
                rental.location = location
                rental.description = description
                rental.price = price
                rental.status = status
                db.session.commit()
                return True
            except:
                return False
        else:
            return False


    @classmethod
    def update_rental_by_id(cls, id):
        rental = cls.query.filter_by(id=id).first()

        if rental:
            status = rental.status
            if status:
                if status == 'booked':
                    newstatus = 'vacant'
                    rental.status = newstatus
                    db.session.commit()
                    return True
                else:
                    newstatus = 'booked'
                    rental.status = newstatus
                    db.session.commit()
                    return True
            else:
                return False
        else:
            return False

    # delete rental by id
    @classmethod
    def delete_by_id(cls, id):
        rental = cls.query.filter_by(id=id)
        if rental.first():
            rental.delete()
            db.session.commit()
            return True
        else:
            return False


class bookings(db.Model):
    id = db.Column(db.Integer, nullable=False,
                   primary_key=True, autoincrement=True)
    rental_id = db.Column(db.Integer)
    booking_date = db.Column(db.Date)
    customer_email = db.Column(db.String)


    def insert_record(self):
        db.session.add(self)
        db.session.commit()


    @classmethod
    def fetch_all(cls):
        return cls.query.all()

   
   
    @classmethod
    def get_booking_id_by_rental_id(cls, id):
        return cls.query.filter_by(rental_id=id).first().id

    @classmethod
    def get_booking_by_id(cls, fid):
        tw =  cls.query.filter_by(id=fid).first()
        if tw:

            return tw
        else:
            return False


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

