#!/bin/bash
# ShopFlask 설치 스크립트
# 사용법: 이 파일을 app.py와 같은 폴더에 놓고 bash setup.sh 실행

DEST=$(dirname "$0")

echo "📁 폴더 생성 중..."
mkdir -p "$DEST/templates/auth"
mkdir -p "$DEST/templates/user"
mkdir -p "$DEST/templates/admin"
mkdir -p "$DEST/models"
mkdir -p "$DEST/routes"
mkdir -p "$DEST/static/uploads"

echo "✅ 폴더 구조:"
find "$DEST/templates" -type d | sort
echo ""
echo "👉 다음 단계: 각 HTML 파일을 올바른 폴더에 배치하세요"
echo "   templates/base.html"
echo "   templates/auth/login.html"
echo "   templates/auth/register.html"
echo "   templates/user/index.html  ← 여기에 없으면 TemplateNotFound 에러!"
echo "   templates/user/shop.html"
echo "   templates/user/product_detail.html"
echo "   templates/user/cart.html"
echo "   templates/user/checkout.html"
echo "   templates/user/orders.html"
echo "   templates/user/order_detail.html"
echo "   templates/user/profile.html"
echo "   templates/admin/base_admin.html"
echo "   templates/admin/dashboard.html"
echo "   templates/admin/products.html"
echo "   templates/admin/product_form.html"
echo "   templates/admin/orders.html"
echo "   templates/admin/users.html"
echo "   templates/admin/categories.html"
