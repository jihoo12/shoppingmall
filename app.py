from flask import Flask
from extensions import db, login_manager, bcrypt
import os

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'your-secret-key-change-in-production'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///shop.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'static/uploads')

    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)

    login_manager.login_view = 'auth.login'
    login_manager.login_message = '로그인이 필요합니다.'
    login_manager.login_message_category = 'warning'

    from routes.auth import auth_bp
    from routes.user import user_bp
    from routes.admin import admin_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(user_bp, url_prefix='/')
    app.register_blueprint(admin_bp, url_prefix='/admin')

    with app.app_context():
        db.create_all()
        from models.user import User
        from models.product import Product, Category
        if not User.query.filter_by(email='admin@shop.com').first():
            admin = User(
                username='admin',
                email='admin@shop.com',
                password=bcrypt.generate_password_hash('admin1234').decode('utf-8'),
                is_admin=True
            )
            db.session.add(admin)
            for c in ['전자제품', '의류', '식품', '도서', '스포츠']:
                if not Category.query.filter_by(name=c).first():
                    db.session.add(Category(name=c))
            db.session.commit()

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)
