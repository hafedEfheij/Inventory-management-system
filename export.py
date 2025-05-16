import csv
import os
import pandas as pd
from fpdf import FPDF
from io import StringIO, BytesIO
import datetime

class PDF(FPDF):
    """Custom PDF class with header and footer"""
    
    def __init__(self, title="Report", *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title = title
        self.set_auto_page_break(auto=True, margin=15)
        
    def header(self):
        # Logo (if needed)
        # self.image('logo.png', 10, 8, 33)
        
        # Title
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, self.title, 0, 1, 'C')
        
        # Date
        self.set_font('Arial', '', 10)
        self.cell(0, 10, f'Generated on: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', 0, 1, 'R')
        
        # Line break
        self.ln(5)
        
    def footer(self):
        # Position at 1.5 cm from bottom
        self.set_y(-15)
        
        # Arial italic 8
        self.set_font('Arial', 'I', 8)
        
        # Page number
        self.cell(0, 10, f'Page {self.page_no()}/{{nb}}', 0, 0, 'C')

def export_to_csv(data, headers, filename):
    """
    Export data to CSV file
    
    Args:
        data (list): List of data rows
        headers (list): List of column headers
        filename (str): Output filename
        
    Returns:
        str: Path to the saved CSV file
    """
    # Ensure the exports directory exists
    os.makedirs('static/exports', exist_ok=True)
    
    filepath = f'static/exports/{filename}.csv'
    
    with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(headers)
        writer.writerows(data)
    
    return filepath

def export_to_pdf(data, headers, filename, title="Report"):
    """
    Export data to PDF file
    
    Args:
        data (list): List of data rows
        headers (list): List of column headers
        filename (str): Output filename
        title (str): Title of the PDF document
        
    Returns:
        str: Path to the saved PDF file
    """
    # Ensure the exports directory exists
    os.makedirs('static/exports', exist_ok=True)
    
    filepath = f'static/exports/{filename}.pdf'
    
    # Create PDF object
    pdf = PDF(title=title, orientation='L')
    pdf.alias_nb_pages()
    pdf.add_page()
    
    # Set font
    pdf.set_font('Arial', 'B', 10)
    
    # Calculate column width
    col_width = pdf.w / len(headers)
    
    # Add headers
    for header in headers:
        pdf.cell(col_width, 10, str(header), 1, 0, 'C')
    pdf.ln()
    
    # Add data rows
    pdf.set_font('Arial', '', 10)
    for row in data:
        for item in row:
            pdf.cell(col_width, 10, str(item), 1, 0, 'L')
        pdf.ln()
    
    # Save PDF
    pdf.output(filepath)
    
    return filepath

def generate_product_report(products, format='csv'):
    """
    Generate a product report in the specified format
    
    Args:
        products (list): List of Product objects
        format (str): Output format ('csv' or 'pdf')
        
    Returns:
        str: Path to the saved report file
    """
    # Prepare data
    headers = ['ID', 'Name', 'Category', 'Barcode', 'SKU', 'Purchase Price', 'Sale Price', 'Quantity']
    data = []
    
    for product in products:
        category_name = product.category.name if product.category else 'N/A'
        quantity = product.inventory.quantity if product.inventory else 0
        
        data.append([
            product.id,
            product.name,
            category_name,
            product.barcode or 'N/A',
            product.sku or 'N/A',
            product.purchase_price,
            product.sale_price,
            quantity
        ])
    
    # Generate filename
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f'products_report_{timestamp}'
    
    # Export in the specified format
    if format.lower() == 'csv':
        return export_to_csv(data, headers, filename)
    elif format.lower() == 'pdf':
        return export_to_pdf(data, headers, filename, title="Products Report")
    else:
        raise ValueError(f"Unsupported format: {format}")

def generate_inventory_report(inventory_items, format='csv'):
    """
    Generate an inventory report in the specified format
    
    Args:
        inventory_items (list): List of Inventory objects
        format (str): Output format ('csv' or 'pdf')
        
    Returns:
        str: Path to the saved report file
    """
    # Prepare data
    headers = ['ID', 'Product', 'Category', 'Quantity', 'Last Updated']
    data = []
    
    for item in inventory_items:
        category_name = item.product.category.name if item.product.category else 'N/A'
        
        data.append([
            item.id,
            item.product.name,
            category_name,
            item.quantity,
            item.updated_at.strftime("%Y-%m-%d %H:%M:%S") if item.updated_at else 'N/A'
        ])
    
    # Generate filename
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f'inventory_report_{timestamp}'
    
    # Export in the specified format
    if format.lower() == 'csv':
        return export_to_csv(data, headers, filename)
    elif format.lower() == 'pdf':
        return export_to_pdf(data, headers, filename, title="Inventory Report")
    else:
        raise ValueError(f"Unsupported format: {format}")

def generate_sales_report(sales, format='csv'):
    """
    Generate a sales report in the specified format
    
    Args:
        sales (list): List of Sale objects
        format (str): Output format ('csv' or 'pdf')
        
    Returns:
        str: Path to the saved report file
    """
    # Prepare data
    headers = ['ID', 'Customer', 'Date', 'Total Amount', 'Items Count', 'Status']
    data = []
    
    for sale in sales:
        customer_name = sale.customer.name if sale.customer else 'N/A'
        items_count = len(sale.items) if sale.items else 0
        
        data.append([
            sale.id,
            customer_name,
            sale.date.strftime("%Y-%m-%d") if sale.date else 'N/A',
            sale.total_amount,
            items_count,
            sale.status
        ])
    
    # Generate filename
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f'sales_report_{timestamp}'
    
    # Export in the specified format
    if format.lower() == 'csv':
        return export_to_csv(data, headers, filename)
    elif format.lower() == 'pdf':
        return export_to_pdf(data, headers, filename, title="Sales Report")
    else:
        raise ValueError(f"Unsupported format: {format}")

def generate_purchases_report(purchases, format='csv'):
    """
    Generate a purchases report in the specified format
    
    Args:
        purchases (list): List of Purchase objects
        format (str): Output format ('csv' or 'pdf')
        
    Returns:
        str: Path to the saved report file
    """
    # Prepare data
    headers = ['ID', 'Supplier', 'Date', 'Total Amount', 'Items Count', 'Status']
    data = []
    
    for purchase in purchases:
        supplier_name = purchase.supplier.name if purchase.supplier else 'N/A'
        items_count = len(purchase.items) if purchase.items else 0
        
        data.append([
            purchase.id,
            supplier_name,
            purchase.date.strftime("%Y-%m-%d") if purchase.date else 'N/A',
            purchase.total_amount,
            items_count,
            purchase.status
        ])
    
    # Generate filename
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f'purchases_report_{timestamp}'
    
    # Export in the specified format
    if format.lower() == 'csv':
        return export_to_csv(data, headers, filename)
    elif format.lower() == 'pdf':
        return export_to_pdf(data, headers, filename, title="Purchases Report")
    else:
        raise ValueError(f"Unsupported format: {format}")
