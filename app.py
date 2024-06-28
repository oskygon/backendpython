from flask import Flask, jsonify, request, render_template, redirect, url_for
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from functools import wraps
from flask import request, Response

app = Flask(__name__)
CORS(app)

# Configuración de la base de datos
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:root@localhost/proyecto'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
ma = Marshmallow(app)

# Definir las tablas
class Producto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100))
    precio = db.Column(db.Integer)
    stock = db.Column(db.Integer)
    imagen = db.Column(db.String(400))

    def __init__(self, nombre, precio, stock, imagen):
        self.nombre = nombre
        self.precio = precio
        self.stock = stock
        self.imagen = imagen

class ProductoSchema(ma.Schema):
    class Meta:
        fields = ('id', 'nombre', 'precio', 'stock', 'imagen')

producto_schema = ProductoSchema()
productos_schema = ProductoSchema(many=True)

# Crear las tablas
with app.app_context():
    db.create_all()

# Función de autenticación
def check_auth(username, password):
    return username == 'admin' and password == 'adminpassword'

def authenticate():
    return Response(
        'No autorizado', 401,
        {'WWW-Authenticate': 'Basic realm="Login Required"'}
    )

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated

@app.route('/')
def index():
    return 'Bienvenidos al Backend!'

@app.route('/admin')
@requires_auth
def admin():
    return render_template('admin.html')

# Crear los endpoints o rutas (json)
@app.route('/productos', methods=['GET'])
def get_Productos():
    all_productos = Producto.query.all()
    result = productos_schema.dump(all_productos)
    return jsonify(result)

@app.route('/productos/<id>', methods=['GET'])
def get_producto(id):
    producto = Producto.query.get(id)
    return producto_schema.jsonify(producto)

@app.route('/productos/<id>', methods=['DELETE'])
def delete_producto(id):
    producto = Producto.query.get(id)
    db.session.delete(producto)
    db.session.commit()
    return producto_schema.jsonify(producto)

@app.route('/productos', methods=['POST'])
def create_producto():
    nombre = request.json['nombre']
    precio = request.json['precio']
    stock = request.json['stock']
    imagen = request.json['imagen']
    new_producto = Producto(nombre, precio, stock, imagen)
    db.session.add(new_producto)
    db.session.commit()
    return producto_schema.jsonify(new_producto)

@app.route('/productos/<id>', methods=['PUT'])
def update_producto(id):
    producto = Producto.query.get(id)
    producto.nombre = request.json['nombre']
    producto.precio = request.json['precio']
    producto.stock = request.json['stock']
    producto.imagen = request.json['imagen']
    db.session.commit()
    return producto_schema.jsonify(producto)

# Programa principal
if __name__ == '__main__':
    app.run(debug=True, port=5000)
