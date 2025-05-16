from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_from_directory
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
import os
from models import db, User, Category, Product, Supplier, Customer, Purchase, PurchaseItem, Sale, SaleItem, Inventory, InventoryTransaction, Setting
from forms import LoginForm, RegisterForm, CategoryForm, ProductForm, SupplierForm, CustomerForm, PasswordResetRequestForm, PasswordResetForm
from utils import generate_barcode_file, generate_barcode_base64, generate_random_barcode

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///makhzan.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Create database tables and admin user
def create_tables():
    with app.app_context():
        db.create_all()
        # Create admin user if not exists
        if not User.query.filter_by(username='admin').first():
            admin = User(
                username='admin',
                email='admin@example.com',
                full_name='Admin User',
                role='admin',
                is_active=True
            )
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()

# Routes
@app.route('/')
@login_required
def index():
    # Dashboard data
    total_products = Product.query.count()
    total_suppliers = Supplier.query.count()
    total_customers = Customer.query.count()

    # Recent sales
    recent_sales = Sale.query.order_by(Sale.created_at.desc()).limit(5).all()

    # Recent purchases
    recent_purchases = Purchase.query.order_by(Purchase.created_at.desc()).limit(5).all()

    # Low stock products
    low_stock_products = db.session.query(Product, Inventory).join(
        Inventory, Product.id == Inventory.product_id
    ).filter(Inventory.quantity <= Product.min_quantity).limit(5).all()

    # Sales data for chart
    today = datetime.now().date()
    start_date = today - timedelta(days=6)

    sales_data = []
    for i in range(7):
        date = start_date + timedelta(days=i)
        sales_on_date = Sale.query.filter(Sale.sale_date == date).all()
        total_sales = sum(sale.total_amount for sale in sales_on_date)
        sales_data.append({
            'date': date.strftime('%Y-%m-%d'),
            'total': total_sales
        })

    return render_template(
        'index.html',
        total_products=total_products,
        total_suppliers=total_suppliers,
        total_customers=total_customers,
        recent_sales=recent_sales,
        recent_purchases=recent_purchases,
        low_stock_products=low_stock_products,
        sales_data=sales_data
    )

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('index'))
        else:
            flash('اسم المستخدم أو كلمة المرور غير صحيحة', 'danger')

    # Pass the current datetime to the template
    return render_template('login.html', form=form, now=datetime.now())

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = PasswordResetRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            token = user.generate_reset_token()
            # In a real application, you would send an email with the reset link
            # For this demo, we'll just show the token in a flash message
            reset_url = url_for('reset_password', token=token, _external=True)
            flash(f'تم إرسال رابط إعادة تعيين كلمة المرور إلى بريدك الإلكتروني. الرابط: {reset_url}', 'info')
            db.session.commit()
        else:
            # Don't reveal that the user doesn't exist
            flash('تم إرسال تعليمات إعادة تعيين كلمة المرور إلى بريدك الإلكتروني إذا كان الحساب موجودًا.', 'info')

        return redirect(url_for('login'))

    return render_template('reset_password_request.html', form=form)

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    # Find the user with this token
    user = User.query.filter_by(reset_token=token).first()

    if not user or not user.verify_reset_token(token):
        flash('رابط إعادة تعيين كلمة المرور غير صالح أو منتهي الصلاحية.', 'danger')
        return redirect(url_for('reset_password_request'))

    form = PasswordResetForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        user.clear_reset_token()
        db.session.commit()
        flash('تم إعادة تعيين كلمة المرور بنجاح.', 'success')
        return redirect(url_for('login'))

    return render_template('reset_password.html', form=form, token=token)

# Categories routes
@app.route('/categories')
@login_required
def categories():
    categories = Category.query.all()
    return render_template('categories/index.html', categories=categories)

@app.route('/categories/add', methods=['GET', 'POST'])
@login_required
def add_category():
    form = CategoryForm()
    if form.validate_on_submit():
        category = Category(
            name=form.name.data,
            description=form.description.data
        )
        db.session.add(category)
        db.session.commit()
        flash('تم إضافة التصنيف بنجاح', 'success')
        return redirect(url_for('categories'))

    return render_template('categories/add.html', form=form)

