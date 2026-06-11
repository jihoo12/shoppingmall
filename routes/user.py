from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from extensions import db
from models.product import Product, Category, Order, OrderItem, CartItem

user_bp = Blueprint('user', __name__)

@user_bp.route('/')
def index():
    categories = Category.query.all()
    featured = Product.query.filter(Product.stock > 0).order_by(Product.created_at.desc()).limit(8).all()
    return render_template('user/index.html', categories=categories, featured=featured)

@user_bp.route('/shop')
def shop():
    cat_id = request.args.get('category', type=int)
    query_str = request.args.get('q', '').strip()
    sort = request.args.get('sort', 'newest')
    page = request.args.get('page', 1, type=int)

    q = Product.query
    if cat_id:
        q = q.filter_by(category_id=cat_id)
    if query_str:
        q = q.filter(Product.name.ilike(f'%{query_str}%'))
    if sort == 'price_asc':
        q = q.order_by(Product.price.asc())
    elif sort == 'price_desc':
        q = q.order_by(Product.price.desc())
    else:
        q = q.order_by(Product.created_at.desc())

    products = q.paginate(page=page, per_page=12, error_out=False)
    categories = Category.query.all()
    return render_template('user/shop.html', products=products, categories=categories,
                           current_cat=cat_id, query_str=query_str, sort=sort)

@user_bp.route('/product/<int:product_id>')
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)
    related = Product.query.filter_by(category_id=product.category_id).filter(Product.id != product_id).limit(4).all()
    return render_template('user/product_detail.html', product=product, related=related)

@user_bp.route('/cart')
@login_required
def cart():
    items = CartItem.query.filter_by(user_id=current_user.id).all()
    total = sum(item.product.price * item.quantity for item in items)
    return render_template('user/cart.html', items=items, total=total)

@user_bp.route('/cart/add/<int:product_id>', methods=['POST'])
@login_required
def add_to_cart(product_id):
    product = Product.query.get_or_404(product_id)
    qty = int(request.form.get('quantity', 1))
    if product.stock < qty:
        flash('재고가 부족합니다.', 'danger')
        return redirect(url_for('user.product_detail', product_id=product_id))
    item = CartItem.query.filter_by(user_id=current_user.id, product_id=product_id).first()
    if item:
        item.quantity = min(item.quantity + qty, product.stock)
    else:
        item = CartItem(user_id=current_user.id, product_id=product_id, quantity=qty)
        db.session.add(item)
    db.session.commit()
    flash(f'{product.name}을(를) 장바구니에 담았습니다.', 'success')
    return redirect(request.referrer or url_for('user.shop'))

@user_bp.route('/cart/update/<int:item_id>', methods=['POST'])
@login_required
def update_cart(item_id):
    item = CartItem.query.get_or_404(item_id)
    if item.user_id != current_user.id:
        flash('권한이 없습니다.', 'danger')
        return redirect(url_for('user.cart'))
    qty = int(request.form.get('quantity', 1))
    if qty <= 0:
        db.session.delete(item)
    else:
        item.quantity = min(qty, item.product.stock)
    db.session.commit()
    return redirect(url_for('user.cart'))

@user_bp.route('/cart/remove/<int:item_id>', methods=['POST'])
@login_required
def remove_from_cart(item_id):
    item = CartItem.query.get_or_404(item_id)
    if item.user_id != current_user.id:
        flash('권한이 없습니다.', 'danger')
        return redirect(url_for('user.cart'))
    db.session.delete(item)
    db.session.commit()
    flash('상품을 장바구니에서 제거했습니다.', 'info')
    return redirect(url_for('user.cart'))

@user_bp.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    items = CartItem.query.filter_by(user_id=current_user.id).all()
    if not items:
        flash('장바구니가 비어있습니다.', 'warning')
        return redirect(url_for('user.cart'))
    total = sum(item.product.price * item.quantity for item in items)
    if request.method == 'POST':
        address = request.form.get('address', '').strip()
        if not address:
            flash('배송 주소를 입력해주세요.', 'danger')
            return render_template('user/checkout.html', items=items, total=total)
        # 재고 확인
        for item in items:
            if item.product.stock < item.quantity:
                flash(f'{item.product.name} 재고가 부족합니다.', 'danger')
                return redirect(url_for('user.cart'))
        order = Order(user_id=current_user.id, total_price=total, address=address)
        db.session.add(order)
        db.session.flush()
        for item in items:
            oi = OrderItem(order_id=order.id, product_id=item.product_id,
                           quantity=item.quantity, price=item.product.price)
            item.product.stock -= item.quantity
            db.session.add(oi)
            db.session.delete(item)
        db.session.commit()
        flash('주문이 완료되었습니다!', 'success')
        return redirect(url_for('user.order_detail', order_id=order.id))
    return render_template('user/checkout.html', items=items, total=total)

@user_bp.route('/orders')
@login_required
def orders():
    my_orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.created_at.desc()).all()
    return render_template('user/orders.html', orders=my_orders)

@user_bp.route('/orders/<int:order_id>')
@login_required
def order_detail(order_id):
    order = Order.query.get_or_404(order_id)
    if order.user_id != current_user.id and not current_user.is_admin:
        flash('권한이 없습니다.', 'danger')
        return redirect(url_for('user.orders'))
    return render_template('user/order_detail.html', order=order)

@user_bp.route('/profile')
@login_required
def profile():
    order_count = Order.query.filter_by(user_id=current_user.id).count()
    return render_template('user/profile.html', order_count=order_count)
