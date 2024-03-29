from os import error
from flask import request, session, Response
from Flaskapp.forms import LoginForm, signUpForm, adminForm
import json
from Flaskapp import engine, artisans, services, customers, records, db, admin, popular_services, top_rated_artisans
from wtforms_json import from_json
from Flaskapp import app, bcrypt, db
# from Flaskapp.decos import admin_login_required, login_requireds
from datetime import datetime



@app.before_request
def before_request():

    if 'admin' in session:
        app.config['State_Admin'] = True
        # print(State)
    elif 'username' in session:
        # print(State)
        app.config['State'] = True

    else:
        app.config['State'] = None


@app.route('/before_page_load', methods=['GET'])
def before_page_load():

    return {"loggedIn":session['loggedIn'], "admin":session['admin'], "username":session['username'], "id":session['id']}


# --------------------------------------------------------------- LOGIN --------------------------------------------------------------------


@app.route('/login', methods=['POST', 'GET'])
def login():

    # session['loggedin'] = True
    # session['username'] = input("Name")
    # return {"info":"LoggedIn"}

    if request.method == 'POST':

        login_details = request.get_json(force=True)
        # login_details = json.loads(login_details)
        form = LoginForm.from_json(login_details)

        # what to be returned
        return_info = {"alert": "", "message": "", "passed": False, "type": ""}
        # Requires reformating

        # Establishing connection
        connection = engine.connect()

        user = connection.execute(db.select([customers.columns.customer_username]).where(
            customers.columns.customer_username == form.customer_username.data)).fetchall()

        admin_name = connection.execute(db.select([admin.columns.username]).where(
            admin.columns.username == form.customer_username.data)).fetchall()
        try:
            customer_id = connection.execute(db.select([customers.columns.customer_id]).where(
                customers.columns.customer_username == form.customer_username.data)).fetchone()[0]
        except:
            customer_id = None

        if user:
            password = connection.execute(db.select([customers.columns.password]).where(
                customers.columns.customer_username == form.customer_username.data)).fetchall()

            if bcrypt.check_password_hash(password[0][0], form.password.data):
                # log the user in

                # session['loggedin'] = True
                # session['id'] = customer_id
                # session['username'] = 'username'

                # return to the dashboard of the user
                return_info["passed"] = True
                return_info["alert"] = "success"
                return_info["message"] = "Successfully logged in"
                return_info["type"] = "customer"
                return_info["user"] = str(customer_id)

                return return_info

            else:
                return_info["alert"] = "danger"
                return_info["message"] = "Invalid credentials"
                return return_info

        elif admin_name:
            password = connection.execute(db.select([admin.columns.password]).where(
                admin.columns.username == form.customer_username.data)).fetchall()

            if bcrypt.check_password_hash(password[0][0], form.password.data):
                # log the user in

                # session['loggedin'] = True
                # session['id'] = customer_id
                # session['username'] = 'username'
                # session['admin'] = True

                # return to the dashboard of the user
                return_info["passed"] = True
                return_info["alert"] = "success"
                return_info["message"] = "Successfully logged in"
                return_info["type"] = "admin"
                return return_info

            else:
                return_info["alert"] = "danger"
                return_info["message"] = "Invalid credentials"
                return return_info

        else:
            return_info["alert"] = "danger"
            return_info["message"] = "Invalid credentials"
            return return_info


# ----------------------------------------------------------------- SIGN UP ----------------------------------------------------------

@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':

        request_react = request.get_json(force=True)
        # hashing password before converting json to form
        password = bcrypt.generate_password_hash(
            str(request_react['password'])).decode('utf-8')
        request_react['password'] = password
        customer_email = request_react.get("email")
        customer_username = request_react.get('customer_username')

        # Establishing connection
        connection = engine.connect()

        exist_email = connection.execute(db.select([customers.columns.email]).where(
            customers.columns.email == customer_email)).fetchall()
        exist_username = connection.execute(db.select([customers.columns.customer_username]).where(
            customers.columns.customer_username == customer_username)).fetchall()

        if exist_email:
            return {"message": f"Account or Username already exists", "alert": "danger", "passed": False}
        else:
            try:
                connection.execute(
                    db.insert(customers).values([dict(request_react)]))
                return {"message": f"Account successfully created for {request_react.get('customer_username')}", "alert": "success", "passed": True}
            except(error):
                return Response(status=500)


# ------------------------------------------------------- ADMINISTRATOR -------------------------------------------------------