@app.route('/categories/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_category(id):
    category = Category.query.get_or_404(id)
    form = CategoryForm(obj=category)

    if form.validate_on_submit():
        category.name = form.name.data
        category.description = form.description.data
        db.session.commit()
        flash('تم تحديث التصنيف بنجاح', 'success')
        return redirect(url_for('categories'))

    return render_template('categories/edit.html', form=form, category=category)

@app.route('/categories/delete/<int:id>', methods=['POST'])
@login_required
def delete_category(id):
    category = Category.query.get_or_404(id)
    db.session.delete(category)
    db.session.commit()
    flash('تم حذف التصنيف بنجاح', 'success')
    return redirect(url_for('categories'))

# Serve static files
@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)

# Products routes
@app.route('/products')
@login_required
def products():
    products = Product.query.all()
    return render_template('products/index.html', products=products)

@app.route('/products/barcode/<int:id>')
@login_required
def product_barcode(id):
    product = Product.query.get_or_404(id)

    # If product doesn't have a barcode, generate one
    if not product.barcode:
        product.barcode = generate_random_barcode()
        db.session.commit()

    # Generate barcode image
    barcode_path = generate_barcode_file(product.barcode, f"{product.id}_{product.barcode}")

    # Get barcode as base64 for display
    barcode_base64 = generate_barcode_base64(product.barcode)

    return render_template('products/barcode.html',
                          product=product,
                          barcode_path=barcode_path,
                          barcode_base64=barcode_base64)

@app.route('/products/add', methods=['GET', 'POST'])
@login_required
def add_product():
    form = ProductForm()

    # Get all categories for the dropdown
    categories = Category.query.all()

    # Check if there are any categories
    if not categories:
        # Create some default categories if none exist
        default_categories = [
            Category(name='ألبان', description='منتجات الألبان والأجبان'),
            Category(name='مشروبات', description='المشروبات الغازية والعصائر'),
            Category(name='معلبات', description='الأطعمة المعلبة'),
            Category(name='منظفات', description='منتجات التنظيف'),
            Category(name='حلويات', description='الحلويات والشوكولاتة')
        ]
        db.session.add_all(default_categories)
        db.session.commit()
        categories = Category.query.all()

    # Set the choices for the category dropdown
    form.category_id.choices = [(c.id, c.name) for c in categories]
    form.category_id.choices.insert(0, (0, 'بدون تصنيف'))

    if form.validate_on_submit():
        product = Product(
            name=form.name.data,
            description=form.description.data,
            barcode=form.barcode.data,
            sku=form.sku.data,
            purchase_price=form.purchase_price.data,
            sale_price=form.sale_price.data,
            min_quantity=form.min_quantity.data,
            category_id=form.category_id.data if form.category_id.data != 0 else None
        )
        db.session.add(product)
        db.session.commit()

        # Create inventory record
        inventory = Inventory(
            product_id=product.id,
            quantity=form.initial_quantity.data
        )
        db.session.add(inventory)

        # Create inventory transaction
        if form.initial_quantity.data > 0:
            transaction = InventoryTransaction(
                product_id=product.id,
                quantity_before=0,
                quantity_change=form.initial_quantity.data,
                quantity_after=form.initial_quantity.data,
                transaction_type='adjustment',
                reference_type='adjustment',
                notes='الكمية الأولية عند إضافة المنتج',
                user_id=current_user.id
            )
            db.session.add(transaction)

        db.session.commit()
        flash('تم إضافة المنتج بنجاح', 'success')
        return redirect(url_for('products'))

    return render_template('products/add.html', form=form)

