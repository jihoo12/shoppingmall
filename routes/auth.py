from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from extensions import db, bcrypt
from models.user import User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('user.index'))
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm = request.form.get('confirm_password', '')

        if not username or not email or not password:
            flash('모든 필드를 입력해주세요.', 'danger')
            return render_template('auth/register.html')
        if password != confirm:
            flash('비밀번호가 일치하지 않습니다.', 'danger')
            return render_template('auth/register.html')
        if len(password) < 6:
            flash('비밀번호는 6자 이상이어야 합니다.', 'danger')
            return render_template('auth/register.html')
        if User.query.filter_by(email=email).first():
            flash('이미 사용 중인 이메일입니다.', 'danger')
            return render_template('auth/register.html')
        if User.query.filter_by(username=username).first():
            flash('이미 사용 중인 닉네임입니다.', 'danger')
            return render_template('auth/register.html')

        hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')
        user = User(username=username, email=email, password=hashed_pw)
        db.session.add(user)
        db.session.commit()
        flash('회원가입이 완료되었습니다! 로그인해주세요.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('user.index'))
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        remember = request.form.get('remember') == 'on'
        user = User.query.filter_by(email=email).first()
        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user, remember=remember)
            flash(f'{user.username}님 환영합니다!', 'success')
            next_page = request.args.get('next')
            if user.is_admin:
                return redirect(next_page or url_for('admin.dashboard'))
            return redirect(next_page or url_for('user.index'))
        flash('이메일 또는 비밀번호가 올바르지 않습니다.', 'danger')
    return render_template('auth/login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('로그아웃되었습니다.', 'info')
    return redirect(url_for('user.index'))
