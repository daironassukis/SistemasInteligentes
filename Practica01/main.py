import pygame
from pygame.locals import *
import tkinter
from tkinter import *
from tkinter.simpledialog import *
from tkinter import messagebox as MessageBox
import sys
import time
import copy
from tablero import *
from variable import *
from algorithms import *
from tkinter.filedialog import askopenfilename

GREY=(190, 190, 190)
NEGRO=(100,100, 100)
BLANCO=(255, 255, 255)
GRIS_ACTIVO=(245,245,245)
GRIS_NORMAL=(169,169,169)

MARGEN=5 #ancho del borde entre celdas
MARGEN_DERECHO=125 #ancho del margen derecho entre la cuadrícula y la ventana
TAM=60  #tamaño de la celda

LLENA='*' 
VACIA='-'

#########################################################################
# Detecta si se pulsa un botón
#########################################################################   
def pulsaBoton(pos, boton):
    if boton.collidepoint(pos[0], pos[1]):    
        return True
    else:
        return False
    
#########################################################################
# Pintar un boton
#########################################################################   
def pintarBoton(screen, fuenteBot, boton, mensaje):
    if boton.collidepoint(pygame.mouse.get_pos()):
        pygame.draw.rect(screen, GRIS_ACTIVO, boton, 0)        
    else:
        pygame.draw.rect(screen, GRIS_NORMAL, boton, 0)
        
    texto=fuenteBot.render(mensaje, True, NEGRO)
    screen.blit(texto, (boton.x+(boton.width-texto.get_width())/2, boton.y+(boton.height-texto.get_height())/2))         

#########################################################################
# Pintar el crucigrama
#########################################################################         
def pintarTablero(screen, fuenteCelda,tablero, filas, cols):
    pygame.draw.rect(screen, GREY, [0, 0, filas*(TAM+MARGEN)+MARGEN, cols*(TAM+MARGEN)+MARGEN],0)
    for fil in range(tablero.getAlto()):
        for col in range(tablero.getAncho()):
            if tablero.getCelda(fil, col)==VACIA: 
                pygame.draw.rect(screen, BLANCO, [(TAM+MARGEN)*col+MARGEN, (TAM+MARGEN)*fil+MARGEN, TAM, TAM], 0)
            elif tablero.getCelda(fil, col)==LLENA: 
                pygame.draw.rect(screen, NEGRO, [(TAM+MARGEN)*col+MARGEN, (TAM+MARGEN)*fil+MARGEN, TAM, TAM], 0)
            else: #dibujar letra                    
                pygame.draw.rect(screen, BLANCO, [(TAM+MARGEN)*col+MARGEN, (TAM+MARGEN)*fil+MARGEN, TAM, TAM], 0)                
                texto= fuenteCelda.render(tablero.getCelda(fil, col), True, NEGRO)            
                screen.blit(texto, [(TAM+MARGEN)*col+MARGEN+15, (TAM+MARGEN)*fil+MARGEN+5])    
         
    
######################################################################### 
# Detecta si el ratón se pulsa en la cuadrícula
######################################################################### 
def inTablero(pos, filas, cols):
    if pos[0]>=MARGEN and pos[0]<=(TAM+MARGEN)*cols+MARGEN and pos[1]>=MARGEN and pos[1]<=(TAM+MARGEN)*filas+MARGEN:        
        return True
    else:
        return False
   
  
######################################################################### 
# Crea el almacen de palabras
######################################################################### 
def creaAlmacen(file):   
    f= open(file, 'r', encoding="utf-8")
    lista=f.read()
    f.close()
    listaPal=lista.split()
    almacen={}
    for pal in listaPal:        
        if len(pal) not in almacen:
            almacen[len(pal)]=set()
            almacen[len(pal)].add(pal.upper())
        else:
            almacen[len(pal)].add(pal.upper())   
    
    return almacen

######################################################################### 
# Imprime el contenido del almacen
######################################################################### 
def imprimeAlmacen(almacen):
    for tam, palabras in almacen.items():
        print (f'tam: {tam}: {palabras}')



#########################################################################
# Obtiene una lista de variables horizontales
#########################################################################
def construyeVariablesHorizontal(tablero, almacen):
    variables = []
    contador = 0

    for fila in range(tablero.getAlto()):
        longitudVariable = 0
        col_inicio = 0
        for col in range(tablero.getAncho()):
            if tablero.getCelda(fila,col) != LLENA:
                if longitudVariable == 0:
                    col_inicio = col
                longitudVariable += 1
                
            elif longitudVariable >= 2:                 # Evitamos crear variables de un solo hueco
                # Creamos la variable
                dominio = filtraDominioHorizontal(tablero, almacen, fila, col_inicio, longitudVariable)
                nuevaVariable = Variable(contador, "H", fila, col_inicio, longitudVariable, dominio)
                variables.append(nuevaVariable)
                contador += 1
                longitudVariable = 0
            else:
                longitudVariable = 0

        if longitudVariable >= 2:
            dominio = filtraDominioHorizontal(tablero, almacen, fila, col_inicio, longitudVariable)
            nuevaVariable = Variable(contador, "H", fila, col_inicio, longitudVariable, dominio)
            variables.append(nuevaVariable)
            contador += 1
            longitudVariable = 0

    return variables, contador

