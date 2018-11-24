import numpy as np
import pandas as pd
import json
from bayespy.nodes import Categorical, Mixture
from bayespy.inference import VB

class Restaurant:
    availability = "No Disponible"
    apreciation = "No Popular"

    def __init__(self, name, price, popularity, quorum, tipo,rating,description):
        self.name = name
        self.price = price
        self.popularity = popularity 
        self.quorum = quorum  
        self.tipo = tipo
        self.rating = rating
        self.description = description


def cargarExcel(tipo, precio):

  xl = pd.ExcelFile("restaurantes.xlsx")
  df = xl.parse("Sheet1")

  return df.loc[(df['tipo'] == tipo)&(df['price'] == precio)]

def parseToJSON(dataFrame):
  d = [ 
    dict([
        (colname, row[i]) 
        for i,colname in enumerate(dataFrame.columns)
    ])
    for row in dataFrame.values
  ]
  return json.dumps(d)


def Model(_tipo, _precio, _dia, _hora):
    FALSE = 0
    TRUE = 1

    def _or(p_false, p_true):    

        return np.take([p_false, p_true], [[FALSE, TRUE], [TRUE, TRUE]], axis=0)

   
    tipo = Categorical([0.6896551724, 0.3103448276])
    aforo = Categorical([0.4, 0.6])
    dia = Categorical([0.724137931, 0.275862069])


    precio = Mixture(tipo, Categorical, [[0.2, 0.8], [0.6, 0.4]])
    popularidad = Mixture(tipo, Categorical, [[0.4, 0.6], [0.7, 0.3]])
    horario = Mixture(dia, Categorical, [[0.9, 0.1], [0.3,0.7]])

    rating = Mixture(precio, Mixture, popularidad, Categorical,
                  _or([0.6, 0.4], [0.2, 0.8]))

    disponibilidad = Mixture(aforo, Mixture, horario, Mixture, popularidad, Categorical,
                       [_or([0.9, 0.1], [0.3, 0.7]),
                        _or([0.4, 0.6], [0.01, 0.99])])
    
    tipo.observe(TRUE if _tipo == "nacional" else FALSE)
    precio.observe(TRUE if _tipo == "economico" else FALSE)
    dia.observe(TRUE if _tipo == "semana" else FALSE)
    horario.observe(TRUE if _tipo == "tarde" else FALSE)

    Q = VB(tipo, aforo, dia, precio, popularidad, horario, rating, disponibilidad)
    Q.update(repeat=100)

    return{'rating': rating.get_moments()[0][TRUE],'disp':disponibilidad.get_moments()[0][TRUE]}

def Bayes(_tipo, _precio, _dia, _hora):

    df = cargarExcel(_tipo, _precio)
    jsondf = parseToJSON(df)
    jsonloads = json.loads(jsondf)

    restaurants = []
    for item in jsonloads:
        restaurant = Restaurant(
        item['name'],
        item['price'],
        item['popularity'],
        item['quorum'],
        item['tipo'],
        item['rating'],
        item['description']
        )
    
        restaurants.append(restaurant)

    for restaurant in restaurants:
        model = Model(restaurant.tipo, restaurant.price, _dia, _hora)
        restaurant.apreciation = model['rating']
        restaurant.disponibilidad = model['disp']
    return restaurants
