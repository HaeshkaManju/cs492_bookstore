#!/usr/bin/env python
"""
Database Seed Script
====================

Creates the database tables and populates with test data for prototyping.

Usage:
    python seed_database.py

This script will:
1. Create all database tables
2. Create test users (admin, employee, customer)
3. Create sample books, inventory, and warehouses
4. Create sample manufacturers

TEST ACCOUNTS (username = password for easy testing):
    - admin@bookstore.com / admin
    - employee@bookstore.com / employee  
    - customer@bookstore.com / customer
"""

import os
import sys
from decimal import Decimal

# Ensure we can import from app
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.extensions import db
from app.models import User, Customer, Book, Warehouse, Inventory, Manufacturer, Address


def create_test_users():
    """Create test users for each role."""
    users = []
    
    # Admin user
    admin = User(
        email='admin@bookstore.com',
        first_name='Admin',
        last_name='User',
        role='admin',
        is_active=True
    )
    admin.set_password('admin')
    users.append(admin)
    print("  Created: admin@bookstore.com / admin (Admin)")
    
    # Employee user
    employee = User(
        email='employee@bookstore.com',
        first_name='Employee',
        last_name='User',
        role='employee',
        is_active=True
    )
    employee.set_password('employee')
    users.append(employee)
    print("  Created: employee@bookstore.com / employee (Employee)")
    
    # Customer user
    customer_user = User(
        email='customer@bookstore.com',
        first_name='Customer',
        last_name='User',
        role='customer',
        is_active=True
    )
    customer_user.set_password('customer')
    users.append(customer_user)
    print("  Created: customer@bookstore.com / customer (Customer)")
    
    for user in users:
        db.session.add(user)
    
    db.session.flush()
    return users


def create_customer_profile(customer_user):
    """Create customer profile for the customer user."""
    customer = Customer(
        user_id=customer_user.id,
        company_name='Test Company LLC',
        phone='555-123-4567',
        credit_terms='Net 30',
        is_active=True
    )
    db.session.add(customer)
    db.session.flush()
    
    # Add a billing address
    address = Address(
        customer_id=customer.id,
        address_type='billing',
        street='123 Main Street',
        city='Boston',
        state='MA',
        zip_code='02101',
        country='USA',
        is_primary=True
    )
    db.session.add(address)
    print("  Created customer profile with billing address")
    
    return customer


def create_warehouses():
    """Create sample warehouses."""
    warehouses = [
        Warehouse(
            name='Main Warehouse',
            location='100 Storage Lane, Boston, MA 02102',
            capacity=5000
        ),
        Warehouse(
            name='Climate Controlled Vault',
            location='200 Archive Drive, Boston, MA 02103',
            capacity=1000
        ),
    ]
    
    for wh in warehouses:
        db.session.add(wh)
    
    db.session.flush()
    print(f"  Created {len(warehouses)} warehouses")
    return warehouses


def create_sample_books():
    """Create sample rare books."""
    books = [
        Book(
            isbn='978-0-14-028329-7',
            title='The Great Gatsby (First Edition)',
            author='F. Scott Fitzgerald',
            publisher='Charles Scribner\'s Sons',
            year_published=1925,
            category='Fiction',
            description='First edition, first printing. Original dust jacket present with minor wear.'
        ),
        Book(
            isbn='978-0-06-112008-4',
            title='To Kill a Mockingbird (Signed)',
            author='Harper Lee',
            publisher='J.B. Lippincott & Co.',
            year_published=1960,
            category='Fiction',
            description='First edition, signed by the author. Near fine condition.'
        ),
        Book(
            isbn='978-0-452-28423-4',
            title='1984 (First Edition)',
            author='George Orwell',
            publisher='Secker & Warburg',
            year_published=1949,
            category='Fiction',
            description='UK first edition. Red cloth binding, slight fading to spine.'
        ),
        Book(
            isbn='978-0-7432-7356-5',
            title='The Catcher in the Rye (First Edition)',
            author='J.D. Salinger',
            publisher='Little, Brown and Company',
            year_published=1951,
            category='Fiction',
            description='First edition with original dust jacket. Very good condition.'
        ),
        Book(
            isbn='978-0-19-953556-9',
            title='Pride and Prejudice (1813 Edition)',
            author='Jane Austen',
            publisher='T. Egerton',
            year_published=1813,
            category='Classic Literature',
            description='Extremely rare first edition, three volumes. Museum quality.'
        ),
        Book(
            isbn='978-0-553-21311-7',
            title='Moby-Dick (First American Edition)',
            author='Herman Melville',
            publisher='Harper & Brothers',
            year_published=1851,
            category='Classic Literature',
            description='First American edition. Original cloth binding, professionally restored.'
        ),
        Book(
            isbn='978-0-14-044913-6',
            title='Crime and Punishment (First Russian)',
            author='Fyodor Dostoevsky',
            publisher='The Russian Messenger',
            year_published=1866,
            category='Classic Literature',
            description='Original Russian serialization bound volume. Extremely rare.'
        ),
        Book(
            isbn='978-0-13-235088-4',
            title='Clean Code',
            author='Robert C. Martin',
            publisher='Prentice Hall',
            year_published=2008,
            category='Programming',
            description='First printing, signed by Uncle Bob.'
        ),
    ]
    
    for book in books:
        db.session.add(book)
    
    db.session.flush()
    print(f"  Created {len(books)} sample books")
    return books


