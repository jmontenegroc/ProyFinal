"""
 * Copyright 2020, Departamento de sistemas y Computación
 * Universidad de Los Andes
 *
 *
 * Desarrolado para el curso ISIS1225 - Estructuras de Datos y Algoritmos
 *
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 * Contribución de:
 *
 * Dario Correal
 *
 """
import config
from DISClib.ADT.graph import gr
from DISClib.ADT import map 
from DISClib.ADT import orderedmap as om
from DISClib.ADT import list as lt
from DISClib.DataStructures import mapentry as me
from DISClib.DataStructures import listiterator as it
from DISClib.Algorithms.Graphs import scc
from DISClib.Algorithms.Graphs import dijsktra as djk
from DISClib.Utils import error as error
import operator
import datetime
assert config

"""
En este archivo definimos los TADs que vamos a usar y las operaciones
de creacion y consulta sobre las estructuras de datos.
"""

# -----------------------------------------------------
#                       API
# -----------------------------------------------------

# Funciones para agregar informacion al grafo
def newAnalyzer():
    try:
        trips=om.newMap(omaptype='BST',
                            comparefunction=compareDates)

        return trips
    except Exception as exp:
        error.reraise(exp, 'model:newAnalyzer')

def addTrip(cont, trip):
    date=trip['trip_start_timestamp'][0:10]
    date=datetime.datetime.strptime(date, '%Y-%m-%d')
    date=date.date()
    entry = om.get(cont,date)
    if entry is None:
        datentry = newDataEntry(trip)
        om.put(cont, date, datentry)
    else:
        datentry=me.getValue(entry)
    addDateIndex(datentry, trip)

def newDataEntry(trip):
    """
    Crea una entrada en el indice por fechas, es decir en el arbol
    binario.
    """
    entry = {'taxiIndex': None, 'lstcrimes': None}
    entry['taxiIndex'] = map.newMap(numelements=30,
                                     maptype='PROBING',
                                     comparefunction=compareOffenses)
    entry['lsttrips'] = lt.newList('ARRAY_LIST', compareDates)
    return entry

def addDateIndex(datentry, trip):

    lst = datentry['lsttrips']
    lt.addLast(lst, trip)
    taxiIndex = datentry['taxiIndex']
    offentry = map.get(taxiIndex, trip['taxi_id'])
    if (offentry is None):
        entry = newOffenseEntry(trip['taxi_id'], trip)
        lt.addLast(entry['lsttrips'], trip)
        map.put(taxiIndex, trip['taxi_id'], entry)
    else:
        entry = me.getValue(offentry)
        lt.addLast(entry['lsttrips'], trip)
    return datentry

def newOffenseEntry(taxid, crime):

    ofentry = {'taxi': None, 'lst': None}
    ofentry['taxid'] = taxid
    ofentry['lsttrips'] = lt.newList('ARRAY_LIST', compareOffenses)
    return ofentry
# ==============================
# Funciones de consulta
# ==============================
def getdates(cont):
    date=input(print('Ingrese la fecha:'))
    n=int(input(print('Ingrese el numero de taxis:')))
    date=datetime.datetime.strptime(date, '%Y-%m-%d')
    date=date.date()
    crimedate=om.get(cont, date)
    a=me.getValue(crimedate)['taxiIndex']
    b=map.keySet(a)
    i=it.newIterator(b)
    puntajes={}
    while it.hasNext(i):
        c=it.next(i)
        millas=0
        servicios=0
        dinero=0
        taxi=map.get(a,c)
        taxi=me.getValue(taxi)
        taxi=taxi['lsttrips']
        x=it.newIterator(taxi)
        while it.hasNext(x):
            w=it.next(x)
            if float(w['trip_total'])>0:
                milla=float(w['trip_miles'])
                millas+=milla
                money=float(w['trip_total'])
                dinero+=money
                servicios+=1
        if dinero>0:
            puntaje=(millas/dinero)*servicios
            puntajes[c]=puntaje
    puntajes_ord=sorted(puntajes.items(),key=operator.itemgetter(1), reverse=True)
    num=1
    cent=0
    while n>=0:
        print(str(num)+'.'+puntajes_ord[cent][0]+' con un total de' +' '+str(puntajes_ord[cent][1]))
        num+=1
        cent+=1
        n-=1

def getdatesbyrange(cont):
    initialdate=input('ingrese la fecha inicial')
    finaldate=input('Ingrese la fecha final')
    n=int(input('Ingrese número de taxis:'))-1
    initialdate=datetime.datetime.strptime(initialdate, '%Y-%m-%d')
    initialdate=initialdate.date()
    finaldate=datetime.datetime.strptime(finaldate, '%Y-%m-%d')
    finaldate=finaldate.date()
    crimedates=om.values(cont,initialdate,finaldate)
    crimedates=crimedates['last']
    crimedates=crimedates['info']
    a=crimedates['taxiIndex']
    millas1={}
    dinero1={}
    servicios1={}
    b=map.keySet(a)
    i=it.newIterator(b)
    puntajes={}
    while it.hasNext(i):
        c=it.next(i)
        millas=0
        servicios=0
        dinero=0
        taxi=map.get(a,c)
        taxi=me.getValue(taxi)
        taxi=taxi['lsttrips']
        x=it.newIterator(taxi)
        while it.hasNext(x):
                w=it.next(x)                
                if float(w['trip_total'])>0:
                    milla=float(w['trip_miles'])
                    millas+=milla
                    money=float(w['trip_total'])
                    dinero+=money
                    servicios+=1    
        if dinero>0:
            if not w['taxi_id'] in millas1:
                millas1[w['taxi_id']]=millas
                servicios1[w['taxi_id']]=servicios
                dinero1[w['taxi_id']]=dinero
            if w['taxi_id'] in millas1:
                millas1[w['taxi_id']]=millas1[w['taxi_id']]+millas
                servicios1[w['taxi_id']]=servicios1[w['taxi_id']]
                dinero1[w['taxi_id']]=dinero1[w['taxi_id']]
    b=map.keySet(a)
    i=it.newIterator(b)
    puntajes={}
    millas=0
    dinero=0
    servicios=0
    while it.hasNext(i):
        c=it.next(i)
        if c in millas1:
            millas=millas1[c]
            dinero=dinero1[c]
            servicios=servicios1[c]
            puntaje=(millas/dinero)*servicios
            puntajes[c]=puntaje
    puntajes_ord=sorted(puntajes.items(),key=operator.itemgetter(1), reverse=True)
    num=1
    cent=0
    while n>=0:
        print(str(num)+'.'+puntajes_ord[cent][0]+' con un total de' +' '+str(puntajes_ord[cent][1]))
        num+=1
        cent+=1
        n-=1


# ==============================
# Funciones Helper
# ==============================

# ==============================
# Funciones de Comparacion
# ==============================
def compareDates(date1, date2):

    if (date1 == date2):
        return 0
    elif (date1 > date2):
        return 1
    else:
        return -1

def compareIds(id1, id2):

    if (id1 == id2):
        return 0
    elif id1 > id2:
        return 1
    else:
        return -1

def compareOffenses(offense1, offense2):
    """
    Compara dos ids de libros, id es un identificador
    y entry una pareja llave-valor
    """
    offense = me.getKey(offense2)
    if (offense1 == offense):
        return 0
    elif (offense1 > offense):
        return 1
    else:
        return -1