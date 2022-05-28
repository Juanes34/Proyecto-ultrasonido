from types import MethodType
from flask import Flask, render_template,request
from flask.wrappers import Request
import geocoder
from threading import Thread
from time import sleep
from pyo import *
import serial

app=Flask(__name__)
coordenadas=[]
sonido,volumen,distancia,cont2,recorrido=0,0,0,0,0

@app.route('/')
def ingreso():
    return render_template('inicio.html')

@app.route('/registro')
def registro():
    return render_template('registro.html')

@app.route('/login')
def inicio():
    return render_template('login.html')

@app.route('/regis',methods=['POST'])
def guardar_usuario():
    if request.method=="POST":
        usuario=request.form['usuario']
        password=request.form['password']
        resultado=verificar(usuario,password)
        if resultado==True:
            return render_template("registro2.html")
        else:
            savefile(usuario,password)
            return render_template('menu.html')

@app.route('/menu',methods=['POST'])
def menu():
    if request.method=="POST":
        usuario=request.form['usuario']
        password=request.form['password']
        resultado=verificar(usuario,password)
        if resultado==True:
            return render_template("menu.html")
        else:
            return render_template("login2.html")

@app.route('/menu2')
def menu2():
    global coordenadas
    saverecorrido(coordenadas)
    return render_template("menu.html")

@app.route('/menu3')
def menu3():
    return render_template("menu.html")

@app.route('/sensor')
def sensor():
    return render_template('sensor.html')

@app.route('/sensor2')
def sensor2():
    global distancia
    global volumen
    global sonido
    dis=int(distancia)
    vol=int(volumen)/100
    son=(int(sonido)*2)+200
    puerto=serial.Serial('COM4',9600)
    puerto.close()
    puerto.open()
    dato=puerto.readline().decode().strip()
    try:
        datofloat=float(dato)/100
        if datofloat<=dis:
            server = Server().boot()
            server.start()
            sine = Sine(son, mul=vol).out()
            for i in range(0,5):
                sleep(0.2)
            server.stop()
    except:
        pass
    return render_template('sensor2.html',dato=dato)

@app.route('/recorrido',methods=['POST','GET'])
def recorrido():
    global coordenadas
    if request.method=="POST":
        latitud=request.form['lati1']
        longitud=request.form['longi1']
        coords1=latitud+','+longitud
        coordenadas.append(coords1)
        return render_template('recorrido.html')
    else:
        return render_template('recorrido.html')

@app.route('/ajustes')
def ajustes():
    global sonido
    global volumen
    global distancia
    sonido=int(loadsonido())
    volumen=int(loadvolumen())
    distancia=int(loaddeteccion())
    return render_template('ajustes.html',sonido=sonido,volumen=volumen,distancia=distancia)

@app.route('/ajustes2',methods=['POST'])
def ajustes2():
    if request.method=="POST":
        global distancia
        global volumen
        global sonido
        distancia=request.form['distancia']
        volumen=request.form['volumen']
        sonido=request.form['tono']
        savedistancia(distancia)
        savesonido(sonido)
        savevolumen(volumen)
        return render_template('ajustes.html',sonido=sonido,volumen=volumen,distancia=distancia)
    else:
        return render_template('ajustes.html',sonido=sonido,volumen=volumen,distancia=distancia)

@app.route('/ajustes3',methods=['POST'])
def ajustes3():
    if request.method=="POST":
        global distancia
        global volumen
        global sonido
        distancia=request.form['distancia2']
        volumen=request.form['volumen2']
        sonido=request.form['tono2']
        volprueba=int(volumen)/100
        sonprueba=(int(sonido)*2)+200
        server = Server().boot()
        server.start()
        sine = Sine(sonprueba, mul=volprueba).out()
        for i in range(0,5):
            sleep(0.2)
        server.stop()
        return render_template('ajustes.html',sonido=sonido,volumen=volumen,distancia=distancia)
    else:
        return render_template('ajustes.html',sonido=sonido,volumen=volumen,distancia=distancia)

@app.route('/ajustes4')
def ajustes4():
    dis=int(loaddeteccion())
    vol=int(loadvolumen())
    son=int(loadsonido())
    print(dis)
    return render_template('ajustes.html',sonido=son,volumen=vol,distancia=dis)

@app.route('/verrecorrido')
def verrecorrido():
    global cont2
    cont2=0
    recorridos=[]
    recorridos=loadrecorridos()
    maximo=len(recorridos)
    return render_template('verrecorrido.html',maximo=maximo)

