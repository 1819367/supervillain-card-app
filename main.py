import os #added for database initialization on Render
import webbrowser 
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from threading import Timer
import sqlalchemy as sa #added for database initialization on Render

app = Flask("app")
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get('DATABASE_URL', "sqlite:///villain.db") #Updated to use the PostgreSQL database by Render
db = SQLAlchemy(app)

class Villain(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.String(120), nullable=False)
    interests = db.Column(db.String(250), nullable=False)
    url = db.Column(db.String(250), nullable=False)
    date_added = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return "<Villain "+ self.name + ">"

with app.app_context():
	db.create_all()
	db.session.commit()
  
# New code for database to initialize and deployment on Render
engine = sa.create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
inspector = sa.inspect(engine)
if not inspector.has_table("villain"):
    with app.app_context():
        db.create_all()
        app.logger.info('Initialized the database!')
else:
    app.logger.info('Database already contains the villain table.')


#### Serving Static Files
@app.route("/")
def villain_cards():
  return app.send_static_file("villain.html")

@app.route("/add")
def add():
  return app.send_static_file("addvillain.html")

@app.route("/delete")
def delete():
  return app.send_static_file("deletevillain.html")
####

#ADD CODE: add /api/villains route here
@app.route("/api/villains/", methods=["GET"])
def get_villains():
  villains = Villain.query.all()
  data = []
  for villain in villains: 
    data.append({
      "name": villain.name,
      "description": villain.description,
      "interests": villain.interests,
      "url": villain.url,
      "date_added": villain.date_added
    })
  return jsonify(data)

@app.route("/api/villains/add", methods=["POST"])
def add_villain():
  errors = []
  name = request.form.get("name")

  if not name:
    errors.append("Oops! Looks like you forgot a name!")

  description = request.form.get("description")
  if not description:
    errors.append("Oops! Looks like you forgot a description!")
  
  interests = request.form.get("interests")
  if not interests:
    errors.append("Oops! Looks like you forgot some interests!")
  
  url = request.form.get("url")
  if not url:
    errors.append("Oops! Looks like you forgot an image!")
  
  villain = Villain.query.filter_by(name=name).first()
  if villain:
    errors.append("Oops! A villain with that name already exists!")
  
  if errors:
    return jsonify({"errors": errors})
  else:
    new_villain = Villain(name=name,description=description, interests=interests, url=url)
    db.session.add(new_villain)
    db.session.commit()
    return jsonify({"status": "success"})

@app.route("/api/villains/delete", methods=["POST"])
def delete_villain():
  name = request.form.get("name", "")
  villain = Villain.query.filter_by(name=name).first()
  if villain:
    db.session.delete(villain)
    db.session.commit()
    return jsonify({"status": "success"})
  else:
    return jsonify({"errors": ["Oops! A villain with that name doesn't exist!"]})

@app.route("/api/", methods=["GET"])
def get_endpoints():
    endpoints = {
        "/api/villains": "GET - Retrieves villains from the database",
        "/api/villains/delete": "POST - Deletes a villain from the database",
        "/api/villains/add": "POST - Adds a single villain to the database"
    }
    return jsonify(endpoints)

def open_browser():
   webbrowser.open_new('http://127.0.0.1:5000/')

if __name__ == '__main__':
  Timer(1, open_browser).start()
  app.run(host='0.0.0.0', port=5000)