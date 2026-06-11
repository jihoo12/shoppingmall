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
        # 샘플 상품 추가 (최초 1회만)
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
        if Product.query.count() == 0:
            samples = [
                Product(name='무선 이어폰', description='고음질 블루투스 이어폰', price=59000, stock=20, category_id=1),
                Product(name='코튼 티셔츠', description='부드러운 순면 티셔츠', price=19000, stock=50, category_id=2),
                Product(name='유기농 그래놀라', description='건강한 아침식사용 그래놀라', price=12000, stock=30, category_id=3),
                Product(name='파이썬 입문서', description='초보자를 위한 파이썬 프로그래밍', price=28000, stock=15, category_id=4),
                Product(name='요가 매트', description='미끄럼 방지 TPE 소재', price=35000, stock=25, category_id=5),
            ]
            db.session.add_all(samples)
            db.session.commit()

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)
