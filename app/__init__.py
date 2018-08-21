from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager


'''
The script above simply creates the application object 
as an instance of class Flask imported from the flask 
package. The __name__ variable passed to the Flask class 
is a Python predefined variable, which is set to the name 
of the module in which it is used
'''
app = Flask(__name__)
app.config.from_object(Config)

'''
The database is going to be represented in the application 
by the database instance. The database migration engine will 
also have an instance. These are objects that need to be 
created after the application
'''
db = SQLAlchemy(app)
migrate = Migrate(app, db)



'''
As with other extensions, Flask-Login needs to be created 
and initialized right after the application instance
'''
login = LoginManager(app)



'''
The bottom import is a workaround to circular imports, 
a common problem with Flask applications
'''
from app import routes, models