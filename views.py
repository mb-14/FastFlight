from flask import session, request, flash, url_for, redirect, render_template, abort ,g , make_response
from app import app
from datetime import datetime
from models import *
from flask.ext.login import login_user , logout_user , current_user , login_required
from functools import wraps
from authomatic.adapters import WerkzeugAdapter
from authomatic import Authomatic
from config import CONFIG
from sqlalchemy import *
from flask_weasyprint import HTML, render_pdf
import smtplib
authomatic = Authomatic(CONFIG, 'abcde', report_errors=False)
@app.route('/', methods=['GET', 'POST'])
def index():
    if g.user.is_authenticated():
        return render_template('search.html')
    else:
        return redirect(url_for('login'))

@app.route('/login')
def login():
	return render_template("login.html")
		
@app.route('/login/google',methods=['GET', 'POST'])
def login_google():
    # We need response object for the WerkzeugAdapter.
    response = make_response()
    # Log the user in, pass it the adapter and the provider name.
    result = authomatic.login(WerkzeugAdapter(request, response), 'google')
    user = None
    if result:
        if result.user:
            result.user.update()
            user = User.query.filter_by(email=result.user.email).first()
            if user is None:
                user = User(result.user.email,result.user.name)
                db.session.add(user)
                db.session.commit()
        login_user(user, remember = True)
        return redirect(request.args.get('next') or url_for('index'))
    return response

@app.route('/selectflight',methods=['GET', 'POST'])
def select_flight():
    from_city = City.query.filter_by(name=request.form['city_from']).first()
    to_city = City.query.filter_by(name=request.form['city_to']).first()
    print request.form['date']
    journeys = db.session.query(Flight,Journey).join(Journey).filter(and_(Journey.from_city_id==from_city.id,Journey.to_city_id==to_city.id, func.strftime('%d-%m-%Y',Journey.date_time) == request.form['date'])).all()
    return render_template("select_flight.html", from_city=from_city, to_city=to_city,journeys =journeys)


@app.route('/book/<int:journey_id>')
def book(journey_id):
    journey = Journey.query.get(journey_id)
    from_city = City.query.get(journey.from_city_id)
    to_city = City.query.get(journey.to_city_id)
    flight = Flight.query.get(journey.flight_id)
    return render_template("book_flight.html",journey = journey,to_city= to_city,from_city=from_city,flight= flight,user = g.user)

@app.route('/confirm/<int:journey_id>',methods=['GET', 'POST'])
def confirm(journey_id):
    journey = Journey.query.get(journey_id)
    from_city = City.query.get(journey.from_city_id)
    to_city = City.query.get(journey.to_city_id)
    flight = Flight.query.get(journey.flight_id)
    #subject = "FastFlight Booking Confirmation"
    #receiver = request.form['email']
    #mail_to_be_sent = Message(subject=subject, recipients=[receiver])
    #mail_to_be_sent.body = "Please find attached your flight ticket document. Thank you for using FastFlight"
    #html = render_template('pdf.html',name = request.form['name'],age=request.form['age'],journey=journey,from_city=from_city,to_city=to_city,flight=flight)
    #pdf = HTML(string = html).write_pdf()
    #mail_to_be_sent.attach("booking_confirmation.pdf", "application/pdf", pdf.getvalue())
    #mail_ext.send(mail_to_be_sent)
    fromaddr="admatfastflight@gmail.com"
    toaddr=request.form['email'] 
    msg ="""From: FastFlight <admatfastflight@gmail.com>
To:<"""+toaddr+">"+"""
Subject: Booking Successful

This is a test e-mail message.
"""
    server = smtplib.SMTP("smtp.gmail.com:587")
    server.starttls()
    server.login("admatfastflight@gmail.com","dudeflyfast")
    server.sendmail(fromaddr,toaddr,msg)
    server.quit()     
    return render_template("confirm.html",journey = journey,email=request.form['email'],name=request.form['name'],age=request.form['age'])


@app.route('/confirmpdf_<int:journey_id>')
def confirm_pdf(journey_id):
    journey = Journey.query.get(journey_id)
    print journey.flight_id
    from_city = City.query.get(journey.from_city_id)
    to_city = City.query.get(journey.to_city_id)
    flight = Flight.query.get(journey.flight_id)
    html = render_template('pdf.html', name = request.args['name'],age=request.args['age'],journey=journey,from_city=from_city,to_city=to_city,flight=flight)
    return render_pdf(HTML(string=html))

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login')) 

@app.before_request
def before_request():
    g.user = current_user

