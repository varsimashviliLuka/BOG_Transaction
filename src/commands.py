from flask.cli import with_appcontext
import click
from src.extensions import db
from src.models import User



@click.command("init_db")
@with_appcontext
def init_db():
    # აპლიკაციის შექმნისას თავდაპირველი ბრძანებები ნ1
    click.echo("Creating Database")
    db.drop_all()
    db.create_all()
    click.echo("Database Created")


@click.command("populate_db")
@with_appcontext
def populate_db():
    # აპლიკაციის შექმნისას თავდაპირველი ბრძანებები ნ2
    click.echo("Creating User")
    admin_user = User (
        email="luka.varsimashvili@iliauni.edu.ge",
        password="Lukito592"
    )

    admin_user.create()
    click.echo("First Tables Created")

@click.command("insert_db")
@with_appcontext
def insert_db():
    # Insert-ით რაც გინდა ის ქენი
    pass