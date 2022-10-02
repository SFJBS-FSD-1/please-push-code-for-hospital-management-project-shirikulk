from flask import Flask, request, jsonify, render_template
from flask_restful import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from http import HTTPStatus
from flask_migrate import Migrate
import os

class Config():
    SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://root:1234@localhost/HospitalDatabase'

class Development_Config(Config):
    SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://root:1234@localhost/HospitalDatabase'

class Production_Config(Config):
    uri = os.environ.get('DATABASE_URL')
    if uri and uri.startswith("postgres://"):
        uri = uri.replace("postgres://","postgresql://",1)
    SQLALCHEMY_DATABASE_URI = uri

env = os.environ.get("ENV","Development")

if env == "Production":
    config_str = Production_Config
else:
    config_str = Development_Config


app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:welcome$1234@localhost/HospitalDatabase'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://root:1234@localhost/HospitalDatabase'
db = SQLAlchemy(app)
# api = Api(app)
migrate = Migrate(app, db)

class Patients(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    phone_number = db.Column(db.BigInteger, nullable=False)
    age = db.Column(db.Integer, nullable=False)
    bed_type = db.Column(db.String(80))
    address = db.Column(db.String(100))
    state = db.Column(db.String(50), nullable=False)
    city = db.Column(db.String(50), nullable=False)
    patient_status = db.Column(db.String(50), nullable=False)

@app.route("/", methods=["GET"])
def home():
    return render_template("homepage.html")

@app.route("/register_patient", methods=["GET", "POST"])
def register_patient():
    if request.method == "GET":
        return render_template("patients.html")

    if request.method == "POST":
        name = request.form["name"]
        phone_number = request.form["phone_number"]
        age = request.form["age"]
        bed_type = request.form["bed_type"]
        address = request.form["address"]
        state = request.form["state"]
        city = request.form["city"]
        patient_status = request.form["patient_status"]

        data = Patients.query.all()
        for patientsdata in data:
            if patientsdata.phone_number == phone_number:
                return render_template("patients.html", status="Patient is already registered")
        else:
                registerpatient = Patients(name=name, phone_number=phone_number, age=age, bed_type=bed_type, address=address, state=state,city=city, patient_status=patient_status)
                db.session.add(registerpatient)
                db.session.commit()
                return render_template("patients.html", patient=name)

@app.route("/getallpatients",methods=["GET"])
def patients_list():
    if request.method == "GET":
        patients = Patients.query.all()
        patientslst = []
        for i in patients:
            pat = {}
            pat['id'] = i.id
            pat['name'] = i.name
            pat['phone_number'] = i.phone_number
            pat['age'] = i.age
            pat['bed'] = i.bed_type
            pat['address'] = i.address
            pat['state'] = i.state
            pat['city'] = i.city
            pat['status'] = i.patient_status
            patientslst.append(pat)
        return render_template("patientsdetails.html",active_patient = patientslst)

@app.route("/getallactivepatient",methods=["GET"])
def active_patients():
    if request.method == "GET":
        pat = Patients.query.all()
        patientlst = []
        for patients in pat:
            data = {}
            if patients.patient_status == 'Active':
                data['id']= patients.id
                data['name'] = patients.name
                data['phone_number'] = patients.phone_number
                data['age'] = patients.age
                data['bed_type'] = patients.bed_type
                data['address'] = patients.address
                data['state'] = patients.state
                data['city'] = patients.city
                data['status'] = patients.patient_status
                patientlst.append(data)
        return render_template("patientsdetails.html",active_patient = patientlst)

@app.route("/getpatient",methods=["GET"])
def patient_details():
    if request.method == "GET":
        return render_template("patientid.html")

@app.route("/getpatientsbyphonenumber", methods=["GET","POST"])
def patient_by_Id():
    if request.method == "POST":
        phone_number = request.form["phone_number"]
        patient = Patients.query.filter_by(phone_number=phone_number).first()
        pat_data = {}
        if patient:
            pat_data = {'id':patient.id, 'name':patient.name,'phone':patient.phone_number,'age':patient.age,'bed':patient.bed_type,'address':patient.address,'state':patient.state,'city':patient.city,'status':patient.patient_status}
            return render_template("patientid.html",data=pat_data)
        else:
            return render_template("patientid.html", update_status="Patient id not Found")

@app.route("/update_patient", methods=["POST"])
def patient_update():
    if request.method == "POST":
        phone_number = request.form["phone_number"]
        patient = Patients.query.filter_by(phone_number=phone_number).first()
        if patient:
            patient_data = {"id":patient.id, "name":patient.name,"phone_number":patient.phone_number, 'age':patient.age, 'bed':patient.bed_type, 'address':patient.address, 'state':patient.state,'city':patient.city, 'status':patient.patient_status}
            return render_template("patientid.html", status =patient_data)
        else:
            return render_template("patientid.html", update_status="Patient id not Found")


@app.route("/update", methods=["POST"])
def update():
    if request.method == "POST":
        name = request.form['name']
        phone_number = request.form['phone_number']
        age = request.form['age']
        bed_type = request.form['bed']
        address=request.form['address']
        state=request.form['state']
        city=request.form['city']
        patient_status=request.form['status']

        pat = Patients(name=name,phone_number=phone_number,age=age,bed_type=bed_type,address=address,state=state,city=city,patient_status=patient_status)
        pat_data = {'name': pat.name, 'phone_number': pat.phone_number,
                        'age': pat.age, 'address': pat.address,
                        'state': pat.state, 'city': pat.city,
                        'patient_status': pat.patient_status, 'bed_type': pat.bed_type
                        }
        Patients.query.filter_by(phone_number=phone_number).update(pat_data)
        db.session.commit()

        # pat_data = {'id': pat.id, 'name': pat.name, 'phone_number': pat.phone_number, 'age': pat.age, 'bed': pat.bed_type, 'address': pat.address, 'state': pat.state, 'city': pat.city, 'status': pat.patient_status}
        return render_template("patientid.html", update=pat_data)

@app.route("/deletepatient", methods=["GET","POST"])
def patient_delete():
    if request.method == "POST":
        phone_number = request.form["phone_number"]
        patient = Patients.query.filter_by(phone_number=phone_number).first()
        if patient:
            Patients.query.filter_by(phone_number=phone_number).delete()
            db.session.commit()
            return render_template("patientid.html", update_status = "patient details deleted successfully")
        else:
            return render_template("patientid.html", update_status = "Patient id not found")

if __name__=="__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(port=port)

#
#     @staticmethod
#     def register_patient(name,phone_number,age,bed_type,address,state,city,patient_status):
#         new_patient = Patients(name=name,phone_number=phone_number,age=age,bed_type=bed_type,address=address,state=state,city=city,patient_status=patient_status)
#         db.session.add(new_patient)
#         db.session.commit()
#
#     @staticmethod
#     def edit_patient(id,age,bed_type,address,state,city,patient_status):
#         data = Patients.query.filter_by(id=id).first()
#         data.age = age
#         data.bed_type = bed_type
#         data.address = address
#         data.state = state
#         data.city = city
#         data.patient_status = patient_status
#
#         db.session.commit()
#
#     @staticmethod
#     def get_patients():
#         data = Patients.query.all()
#         return data
#
#     @staticmethod
#     def get_patients_id(id):
#         data = Patients.query.filter_by(id=id).first()
#         return data
#
#     @staticmethod
#     def get_patients_status(patient_status):
#         data = Patients.query.filter_by(patient_status=patient_status).all()
#         return data
#
#     @staticmethod
#     def delete_patient(id):
#         data = Patients.query.filter_by(id=id).delete()
#         db.session.commit()
#         return data
#
# class allpatients(Resource):
#     def post(self):
#         data=request.get_json()
#         print(data)
#         Patients.register_patient(name=data['name'],phone_number=data['phone_number'],age=data['age'],bed_type=data['bed_type'],address=data['address'],state=data['state'],city=data['city'],patient_status=data['patient_status'])
#         return "new patient details are added"
#
#     def get(self):
#         data = Patients.get_patients()
#         print(data)
#         # patientslst=[]
#         #
#         # for patientsdata in data:
#         #     patientsdict = {'name':patientsdata.name, 'phone_number':patientsdata.phone_number, 'age':patientsdata.age, 'bed_type':patientsdata.bed_type, 'address':patientsdata.address, 'state':patientsdata.state, 'city':patientsdata.city, 'patient_status':patientsdata.patient_status}
#         #     patientslst.append(patientsdict)
#         # # return patientslst
#         return render_template("homepage.html", data=data)
#
# class patient_id(Resource):
#     def put(self, id):
#         data = request.get_json()
#         print(data)
#         Patients.edit_patient(id,data['age'],data['bed_type'],data['address'],data['state'],data['city'],data['patient_status'])
#         if data:
#             return "patient details are successfully updated".format(id)
#         else:
#             return jsonify({'message': 'Patient ID not found', 'status': HTTPStatus.NOT_FOUND})
#
#     def get(self, id):
#         data = Patients.get_patients()
#         for i in data:
#             pat = {}
#             if i.id == id:
#                 pat['name'] = i.name
#                 pat['phone_number'] = i.phone_number
#                 pat['age'] = i.age
#                 pat['bed_type'] = i.bed_type
#                 pat['address'] = i.address
#                 pat['state'] = i.state
#                 pat['city'] = i.city
#                 pat['patient_status'] = i.patient_status
#                 return jsonify((pat),{"status_msg":HTTPStatus.OK})
#         else:
#                 return {'message':'patient id not found','status':HTTPStatus.NOT_FOUND}
#
#
# class del_patient(Resource):
#     def delete(self, id):
#         delete_patient = Patients.delete_patient(id)
#         print(delete_patient)
#         if delete_patient:
#             return "patient details are successfully deleted {0}".format(id)
#         else:
#             return jsonify({'message': 'Patient ID not found', 'status': HTTPStatus.NOT_FOUND})
#
#
# class active_patient(Resource):
#     def get(self, patient_status):
#         data = Patients.get_patients_status(patient_status)
#         pat = []
#         for i in data:
#             activepatient = {'id': i.id, 'phone_number': i.phone_number, 'age': i.age, 'bed_type': i.bed_type, 'address': i.address, 'state': i.state, 'city': i.city, 'patient_status': i.patient_status}
#             pat.append(activepatient)
#         return jsonify((pat),{"status_msg":HTTPStatus.OK})
#
#
# api.add_resource(allpatients,"/register_patient")
# api.add_resource(patient_id,"/edit_patient/<int:id>")
# api.add_resource(del_patient,"/delete_patient/<int:id>")
# api.add_resource(active_patient,"/active_patient/<string:patient_status>")






#after adding the migrate package and migrate commands run below 3 commands
#flask --app movies.py db init
#flask --app movies.py db migrate
#flask --app movies.py db upgrade


#from flask_sqlalchemy_test import db
# db.create_all()
# from flask_sqlalchemy_test import Profile
# admin = Profile(username= "admin",email="shirish@email.com")
#Profile.query.all()
#Profile.query.filter_by(username = 'admin').first()
#add(request.get_json())
#jsonify({'message':'id not found','status':'404'})

#pip install psycopg2
#pip install gunicorn ---functionalities of http server is given by gunicorn