@app.route('/products/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_product(id):
    product = Product.query.get_or_404(id)
    form = ProductForm(obj=product)
    form.category_id.choices = [(c.id, c.name) for c in Category.query.all()]
    form.category_id.choices.insert(0, (0, 'بدون تصنيف'))

    if request.method == 'GET':
        form.category_id.data = product.category_id if product.category_id else 0
        if product.inventory:
            form.initial_quantity.data = product.inventory.quantity

    if form.validate_on_submit():
        old_quantity = product.inventory.quantity if product.inventory else 0

        product.name = form.name.data
        product.description = form.description.data
        product.barcode = form.barcode.data
        product.sku = form.sku.data
        product.purchase_price = form.purchase_price.data
        product.sale_price = form.sale_price.data
        product.min_quantity = form.min_quantity.data
        product.category_id = form.category_id.data if form.category_id.data != 0 else None

        # Update inventory
        if not product.inventory:
            inventory = Inventory(
                product_id=product.id,
                quantity=form.initial_quantity.data
            )
            db.session.add(inventory)
        else:
            if old_quantity != form.initial_quantity.data:
                # Create inventory transaction
                transaction = InventoryTransaction(
                    product_id=product.id,
                    quantity_before=old_quantity,
                    quantity_change=form.initial_quantity.data - old_quantity,
                    quantity_after=form.initial_quantity.data,
                    transaction_type='adjustment',
                    reference_type='adjustment',
                    notes='تعديل الكمية من خلال تحرير المنتج',
                    user_id=current_user.id
                )
                db.session.add(transaction)

                product.inventory.quantity = form.initial_quantity.data

        db.session.commit()
        flash('تم تحديث المنتج بنجاح', 'success')
        return redirect(url_for('products'))

    return render_template('products/edit.html', form=form, product=product)

@app.route('/products/delete/<int:id>', methods=['POST'])
@login_required
def delete_product(id):
    product = Product.query.get_or_404(id)
    db.session.delete(product)
    db.session.commit()
    flash('تم حذف المنتج بنجاح', 'success')
    return redirect(url_for('products'))

# Suppliers routes
@app.route('/suppliers')
@login_required
def suppliers():
    suppliers = Supplier.query.all()
    return render_template('suppliers/index.html', suppliers=suppliers)

@app.route('/suppliers/add', methods=['GET', 'POST'])
@login_required
def add_supplier():
    form = SupplierForm()
    if form.validate_on_submit():
        supplier = Supplier(
            name=form.name.data,
            contact_person=form.contact_person.data,
            phone=form.phone.data,
            email=form.email.data,
            address=form.address.data,
            notes=form.notes.data
        )
        db.session.add(supplier)
        db.session.commit()
        flash('تم إضافة المورد بنجاح', 'success')
        return redirect(url_for('suppliers'))

    return render_template('suppliers/add.html', form=form)

@app.route('/suppliers/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_supplier(id):
    supplier = Supplier.query.get_or_404(id)
    form = SupplierForm(obj=supplier)

    if form.validate_on_submit():
        supplier.name = form.name.data
        supplier.contact_person = form.contact_person.data
        supplier.phone = form.phone.data
        supplier.email = form.email.data
        supplier.address = form.address.data
        supplier.notes = form.notes.data
        db.session.commit()
        flash('تم تحديث المورد بنجاح', 'success')
        return redirect(url_for('suppliers'))

    return render_template('suppliers/edit.html', form=form, supplier=supplier)

@app.route('/suppliers/delete/<int:id>', methods=['POST'])
@login_required
def delete_supplier(id):
    supplier = Supplier.query.get_or_404(id)
    db.session.delete(supplier)
    db.session.commit()
    flash('تم حذف المورد بنجاح', 'success')
    return redirect(url_for('suppliers'))

# Customers routes
@app.route('/customers')
@login_required
def customers():
    customers = Customer.query.all()
    return render_template('customers/index.html', customers=customers)

@app.route('/customers/add', methods=['GET', 'POST'])
@login_required
def add_customer():
    form = CustomerForm()
    if form.validate_on_submit():
        customer = Customer(
            name=form.name.data,
            phone=form.phone.data,
            email=form.email.data,
            address=form.address.data,
            notes=form.notes.data
        )
        db.session.add(customer)
        db.session.commit()
        flash('تم إضافة العميل بنجاح', 'success')
        return redirect(url_for('customers'))

    return render_template('customers/add.html', form=form)

@app.route('/customers/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_customer(id):
    customer = Customer.query.get_or_404(id)
    form = CustomerForm(obj=customer)

    if form.validate_on_submit():
        customer.name = form.name.data
        customer.phone = form.phone.data
        customer.email = form.email.data
        customer.address = form.address.data
        customer.notes = form.notes.data
        db.session.commit()
        flash('تم تحديث العميل بنجاح', 'success')
        return redirect(url_for('customers'))

    return render_template('customers/edit.html', form=form, customer=customer)

@app.route('/customers/delete/<int:id>', methods=['POST'])
@login_required
def delete_customer(id):
    customer = Customer.query.get_or_404(id)
    db.session.delete(customer)
    db.session.commit()
    flash('تم حذف العميل بنجاح', 'success')
    return redirect(url_for('customers'))

# Purchases routes
@app.route('/purchases')
@login_required
def purchases():
    purchases = Purchase.query.order_by(Purchase.created_at.desc()).all()
    return render_template('purchases/index.html', purchases=purchases)

@app.route('/purchases/add', methods=['GET', 'POST'])
@login_required
def add_purchase():
    from forms import PurchaseForm
    form = PurchaseForm()
    form.supplier_id.choices = [(s.id, s.name) for s in Supplier.query.all()]

    # Get all products for the dropdown
    products = Product.query.all()

    if request.method == 'POST':
        # Process the form submission
        if form.validate_on_submit():
            # Create new purchase - remove user_id parameter
            purchase = Purchase(
                invoice_number=form.invoice_number.data,
                purchase_date=form.purchase_date.data,
                supplier_id=form.supplier_id.data,
                total_amount=request.form.get('total_amount', 0),
                payment_method=request.form.get('payment_method', 'cash'),
                notes=request.form.get('notes', '')
                # Remove user_id parameter
            )
            db.session.add(purchase)
            db.session.flush()  # Get the purchase ID

            # Process purchase items
            items_count = 0
            while f'items-{items_count}-product_id' in request.form:
                product_id = request.form.get(f'items-{items_count}-product_id')
                quantity = int(request.form.get(f'items-{items_count}-quantity', 0))
                price = float(request.form.get(f'items-{items_count}-price', 0))

                if product_id and quantity > 0 and price > 0:
                    # Add purchase item
                    item = PurchaseItem(
                        purchase_id=purchase.id,
                        product_id=product_id,
                        quantity=quantity,
                        price=price,
                        total=quantity * price
                    )
                    db.session.add(item)

                    # Update inventory
                    inventory = Inventory.query.filter_by(product_id=product_id).first()
                    if inventory:
                        old_quantity = inventory.quantity
                        inventory.quantity += quantity

                        # Create inventory transaction
                        transaction = InventoryTransaction(
                            product_id=product_id,
                            quantity_before=old_quantity,
                            quantity_change=quantity,
                            quantity_after=old_quantity + quantity,
                            transaction_type='purchase',
                            reference_type='purchase',
                            reference_id=purchase.id,
                            user_id=current_user.id
                        )
                        db.session.add(transaction)

                items_count += 1

            db.session.commit()
            flash('تم إضافة فاتورة الشراء بنجاح', 'success')
            return redirect(url_for('purchases'))

    return render_template('purchases/add.html', form=form, products=products)

@app.route('/purchases/view/<int:id>')
@login_required
def view_purchase(id):
    purchase = Purchase.query.get_or_404(id)
    return render_template('purchases/view.html', purchase=purchase)

# Sales routes
@app.route('/sales')
@login_required
def sales():
    sales = Sale.query.order_by(Sale.created_at.desc()).all()
    return render_template('sales/index.html', sales=sales)

@app.route('/sales/add', methods=['GET', 'POST'])
@login_required
def add_sale():
    # This is a placeholder - you'll need to implement the form and logic
    return render_template('sales/add.html')

@app.route('/sales/view/<int:id>')
@login_required
def view_sale(id):
    sale = Sale.query.get_or_404(id)
    return render_template('sales/view.html', sale=sale)

# Inventory routes
@app.route('/inventory')
@login_required
def inventory():
    status = request.args.get('status', 'all')

    query = db.session.query(Product, Inventory).join(
        Inventory, Product.id == Inventory.product_id
    )

    if status == 'low':
        query = query.filter(Inventory.quantity <= Product.min_quantity, Inventory.quantity > 0)
    elif status == 'out':
        query = query.filter(Inventory.quantity <= 0)

    inventory_items = query.all()

    total_value = sum(item.quantity * item.product.purchase_price for _, item in inventory_items)

    return render_template('inventory/index.html',
                          inventory=inventory_items,
                          total_value=total_value,
                          status=status)

@app.route('/inventory/adjustment', methods=['GET', 'POST'])
@login_required
def inventory_adjustment():
    # This is a placeholder - you'll need to implement the form and logic
    return render_template('inventory/adjustment.html')

@app.route('/product/transactions/<int:id>')
@login_required
def product_transactions(id):
    product = Product.query.get_or_404(id)
    transactions = InventoryTransaction.query.filter_by(product_id=id).order_by(InventoryTransaction.created_at.desc()).all()
    return render_template('inventory/transactions.html', product=product, transactions=transactions)

# Reports routes
@app.route('/reports')
@login_required
def reports():
    return render_template('reports/index.html')

@app.route('/reports/sales')
@login_required
def sales_report():
    start_date = request.args.get('start_date', (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'))
    end_date = request.args.get('end_date', datetime.now().strftime('%Y-%m-%d'))

    if isinstance(start_date, str):
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    if isinstance(end_date, str):
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()

    sales = Sale.query.filter(Sale.sale_date.between(start_date, end_date)).order_by(Sale.sale_date.desc()).all()

    total_sales = sum(sale.total_amount for sale in sales)
    total_profit = sum(sale.profit for sale in sales if sale.profit)

    return render_template('reports/sales.html',
                          sales=sales,
                          total_sales=total_sales,
                          total_profit=total_profit,
                          start_date=start_date,
                          end_date=end_date)

@app.route('/reports/purchases')
@login_required
def purchases_report():
    start_date = request.args.get('start_date', (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'))
    end_date = request.args.get('end_date', datetime.now().strftime('%Y-%m-%d'))

    if isinstance(start_date, str):
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    if isinstance(end_date, str):
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()

    purchases = Purchase.query.filter(Purchase.purchase_date.between(start_date, end_date)).order_by(Purchase.purchase_date.desc()).all()

    total_purchases = sum(purchase.total_amount for purchase in purchases)

    return render_template('reports/purchases.html',
                          purchases=purchases,
                          total_purchases=total_purchases,
                          start_date=start_date,
                          end_date=end_date)

@app.route('/reports/inventory')
@login_required
def inventory_report():
    inventory_items = db.session.query(Product, Inventory).join(
        Inventory, Product.id == Inventory.product_id
    ).all()

    total_value = sum(item.quantity * item.product.purchase_price for _, item in inventory_items)

    return render_template('reports/inventory.html',
                          inventory=inventory_items,
                          total_value=total_value)

# Users routes
@app.route('/users')
@login_required
def users():
    # Only admin users should be able to manage users
    if current_user.role != 'admin':
        flash('ليس لديك صلاحية للوصول إلى هذه الصفحة', 'danger')
        return redirect(url_for('index'))

    users = User.query.all()
    return render_template('users/index.html', users=users)

@app.route('/users/add', methods=['GET', 'POST'])
@login_required
def add_user():
    # Only admin users should be able to add users
    if current_user.role != 'admin':
        flash('ليس لديك صلاحية للوصول إلى هذه الصفحة', 'danger')
        return redirect(url_for('index'))

    form = RegisterForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            full_name=form.full_name.data,
            role=form.role.data,
            is_active=True
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('تم إضافة المستخدم بنجاح', 'success')
        return redirect(url_for('users'))

    return render_template('users/add.html', form=form)

@app.route('/users/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_user(id):
    # Only admin users should be able to edit users
    if current_user.role != 'admin':
        flash('ليس لديك صلاحية للوصول إلى هذه الصفحة', 'danger')
        return redirect(url_for('index'))

    user = User.query.get_or_404(id)
    form = RegisterForm(obj=user)

    # Don't require password on edit
    form.password.validators = []
    form.password.flags.required = False
    form.confirm_password.validators = []
    form.confirm_password.flags.required = False

    if form.validate_on_submit():
        user.username = form.username.data
        user.email = form.email.data
        user.full_name = form.full_name.data
        user.role = form.role.data

        # Only update password if provided
        if form.password.data:
            user.set_password(form.password.data)

        db.session.commit()
        flash('تم تحديث المستخدم بنجاح', 'success')
        return redirect(url_for('users'))

    return render_template('users/edit.html', form=form, user=user)

@app.route('/users/toggle/<int:id>', methods=['POST'])
@login_required
def toggle_user(id):
    # Only admin users should be able to toggle user status
    if current_user.role != 'admin':
        flash('ليس لديك صلاحية للوصول إلى هذه الصفحة', 'danger')
        return redirect(url_for('index'))

    user = User.query.get_or_404(id)

    # Don't allow deactivating the last admin
    if user.role == 'admin' and user.is_active and User.query.filter_by(role='admin', is_active=True).count() <= 1:
        flash('لا يمكن إلغاء تنشيط المسؤول الوحيد', 'danger')
        return redirect(url_for('users'))

    # Don't allow deactivating yourself
    if user.id == current_user.id:
        flash('لا يمكنك إلغاء تنشيط حسابك الحالي', 'danger')
        return redirect(url_for('users'))

    user.is_active = not user.is_active
    db.session.commit()

    status = 'تنشيط' if user.is_active else 'إلغاء تنشيط'
    flash(f'تم {status} المستخدم بنجاح', 'success')
    return redirect(url_for('users'))

# Settings routes
@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    # Only admin users should be able to manage settings
    if current_user.role != 'admin':
        flash('ليس لديك صلاحية للوصول إلى هذه الصفحة', 'danger')
        return redirect(url_for('index'))

    # Get or create settings
    store_name = Setting.query.filter_by(key='store_name').first()
    if not store_name:
        store_name = Setting(key='store_name', value='نظام إدارة المخزن')
        db.session.add(store_name)

    store_address = Setting.query.filter_by(key='store_address').first()
    if not store_address:
        store_address = Setting(key='store_address', value='')
        db.session.add(store_address)

    store_phone = Setting.query.filter_by(key='store_phone').first()
    if not store_phone:
        store_phone = Setting(key='store_phone', value='')
        db.session.add(store_phone)

    store_email = Setting.query.filter_by(key='store_email').first()
    if not store_email:
        store_email = Setting(key='store_email', value='')
        db.session.add(store_email)

    tax_rate = Setting.query.filter_by(key='tax_rate').first()
    if not tax_rate:
        tax_rate = Setting(key='tax_rate', value='0')
        db.session.add(tax_rate)

    currency = Setting.query.filter_by(key='currency').first()
    if not currency:
        currency = Setting(key='currency', value='ر.س')
        db.session.add(currency)

    db.session.commit()

    if request.method == 'POST':
        store_name.value = request.form.get('store_name', '')
        store_address.value = request.form.get('store_address', '')
        store_phone.value = request.form.get('store_phone', '')
        store_email.value = request.form.get('store_email', '')
        tax_rate.value = request.form.get('tax_rate', '0')
        currency.value = request.form.get('currency', 'ر.س')

        db.session.commit()
        flash('تم تحديث الإعدادات بنجاح', 'success')
        return redirect(url_for('settings'))

    return render_template('settings/index.html',
                          store_name=store_name.value,
                          store_address=store_address.value,
                          store_phone=store_phone.value,
                          store_email=store_email.value,
                          tax_rate=tax_rate.value,
                          currency=currency.value)

# Profile route
@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = RegisterForm(obj=current_user)

    # Don't require password on edit
    form.password.validators = []
    form.password.flags.required = False
    form.confirm_password.validators = []
    form.confirm_password.flags.required = False

    # Remove role field for non-admin users
    if current_user.role != 'admin':
        del form.role

    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.full_name = form.full_name.data

        # Only admin can change role
        if current_user.role == 'admin' and hasattr(form, 'role'):
            current_user.role = form.role.data

        # Only update password if provided
        if form.password.data:
            current_user.set_password(form.password.data)

        db.session.commit()
        flash('تم تحديث الملف الشخصي بنجاح', 'success')
        return redirect(url_for('profile'))

    return render_template('profile.html', form=form)

# Add more routes for purchases, sales, inventory, etc.

if __name__ == '__main__':
    create_tables()  # Call the function to create tables and admin user
    app.run(debug=True)