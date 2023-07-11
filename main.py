from flask import Flask, render_template, request, redirect, url_for, flash
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, FloatField, SubmitField
from wtforms.validators import DataRequired, URL
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)
app.config["SECRET_KEY"] = "dalkjdianfdkjf73.sdka.dkae"
Bootstrap(app)

app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///cafes.db'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# Cafe TABLE Configuration
with app.app_context():
    class Cafe(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(250), unique=True, nullable=False)
        map_url = db.Column(db.String(250), nullable=False)
        img_url = db.Column(db.String(250), nullable=False)
        location = db.Column(db.String(250), nullable=False)
        seats = db.Column(db.String(250), nullable=False)
        has_toilet = db.Column(db.Boolean, nullable=False)
        has_wifi = db.Column(db.Boolean, nullable=False)
        has_sockets = db.Column(db.Boolean, nullable=False)
        can_take_calls = db.Column(db.Boolean, nullable=False)
        coffee_price = db.Column(db.String(250), nullable=True)

    db.create_all()


# create CafeFrom
class CafeFrom(FlaskForm):
    id = db.Column(db.Integer, primary_key=True)
    name = StringField('Cafe name', validators=[DataRequired()])
    map_url = StringField('Cafe Location on Google Maps (URL)',
                          validators=[DataRequired(), URL()])
    img_url = StringField('Cafe Image (URL)', validators=[
                          DataRequired(), URL()])
    location = StringField('Location', validators=[DataRequired()])
    seats = StringField('Seats', validators=[DataRequired()])
    has_toilet = SelectField('Has Toilet', choices=[(
        1, '✔'), (0, '✘')], validators=[DataRequired()])
    has_wifi = SelectField('Has Wifi', choices=[(
        1, '✔'), (0, '✘')], validators=[DataRequired()])
    has_sockets = SelectField('Has Sockets', choices=[(
        1, '✔'), (0, '✘')], validators=[DataRequired()])
    can_take_calls = SelectField('Can Take Calls', choices=[
                                 (1, '✔'), (0, '✘')], validators=[DataRequired()])
    coffee_price = FloatField('Coffee Price (£)', validators=[DataRequired()])
    submit = SubmitField('Submit')


@app.route("/")
def home():
    cafes = Cafe.query.all()
    return render_template("index.html", cafes=cafes)


@app.route("/add", methods=["GET", "POST"])
def add():
    form = CafeFrom()
    if request.method == 'POST' and form.validate_on_submit():
        new_cafe = Cafe(name=request.form.get('name'),
                        map_url=request.form.get('map_url'),
                        img_url=request.form.get('img_url'),
                        location=request.form.get('location'),
                        seats=request.form.get('seats'),
                        has_toilet=bool(int(request.form.get('has_toilet'))),
                        has_wifi=bool(int(request.form.get('has_wifi'))),
                        has_sockets=bool(int(request.form.get('has_sockets'))),
                        can_take_calls=bool(
                            int(request.form.get('can_take_calls'))),
                        coffee_price=f"£{request.form.get('coffee_price')}",
                        )
        if Cafe.query.filter_by(name=new_cafe.name).first():
            flash(
                f"{new_cafe.name} already exists in 'Cafe and Wifi, please try again!'")
            return render_template('add.html', form=form)
        try:
            with app.app_context():
                db.session.add(new_cafe)
                db.session.commit()
                flash(f"{new_cafe.name} is added successfully!")
                return redirect(url_for('home'))
        except IntegrityError:
            flash("Failed to add the new cafe. Please try again.")
            return render_template('add.html', form=form)
    return render_template('add.html', form=form)


@app.route("/delete")
def delete():
    cafe_id = request.args.get("cafe_id")
    if cafe_id:
        with app.app_context():
            cafe_to_delete = db.session.get(Cafe, cafe_id)
            if cafe_to_delete:
                db.session.delete(cafe_to_delete)
                db.session.commit()
                flash(f"{cafe_to_delete.name} is deleted.")
                return redirect(url_for('home'))
            else:
                flash("Failed to delete, please try again.")
                cafes = Cafe.query.all()
                return render_template('delete.html', cafes=cafes)
    else:
        cafes = Cafe.query.all()
        return render_template('delete.html', cafes=cafes)


if __name__ == "__main__":
    app.run(debug=True)