@app.route('/register/admin', methods=['GET', 'POST'])
def Admin_register():

    if request.method == 'POST':

        request_react = request.get_json(force=True)
        # hashing password before converting json to form
        password = bcrypt.generate_password_hash(
            str(request_react['password'])).decode('utf-8')
        request_react['password'] = password

        form = adminForm.from_json(request_react)

        if form.validate():
            # -------------------------------------------
            # Database commiting and further validation
            # Establishing connection
            connection = engine.connect()
            connection.execute(db.insert(admin).values([dict(request_react)]))
            # -------------------------------------------
            return {"message": f"Account successfully created for {request_react.get('customer_username')}", "alert": "success", "passed": True}
        else:
            return {"Errors": form.errors}

    # to be changed
    return {"Page": "Sign Up"}  # return to dashboard route


@app.route('/admin/artisan_table', methods=['GET'])
def artisan_table():
    # Establishing connection
    connection = engine.connect()
    query = connection.execute(db.select([artisans])).fetchall()
    result = {}
    for num, i in enumerate(query):
        result[str(num)] = {"id": f"{i[0]}",
                            "service_id": f"{i[1]}",
                            "first_name": f"{i[2]}",
                            "last_name": f"{i[3]}",
                            "rating": f"{i[4]}",
                            "address": f"{i[5]}",
                            "contact": f"{i[6]}",
                            "profile_image_path": f"{i[7]}",
                            "skill":f"{connection.execute(db.select(services).where(services.columns.service_id == i[1])).fetchall()[0][0]}"}

    return result


@app.route('/admin/customer_table', methods=['GET'])
def customer_table():
    # Establishing connection
    connection = engine.connect()
    query = connection.execute(db.select([customers])).fetchall()
    result = {}
    for num, i in enumerate(query):
        result[str(num)] = {"customer_id": f"{i[0]}",
                            "customer_username": f"{i[1]}",
                            "first_name": f"{i[2]}",
                            "last_name": f"{i[3]}",
                            "contact": f"{i[4]}",
                            "address": f"{i[5]}",
                            "email": f"{i[6]}",
                            "profile_image_path": f"{i[8]}"}

    return result


# to be tested -----------------------------
@app.route('/admin/<string:table>/edit/<string:id>', methods=['POST', 'DELETE'])
def edit_table(id, table):

    reference = {"artisans": [artisans, artisans.columns.artisan_id],
                 "customers": [customers, customers.columns.customer_id]}

    if request.method == 'POST':

        artisan = request.get_json(force=True)

        # Establishing connection
        connection = engine.connect()

        try:
            connection.execute(
                db.insert(artisans).values([dict(artisan)]))
            return {"message": f"Artisan {artisan.get('last_name')} successfully added", "alert": "success", "passed": True}
        except(error):
            return Response(status=500)

    elif request.method == 'DELETE':

        # Establishing connection
        connection = engine.connect()

        connection.execute(db.delete(records).where(
            records.columns.artisan_id == int(id)))
        connection.execute(db.delete(reference[table][0]).where(
            reference[table][1] == int(id)))
        return {"Info": "Done"}


# to be changed
@app.route('/admin/report/<int:id>', methods=['GET', 'DELETE'])
def reports(id):
    # Establishing connection
    connection = engine.connect()

    if request.method == 'DELETE':
        connection.execute(db.delete(records).where(
            records.columns.record_id == int(id)))

    if request.method == 'GET':
        query = connection.execute("""SELECT r1.record_id, artisans.first_name, artisans.last_name, customers.first_name, customers.last_name, services.skill, r1.date 
        FROM records as r1 
        INNER JOIN services ON r1.service_id = services.service_id 
        INNER JOIN artisans ON r1.artisan_id = artisans.artisan_id 
        INNER JOIN customers ON r1.customer_id = customers.customer_id 
        ORDER BY r1.date DESC""").fetchall()

        result = {}
        for num, i in enumerate(query):
            result[str(num)] = {"record_id": f"{i[0]}",
                                "artisan": f"{i[1]} {i[2]}",
                                "customer": f"{i[3]} {i[4]}",
                                "skill": f"{i[5]}",
                                "date": f"{i[6]}"}

        return result


@app.route('/admin/services/<int:id>', methods=['POST', 'GET', 'DELETE'])
def get_admin_services(id):

    # Establishing connection
    connection = engine.connect()

    if request.method == 'POST':

        service = request.get_json(force=True)
        # adding a service
        if id == 0:
            connection.execute(db.insert(services).values([dict(service)]))
            return {"message": f"{service.get('skill')} successfully added", "alert": "success", "passed": True}
        else:
            connection.execute(db.update(services).values(skill = service['skill'], description = service['description'], image_path = service['image_path']).where(services.columns.service_id == id))
            return {"message": f"{service.get('skill')} successfully updated", "alert": "success", "passed": True}

    if request.method == 'GET':
        query = connection.execute( db.select([services]).where(services.columns.service_id == id)).fetchall()
        return_items = [{**row} for row in query]
        return_items = json.dumps(return_items, default=str)
        return return_items
        # for num, i in enumerate(query):
        #     result[str(num)] = {"name":i[1], "id":i[0]}

        # return result

    if request.method == 'DELETE':
        connection.execute(db.delete(services).where(services.columns.service_id == id))


