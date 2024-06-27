#@Pablo Cortínez Serrano
#@Diego Enrique Vilches Jiménez
# app.py2
from flask import Flask, render_template, request, redirect, url_for, session, flash
from datetime import datetime
import bcrypt
import mysql.connector
import os
from cryptography.fernet import Fernet
import base64
import hashlib

app = Flask(__name__)

app.secret_key = os.urandom(24)
session_password = None
session_id = None

db_config = {
        'user' : 'diego',
        'password' : '711571',
        'host' : 'localhost',
        'database' : 'LOCKBOX_LOCAL_DEVELOPMENT'
        }

def signup_values(username, email, password_hash, creado_en, ultima_modificacion):
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        # Inserción en la tabla usuarios
        cursor.execute("""INSERT INTO usuario (nombre_usuario, correo_electronico, contraseña_hash, creado_en, ultima_modificacion)
                          VALUES (%s, %s, %s, %s, %s)""", (username, email, password_hash, creado_en, ultima_modificacion))
        conn.commit()
        cursor.close()

def credentials_values(id_usrcrd, nombre_sitio, url_sitio, nombre_usuario_sitio, contraseña_sitio):
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        creado_en = datetime.now()
        ultima_modificacion = datetime.now()
        # Inserción en la tabla usuarios
        cursor.execute("""INSERT INTO credencial (id_usrcrd, nombre_sitio, url_sitio, nombre_usuario_sitio, contraseña_sitio_hash, creado_en, ultima_modificacion, id_ico)
                          VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""", (id_usrcrd, nombre_sitio, url_sitio, nombre_usuario_sitio, contraseña_sitio, creado_en, ultima_modificacion, 7))
        conn.commit()
        cursor.close()

def verificar_datos(email, password):
    global session_password, session_id
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    aux = 'SELECT * FROM usuario WHERE correo_electronico = \'' + email + '\''
    cursor.execute(aux)
    row = cursor.fetchone()
    if row and check_password(bytes(row[3], 'utf-8'), password):
        session['username'] = str(row[1])
        session_password = str(row[3])
        session_id = str(row[0])
        return True
    else:
        return False
    conn.commit()
    cursor.close()


def check_password(hashed, password):
    return bcrypt.checkpw(password.encode('utf-8'), hashed)

# En un gestor de contraseñas una de las partes esenciales
# es la de mantener los datos de usuarios seguros, por lo que
# en la base de datos no podemos almacenar datos sensibles
# como las credenciales de usuarios, especificamente las contraseñas.
# O al menos no las podemos tener en su estado natural, es por esto 
# que utilizamos una función hash, que convierte un elemento de entrada
# en una versión ininteligible del mismo, o mejor dicho su versión 
# encriptada.

# Función principal para hashear una contraseña que recibe como argumento
# la contraseña del usuario (solo se manejará en ram y nunca se almacenará)
def hash_password(password):
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed 

def generate_key(session_password):
    key = hashlib.sha256(session_password.encode('utf-8')).digest()
    return base64.urlsafe_b64encode(key[:32])

def encrypt_credentials(session_password, credential_password):
    key = generate_key(session_password) # Al generar la key la session_password debe ir codificada
    cipher_suite = Fernet(key)
    encrypted_text = cipher_suite.encrypt(credential_password)
    return encrypted_text

def decrypt_credentials(session_password, encrypted_password):
    key = generate_key(session_password)
    cipher_suite = Fernet(key)
    decrypted_text = cipher_suite.decrypt(encrypted_password)
    return decrypted_text


def find_ico():
    return 0

@app.route('/')
def index():
    if 'username' in session:
        return render_template('index.html', username=session['username'])
    else:
        return redirect(url_for('login'))

################################################################################################################
        ## LOGIN DE USUARIOS ##
################################################################################################################
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        if verificar_datos(email, password):
            session_password = password
            return redirect(url_for('index'))
        else:
            flash('Correo Electrónico o Contraseña Invalida', 'error')
    
    return render_template('login.html')
################################################################################################################
@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('Se ha cerrado la sesión con éxito', 'info')
    return redirect(url_for('login'))
################################################################################################################
        ## REGISTRO DE USUARIOS ##
################################################################################################################
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        if password == confirm_password:
            password_hash = hash_password(password)
        else:
            flash('Las contraseñas no coinciden', 'error')
        
        creado_en = datetime.now()
        ultima_modificacion = datetime.now()
        if verificar_datos(username, email)=="Nusr":
            flash('El nombre de usuario ya está registrado', 'error')
        elif verificar_datos(username, email)=="Email":
            flash('El email ya está registrado', 'error')
        else:
            signup_values(username, email, password_hash, creado_en, ultima_modificacion)
            flash('Registro Realizado!', 'success')
            return redirect(url_for('login'))
            

    return render_template('signup.html')


@app.route('/add_credentials', methods=['GET', 'POST'])
def add_credentials():
    if request.method == 'POST':
        nombre_sitio = request.form['webname']
        url_sitio = request.form['weburl']
        nombre_usuario_sitio = request.form['username']
        contraseña_sitio = request.form['password']
        contraseña_confirmado = request.form['confirm_password']
        if contraseña_sitio == contraseña_confirmado:
            encrypted_password = encrypt_credentials(session_password, contraseña_sitio.encode('utf-8'))
            credentials_values(session_id, nombre_sitio, url_sitio, nombre_usuario_sitio, encrypted_password)
            flash('Registro Realizado!', 'success')
            return redirect(url_for('add_credentials'))
        else:
            flash('Las contraseñas no coinciden', 'error')
            return redirect(url_for('add_credentials'))
        

    return render_template('add_credentials.html')


@app.route('/view_credentials')
def view_credentials():
    if session_id == None:
        flash('La sesión ha expirado!', 'error')
        return redirect(url_for('login'))

    credentials = []
    with mysql.connector.connect(**db_config) as conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT nombre_sitio, url_sitio, nombre_usuario_sitio, contraseña_sitio_hash FROM credencial WHERE id_usrcrd='+session_id+';')
        credentials = cursor.fetchall()

    for credential in credentials:
        encrypted_password = credential['contraseña_sitio_hash']
        decrypted_password = decrypt_credentials(session_password, encrypted_password)
        credential['contraseña_sitio_hash'] = decrypted_password

    return render_template('view_credentials.html', credentials=credentials)
################################################################################################################
if __name__ == '__main__':
    app.run(debug=True)