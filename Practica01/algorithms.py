#########################################################################
# Comprueba si la palabra es válida para la variable
#########################################################################

def isFeasible(variable, palabra, listaVariables):

    # Si la palabra pasada por parámetro esta siendo utilizada en otra variable, FALSE
    for var in listaVariables:
        if var != variable:
            if var.valor == palabra:
                return False

    for restriction in variable.restricciones:
        # El vecino si tiene una palabra puesta
        if restriction[0].valor is not None:
            # Si donde se cruzan NO coincide su carácter, la palabra no es válida
            if palabra[restriction[1]] != restriction[0].valor[restriction[2]]:
                return False
    return True

#########################################################################
# Algoritmo backTracking
#########################################################################

def backTracking(k, listaVariables):
    if k == len(listaVariables):
        return True
    else:
        actualVariable = listaVariables[k]
        for dom in actualVariable.dominio:
            if isFeasible(actualVariable, dom, listaVariables):
                actualVariable.valor = dom
                if backTracking(k+1, listaVariables):
                    return True
                actualVariable.valor = None
    return False

#######################
# Comprueba si dos valores son consistentes en el cruce entre dos variables
# (La usa forward para podar dominios)
#######################

def esConsistenteFC(var_i ,valor_i, var_j, valor_j):
    for restriction in var_i.restricciones:
        if restriction[0] == var_j:
            if valor_i[restriction[1]] == valor_j[restriction[2]]:
                return True
            else:
                return False
    return True

########################################################################
# Poda los dominios de las variables futuras tras asignar la variable k
########################################################################

def forward(k, listaVariables):
    dominio_vacio = False
    var_i = listaVariables[k]
    valor_i = var_i.valor

    for j in range(k+1, len(listaVariables)):
        var_j = listaVariables[j]

        for a in var_j.dominio.copy():
            if not esConsistenteFC(var_i, valor_i, var_j, a):
                var_j.dominio.remove(a)
                var_j.podado.append((a, var_i))

        if len(var_j.dominio) == 0:
            dominio_vacio = True
            break
    return not dominio_vacio

###################################################################
# Restaura las podas realizadas por la variable k al desasignarla
###################################################################
def restaurar(k, listaVariables):
    var_i = listaVariables[k]

    for j in range(k+1, len(listaVariables)):
        var_j = listaVariables[j]

        for elem_podado in var_j.podado.copy():
            palabra, responsable = elem_podado
            if responsable == var_i:
                var_j.podado.remove(elem_podado)
                var_j.dominio.add(palabra)

#############################################################
# Algoritmo de Forward Checking
#############################################################
def FC(k, listaVariables):
    if k == len(listaVariables):
        return True
    actualVar = listaVariables[k]
    for a in listaVariables[k].dominio.copy():
        if isFeasible(actualVar, a, listaVariables):
            actualVar.valor = a
            if forward(k,listaVariables):
                if FC(k+1, listaVariables):
                    return True
            actualVar.valor = None
            restaurar(k, listaVariables)
    return False

#########################################################################
# AC3 (pseudocódigo del enunciado)
#########################################################################
def AC3(listaVariables):
    cola = []
    for var_i in listaVariables:
        for restriction in var_i.restricciones:
            cola.append((var_i, restriction[0]))

    while len(cola) > 0:
        var_k, var_m = cola.pop(0)
        cambio = False

        for palabra_k in var_k.dominio.copy():
            hay_apoyo = False
            for palabra_m in var_m.dominio:
                if esConsistenteFC(var_k, palabra_k, var_m, palabra_m):
                    hay_apoyo = True
                    break
            if not hay_apoyo:
                var_k.dominio.remove(palabra_k)
                cambio = True

        if len(var_k.dominio) == 0:
            return False

        if cambio:
            for restriction in var_k.restricciones:
                var_i = restriction[0]
                if var_i != var_m and (var_i, var_k) not in cola:
                    cola.append((var_i, var_k))
    return True

#########################################################################
# Backjumping
#########################################################################

def conflictosCon(variable, palabra, k, listaVariables):
    conflictos = set()

    for j in range(k):
        var_j = listaVariables[j]

        # Misma palabra ya usada por una variable anterior
        if var_j.valor == palabra:
            conflictos.add(j)

        # Letra distinta en el cruce con una variable anterior
        for restriction in variable.restricciones:
            if restriction[0] == var_j:
                if palabra[restriction[1]] != var_j.valor[restriction[2]]:
                    conflictos.add(j)

    return conflictos


def backJumpingRec(k, listaVariables):
    if k == len(listaVariables):
        return True, set()

    actualVar = listaVariables[k]
    actualVar.conflictos = set()

    for valor in actualVar.dominio:
        actualVar.valor = valor
        conflictosValor = conflictosCon(actualVar, valor, k, listaVariables)

        if len(conflictosValor) == 0:
            exito, conflictos = backJumpingRec(k+1, listaVariables)

            if exito:
                return True, set()

            if k not in conflictos:
                actualVar.valor = None
                return False, conflictos
            else:
                actualVar.conflictos = actualVar.conflictos | (conflictos - {k})

        else:
            actualVar.conflictos = actualVar.conflictos | conflictosValor

        actualVar.valor = None

    return False, actualVar.conflictos | {k}


def backJumping(k, listaVariables):
    exito, conflictos = backJumpingRec(k, listaVariables)
    return exito

