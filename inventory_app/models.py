from inventory_app import db
from datetime import datetime

class Product(db.Model):
    product_id = db.Column(db.Integer, primary_key = True)
    sku_id = db.Column(db.String(20), nullable = False)
    product_name = db.Column(db.String(20),unique = True ,nullable = False)
    product_description =  db.Column(db.String(50))
    prodcut_price = db.Column(db.Numeric(10,2))

class Warehouse(db.Model):
    warehouse_id = db.Column(db.Integer, primary_key = True)
    warehouse_name = db.Column(db.String(20),unique = True, nullable = False)

class Allocation(db.Model):
    aid = db.Column(db.Integer, primary_key= True,nullable = False)
    product_name = db.Column(db.String(20),nullable = False)
    warehouse_name = db.Column(db.String(20),nullable = False)
    available_quantity = db.Column(db.Integer, nullable = False)
    reserved_qunatity =  db.Column(db.Integer, nullable = False)
    damaged_quantity = db.Column(db.Integer, nullable = False)

class AllocationLog(db.Model):
    lid = db.Column(db.Integer, primary_key= True)
    datetime = db.Column(db.DateTime, default=datetime.utcnow)
    warehouse_name = db.Column(db.String(20),nullable = False)
    product_name = db.Column(db.String(20),nullable = False)
    available_quantity = db.Column(db.Integer, nullable = False)
    reserved_qunatity =  db.Column(db.Integer, nullable = False)
    damaged_quantity = db.Column(db.Integer, nullable = False)  
    action = db.Column(db.String(20))
