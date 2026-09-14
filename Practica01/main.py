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
# Función auxiliar
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

    return dominio





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
# Función auxiliar
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

    return dominio


#########################################################################
# Función encuentraRestricciones
#########################################################################
        
def encuentraRestricciones(listaVariables):
    for var1 in listaVariables:
        for var2 in listaVariables:
            if var1.tipo != var2.tipo:
                if var1.tipo == 'H':
                    var_h = var1
                    var_v = var2
                else:
                    var_h = var2
                    var_v = var1

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
# Principal
#########################################################################
def main():
    root= tkinter.Tk() #para eliminar la ventana de Tkinter
    root.withdraw() #se cierra
    pygame.init()
    
    reloj=pygame.time.Clock()
    
    print("Uso: python main.py --filas M --columnas N --dic archivo.txt")
    if '--filas' in sys.argv:
        filas = int(sys.argv[sys.argv.index("--filas") + 1])
    else:
        filas=5
    if '--columnas' in sys.argv:
        cols = int(sys.argv[sys.argv.index("--columnas") + 1])
    else:
        cols=6
    if '--dic' in sys.argv:
        file = sys.argv[sys.argv.index("--fich") + 1]
    else:
        file='d0.txt'    
        
    anchoVentana=cols*(TAM+MARGEN)+MARGEN_DERECHO
    altoVentana= filas*(TAM+MARGEN)+2*MARGEN 
    dimension=[anchoVentana,altoVentana]
    screen=pygame.display.set_mode(dimension) 
    pygame.display.set_caption("Practica 1: Crucigrama")    
     
    #La altura del botón depende del tamaño de la ventana pero hay una altura máxima
    altoBoton=altoVentana//5    
    if altoBoton>=65:
        altoBoton=65    
    
    posBotBK=altoVentana//5-altoBoton//2
    posBotFC=(altoVentana//5)*2-altoBoton//2
    posBotAC3=(altoVentana//5)*3-altoBoton//2
    posBotVariable=(altoVentana//5)*4-altoBoton//2

    botBK=pygame.Rect(anchoVentana-95, posBotBK, 70, altoBoton)    
    botFC=pygame.Rect(anchoVentana-95,posBotFC , 70, altoBoton)
    botAC3=pygame.Rect(anchoVentana-95, posBotAC3, 70, altoBoton)
    botVariable=pygame.Rect(anchoVentana-95, posBotVariable, 70, altoBoton)

    tamFuenteBot=int(altoBoton//1.5)    
    fuenteBot=pygame.font.Font(None, tamFuenteBot)
    fuenteCelda= pygame.font.Font(None, 70)
    
    almacen=creaAlmacen(file)
    #imprimeAlmacen(almacen)
    game_over=False
    tablero=Tablero(filas, cols)

    ac3=False
    while not game_over:
        for event in pygame.event.get():
            if event.type==pygame.QUIT:               
                game_over=True
            if event.type==pygame.MOUSEBUTTONUP:                
                #obtener posición y calcular coordenadas matriciales                               
                pos=pygame.mouse.get_pos()                
                if pulsaBoton(pos, botBK):
                    print('BK')
                    res=True #esta variable debe estar a falso si el problema no tiene solución
                    if res==False:
                            MessageBox.showwarning("Alerta", "No hay solución")                     
                elif pulsaBoton(pos, botFC):
                    print('FC')
                    res=True #esta variable debe estar a falso si el problema no tiene solución               
                    if res==False:
                        MessageBox.showwarning("Alerta", "No hay solución")  
                elif pulsaBoton(pos, botAC3):
                    print('AC3')
                elif pulsaBoton(pos, botVariable):
                    variablesHorizontales, contador = construyeVariablesHorizontal(tablero, almacen)
                    variablesVerticales = construyeVariablesVertical(tablero, almacen, contador)    
                    todasVariables = variablesHorizontales + variablesVerticales
                    for v in todasVariables:
                        print(v)
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
        #limpiar pantalla
        screen.fill(GREY)
        #pintar crucigrama 
        pintarTablero(screen, fuenteCelda, tablero, filas, cols)                   
        #pintar botones           
        pintarBoton(screen, fuenteBot, botBK, "BK")
        pintarBoton(screen, fuenteBot, botFC, "FC")
        pintarBoton(screen, fuenteBot, botAC3, "AC3")
        pintarBoton(screen, fuenteBot, botVariable, "VAR") 
        #actualizar pantalla
        pygame.display.flip()
        reloj.tick(40)
        if game_over==True: #retardo cuando se cierra la ventana
            pygame.time.delay(500)
    
    pygame.quit()
 
if __name__=="__main__":
    main()
 