@app.route('/admin/update/artisan/<int:id>', methods=['GET', 'POST'])
def update_artisan(id):
    connection = engine.connect()

    if request.method == 'GET':
        query = connection.execute(
                        db.select([artisans]).where(artisans.columns.artisan_id == id)).fetchall()
        return_items = [{**row} for row in query]
        return_items = json.dumps(return_items, default=str)
        return return_items
      

    if request.method == 'POST':
        
        artisan_update = request.get_json(force=True)
        print(artisan_update)

        connection.execute(db.update(artisans).values(service_id = artisan_update['service_id'], first_name = artisan_update['first_name'], last_name = artisan_update['last_name'], contact = artisan_update['contact'], address = artisan_update['address']).where(artisans.columns.artisan_id == id))

        return {"message": f"Artisan {artisan_update.get('last_name')} successfully updated", "alert": "success", "passed":True}

# -------------------------------------------------------------- VIEWS -----------------------------------------------------------------

@app.route('/top_rated_artisans')
def popular_artisans():
    # Establishing connection
    connection = engine.connect()

    top_rated_artisans_list = connection.execute(
        db.select([top_rated_artisans])).fetchall()

    return_items = [{**row} for row in top_rated_artisans_list]
    return_items = json.dumps(return_items, default=str)
    return return_items


@app.route('/popular_service')
def popularServices():
    # Establishing connection
    connection = engine.connect()

    query = connection.execute(
        db.select([popular_services])).fetchall()
    return_items = [{**row} for row in query]
    return_items = json.dumps(return_items, default=str)
    return return_items


@app.route('/services')
def Services():
    # Establishing connection
    connection = engine.connect()

    query = connection.execute(db.select([services])).fetchall()
    result = {}

    for num, i in enumerate(query):
        result[str(num)] = {
            "id": f"{i[0]}","service": f"{i[1]}",
                            "description": f"{i[2]}", "image": f"{i[3]}"}

    return result



@app.route('/service/<int:service_id>')
def get_service(service_id):
      # Establishing connection
    connection = engine.connect()
    query = connection.execute(
        db.select([services.columns.service_id, services.columns.skill]).where(services.columns.service_id==service_id)).fetchall()

    result = {}
    for i in query:
        artisan_group = connection.execute(db.select([artisans.columns.artisan_id, artisans.columns.first_name,
                                                      artisans.columns.address,
                                                      artisans.columns.rating,
                                                      artisans.columns.profile_image_path]).where(artisans.columns.service_id == i[0])).fetchall()

        artisan_group_list = [{"id": f"{i[0]}", "Name": f"{i[1]}", "Address": f"{i[2]}",
                               "rating": f"{i[3]}", "Path": f"{i[4]}"} for i in artisan_group]
        result[i[1]] = artisan_group_list

    return result


# -------------------------------------------------------------------- CUSTOMER ROUTES --------------------------------------------------

@app.route('/logout', methods=['GET', 'POST'])
def logout():

    # session.pop('loggedin', None)
    # # id
    # session.pop('username', None)

    return {"info": 'back to login route'}


@app.route('/delete_account', methods=['DELETE'])
def delete_account():
    print(session['username'])
    # Establishing connection
    connection = engine.connect()

    # logout()
    # connection.execute(db.delete(customers).where(customers.columns.customer_id == int(id)))

# To be worked on
@app.route('/report/<int:customer_Id>')
def report(customer_Id):
    # Establishing connection
    connection = engine.connect()

    query = connection.execute(
        f"SELECT r1.record_id, artisans.first_name, artisans.last_name, services.skill, r1.date, r1.rating, r1.status, record_statuses.name, r1.artisan_id FROM records as r1 INNER JOIN services ON r1.service_id = services.service_id INNER JOIN artisans ON r1.artisan_id = artisans.artisan_id INNER JOIN record_statuses ON r1.status = record_statuses.record_status_id WHERE r1.customer_id = {customer_Id} ORDER BY r1.date DESC ").fetchall()

    result = {}
    for i in query:
        result[str(i[0])] = {"Artisan_name": f"{i[1]} {i[2]}",
                             "Skill": f"{i[3]}", "Date": f"{i[4]}", "rating":f"{i[5]}", "status":f"{i[7]}", "artisan_id":f"{i[8]}"}

    return result


@app.route('/confirm_order/<int:artisan_id>/<int:customer_id>')
def confirm_id(artisan_id, customer_id):
    # Establishing connection
    connection = engine.connect()

    service = connection.execute(db.select(artisans.columns.service_id).where(
        artisans.columns.artisan_id == artisan_id)).fetchall()

    connection.execute(db.insert(records).values(customer_id=customer_id,
                                                 artisan_id=artisan_id, service_id=service[0][0]))

    return {"info": 1}

