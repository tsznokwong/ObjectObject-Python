from flask import Flask
app = Flask(__name__)
import codeitsuisse.routes.square
import codeitsuisse.routes.revisitgeometry
import codeitsuisse.routes.olympiad_of_babylon
import codeitsuisse.routes.inventory_management
import codeitsuisse.routes.cluster