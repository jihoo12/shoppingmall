# 🛒 ShopFlask - Python Flask 쇼핑몰

## 프로젝트 구조
```
shop/
├── app.py                  # 앱 팩토리 & DB 초기화
├── models/
│   ├── user.py             # User 모델
│   └── product.py          # Product, Category, Order, CartItem 모델
├── routes/
│   ├── auth.py             # 로그인, 회원가입, 로그아웃
│   ├── user.py             # 쇼핑몰 (홈, 상품, 장바구니, 주문)
│   └── admin.py            # 관리자 (대시보드, 상품/주문/회원 관리)
├── templates/
│   ├── base.html           # 사용자 공통 레이아웃
│   ├── auth/               # 로그인/회원가입 페이지
│   ├── user/               # 쇼핑몰 페이지들
│   └── admin/              # 관리자 페이지들
└── static/uploads/         # 상품 이미지 업로드 폴더
```

## 설치 및 실행

### 1. 패키지 설치
```bash
pip install flask flask-sqlalchemy flask-login flask-bcrypt flask-wtf pillow
```

### 2. 실행
```bash
python app.py
```
→ http://localhost:5000 접속

## 기본 계정
| 역할 | 이메일 | 비밀번호 |
|------|--------|---------|
| 관리자 | admin@shop.com | admin1234 |

## 주요 기능

### 👤 사용자
- 회원가입 / 로그인 / 로그아웃 (bcrypt 암호화)
- 상품 목록 / 검색 / 카테고리 필터 / 정렬
- 상품 상세보기 + 관련 상품
- 장바구니 추가 / 수량 변경 / 삭제
- 주문하기 (배송 주소 입력, 재고 자동 차감)
- 주문 내역 / 주문 상세
- 프로필 페이지

### 🔧 관리자 (/admin)
- 대시보드 (회원수, 상품수, 주문수, 총매출, 재고부족 알림)
- 상품 관리 (등록 / 수정 / 삭제 / 이미지 업로드)
- 주문 관리 (상태 변경: 주문완료→배송중→배송완료)
- 회원 관리 (관리자 권한 지정/해제)
- 카테고리 관리 (추가 / 삭제)

## DB 구조
- **SQLite** (shop.db) - 개발용, 운영 시 PostgreSQL/MySQL로 교체 권장
- ORM: Flask-SQLAlchemy

## 운영 환경 주의사항
- `app.config['SECRET_KEY']`를 안전한 랜덤 값으로 교체
- `SQLALCHEMY_DATABASE_URI`를 PostgreSQL로 교체
- `DEBUG=False` 설정
