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
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.MIMEBase import MIMEBase
from email import Encoders
from sqlalchemy.orm import aliased
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
@login_required
def select_flight():
    from_city = City.query.filter_by(name=request.form['city_from']).first()
    to_city = City.query.filter_by(name=request.form['city_to']).first()
    journeys = db.session.query(Flight,Journey).join(Journey).filter(and_(Journey.from_city_id==from_city.id,Journey.to_city_id==to_city.id, func.strftime('%d-%m-%Y',Journey.date_time) == request.form['date'])).all()
    return render_template("select_flight.html", from_city=from_city, to_city=to_city,journeys =journeys)


@app.route('/book/<int:journey_id>')
@login_required
def book(journey_id):
    journey = Journey.query.get(journey_id)
    from_city = City.query.get(journey.from_city_id)
    to_city = City.query.get(journey.to_city_id)
    flight = Flight.query.get(journey.flight_id)
    return render_template("book_flight.html",journey = journey,to_city= to_city,from_city=from_city,flight= flight,user = g.user)

@app.route('/confirm/<int:journey_id>',methods=['GET', 'POST'])
@login_required
def confirm(journey_id):
    booking = Book(g.user.id,journey_id,request.form['name'],request.form['age'])
    db.session.add(booking)
    db.session.commit()
    journey = Journey.query.get(journey_id)
    from_city = City.query.get(journey.from_city_id)
    to_city = City.query.get(journey.to_city_id)
    flight = Flight.query.get(journey.flight_id)
    html = render_template('pdf.html', booking = booking,journey=journey,from_city=from_city,to_city=to_city,flight=flight)
    fromaddr="admatfastflight@gmail.com"
    toaddr=request.form['email']
    msg = MIMEMultipart()
    msg['Subject'] = "FastFlight Ticket Confirmation"
    msg['From'] = fromaddr
    msg['To'] = toaddr
    part = MIMEText(html) 
    server = smtplib.SMTP("smtp.gmail.com:587")
    server.starttls()
    server.login("admatfastflight@gmail.com","dudeflyfast")
    server.sendmail(fromaddr,toaddr,msg.as_string())
    server.quit()     
    return render_template("confirm.html",booking = booking , email=toaddr)


@app.route('/confirmpdf_<int:booking_id>')
@login_required
def confirm_pdf(booking_id):
    booking = Book.query.get(booking_id)
    journey = Journey.query.get(booking.journey_id)
    from_city = City.query.get(journey.from_city_id)
    to_city = City.query.get(journey.to_city_id)
    flight = Flight.query.get(journey.flight_id)
    html = render_template('pdf.html', booking = booking,journey=journey,from_city=from_city,to_city=to_city,flight=flight)
    return render_pdf(HTML(string=html))

@app.route('/bookinghistory')
@login_required
def booking_history():
    from_city = aliased(City,name="from_city")
    to_city = aliased(City,name="to_city")
    result = db.session.query(Book,Journey,Flight,from_city,to_city).join(Journey).join((Flight,Journey.flight_id==Flight.id)).join((from_city,Journey.from_city_id==from_city.id)).join((to_city,Journey.to_city_id==to_city.id)).filter(Book.user_id == g.user.id).all()
    return render_template('history.html',results=result)

@app.route('/cancel/<int:booking_id>',methods=['GET','POST'])
@login_required
def cancel(booking_id):
    booking = Book.query.get(booking_id)
    if request.method == 'GET':
        return render_template('cancel.html',booking=booking)
    db.session.delete(booking)
    db.session.commit()
    flash('Flight ticket cancelled')
    return redirect(url_for('booking_history'))
    
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login')) 



@app.before_request
def before_request():
    g.user = current_user

