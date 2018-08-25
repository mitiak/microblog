from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
import logging
from logging.handlers import SMTPHandler, RotatingFileHandler
import os
from flask_mail import Mail



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
Like most Flask extensions, you need to create an instance 
right after the Flask application is created. In this case 
this is an object of class Mail
'''
mail = Mail(app)



if not app.debug:

    if app.config['MAIL_SERVER']:
        auth = None
        if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
            auth = (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
        secure = None
        if app.config['MAIL_USE_TLS']:
            secure = ()
        mail_handler = SMTPHandler(
            mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
            fromaddr='no-reply@' + app.config['MAIL_SERVER'],
            toaddrs=app.config['ADMINS'], subject='Microblog Failure',
            credentials=auth, secure=secure)
        mail_handler.setLevel(logging.INFO)
        app.logger.addHandler(mail_handler)
    else:
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/microblog.log', maxBytes=10240,
                                            backupCount=10)
        file_handler.setFormatter(logging.Formatter
            ('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('Microblog startup')


        




'''
The bottom import is a workaround to circular imports, 
a common problem with Flask applications
'''
from app import routes, models, errors