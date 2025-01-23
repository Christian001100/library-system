from flask import Flask
from config import SECRET_KEY
from db_config import create_app, mysql
from routes.book_routes import book_routes
from routes.member_routes import member_routes
from routes.lending_routes import lending_routes
from routes.auth_routes import auth_routes
from models.librarians import authenticate_librarian


app = create_app()
mysql.init_app(app)
app.secret_key = SECRET_KEY

app.register_blueprint(book_routes, url_prefix='/api')
app.register_blueprint(member_routes, url_prefix='/api')
app.register_blueprint(lending_routes, url_prefix='/api')
app.register_blueprint(auth_routes, url_prefix='/api')



if __name__ == '__main__':
    app.run(debug=True)
