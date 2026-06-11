from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from functools import wraps
from extensions import db
from models.user import User
from models.product import Product, Category, Order
import os

admin_bp = Blueprint('admin', __name__)

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('관리자 권한이 필요합니다.', 'danger')
            return redirect(url_for('user.index'))
        return f(*args, **kwargs)
    return login_required(decorated)

@admin_bp.route('/')
@admin_required
def dashboard():
    total_users = User.query.filter_by(is_admin=False).count()
    total_products = Product.query.count()
    total_orders = Order.query.count()
    revenue = db.session.query(db.func.sum(Order.total_price)).scalar() or 0
    recent_orders = Order.query.order_by(Order.created_at.desc()).limit(5).all()
    low_stock = Product.query.filter(Product.stock < 5).all()
    return render_template('admin/dashboard.html',
                           total_users=total_users, total_products=total_products,
                           total_orders=total_orders, revenue=revenue,
                           recent_orders=recent_orders, low_stock=low_stock)

# ── 상품 관리 ──────────────────────────────────────────
@admin_bp.route('/products')
@admin_required
def products():
    page = request.args.get('page', 1, type=int)
    products = Product.query.order_by(Product.created_at.desc()).paginate(page=page, per_page=15)
    return render_template('admin/products.html', products=products)

@admin_bp.route('/products/new', methods=['GET', 'POST'])
@admin_required
def new_product():
    categories = Category.query.all()
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        desc = request.form.get('description', '').strip()
        price = request.form.get('price', 0)
        stock = request.form.get('stock', 0)
        cat_id = request.form.get('category_id')
        image_file = request.files.get('image')

        if not name or not price:
            flash('상품명과 가격은 필수입니다.', 'danger')
            return render_template('admin/product_form.html', categories=categories)

        filename = 'default.png'
        if image_file and image_file.filename:
            from werkzeug.utils import secure_filename
            filename = secure_filename(image_file.filename)
            upload_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static/uploads')
            os.makedirs(upload_path, exist_ok=True)
            image_file.save(os.path.join(upload_path, filename))

        product = Product(name=name, description=desc, price=int(price),
                          stock=int(stock), category_id=cat_id or None, image=filename)
        db.session.add(product)
        db.session.commit()
        flash('상품이 등록되었습니다.', 'success')
        return redirect(url_for('admin.products'))
    return render_template('admin/product_form.html', categories=categories, product=None)

@admin_bp.route('/products/<int:product_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_product(product_id):
    product = Product.query.get_or_404(product_id)
    categories = Category.query.all()
    if request.method == 'POST':
        product.name = request.form.get('name', '').strip()
        product.description = request.form.get('description', '').strip()
        product.price = int(request.form.get('price', 0))
        product.stock = int(request.form.get('stock', 0))
        product.category_id = request.form.get('category_id') or None
        image_file = request.files.get('image')
        if image_file and image_file.filename:
            from werkzeug.utils import secure_filename
            filename = secure_filename(image_file.filename)
            upload_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static/uploads')
            os.makedirs(upload_path, exist_ok=True)
            image_file.save(os.path.join(upload_path, filename))
            product.image = filename
        db.session.commit()
        flash('상품이 수정되었습니다.', 'success')
        return redirect(url_for('admin.products'))
    return render_template('admin/product_form.html', categories=categories, product=product)

@admin_bp.route('/products/<int:product_id>/delete', methods=['POST'])
@admin_required
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    flash('상품이 삭제되었습니다.', 'info')
    return redirect(url_for('admin.products'))

# ── 주문 관리 ──────────────────────────────────────────
@admin_bp.route('/orders')
@admin_required
def orders():
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status', '')
    q = Order.query
    if status_filter:
        q = q.filter_by(status=status_filter)
    orders = q.order_by(Order.created_at.desc()).paginate(page=page, per_page=15)
    return render_template('admin/orders.html', orders=orders, status_filter=status_filter)

@admin_bp.route('/orders/<int:order_id>/status', methods=['POST'])
@admin_required
def update_order_status(order_id):
    order = Order.query.get_or_404(order_id)
    order.status = request.form.get('status', order.status)
    db.session.commit()
    flash('주문 상태가 변경되었습니다.', 'success')
    return redirect(url_for('admin.orders'))

# ── 회원 관리 ──────────────────────────────────────────
@admin_bp.route('/users')
@admin_required
def users():
    page = request.args.get('page', 1, type=int)
    users = User.query.order_by(User.created_at.desc()).paginate(page=page, per_page=20)
    return render_template('admin/users.html', users=users)

@admin_bp.route('/users/<int:user_id>/toggle-admin', methods=['POST'])
@admin_required
def toggle_admin(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash('자기 자신의 권한은 변경할 수 없습니다.', 'danger')
    else:
        user.is_admin = not user.is_admin
        db.session.commit()
        flash(f'{user.username}의 권한이 변경되었습니다.', 'success')
    return redirect(url_for('admin.users'))

# ── 카테고리 관리 ──────────────────────────────────────
@admin_bp.route('/categories', methods=['GET', 'POST'])
@admin_required
def categories():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        if name and not Category.query.filter_by(name=name).first():
            db.session.add(Category(name=name))
            db.session.commit()
            flash('카테고리가 추가되었습니다.', 'success')
        else:
            flash('이미 존재하는 카테고리입니다.', 'danger')
    categories = Category.query.all()
    return render_template('admin/categories.html', categories=categories)

@admin_bp.route('/categories/<int:cat_id>/delete', methods=['POST'])
@admin_required
def delete_category(cat_id):
    cat = Category.query.get_or_404(cat_id)
    db.session.delete(cat)
    db.session.commit()
    flash('카테고리가 삭제되었습니다.', 'info')
    return redirect(url_for('admin.categories'))
