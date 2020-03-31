#Package imports
import sys
import numpy as np
import pickle
from itertools import groupby
import matplotlib.pyplot as plt
from sklearn import linear_model
from sklearn.metrics import mean_squared_error, r2_score

from sklearn.linear_model import Ridge
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import make_pipeline

#Module imports
sys.path.insert(0, 'database')
import mongoConfig
from mongoModels import Video, Behaviour, Prediction

def getAmountActionsByGenre(genre):
    actions = { "played": 0,
                "paused": 0,
                "fastforwarded": 0,
                "rewound": 0 }
    for video in mongoConfig.filterBehaviourByGenre(str(genre)):
        actions["played"] = actions["played"] + len(video.played)
        actions["paused"] = actions["paused"] + len(video.paused)
        actions["fastforwarded"] = actions["fastforwarded"] + len(video.fastforwarded)
        actions["rewound"] = actions["rewound"] + len(video.rewound)
    return actions

def getActionDataByGenre(genre):
    actionPercentTimes = []
    for video in mongoConfig.filterBehaviourByGenre(str(genre)):
        length = mongoConfig.findVideoById(video.videoID).length
        for time in video.played:
            actionPercentTimes.append(int((time/length)*100))
        for time in video.paused:
            actionPercentTimes.append(int((time/length)*100))
        for time in video.fastforwarded:
            actionPercentTimes.append(int((time/length)*100))
        for time in video.rewound:
            actionPercentTimes.append(int((time/length)*100))
    actionPercentTimes.sort()
    return actionPercentTimes

def generateGraphData(genre):
    data = getActionDataByGenre(str(genre))
    #Generate array of y values based on the amount of x occurances
    y = [len(list(group)) for key, group in groupby(data)]
    #Remove duplicate values
    x = list(set(data))
    #Re-sort to be ascending
    x.sort()

    #Initialize empty (full of zeros) 2D array
    xTrain = [[0] for a in range(len(x))]
    yTrain = [[0] for a in range(len(x))]

    #Shape data for linear regression
    #LR inputs a 2D array with structure [[1],[2],[3]]
    for elem in x:
        xTrain[x.index(elem)][0] = elem
        yTrain[x.index(elem)][0] = y[x.index(elem)]

    return xTrain, yTrain

# linearRegression(generateGraphData("Action")[0], generateGraphData("Action")[1])
def linearRegression(x, y):
    # Create linear regression object
    regr = linear_model.LinearRegression()

    # Train the model using the training sets
    regr.fit(x, y)

    # Make predictions using the testing set
    y_pred = regr.predict(x)

    # The coefficients
    print('Coefficients', regr.coef_)
    # The mean squared error
    print('Mean squared error: %.2f' % mean_squared_error(y, y_pred))
    # The coefficient of determination: 1 is perfect prediction
    print('Coefficient of determination: %.2f' % r2_score(y, y_pred))

    # Plot outputs
    plt.scatter(x, y,  color='black')
    plt.plot(x, y_pred, color='blue', linewidth=3)
    plt.xticks(())
    plt.yticks(())
    plt.show()

def polynomialInterpolation(x, y):
    plt.plot(x, y, color='cornflowerblue', linewidth=1, label="ground truth")
    plt.scatter(x, y, color='navy', s=30, marker='o', label="training points")

    colors = ['teal', 'yellowgreen', 'gold']
    for count, degree in enumerate([3, 4, 5]):
        model = make_pipeline(PolynomialFeatures(degree), Ridge())
        model.fit(x, y)
        y_plot = model.predict(x)
        plt.plot(x, y_plot, color=colors[count], linewidth=2, label="degree %d" % degree)

        #Most accurate model is at degree 5
        if degree == 5:
            # save the model to disk
            filename = 'finalized_model.sav'
            pickle.dump(model, open(filename, 'wb'))

    # plt.legend(loc='upper right')
    # plt.show()
    generatePredictions(x, y)

def generatePredictions(x, y):
    # load the model from disk
    loaded_model = pickle.load(open('finalized_model.sav', 'rb'))
    #print(loaded_model.score(x, y))
    yPredict = loaded_model.predict(x)

    predictedAction, count = [], 0
    for elem in yPredict:
        if (abs(elem[0] - y[count][0])) <= 0.25:
            # print(x[count][0])
            predictedAction.append(x[count][0])
        count += 1
    predictedAction.sort()
    mongoConfig.addPrediction(Prediction(genre="Action", activateControls=predictedAction))

polynomialInterpolation(generateGraphData("Action")[0], generateGraphData("Action")[1])