#########################################################################
# Calcula el dominio de una variable horizontal, filtrando por letras fijas
#########################################################################
def filtraDominioHorizontal(tablero, almacen, fila, col_inicio, longitud):
    dominio = almacen.get(longitud, set()).copy()

    for i in range(longitud):
        celda = tablero.getCelda(fila, col_inicio + i)
        if celda != VACIA and celda != LLENA:
            nuevoFiltrado = []
            for palabra in dominio:
                if palabra[i] == celda:
                    nuevoFiltrado.append(palabra)
            dominio = nuevoFiltrado

    return set(dominio)

#########################################################################
# Obtiene una lista de variables verticales
#########################################################################
def construyeVariablesVertical(tablero, almacen, contador):             # Aqui pasamos el contador como parametro para evitar que el nombre de las variables se solapen con los de la funcion "construyeVariablesHorizontal"
    variables = []

    for col in range(tablero.getAncho()):
        longitudVariable = 0
        fila_inicio = 0
        for fila in range(tablero.getAlto()):
            if tablero.getCelda(fila,col) != LLENA:
                if longitudVariable == 0:
                    fila_inicio = fila
                longitudVariable += 1
                
            elif longitudVariable >= 2:                 # Evitamos crear variables de un solo hueco
                # Creamos la variable
                dominio = filtraDominioVertical(tablero, almacen, fila_inicio, col, longitudVariable)

                nuevaVariable = Variable(contador, "V", fila_inicio, col, longitudVariable, dominio)
                variables.append(nuevaVariable)
                contador += 1
                longitudVariable = 0
            else:
                longitudVariable = 0

        if longitudVariable >= 2:
            dominio = filtraDominioVertical(tablero, almacen, fila_inicio, col, longitudVariable)
            nuevaVariable = Variable(contador, "V", fila_inicio, col, longitudVariable, dominio)
            variables.append(nuevaVariable)
            contador += 1
            longitudVariable = 0

    return variables

#########################################################################
# Calcula el dominio de una variable vertical, filtrando por letras fijas
#########################################################################
def filtraDominioVertical(tablero, almacen, fila_inicio, col, longitud):
    dominio = almacen.get(longitud, set()).copy()

    for i in range(longitud):
        celda = tablero.getCelda(fila_inicio + i, col)
        if celda != VACIA and celda != LLENA:
            nuevoFiltrado = []
            for palabra in dominio:
                if palabra[i] == celda:
                    nuevoFiltrado.append(palabra)
            dominio = nuevoFiltrado

    return set(dominio)


############################################################
# Obtiene la lista de variables horizontales + verticales, y sus restricciones
############################################################
def obtenerVariables(tablero, almacen):
    variablesHorizontales, contador = construyeVariablesHorizontal(tablero, almacen)
    variablesVerticales = construyeVariablesVertical(tablero, almacen, contador)
    todasVariables = variablesHorizontales + variablesVerticales
    encuentraRestricciones(todasVariables)
    return todasVariables

#########################################################################
# Calcula los cruces entre variables horizontales y verticales
#########################################################################
        
def encuentraRestricciones(listaVariables):
    variablesHorizontales = []
    variablesVerticales = []

    for v in listaVariables:
        if v.tipo == 'H':
            variablesHorizontales.append(v)
        else:
            variablesVerticales.append(v)

    for var_h in variablesHorizontales:
        for var_v in variablesVerticales:
                # CONDICIÓN 1: la variable vertical está posicionada entre la columna inicial y la columna final de la variable horizontal
                # CONDICIÓN 2: la variable horizontal está posicionada entre la fila inicial y la fila final
                # Si se cumplen las 2 condiciones, las variables se cruzan
                if var_h.col <= var_v.col <= var_h.col + var_h.longitud - 1 and var_v.fila <= var_h.fila <= var_v.fila + var_v.longitud - 1:
                    # En que posición de la variable se cruzan
                    pos_en_h = var_v.col - var_h.col
                    pos_en_v = var_h.fila - var_v.fila

                    var_h.restricciones.append((var_v, pos_en_h, pos_en_v))
                    var_v.restricciones.append((var_h, pos_en_v, pos_en_h))


