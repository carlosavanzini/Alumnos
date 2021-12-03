from flask import Flask # usamos esto por que vamos a utilizar todo el framework
from flask import render_template,request,redirect,url_for
import flask# usamos request por que toda la info de html es envio
from flask.app import Flask # esto nos permite mostrar todos los template, mostraremos lo de index.html    
from flaskext.mysql import MySQL
from pymysql.cursors import Cursor #importamos la base de datos
from datetime import datetime #esto es para guardar las fotos segun el tiempo para que no sobrescriban
from flask import send_from_directory
import os #sirve para modificar foto si queremos



app=Flask(__name__)# con esta instruccion podemos usar flask


mysql=MySQL()#pasamos la instrucciones de donde se encuentra esa base de datos
app.config['MYSQL_DATABASE_HOST']='localhost'
app.config['MYSQL_DATABASE_USER']='root'
app.config['MYSQL_DATABASE_PASSWORD']=''
app.config['MYSQL_DATABASE_DB']='sistemaalumnos'
mysql.init_app(app)#iniciamos la base de datos

CARPETA=os.path.join('uploads')
app.config['CARPETA']=CARPETA

@app.route('/uploads/<nombreFoto>')
def uploads(nombreFoto):
    return send_from_directory(app.config['CARPETA'],nombreFoto)

@app.route('/') 
def index():
    sql="SELECT * FROM `alumnos`;"
    conn=mysql.connect()
    cursor=conn.cursor()
    cursor.execute(sql)
    alumnos=cursor.fetchall()
    print(alumnos)
    conn.commit()
    return render_template('alumnos/index.html', alumnos=alumnos)

@app.route("/destroy/<int:id>")
def destroy (id):
    conn=mysql.connect()
    cursor=conn.cursor()

    cursor.execute("SELECT foto FROM alumnos WHERE id=%s", id)
    fila=cursor.fetchall()

    os.remove(os.path.join(app.config['CARPETA'],fila[0][0]))

    cursor.execute("DELETE  FROM alumnos WHERE id=%s",(id))
    conn.commit()
    return redirect('/')

@app.route('/edit/<int:id>')
def edit(id):
    conn=mysql.connect()
    cursor=conn.cursor()
    cursor.execute("SELECT *FROM alumnos WHERE id=%s",(id))
    alumnos=cursor.fetchall()
    print(alumnos)
    conn.commit()
    return render_template('alumnos/edit.html', alumnos=alumnos)

@app.route('/update',methods=['POST'])
def update():
    _escuela=request.form['escuela']
    _nombre=request.form['nombre']
    _correo=request.form['email']
    _telefono=request.form['telefono']
    _foto=request.files['foto']
    id=request.form['txtid']
    sql="UPDATE alumnos SET escuela=%s, nombre=%s, correo=%s, telefono=%s WHERE id=%s;"

    datos=(_escuela,_nombre,_correo,_telefono,id)
    
    conn=mysql.connect()
    cursor=conn.cursor()

    now=datetime.now()
    tiempo=now.strftime("%Y%H%M%S")

    if _foto.filename!="":
        nuevoNombreFoto=tiempo+_foto.filename
        _foto.save("uploads/" + nuevoNombreFoto)
        
        cursor.execute("SELECT foto FROM alumnos WHERE id=%s", id)
        fila=cursor.fetchall()

        os.remove(os.path.join(app.config['CARPETA'],fila[0][0]))
        cursor.execute("UPDATE alumnos SET foto=%s WHERE id=%s",(nuevoNombreFoto,id))
        conn.commit()

    cursor.execute(sql,datos)
    conn.commit()

    return redirect('/')

@app.route('/create')#Con esto llamamos al archivo create 
def create():
    return render_template('alumnos/create.html')

@app.route('/store', methods=['POST'])
def storage():
    _escuela=request.form['escuela']
    _nombre=request.form['nombre']
    _correo=request.form['email']
    _telefono=request.form['telefono']
    _foto=request.files['foto']

    

    now=datetime.now()
    tiempo=now.strftime("%Y%H%M%S")

    if _foto.filename!="":
        nuevoNombreFoto=tiempo+_foto.filename
        _foto.save("uploads/" + nuevoNombreFoto)

    sql="INSERT INTO `alumnos` (`id`,`escuela`, `nombre`, `correo`, `telefono`, `foto`) VALUES (NULL,%s,%s,%s,%s,%s);"

    datos=(_escuela,_nombre,_correo,_telefono,nuevoNombreFoto)
    conn=mysql.connect()
    cursor=conn.cursor()
    cursor.execute(sql,datos)
    conn.commit()
    return redirect('/')
    


if __name__=='__main__':
    app.run(debug=True)