@app.route('/verrecorrido2',methods=['POST'])
def verrecorrido2():
    if request.method=="POST":
        global cont2
        global recorrido
        elec=int(request.form['eleccion'])
        recorridos=[]
        recorridos=loadrecorridos()
        maximo=len(recorridos)
        recorrido=recorridos[elec-1]
        dos=[]
        latitud=[]
        longitud=[]
        cont=0
        for i in recorrido:
            uno=i.replace("'","")
            uno=i.split(",")
            dos.append(uno)
        for i in dos:
            latitud.append(str(dos[cont][0]))
            longitud.append(str(dos[cont][1]))
            cont+=1
        cont2+=1
        try:
            return render_template('verrecorrido2.html',latitud=latitud[cont2-1],longitud=longitud[cont2-1],cont=cont2)
        except:
            return render_template('verrecorrido3.html',maximo=maximo)

@app.route('/verrecorrido3')
def verrecorrido3():
    global cont2
    global recorrido
    flag=len(recorrido)
    if flag<cont2:
        cont2=0
    recorridos=[]
    recorridos=loadrecorridos()
    maximo=len(recorridos)
    dos=[]
    latitud=[]
    longitud=[]
    cont=0
    for i in recorrido:
        uno=i.replace("'","")
        uno=i.split(",")
        dos.append(uno)
    for i in dos:
        latitud.append(str(dos[cont][0]))
        longitud.append(str(dos[cont][1]))
        cont+=1
    cont2+=1
    print(latitud,longitud)
    try:
        return render_template('verrecorrido2.html',latitud=latitud[cont2-1],longitud=longitud[cont2-1],cont=cont2)
    except:
        return render_template('verrecorrido3.html',maximo=maximo)

def verificar(usuario, password):
    cuentas=loadfromusers()
    cuent=False
    passw=False
    for a in cuentas:
        if usuario==a[0]:
            cuent=True
        if password==a[1]:
            passw=True
    if cuent==False:
        return False
    elif cuent==True and passw==False:
        return False
    elif cuent==True and passw==True:
        return True

def loadfromusers():
    users=[]
    total=[]
    fileusers=open("/Users/usuario/OneDrive/Escritorio/Dabm/Proyecto/bd/usuarios.csv","r")
    datos=fileusers.readlines()
    fileusers.close()
    for d in datos:
        users=[]
        d=d.replace("\n","")
        datos=d.split(";")
        usuario=datos[0]
        contraseña=datos[1]
        users.append(usuario)
        users.append(contraseña)
        total.append(users)
    return total

def loadrecorridos():
    recorridos=[]
    filerecorridos=open("/Users/usuario/OneDrive/Escritorio/Dabm/Proyecto/bd/recorridos.csv","r")
    datos=filerecorridos.readlines()
    filerecorridos.close()
    for d in datos:
        datos=0
        d=d.replace("\n","")
        recorridos.append(eval(d))
    return recorridos

def loadsonido():
    sonido1=0
    filesonido=open("/Users/usuario/OneDrive/Escritorio/Dabm/Proyecto/bd/sonido.csv","r")
    datos=filesonido.readlines()
    filesonido.close()
    for d in datos:
        sonido1=d
    return sonido1

def loadvolumen():
    volumen1=0
    filesvolumen=open("/Users/usuario/OneDrive/Escritorio/Dabm/Proyecto/bd/volumen.csv","r")
    datos=filesvolumen.readlines()
    filesvolumen.close()
    for d in datos:
        volumen1=d
    return volumen1

def loaddeteccion():
    distancia1=0
    filedeteccion=open("/Users/usuario/OneDrive/Escritorio/Dabm/Proyecto/bd/detección.csv","r")
    datos=filedeteccion.readlines()
    filedeteccion.close()
    for d in datos:
        distancia1=d
    return distancia1

def savefile(usuario,password):
    fileusers=open("/Users/usuario/OneDrive/Escritorio/Dabm/Proyecto/bd/usuarios.csv","a")
    cuenta=usuario+';'+password+'\n'
    fileusers.write(cuenta)
    fileusers.close()

def saverecorrido(coordenadas):
    filerec=open("/Users/usuario/OneDrive/Escritorio/Dabm/Proyecto/bd/recorridos.csv","a")
    cuenta=str(coordenadas)+'\n'
    filerec.write(cuenta)
    filerec.close()

def savesonido(sonido):
    filesonido=open("/Users/usuario/OneDrive/Escritorio/Dabm/Proyecto/bd/sonido.csv","a")
    cuenta=str(sonido)+'\n'
    filesonido.write(cuenta)
    filesonido.close()

def savevolumen(volumen):
    filevolumen=open("/Users/usuario/OneDrive/Escritorio/Dabm/Proyecto/bd/volumen.csv","a")
    cuenta=str(volumen)+'\n'
    filevolumen.write(cuenta)
    filevolumen.close()

def savedistancia(distancia):
    filesdistancia=open("/Users/usuario/OneDrive/Escritorio/Dabm/Proyecto/bd/detección.csv","a")
    cuenta=str(distancia)+'\n'
    filesdistancia.write(cuenta)
    filesdistancia.close()
if __name__=="__main__":
    app.run(debug=True)

