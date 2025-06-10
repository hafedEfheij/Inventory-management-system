٢# Inventory Management System - نظام إدارة    المخزن

This is a comprehensive inventory management system built with Flask. It provides a complete solution for managing products, suppliers, customers, purchases, sales, and inventory tracking.

## Feature

- **Dashboard**: Get an overview of your business with key metrics and charts
- **Product Management**: Add, edit, and manage products with categories
- **Supplier Management**: Keep track of your suppliers and their information
- **Customer Management**: Manage your customer database
- **Purchase Management**: Record and track purchases from suppliers
- **Sales Management**: Process and track sales to customers
- **Inventory Tracking**: Monitor stock levels with low stock alerts
- **User Management**: Control access with different user roles
- **Reports**: Generate various reports for business analysis
- **RTL Support**: Full support for Arabic language and right-to-left layout

## Installation

### Prerequisites

- Python 3.7+
- pip (Python package manager)

### Setup

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/inventory-system.git
   cd inventory-system
   ```

2. Create and activate a virtual environment:
   ```
   # On Windows
   python -m venv venv
   venv\Scripts\activate

   # On macOS/Linux
   python -m venv venv
   source venv/bin/activate
   ```

3. Install the required packages:
   ```
   pip install flask flask-login flask-sqlalchemy flask-wtf
   ```

4. Run the application:
   ```
   python app.py
   ```

5. Access the application in your browser:
   ```
   http://127.0.0.1:5000/
   ```

## Default Login

- **Username**: admin
- **Password**: admin123

## Database Structure

This system uses SQLite as its database engine. The database file is created automatically when you run the application for the first time.

The main database models include:

- **User**: System users with different access levels
- **Category**: Product categories
- **Product**: Products with details like price, barcode, etc.
- **Supplier**: Suppliers information
- **Customer**: Customers information
- **Purchase**: Purchase orders from suppliers
- **PurchaseItem**: Individual items in purchase orders
- **Sale**: Sales to customers
- **SaleItem**: Individual items in sales
- **Inventory**: Current stock levels for products
- **InventoryTransaction**: History of inventory changes
- **Setting**: System settings

## Usage

### Adding Products

1. Navigate to the Products section
2. Click "Add New Product"
3. Fill in the product details including name, description, prices, and initial quantity
4. Save the product

### Managing Inventory

1. Navigate to the Inventory section
2. View current stock levels for all products
3. Filter by low stock or out of stock items
4. Adjust inventory quantities as needed

### Processing Sales

1. Navigate to the Sales section
2. Click "New Sale"
3. Select a customer (or create a new one)
4. Add products to the sale
5. Complete the sale transaction

### Generating Reports

1. Navigate to the Reports section
2. Select the type of report you want to generate
3. Set the date range and other parameters
4. View or print the report

## Development

### Project Structure

```
inventory-system/
├── app.py              # Main application file
├── models.py           # Database models
├── forms.py            # Form definitions
├── routes.py           # Route definitions
├── templates/          # HTML templates
│   ├── base.html       # Base template
│   ├── index.html      # Dashboard template
│   ├── products/       # Product templates
│   ├── suppliers/      # Supplier templates
│   ├── customers/      # Customer templates
│   ├── purchases/      # Purchase templates
│   ├── sales/          # Sales templates
│   ├── inventory/      # Inventory templates
│   ├── reports/        # Report templates
│   └── users/          # User management templates
├── static/             # Static files (CSS, JS, images)
├── instance/           # Instance-specific files
│   └── database.db     # SQLite database
└── venv/               # Virtual environment
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- [Flask](https://flask.palletsprojects.com/) - The web framework used
- [SQLAlchemy](https://www.sqlalchemy.org/) - ORM for database operations
- [Bootstrap](https://getbootstrap.com/) - Frontend framework
- [Font Awesome](https://fontawesome.com/) - Icons

## Contact

For any questions or suggestions, please contact [your-email@example.com](mailto:your-email@example.com).
