from flask import Flask, request, jsonify
from Bayes import Bayes
import json

app = Flask(__name__)


@app.route('/',methods=['POST'])
def API_example():
    tipo = request.get_json().get('tipo',None)
    precio = request.get_json().get('precio',None)
    hora = request.get_json().get('hora',None)
    dia = request.get_json().get('dia',None)
    restaurants = Bayes(tipo,precio,hora,dia)
    def obj_dict(obj):
        return obj.__dict__
    json_string = json.dumps(restaurants, default=obj_dict)
    json_loads = json.loads(json_string)
    return jsonify({'restaurants': json_loads})



if __name__ == '__main__':
  app.run(debug=True, host='0.0.0.0')