def create_inventory(books, warehouses):
    """Create inventory entries for books."""
    main_warehouse = warehouses[0]
    vault = warehouses[1]
    
    inventory_items = [
        # Great Gatsby - valuable, in vault
        Inventory(
            book_id=books[0].id,
            warehouse_id=vault.id,
            condition=4,  # Very Good
            quantity=1,
            acquisition_cost=Decimal('15000.00'),
            list_price=Decimal('45000.00'),
            reorder_level=0,
            location_code='V-A1-001'
        ),
        # To Kill a Mockingbird - signed
        Inventory(
            book_id=books[1].id,
            warehouse_id=vault.id,
            condition=5,  # Fine
            quantity=1,
            acquisition_cost=Decimal('8000.00'),
            list_price=Decimal('25000.00'),
            reorder_level=0,
            location_code='V-A1-002'
        ),
        # 1984
        Inventory(
            book_id=books[2].id,
            warehouse_id=main_warehouse.id,
            condition=3,  # Good
            quantity=2,
            acquisition_cost=Decimal('3000.00'),
            list_price=Decimal('8500.00'),
            reorder_level=1,
            location_code='M-B2-015'
        ),
        # Catcher in the Rye
        Inventory(
            book_id=books[3].id,
            warehouse_id=main_warehouse.id,
            condition=4,  # Very Good
            quantity=1,
            acquisition_cost=Decimal('5000.00'),
            list_price=Decimal('12000.00'),
            reorder_level=0,
            location_code='M-B2-016'
        ),
        # Pride and Prejudice - museum quality
        Inventory(
            book_id=books[4].id,
            warehouse_id=vault.id,
            condition=4,  # Very Good
            quantity=1,
            acquisition_cost=Decimal('150000.00'),
            list_price=Decimal('450000.00'),
            reorder_level=0,
            location_code='V-S1-001'
        ),
        # Moby-Dick
        Inventory(
            book_id=books[5].id,
            warehouse_id=vault.id,
            condition=3,  # Good (restored)
            quantity=1,
            acquisition_cost=Decimal('25000.00'),
            list_price=Decimal('75000.00'),
            reorder_level=0,
            location_code='V-A2-001'
        ),
        # Clean Code - multiple copies
        Inventory(
            book_id=books[7].id,
            warehouse_id=main_warehouse.id,
            condition=5,  # Fine
            quantity=5,
            acquisition_cost=Decimal('50.00'),
            list_price=Decimal('150.00'),
            reorder_level=2,
            location_code='M-C1-042'
        ),
    ]
    
    for inv in inventory_items:
        db.session.add(inv)
    
    db.session.flush()
    print(f"  Created {len(inventory_items)} inventory entries")
    return inventory_items


def create_manufacturers():
    """Create sample book manufacturers/publishers."""
    manufacturers = [
        Manufacturer(
            name='Heritage Book Auctions',
            contact_name='James Morrison',
            email='james@heritageauctions.com',
            phone='214-528-3500',
            address='3500 Maple Avenue, Dallas, TX 75219'
        ),
        Manufacturer(
            name='Sotheby\'s Books',
            contact_name='Elizabeth Chen',
            email='e.chen@sothebys.com',
            phone='212-606-7000',
            address='1334 York Avenue, New York, NY 10021'
        ),
        Manufacturer(
            name='Bauman Rare Books',
            contact_name='David Bauman',
            email='info@baumanrarebooks.com',
            phone='212-751-0011',
            address='535 Madison Avenue, New York, NY 10022'
        ),
    ]
    
    for mfr in manufacturers:
        db.session.add(mfr)
    
    db.session.flush()
    print(f"  Created {len(manufacturers)} manufacturers/suppliers")
    return manufacturers


def seed_database():
    """Main function to seed the database."""
    app = create_app('development')
    
    with app.app_context():
        print("\n" + "=" * 60)
        print("DATABASE SEED SCRIPT")
        print("=" * 60)
        
        # Check if database already has data
        try:
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables_exist = 'users' in inspector.get_table_names()
            
            if tables_exist:
                existing_users = User.query.first()
                if existing_users:
                    print("\nWARNING: Database already contains data!")
                    response = input("Do you want to reset and reseed? (yes/no): ")
                    if response.lower() != 'yes':
                        print("Aborted.")
                        return
                    
                    print("\nDropping all tables...")
                    db.drop_all()
        except Exception:
            pass  # Tables don't exist yet, continue
        
        print("\nCreating database tables...")
        db.create_all()
        
        print("\nCreating test users...")
        users = create_test_users()
        
        # Find customer user for profile creation
        customer_user = next(u for u in users if u.role == 'customer')
        create_customer_profile(customer_user)
        
        print("\nCreating warehouses...")
        warehouses = create_warehouses()
        
        print("\nCreating sample books...")
        books = create_sample_books()
        
        print("\nCreating inventory...")
        create_inventory(books, warehouses)
        
        print("\nCreating manufacturers...")
        create_manufacturers()
        
        # Commit all changes
        db.session.commit()
        
        print("\n" + "=" * 60)
        print("DATABASE SEEDED SUCCESSFULLY!")
        print("=" * 60)
        print("\nTEST ACCOUNTS:")
        print("-" * 40)
        print("  Admin:    admin@bookstore.com / admin")
        print("  Employee: employee@bookstore.com / employee")
        print("  Customer: customer@bookstore.com / customer")
        print("-" * 40)
        print("\nYou can now run the application with: python run.py")
        print("=" * 60 + "\n")


if __name__ == '__main__':
    seed_database()
