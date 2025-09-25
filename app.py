from flask import Flask
from flask_login import LoginManager
from routes.users.users import users_bp, User
from routes.products.products import products_bp      # <- add this
from routes.orders.orders import orders_bp            # <- add this
import config   # use config for DB_PATH & SECRET_KEY

def create_app():
    app = Flask(__name__)
    app.secret_key = config.SECRET_KEY

    # Register blueprints
    app.register_blueprint(users_bp)
    app.register_blueprint(products_bp)
    app.register_blueprint(orders_bp)

    # later: add products_bp and orders_bp here

    # Flask-Login setup
    login_manager = LoginManager()
    login_manager.login_view = "users.login"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.get_by_id(user_id)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