#########################################################################
# Función pintarsolucion
#########################################################################
def pintarSolucion(listaVariables, tablero):
    for var in listaVariables:
        for i in range(var.longitud):
            if var.tipo == 'H':
                tablero.setCelda(var.fila, var.col+i, var.valor[i])
            else:
                tablero.setCelda(var.fila+i, var.col, var.valor[i])


#########################################################################
# Guarda el tablero en un fichero de texto con formato: 0/1/letra
#########################################################################

def guardarCrucigrama(tablero, file):
    f = open(file, 'w', encoding="utf-8")

    for fila in range(tablero.getAlto()):
        celdas = []
        for col in range(tablero.getAncho()):
            celda = tablero.getCelda(fila, col)
            if celda == VACIA:
                celdas.append('0')
            elif celda == LLENA:
                celdas.append('1')
            else:
                celdas.append(celda)
        f.write(' '.join(celdas) + '\n')
    f.close()


#########################################################################
# Resuelve el crucigrama con el algoritmo indicado
#########################################################################

def resuelve(algoritmo, tablero, todasVariables, tiempoAC3=None):
    inicio = time.perf_counter()
    resuelto = algoritmo(0, todasVariables)
    fin = time.perf_counter()
    tiempo = fin - inicio
    nombre = algoritmo.__name__

    if tiempoAC3 is None:
        print(f"{nombre}: {tiempo * 1e6:.0f} µs")
    else:
        print(f"AC3+{nombre}: {(tiempo + tiempoAC3) * 1e6:.0f} µs (AC3: {tiempoAC3 * 1e6:.0f} µs + {nombre}: {tiempo * 1e6:.0f} µs)")

    if resuelto:
        pintarSolucion(todasVariables, tablero)
    else:
        MessageBox.showwarning("Alerta", "No hay solución")

