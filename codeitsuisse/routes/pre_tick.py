import logging
import json
from io import StringIO
from fbprophet import Prophet
import pandas as pd
import numpy
from sklearn import preprocessing, linear_model
from sklearn.model_selection import TimeSeriesSplit

from flask import request, jsonify

from codeitsuisse import app

logger = logging.getLogger(__name__)


@app.route('/pre-tick', methods=['POST'])
def pre_tick():
    data = StringIO(request.get_data().decode('utf-8'))
    # rawdata = request.get_data().decode('utf-8')
    df = pd.read_csv(data)
    print(df)
    x = df[['Open', 'High', 'Low', 'Volume']]
    y = df[['Close']]
    df = pd.concat([x, y], axis=1)
    result = y.mean().values[0]
    logging.info("My result :{}".format(result))
    return json.dumps(result)


# @app.route('/pre-tick', methods=['POST'])
# def pre_tick():
#     data = StringIO(request.get_data().decode('utf-8'))
#     # rawdata = request.get_data().decode('utf-8')
#     df = pd.read_csv(data)
#     dr = pd.Series(pd.date_range('2000-1-1', periods=2000, freq='D'))
#     ds = pd.DataFrame({'ds': dr})
#     x = pd.concat([df[['Open', 'High', 'Low', 'Volume']], ds], axis=1)
#     y = df[['Close']]
#     fnt = pd.concat([x, y], axis=1)
#     # print(fnt)
#     fntc = fnt.copy()
#     train = fnt.sample(frac=1, random_state=0)
#     test = fntc.drop(train.index)
#     model = Prophet()
#     model.fit(train.reset_index().rename(columns={'Close': 'y'}))
#     # fcst = model.predict(test)
#     # print(fcst.head())
#     future = model.make_future_dataframe(periods=1)
#     fcst = model.predict(future)
#     result = fcst['yhat'].iloc[2000]
#     print('result:', result)
#     return json.dumps(result)

