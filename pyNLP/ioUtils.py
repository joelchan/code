import json
from pathlib import Path

def loadOrRunSave(filePath, saveFunc, loadFunc):
    """
    @loadOrRunSave(fileName, saveJSON, loadJSON)
    def makeFunc():
        time.sleep(1000000)
        data = {'a': 1, 'b': 2}
        return data
    wrapped functions will load and return data on disk if exists. else run&save
    useful for long running functions
    :param filePath: Path object or string
    :param saveFunc: called as saveFunc(filePath, data) same for np.save
    :param loadFunc: called as loadFunc(filePath) same for np.load
    :return: result of loading saved data or running wrapped func
    """
    isPath = isinstance(filePath, Path)
    filePath = str(filePath) if isPath else filePath
    def decorator(makeFunc):
        def wraps(*args, **kwargs):
            try:
                data = loadFunc(filePath)
                return data
            except:
                data = makeFunc(*args, **kwargs)
                saveFunc(filePath, data)
                print('made it')
                return data
        return wraps
    return decorator

def loadJSON(fileName):
    with open(fileName, 'r') as input_handle:
        return json.load(input_handle)

def saveJSON(fileName, data):
    with open(fileName, 'w') as input_handle:
        return json.dump(data, input_handle)

import dill as pickle #to save default dict
def savePickle(fileName, data):
    pickle.dump(data, open(fileName, 'wb'))

def loadPickle(fileName):
    return pickle.load(open(fileName, 'rb'))

