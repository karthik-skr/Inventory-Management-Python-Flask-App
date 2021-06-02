from flask import  render_template,request,url_for,redirect
from flask.helpers import flash, url_for
from sqlalchemy.exc import IntegrityError, InternalError
from sqlalchemy import func

from inventory_app import app,db
from inventory_app.models import Product,Warehouse,Allocation,AllocationLog

@app.route('/')
def home_page():
   products = Product.query.all()
   return render_template('index.html',products = products)

@app.route('/product/add', methods=['POST'])
def add_product():
   formObj = request.form
   product_name = formObj["product_name"]
   product = Product(sku_id="SKU",product_name=product_name,product_description=formObj["product_description"],prodcut_price=formObj["prodcut_price"])
   db.session.add(product)
   try:
      db.session.commit()
      sku_id = "SKU_"+(product_name[0:5]).upper()+"_"+str(product.product_id)
      product.sku_id = sku_id
      db.session.commit()
   except IntegrityError:
      print("Exceptionn") #since product alreay exists
   return redirect(url_for('home_page'))

@app.route('/product/update', methods=['POST'])
def update_product():
   formObj = request.form
   Product.query.filter_by(product_id=int(formObj["product_id"])).update(dict(product_name=formObj["product_name"],product_description=formObj["product_description"],prodcut_price=float(formObj["prodcut_price"])))
   Allocation.query.filter_by(product_name=formObj["actual_product_name"]).update(dict(product_name=formObj["product_name"]))
   AllocationLog.query.filter_by(product_name=formObj["actual_product_name"]).update(dict(product_name=formObj["product_name"]))
   try:
      db.session.commit()
   except InternalError:
      print("Exceptionn") #since product alreay exists
   return redirect(url_for('home_page'))

@app.route('/product/delete', methods=['GET'])
def delete_product():
   product_id = int(request.args.get("product_id"))
   Product.query.filter_by(product_id=product_id).delete()
   db.session.commit()
   return redirect(url_for('home_page'))

@app.route('/warehouses')
def warehouses_page():
   warehouses = Warehouse.query.all()
   return render_template('warehouses.html',warehouses=warehouses)

@app.route('/warehouse/add', methods=['POST'])
def add_warehouse():
   formObj = request.form
   warehouse_name = formObj["warehouse_name"]
   warehouse = Warehouse(warehouse_name=warehouse_name)
   db.session.add(warehouse)
   try:
      db.session.commit()
   except IntegrityError:
      print("Exceptionn") #since warehouse alreay exists
   return redirect(url_for('warehouses_page'))

@app.route('/warehouse/update', methods=['POST'])
def update_warehouse():
   formObj = request.form
   Warehouse.query.filter_by(warehouse_id=int(formObj["warehouse_id"])).update(dict(warehouse_name=formObj["warehouse_name"]))
   Allocation.query.filter_by(warehouse_name=formObj["actual_warehouse_name"]).update(dict(warehouse_name=formObj["warehouse_name"]))
   AllocationLog.query.filter_by(product_name=formObj["actual_warehouse_name"]).update(dict(product_name=formObj["warehouse_name"]))
   try:
      db.session.commit()
   except InternalError:
      print("Exceptionn") #since warehouse alreay exists
   return redirect(url_for('warehouses_page'))

@app.route('/warehouse/delete', methods=['GET'])
def delete_warehouse():
   warehouse_id = int(request.args.get("warehouse_id"))
   Warehouse.query.filter_by(warehouse_id=warehouse_id).delete()
   db.session.commit()
   return redirect(url_for('warehouses_page'))

@app.route('/allocation')
def allocation_page():
   products_options = Product.query.with_entities(Product.product_name).all()
   warehouses_options = Warehouse.query.with_entities(Warehouse.warehouse_name).all()
   allocations = Allocation.query.order_by(Allocation.warehouse_name.desc(),Allocation.product_name.desc()).all()
   return render_template('allocations.html',allocations=allocations,products_options=products_options,warehouses_options=warehouses_options)

@app.route('/allocation/add', methods=['POST'])
def add_allocation():
   formObj = request.form
   allocation = Allocation(product_name=formObj["product_name"],warehouse_name=formObj["warehouse_name"],available_quantity=formObj["available_quantity"],reserved_qunatity=formObj["reserved_qunatity"],damaged_quantity=formObj["damaged_quantity"])
   db.session.add(allocation)
   allocLog = AllocationLog(product_name=formObj["product_name"],warehouse_name=formObj["warehouse_name"],available_quantity=formObj["available_quantity"],reserved_qunatity=formObj["reserved_qunatity"],damaged_quantity=formObj["damaged_quantity"],action="ADDED")
   db.session.add(allocLog)
   try:
      db.session.commit()
   except IntegrityError:
      print("Exceptionn")
   return redirect(url_for('allocation_page'))


@app.route('/allocation/update', methods=['POST'])
def update_allocation():
   formObj = request.form
   print(formObj)
   Allocation.query.filter_by(aid=int(formObj["aid"])).update(dict(available_quantity=formObj["available_quantity"],reserved_qunatity=formObj["reserved_qunatity"],damaged_quantity=formObj["damaged_quantity"]))
   allocLog = AllocationLog(product_name=formObj["product_name"],warehouse_name=formObj["warehouse_name"],available_quantity=formObj["available_quantity"],reserved_qunatity=formObj["reserved_qunatity"],damaged_quantity=formObj["damaged_quantity"],action="UPDATED")
   db.session.add(allocLog)
   try:
      db.session.commit()
   except IntegrityError:
      print("Exceptionn")
   return redirect(url_for('allocation_page'))

@app.route('/allocation/delete', methods=['GET'])
def delete_allocation():
   aid = int(request.args.get("aid"))
   alloationObj = Allocation.query.filter_by(aid=aid).first()
   print("alloationObj",alloationObj)
   Allocation.query.filter_by(aid=aid).delete()
   allocLog = AllocationLog(product_name=alloationObj.product_name,warehouse_name=alloationObj.warehouse_name,available_quantity=alloationObj.available_quantity,reserved_qunatity=alloationObj.reserved_qunatity,damaged_quantity=alloationObj.damaged_quantity,action="DELETED")
   db.session.add(allocLog)
   db.session.commit()
   return redirect(url_for('allocation_page'))

@app.route('/allocation_log')
def allocation_log_page():
   allocation_logs = AllocationLog.query.order_by(AllocationLog.datetime.desc(),AllocationLog.warehouse_name.desc(),AllocationLog.product_name.desc()).all()
   return render_template('allocation_log.html',allocation_logs=allocation_logs)

@app.route('/summary')
def summary():
   summary_by_warehouse = Allocation.query.with_entities(Allocation.warehouse_name,func.sum(Allocation.available_quantity).label('available_quantity'),func.sum(Allocation.reserved_qunatity).label('reserved_qunatity'),func.sum(Allocation.damaged_quantity).label('damaged_quantity')).group_by(Allocation.warehouse_name).all()
   
   summary_by_product = Allocation.query.with_entities(Allocation.product_name,func.sum(Allocation.available_quantity).label('available_quantity'),func.sum(Allocation.reserved_qunatity).label('reserved_qunatity'),func.sum(Allocation.damaged_quantity).label('damaged_quantity')).group_by(Allocation.product_name).all()

   return render_template('summary.html',summary_by_warehouse=summary_by_warehouse,summary_by_product=summary_by_product)
