from flask import Flask

app = Flask(__name__)

import codeitsuisse.routes.square
import codeitsuisse.routes.revisitgeometry
import codeitsuisse.routes.olympiad_of_babylon
import codeitsuisse.routes.inventory_management
# import codeitsuisse.routes.clean_floor
import codeitsuisse.routes.social_distancing
import codeitsuisse.routes.cluster
import codeitsuisse.routes.optimizedportfolio
import codeitsuisse.routes.swaphedge
import codeitsuisse.routes.bucket_fill
import codeitsuisse.routes.word_segmentation
import codeitsuisse.routes.xerox
import codeitsuisse.routes.pre_tick