# update to update record status of record
@app.route('/record_status/<int:record_id>/<int:number>')
def check_rating(record_id, number):
    #select status from records where customer_id = customer_id limit 1
    connection = engine.connect() 
    if number == 0:
        connection.execute(db.update(records).values(status = 2).where(records.columns.record_id == record_id))
    elif number == 1:
        connection.execute(db.update(records).values(status = 4).where(records.columns.record_id == record_id))


    # query = connection.execute(db.select([records]).where(db.and_(
    #     records.columns.customer_id == customer_id, records.columns.status == 1))).fetchone()
    # result = {}
    # for num, i in enumerate(query):
    #     id_=connection.execute(db.select(artisans.columns.first_name).where(artisans.columns.artisan_id == i[2]))
    #     skill = connection.execute(db.select(services.columns.skills).where(services.columns.services_id == i[3]))
        
    #     result[str(num)] = {"record_id": f"{i[0]}",
    #                         "artisan_name": f"{i[2]}",
    #                         "skill": f"{skill}",
    #                         "status": f"{i[5]}"}

    # return result
    return True


def rate(artisan_rating, services_completed,rating):
    return (((artisan_rating*services_completed) + rating)/(services_completed + 1))



@app.route('/rating/<int:record_id>/<int:artisan_id>/<float:rating>')
def rating(record_id,artisan_id,rating):
    connection = engine.connect()
    try:
        artisan_rating = connection.execute(db.select(artisans.columns.rating).where(
        artisans.columns.artisan_id == artisan_id)).fetchall()[0][0]
    except:
        artisan_rating=None

    services_completed = connection.execute(db.select(artisans.columns.services_completed).where(
        artisans.columns.artisan_id == artisan_id)).fetchall()[0][0]
    if artisan_rating:
        new_rating = rate(float(artisan_rating), int(services_completed),float(rating))
    else:
        new_rating = rating
        
        
    # updating the new rating
    connection.execute(db.update(artisans).values(rating = new_rating).where(artisans.columns.artisan_id == artisan_id))
    connection.execute(db.update(records).values(rating = rating).where(records.columns.record_id == record_id))
    #updating the status of the service
    connection.execute(db.update(records).values(status = 3).where(records.columns.record_id == record_id))
    #updating the services completed
    connection.execute(db.update(artisans).values(services_completed = services_completed+1).where(artisans.columns.artisan_id == artisan_id))





# -------------------------------------------------------------------- ARTISAN ROUTES -------------------------------------------------

@app.route('/find_artisan')
def find_artisan():
    # Establishing connection
    connection = engine.connect()

    query = connection.execute(
        db.select([services.columns.service_id, services.columns.skill])).fetchall()

    result = {}
    for i in query:
        artisan_group = connection.execute(db.select([artisans.columns.artisan_id, artisans.columns.first_name,
                                                      artisans.columns.address,
                                                      artisans.columns.rating,
                                                      artisans.columns.profile_image_path]).where(artisans.columns.service_id == i[0])).fetchall()

        artisan_group_list = [{"id": f"{i[0]}", "Name": f"{i[1]}", "Address": f"{i[2]}",
                               "rating": f"{i[3]}", "Path": f"{i[4]}"} for i in artisan_group]
        result[i[1]] = artisan_group_list

    return result


@app.route('/find_artisan/<int:artisan_id>')
def find_artisan_id(artisan_id):
    # Establishing connection
    connection = engine.connect()

    query = connection.execute(db.select([artisans.columns.service_id,
                                          artisans.columns.artisan_id,
                                          artisans.columns.first_name,
                                          artisans.columns.last_name,
                                          artisans.columns.rating,
                                          artisans.columns.address,
                                          artisans.columns.contact,
                                          services.columns.description,
                                          artisans.columns.profile_image_path,
                                          services.columns.skill
                                          ]).select_from(artisans.join(services, artisans.columns.service_id == services.columns.service_id)).where(artisans.columns.artisan_id == artisan_id)).fetchall()

    return {"service_id": f"{query[0][0]}", "artisan_id": f"{query[0][1]}", "Name":f"{query[0][2]} ","first_name": f"{query[0][2]} {query[0][3]}", "last_name":f"{query[0][3]}",
            "rating": f"{query[0][4]}", "Address": f"{query[0][5]}", "contact": f"{query[0][6]}",
            "description": f"{query[0][7]}",
            "Path": f"{query[0][8]}", "Expertise": f"{query[0][9]}"}


# --------------------------------------------------------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------------------------------------------------------


# def login_requireds(*args, **kwargs):

#     def wrapper(original):
#         return original()

#     if kwargs == True:
#         return wrapper
#     else:
#         return {"Info":"Login required"}


# State = None




