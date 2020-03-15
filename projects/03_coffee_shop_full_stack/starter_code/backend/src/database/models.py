import os
from sqlalchemy import Column, String, Integer
from flask_sqlalchemy import SQLAlchemy
import json

database_filename = "database.db"
project_dir = os.path.dirname(os.path.abspath(__file__))
database_path = "sqlite:///{}".format(os.path.join(project_dir, database_filename))

db = SQLAlchemy()

'''
setup_db(app)
    Binds a flask application and a SQLAlchemy service.
'''
def setup_db(app):
    app.config["SQLALCHEMY_DATABASE_URI"] = database_path
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    db.init_app(app)

'''
db_drop_and_create_all()
    Drops the database tables and starts fresh.
    Can be used to initialize a clean database.
    !!NOTE you can change the database_filename variable to have multiple
    verisons of a database.
'''
def db_drop_and_create_all():
    db.drop_all()
    db.create_all()

'''
Drink
    A persistent drink entity, extends the base SQLAlchemy Model.
'''
class Drink(db.Model):
    # Autoincrementing, unique primary key
    id = Column(Integer().with_variant(Integer, "sqlite"), primary_key=True)
    # String Title
    title = Column(String(80), unique=True)
    # The ingredients blob - this stores a lazy json blob
    # The required datatype is [{'color': string, 'name':string, 'parts':number}]
    recipe =  Column(String(180), nullable=False)

    '''
    short()
        Short form representation of the Drink model.
    '''
    def short(self):
        print(json.loads(self.recipe))
        short_recipe = [{'color': r['color'], 'parts': r['parts']} for r in json.loads(self.recipe)]
        return {
            'id': self.id,
            'title': self.title,
            'recipe': short_recipe
        }

    '''
    long()
        Long form representation of the Drink model.
    '''
    def long(self):
        return {
            'id': self.id,
            'title': self.title,
            'recipe': json.loads(self.recipe)
        }

    '''
    insert()
        Inserts a new model into a database.
        The model must have a unique name.
        The model must have a unique id or null id.
        EXAMPLE
            drink = Drink(title=req_title, recipe=req_recipe)
            drink.insert()
    '''
    def insert(self):
        db.session.add(self)
        db.session.commit()

    '''
    delete()
        Deletes a new model into a database.
        The model must exist in the database.
        EXAMPLE
            drink = Drink(title=req_title, recipe=req_recipe)
            drink.delete()
    '''
    def delete(self):
        db.session.delete(self)
        db.session.commit()

    '''
    update()
        Updates a new model into a database.
        The model must exist in the database.
        EXAMPLE
            drink = Drink.query.filter(Drink.id == id).one_or_none()
            drink.title = 'Black Coffee'
            drink.update()
    '''
    def update(self):
        db.session.commit()

    def __repr__(self):
        return json.dumps(self.short())