#########################################################################  
# Principal
#########################################################################
def main():
    root= tkinter.Tk() #para eliminar la ventana de Tkinter
    root.withdraw() #se cierra
    pygame.init()
    
    reloj=pygame.time.Clock()
    
    print("Uso: python main.py --filas M --columnas N --dic archivo.txt")
    
    if '--dic' in sys.argv:
        file = sys.argv[sys.argv.index("--dic") + 1]
    else:
        file='d0.txt'

    if '--filas' in sys.argv:
            filas = int(sys.argv[sys.argv.index("--filas") + 1])
    else:
        filas=5
    if '--columnas' in sys.argv:
        cols = int(sys.argv[sys.argv.index("--columnas") + 1])
    else:
        cols=6
        
    anchoVentana=cols*(TAM+MARGEN)+MARGEN_DERECHO
    altoVentana= filas*(TAM+MARGEN)+2*MARGEN 
    dimension=[anchoVentana,altoVentana]
    screen=pygame.display.set_mode(dimension) 
    pygame.display.set_caption("Practica 1: Crucigrama")    
     
    #La altura del botón depende del tamaño de la ventana pero hay una altura máxima
    altoBoton=altoVentana//7   
    if altoBoton>=65:
        altoBoton=65    
    
    posBotBK=altoVentana//8-altoBoton//2
    posBotBJ=(altoVentana//8)*2-altoBoton/2
    posBotFC=(altoVentana//8)*3-altoBoton//2
    posBotAC3=(altoVentana//8)*4-altoBoton//2
    posBotVariable=(altoVentana//8)*5-altoBoton//2
    posBotGuardarCrucigrama=(altoVentana//8)*6-altoBoton//2
    posBotCargarCrucigrama=(altoVentana//8)*7-altoBoton//2

    botBK=pygame.Rect(anchoVentana-95, posBotBK, 70, altoBoton)
    botBJ=pygame.Rect(anchoVentana-95, posBotBJ, 70, altoBoton)  
    botFC=pygame.Rect(anchoVentana-95,posBotFC , 70, altoBoton)
    botAC3=pygame.Rect(anchoVentana-95, posBotAC3, 70, altoBoton)
    botVariable=pygame.Rect(anchoVentana-95, posBotVariable, 70, altoBoton)
    botGuardarCrucigrama=pygame.Rect(anchoVentana-95, posBotGuardarCrucigrama, 70, altoBoton)
    botCargarCrucigrama=pygame.Rect(anchoVentana-95, posBotCargarCrucigrama, 70, altoBoton)

    tamFuenteBot=int(altoBoton//1.5)    
    fuenteBot=pygame.font.Font(None, tamFuenteBot)
    fuenteCelda= pygame.font.Font(None, 70)
    
    almacen=creaAlmacen(file)
    #imprimeAlmacen(almacen)
    game_over=False
    tablero=Tablero(filas, cols)

    todasVariables = None
    tiempoAC3 = None
    while not game_over:
        for event in pygame.event.get():
            if event.type==pygame.QUIT:               
                game_over=True
            if event.type==pygame.MOUSEBUTTONUP:                
                #obtener posición y calcular coordenadas matriciales                               
                pos=pygame.mouse.get_pos()                
                if pulsaBoton(pos, botBK):
                    if todasVariables is None:
                        todasVariables = obtenerVariables(tablero, almacen)
                    resuelve(backTracking, tablero, todasVariables, tiempoAC3)
                    todasVariables = None
                    tiempoAC3 = None

                elif pulsaBoton(pos, botBJ):
                    if todasVariables is None:
                        todasVariables = obtenerVariables(tablero, almacen)
                    resuelve(backJumping, tablero, todasVariables, tiempoAC3)
                    todasVariables = None
                    tiempoAC3 = None

                elif pulsaBoton(pos, botFC):
                    if todasVariables is None:
                        todasVariables = obtenerVariables(tablero, almacen)
                    resuelve(FC, tablero, todasVariables, tiempoAC3)
                    todasVariables = None
                    tiempoAC3 = None

                elif pulsaBoton(pos, botAC3):
                    if todasVariables is None:
                        todasVariables = obtenerVariables(tablero, almacen)
                    print("DOMINIOS ANTES DE AC3:")
                    for v in todasVariables:
                        print(v)
                    inicio = time.perf_counter()
                    resultado = AC3(todasVariables)
                    fin = time.perf_counter()

                    if tiempoAC3 is None:
                        tiempoAC3 = 0
                    tiempoAC3 = tiempoAC3 + (fin - inicio)
                    print(f"AC3: {(fin - inicio) * 1e6:.0f} µs")
                    if resultado:
                        print("DOMINIOS DESPUES DEL AC3")
                        for v in todasVariables:
                            print(v)
                    else:
                        MessageBox.showwarning("Alerta", "No hay solución")
                elif pulsaBoton(pos, botVariable):
                    todasVariables = obtenerVariables(tablero, almacen)
                    tiempoAC3 = None
                    for v in todasVariables:
                        print(v)

                elif pulsaBoton(pos, botGuardarCrucigrama):
                    nombre = askstring("Guardar", "Nombre del fichero (sin .txt)")
                    if nombre:
                        guardarCrucigrama(tablero, nombre + ".txt")
                    print("Crucigrama guardado")

                elif pulsaBoton(pos, botCargarCrucigrama):
                    ruta = askopenfilename(filetypes=[("Texto", "*.txt")])
                    if ruta:
                        tablero.cargar(ruta)
                        if tablero.getAlto() != filas or tablero.getAncho() != cols:
                            MessageBox.showwarning("Alerta", "El crucigrama guardado no tiene el tamaño del tablero actual")
                            tablero = Tablero(filas, cols)
                    todasVariables = None
                    tiempoAC3 = None

                elif inTablero(pos, filas, cols):
                    colDestino=pos[0]//(TAM+MARGEN)
                    filDestino=pos[1]//(TAM+MARGEN)                    
                    if event.button==1: #botón izquierdo
                        if tablero.getCelda(filDestino, colDestino)==VACIA:
                            tablero.setCelda(filDestino, colDestino, LLENA)
                        else:
                            tablero.setCelda(filDestino, colDestino, VACIA)
                    elif event.button==3: #botón derecho
                        c=askstring('Entrada', 'Introduce carácter')
                        if not c is None:
                            tablero.setCelda(filDestino, colDestino, c.upper())
                    todasVariables = None  
                    tiempoAC3 = None
        #limpiar pantalla
        screen.fill(GREY)
        #pintar crucigrama 
        pintarTablero(screen, fuenteCelda, tablero, filas, cols)                   
        #pintar botones           
        pintarBoton(screen, fuenteBot, botBK, "BK")
        pintarBoton(screen, fuenteBot, botBJ, "BJ")
        pintarBoton(screen, fuenteBot, botFC, "FC")
        pintarBoton(screen, fuenteBot, botAC3, "AC3")
        pintarBoton(screen, fuenteBot, botVariable, "VAR")
        pintarBoton(screen, fuenteBot, botGuardarCrucigrama, "SAVE")
        pintarBoton(screen, fuenteBot, botCargarCrucigrama, "LOAD")
        #actualizar pantalla
        pygame.display.flip()
        reloj.tick(40)
        if game_over==True: #retardo cuando se cierra la ventana
            pygame.time.delay(500)
    
    pygame.quit()
 
if __name__=="__main__":
    main()