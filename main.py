from app import app
from login import login_manager

from models import *
from views import *

if __name__ == '__main__':
	from sys import argv
	if len(argv) == 1:
		app.run()
	elif argv[1] == 'initdb':
		from testdata import *
		db.session.commit()		
		with app.app_context():
			db.drop_all()
			db.create_all()
			for u in cities:
				db.session.add(City(u['name']))
			for u in flights:
				db.session.add(Flight(u['name'], u['max_seats']))
			for u in journeys:
				db.session.add(Journey(u['date'], u['from_city_id'],u['to_city_id'],u['flight_id'],u['fare']))		
			db.session.commit()
