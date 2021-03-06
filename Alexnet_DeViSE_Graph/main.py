import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
import argparse
import numpy as np
import os
from scipy import spatial
import tensorflow as tf
from graphviz import Digraph
import globalV
from loadData import loadData
from attribute import attribute
from classify import classify
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

# For plotting
import plotly.plotly as py
import plotly.graph_objs as go
# py.sign_in('krittaphat.pug', 'oVTAbkhd2RQvodGOwrwp') # G-mail link
# py.sign_in('amps1', 'Z1KAk8xiPUyO2U58JV2K') # kpugdeet@syr.edu/12345678
py.sign_in('amps2', 'jGQHMBArdACog36YYCAI') # yli41@syr.edu/12345678
# py.sign_in('amps3', '5geLaNJlswmzDucmKikR') # liyilan0120@gmail.com/12345678


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    # Dataset Path
    parser.add_argument('--BASEDIR', type=str, default='/media/dataHD3/kpugdeet/', help='Base folder for dataset and logs')
    parser.add_argument('--AWA2PATH', type=str, default='AWA2/Animals_with_Attributes2/', help='Path for AWA2 dataset')
    parser.add_argument('--CUBPATH', type=str, default='CUB/CUB_200_2011/', help='Path for CUB dataset')
    parser.add_argument('--SUNPATH', type=str, default='SUN/SUNAttributeDB/', help='Path for SUN dataset')
    parser.add_argument('--APYPATH', type=str, default='APY/attribute_data/', help='Path for APY dataset')
    parser.add_argument('--GOOGLE', type=str, default='PRE/GoogleNews-vectors-negative300.bin', help='Path for google Word2Vec model')
    parser.add_argument('--KEY', type=str, default='APY',help='Choose dataset (AWA2, CUB, SUN, APY)')
    parser.add_argument('--DIR', type=str, default='APY_0', help='Choose working directory')

    # Image size
    parser.add_argument('--width', type=int, default=227, help='Width')
    parser.add_argument('--height', type=int, default=227, help='Height')

    # Hyper Parameter
    parser.add_argument('--maxSteps', type=int, default=1, help='Number of steps to run trainer.')
    parser.add_argument('--lr', type=float, default=1e-4, help='Initial learning rate')
    parser.add_argument('--numClass', type=int, default=32, help='Number of class')
    parser.add_argument('--batchSize', type=int, default=32, help='Batch size')
    parser.add_argument('--numAtt', type=int, default=300, help='Dimension of Attribute')

    # Initialize or Restore Model
    parser.add_argument('--TD', type=int, default=0, help='Train/Restore Darknet')
    parser.add_argument('--TA', type=int, default=0, help='Train/Restore Attribute')
    parser.add_argument('--TC', type=int, default=0, help='Train/Restore Classify')

    # Choose what to do
    parser.add_argument('--OPT', type=int, default=4, help='1.Darknet, 2.Attribute, 3.Classify, 4.Accuracy')
    parser.add_argument('--SELATT', type=int, default=1, help='1.Att, 2.Word2Vec, 3.Att+Word2Vec')
    globalV.FLAGS, _ = parser.parse_known_args()

    # Check Folder exist
    if not os.path.exists(globalV.FLAGS.BASEDIR + globalV.FLAGS.DIR):
        os.makedirs(globalV.FLAGS.BASEDIR + globalV.FLAGS.DIR)
        os.makedirs(globalV.FLAGS.BASEDIR + globalV.FLAGS.DIR + '/backup')
        os.makedirs(globalV.FLAGS.BASEDIR + globalV.FLAGS.DIR + '/attribute')
        os.makedirs(globalV.FLAGS.BASEDIR + globalV.FLAGS.DIR + '/attribute/logs')
        os.makedirs(globalV.FLAGS.BASEDIR + globalV.FLAGS.DIR + '/attribute/model')
        os.makedirs(globalV.FLAGS.BASEDIR + globalV.FLAGS.DIR + '/classify')
        os.makedirs(globalV.FLAGS.BASEDIR + globalV.FLAGS.DIR + '/classify/logs')
        os.makedirs(globalV.FLAGS.BASEDIR + globalV.FLAGS.DIR + '/classify/model')

    # Load data
    print('\nLoad Data for {0}'.format(globalV.FLAGS.KEY))
    (trainClass, trainAtt, trainVec, trainX, trainY, trainYAtt), (valClass, valAtt, valVec, valX, valY, valYAtt), (testClass, testAtt, testVec, testX, testY, testYAtt) = loadData.getData()
    if globalV.FLAGS.KEY == 'SUN' or globalV.FLAGS.KEY == 'APY':
        print('       {0:>10} {1:>12} {2:>10} {3:>20} {4:>10} {5:>12}'.format('numClass', 'classAtt', 'classVec','inputX', 'outputY', 'outputAtt'))
        print('Train: {0:>10} {1:>12} {2:>10} {3:>20} {4:>10} {5:>12}'.format(len(trainClass), str(trainAtt.shape), str(trainVec.shape), str(trainX.shape), str(trainY.shape), str(trainYAtt.shape)))
        print('Valid: {0:>10} {1:>12} {2:>10} {3:>20} {4:>10} {5:>12}'.format(len(valClass), str(valAtt.shape), str(valVec.shape), str(valX.shape), str(valY.shape), str(valYAtt.shape)))
        print('Test:  {0:>10} {1:>12} {2:>10} {3:>20} {4:>10} {5:>12}'.format(len(testClass), str(testAtt.shape), str(testVec.shape), str(testX.shape), str(testY.shape), str(testYAtt.shape)))
    else:
        print('       {0:>10} {1:>12} {2:>10} {3:>20} {4:>10}'.format('numClass', 'classAtt', 'classVec','inputX', 'outputY'))
        print('Train: {0:>10} {1:>12} {2:>10} {3:>20} {4:>10}'.format(len(trainClass), str(trainAtt.shape), str(trainVec.shape), str(trainX.shape), str(trainY.shape)))
        print('Valid: {0:>10} {1:>12} {2:>10} {3:>20} {4:>10}'.format(len(valClass), str(valAtt.shape), str(valVec.shape), str(valX.shape), str(valY.shape)))
        print('Test:  {0:>10} {1:>12} {2:>10} {3:>20} {4:>10}'.format(len(testClass), str(testAtt.shape), str(testVec.shape), str(testX.shape), str(testY.shape)))

    # Show class name that index with total classes
    def printClassName(pos):
        if pos < len(trainClass):
            return trainClass[pos]
        elif pos < len(trainClass)+len(valClass):
            return valClass[pos-len(trainClass)]
        else:
            return testClass[pos-len(trainClass)-len(valClass)]

    # Attribute Modification
    concatAtt = np.concatenate((trainAtt, valAtt, testAtt), axis=0)
    word2Vec_concatAtt = np.concatenate((trainVec, valVec, testVec), axis=0)
    combineAtt = np.concatenate((concatAtt, word2Vec_concatAtt), axis=1)

    if globalV.FLAGS.SELATT == 1:
        concatAtt_D = concatAtt
    elif globalV.FLAGS.SELATT == 2:
        concatAtt_D = word2Vec_concatAtt
    else:
        concatAtt_D = combineAtt

    # Check where there is some class that has same attributes
    print('\nCheck matching classes attributes')
    for i in range(concatAtt_D.shape[0]):
        for j in range(i + 1, concatAtt_D.shape[0]):
            if np.array_equal(concatAtt_D[i], concatAtt_D[j]):
                print('{0} {1}: {2} {3}'.format(i, printClassName(i), j, printClassName(j)))
    print('')

    # Build Tree
    distanceFunc = spatial.distance.euclidean
    tmpConcatAtt = np.copy(concatAtt_D)
    tmpConcatName = list(trainClass+valClass+testClass)
    excludeNode = list()
    treeMap = dict()
    while len(excludeNode) != tmpConcatAtt.shape[0]-1:
        dMatrix = np.ones((tmpConcatAtt.shape[0], tmpConcatAtt.shape[0]))*100
        for i in range(dMatrix.shape[0]):
            for j in range(dMatrix.shape[1]):
                if i != j and i not in excludeNode and j not in excludeNode:
                    dMatrix[i][j] = distanceFunc(tmpConcatAtt[i], tmpConcatAtt[j])
        ind = np.unravel_index(np.argmin(dMatrix, axis=None), dMatrix.shape)
        tmpAvg = np.expand_dims((tmpConcatAtt[ind[0]] + tmpConcatAtt[ind[1]])/2, axis=0)
        tmpConcatAtt = np.concatenate((tmpConcatAtt, tmpAvg), axis=0)
        tmpConcatName.append(tmpConcatAtt.shape[0]-1)
        excludeNode.append(ind[0])
        excludeNode.append(ind[1])
        treeMap[tmpConcatAtt.shape[0]-1] = ind
    # Visualize
    dot = Digraph(format='png')
    def recursiveAddEdges(index):
        if index in treeMap:
            dot.edge(str(index), str(treeMap[index][0]))
            dot.edge(str(index), str(treeMap[index][1]))
            recursiveAddEdges(treeMap[index][0])
            recursiveAddEdges(treeMap[index][1])
    for i in range(tmpConcatAtt.shape[0]):
        if i < 32:
            dot.node(str(i), str(tmpConcatName[i]))
        else:
            tmpStr = distanceFunc(tmpConcatAtt[treeMap[i][0]], tmpConcatAtt[treeMap[i][1]])
            dot.node(str(i), str(round(tmpStr, 2)) + "_" + str(i))
    recursiveAddEdges(tmpConcatAtt.shape[0]-1)
    dot.render('Tree.gv')

    # Split train data 70/30 for each class
    trX70 = None; trY70 = None; trAtt70 = None
    trX30 = None; trY30 = None; trAtt30 = None
    for z in range(0, len(trainClass)):
        eachInputX = []
        eachInputY = []
        eachInputAtt = []
        for k in range(0, trainX.shape[0]):
            if trainY[k] == z:
                eachInputX.append(trainX[k])
                eachInputY.append(trainY[k])
                # eachInputAtt.append(concatAtt_D[trainY[k]])
                eachInputAtt.append(trainYAtt[k])
        eachInputX = np.array(eachInputX)
        eachInputY = np.array(eachInputY)
        eachInputAtt = np.array(eachInputAtt)
        divEach = int(eachInputX.shape[0] * 0.7)
        if trX70 is None:
            trX70 = eachInputX[:divEach]
            trY70 = eachInputY[:divEach]
            trAtt70 = eachInputAtt[:divEach]
            trX30 = eachInputX[divEach:]
            trY30 = eachInputY[divEach:]
            trAtt30 = eachInputAtt[divEach:]
        else:
            trX70 = np.concatenate((trX70,  eachInputX[:divEach]), axis=0)
            trY70 = np.concatenate((trY70, eachInputY[:divEach]), axis=0)
            trAtt70 = np.concatenate((trAtt70, eachInputAtt[:divEach]), axis=0)
            trX30 = np.concatenate((trX30, eachInputX[divEach:]), axis=0)
            trY30 = np.concatenate((trY30, eachInputY[divEach:]), axis=0)
            trAtt30 = np.concatenate((trAtt30, eachInputAtt[divEach:]), axis=0)

    # Balance training class
    baX70 = None;
    baY70 = None
    sampleEach = 500

    for z in range(len(trainClass)):
        eachInputX = []
        eachInputY = []
        for k in range(0, trX70.shape[0]):
            if trY70[k] == z:
                eachInputX.append(trX70[k])
                eachInputY.append(trY70[k])
        eachInputX = np.array(eachInputX)
        eachInputY = np.array(eachInputY)

        if eachInputX.shape[0] > sampleEach:
            if baX70 is None:
                baX70 = eachInputX[:sampleEach]
                baY70 = eachInputY[:sampleEach]
            else:
                baX70 = np.concatenate((baX70, eachInputX[:sampleEach]), axis=0)
                baY70 = np.concatenate((baY70, eachInputY[:sampleEach]), axis=0)
        else:
            duX70 = np.copy(eachInputX)
            duAtt70 = np.copy(eachInputY)
            while duX70.shape[0] < sampleEach:
                duX70 = np.concatenate((duX70, eachInputX), axis=0)
                duAtt70 = np.concatenate((duAtt70, eachInputY), axis=0)
            if baX70 is None:
                baX70 = duX70[:sampleEach]
                baY70 = duAtt70[:sampleEach]
            else:
                baX70 = np.concatenate((baX70, duX70[:sampleEach]), axis=0)
                baY70 = np.concatenate((baY70, duAtt70[:sampleEach]), axis=0)

    # Val class
    s = np.arange(valX.shape[0])
    tmp = list()
    for i in range(valY.shape[0]):
        # tmp.append(concatAtt_D[valY[i]+len(trainClass)])
        tmp.append(valYAtt[i])
    vX = valX[s]
    vY = valY[s] + len(trainClass)
    vAtt = np.array(tmp)[s]

    # Test class
    s = np.arange(testX.shape[0])
    tmp = list()
    for i in range(testY.shape[0]):
        # tmp.append(concatAtt_D[testY[i]+len(trainClass)+len(valClass)])
        tmp.append(testYAtt[i])
    teX = testX[s]
    teY = testY[s] + len(trainClass) + len(valClass)
    teAtt = np.array(tmp)[s]

    # Balance testing class
    baTeX = None;
    baTeY = None;
    baTeAtt = None
    sampleEach = 150

    for z in range(20, 32):
        eachInputX = []
        eachInputY = []
        eachInputAtt = []
        for k in range(0, teX.shape[0]):
            if teY[k] == z:
                eachInputX.append(teX[k])
                eachInputY.append(teY[k])
                eachInputAtt.append(teAtt[k])
        eachInputX = np.array(eachInputX)
        eachInputY = np.array(eachInputY)
        eachInputAtt = np.array(eachInputAtt)

        if baTeX is None:
            baTeX = eachInputX[:sampleEach]
            baTeY = eachInputY[:sampleEach]
            baTeAtt = eachInputAtt[:sampleEach]
        else:
            baTeX = np.concatenate((baTeX, eachInputX[:sampleEach]), axis=0)
            baTeY = np.concatenate((baTeY, eachInputY[:sampleEach]), axis=0)
            baTeAtt = np.concatenate((baTeAtt, eachInputAtt[:sampleEach]), axis=0)

    print('Shuffle Data shape')
    print(trX70.shape, trY70.shape, trAtt70.shape)
    print(trX30.shape, trY30.shape, trAtt30.shape)
    print(vX.shape, vY.shape, vAtt.shape)
    print(teX.shape, teY.shape, teAtt.shape)
    print(baX70.shape, baY70.shape)

    # Get all Classes name and attribute name
    allClassName = np.concatenate((np.concatenate((trainClass, valClass), axis=0), testClass), axis=0)
    with open(globalV.FLAGS.BASEDIR + globalV.FLAGS.APYPATH + 'attribute_names.txt', 'r') as f:
        allClassAttName = [line.strip() for line in f]

    if globalV.FLAGS.OPT == 2:
        print('\nTrain Attribute')
        attModel = attribute()
        attModel.trainAtt(baX70, baY70,
                          vX, vY-len(trainClass),
                          teX, teY-len(trainClass)-len(valClass),
                          concatAtt_D[:len(trainClass)],
                          concatAtt_D[len(trainClass):len(trainClass)+len(valClass)],
                          concatAtt_D[len(trainClass)+len(valClass):])


    elif globalV.FLAGS.OPT == 4:
        print('\nClassify')
        g1 = tf.Graph()
        with g1.as_default():
            model = attribute()

        predY = model.getClassIndex(trX30, concatAtt_D)
        print('Train Accuracy = {0:.4f}%'.format(np.mean(np.equal(predY, trY30))*100))
        predY = model.getClassIndex(vX, concatAtt_D)
        print('Val Accuracy = {0:.4f}%'.format(np.mean(np.equal(predY, vY)) * 100))
        predY = model.getClassIndex(teX, concatAtt_D)
        print('Test Accuracy = {0:.4f}%'.format(np.mean(np.equal(predY, teY)) * 100))
        predY = model.getClassIndex(baTeX, concatAtt_D)
        print('Balance Test Accuracy = {0:.4f}%'.format(np.mean(np.equal(predY, baTeY)) * 100))

        # Euclidean distance
        print('\nEuclidean')
        attTmp = model.getAttribute(trX30)
        predY = []
        for pAtt in attTmp:
            distance = []
            for cAtt in concatAtt_D:
                distance.append(spatial.distance.euclidean(pAtt, cAtt))
            ind = np.argsort(distance)[:1]
            predY.append(ind[0])
        print('Train Accuracy = {0:.4f}%'.format(np.mean(np.equal(predY, trY30)) * 100))
        attTmp = model.getAttribute(vX)
        predY = []
        for pAtt in attTmp:
            distance = []
            for cAtt in concatAtt_D:
                distance.append(spatial.distance.euclidean(pAtt, cAtt))
            ind = np.argsort(distance)[:1]
            predY.append(ind[0])
        print('Val Accuracy = {0:.4f}%'.format(np.mean(np.equal(predY, vY)) * 100))
        attTmp = model.getAttribute(teX)
        predY = []
        for pAtt in attTmp:
            distance = []
            for cAtt in concatAtt_D:
                distance.append(spatial.distance.euclidean(pAtt, cAtt))
            ind = np.argsort(distance)[:1]
            predY.append(ind[0])
        print('Test Accuracy = {0:.4f}%'.format(np.mean(np.equal(predY, teY)) * 100))

        # Top Accuracy
        topAccList = [1, 3, 5, 7, 10]
        for topAcc in topAccList:
            print('\nTop {0} Accuracy'.format(topAcc))
            tmpScore = model.getScore(trX30, concatAtt_D)
            tmpSort = np.argsort(-tmpScore, axis=1)
            tmpPred = tmpSort[:,:topAcc]
            count = 0
            for i, p in enumerate(tmpPred):
                if trY30[i] in p:
                    count += 1
            print('Train Accuracy = {0:.4f}%'.format((count/trX30.shape[0])*100))
            tmpScore = model.getScore(vX, concatAtt_D)
            tmpSort = np.argsort(-tmpScore, axis=1)
            tmpPred = tmpSort[:, :topAcc]
            count1 = 0
            for i, p in enumerate(tmpPred):
                if vY[i] in p:
                    count1 += 1
            print('Val Accuracy = {0:.4f}%'.format((count1 / vX.shape[0]) * 100))
            tmpScore = model.getScore(teX, concatAtt_D)
            tmpSort = np.argsort(-tmpScore, axis=1)
            tmpPred = tmpSort[:, :topAcc]
            count2 = 0
            for i, p in enumerate(tmpPred):
                if teY[i] in p:
                    count2 += 1
            print('Test Accuracy = {0:.4f}%'.format((count2 / teX.shape[0]) * 100))
            print('Average Accuracy = {0:.4f}%'.format(((count+count1+count2) / (trX30.shape[0]+vX.shape[0]+teX.shape[0])) * 100))

        # Accuracy for each class and Confusion matrix
        topAccList = [1, 3, 5, 7, 10]
        print('')
        for topAcc in topAccList:
            confusion = []
            # Loop each Train class
            for z in range(0, 15):
                eachInputX = []
                eachInputY = []
                for k in range(0, trX30.shape[0]):
                    if trY30[k] == z:
                        eachInputX.append(trX30[k])
                        eachInputY.append(trY30[k])
                eachInputX = np.array(eachInputX)
                eachInputY = np.array(eachInputY)
                predY = model.getClassIndex(eachInputX, concatAtt_D)

                # Confusion matrix
                tmpScore = model.getScore(eachInputX, concatAtt_D)
                tmpSort = np.argsort(-tmpScore, axis=1)
                tmpPred = tmpSort[:, :topAcc]
                tmpPred = np.reshape(tmpPred, -1)
                tmpCountEach = np.bincount(tmpPred, minlength=32)
                tmpCountEach = np.array(tmpCountEach)/(eachInputX.shape[0]*topAcc)
                confusion.append(tmpCountEach)

                if topAcc == 1:
                    print('Class: {0:<15} Size: {1:<10} Accuracy = {2:.4f}%'.format(printClassName(z), eachInputX.shape[0], np.mean(np.equal(predY, eachInputY)) * 100))
                    # Predict attribute for each class and plot
                    s = np.arange(eachInputX.shape[0])
                    np.random.shuffle(s)
                    eachInputX = eachInputX[s]
                    tmpPredAtt = model.getAttribute(eachInputX[:10])
                    tmpPredClass = ['' for x in range(tmpPredAtt.shape[0])]
                    top5Index = np.argsort(-tmpCountEach)[:5]
                    top5PredAtt = concatAtt_D[top5Index, :]
                    top5PredClass = [printClassName(x) for x in top5Index]
                    showAtt = np.concatenate((np.expand_dims(concatAtt_D[z], axis=0), top5PredAtt, tmpPredAtt), axis=0)
                    showName = [printClassName(z)] + top5PredClass + tmpPredClass
                    trace = go.Heatmap(z = showAtt,
                                       x = allClassAttName,
                                       y = showName,
                                       zmax = 1.0,
                                       zmin = 0.0)
                    data = [trace]
                    layout = go.Layout(title=globalV.FLAGS.KEY, width=1920, height=1080,
                                       yaxis=dict(
                                           ticktext = showName,
                                           tickvals = np.arange(len(showName))))
                    fig = go.Figure(data=data, layout=layout)
                    # py.image.save_as(fig, filename=globalV.FLAGS.DIR + '_' + printClassName(z) + '_Tr.png')

            # Loop each Validation class
            for z in range(15, 20):
                eachInputX = []
                eachInputY = []
                for k in range(vX.shape[0]):
                    if vY[k] == z:
                        eachInputX.append(vX[k])
                        eachInputY.append(vY[k])
                eachInputX = np.array(eachInputX)
                eachInputY = np.array(eachInputY)
                predY = model.getClassIndex(eachInputX, concatAtt_D)

                # Confusion matrix
                tmpScore = model.getScore(eachInputX, concatAtt_D)
                tmpSort = np.argsort(-tmpScore, axis=1)
                tmpPred = tmpSort[:, :topAcc]
                tmpPred = np.reshape(tmpPred, -1)
                tmpCountEach = np.bincount(tmpPred, minlength=32)
                tmpCountEach = np.array(tmpCountEach) / (eachInputX.shape[0] * topAcc)
                confusion.append(tmpCountEach)

                if topAcc == 1:
                    print('Class: {0:<15} Size: {1:<10} Accuracy = {2:.4f}%'.format(printClassName(z), eachInputX.shape[0], np.mean(np.equal(predY, eachInputY)) * 100))
                    # Predict attribute for each class and plot
                    s = np.arange(eachInputX.shape[0])
                    np.random.shuffle(s)
                    eachInputX = eachInputX[s]
                    tmpPredAtt = model.getAttribute(eachInputX[:10])
                    tmpPredClass = ['' for x in range(tmpPredAtt.shape[0])]
                    top5Index = np.argsort(-tmpCountEach)[:5]
                    top5PredAtt = concatAtt_D[top5Index, :]
                    top5PredClass = [printClassName(x) for x in top5Index]
                    showAtt = np.concatenate((np.expand_dims(concatAtt_D[z], axis=0), top5PredAtt, tmpPredAtt), axis=0)
                    showName = [printClassName(z)] + top5PredClass + tmpPredClass
                    trace = go.Heatmap(z=showAtt,
                                       x=allClassAttName,
                                       y=showName,
                                       zmax=1.0,
                                       zmin=0.0
                                       )
                    data = [trace]
                    layout = go.Layout(title=globalV.FLAGS.KEY, width=1920, height=1080,
                                       yaxis=dict(
                                           ticktext=showName,
                                           tickvals=np.arange(len(showName))))
                    fig = go.Figure(data=data, layout=layout)
                    # py.image.save_as(fig, filename=globalV.FLAGS.DIR + '_' + printClassName(z) + '_V.png')

            # Loop each Test class
            for z in range(20, 32):
                eachInputX = []
                eachInputY = []
                for k in range(teX.shape[0]):
                    if teY[k] == z:
                        eachInputX.append(teX[k])
                        eachInputY.append(teY[k])
                eachInputX = np.array(eachInputX)
                eachInputY = np.array(eachInputY)
                predY = model.getClassIndex(eachInputX, concatAtt_D)

                # Confusion matrix
                tmpScore = model.getScore(eachInputX, concatAtt_D)
                tmpSort = np.argsort(-tmpScore, axis=1)
                tmpPred = tmpSort[:, :topAcc]
                tmpPred = np.reshape(tmpPred, -1)
                tmpCountEach = np.bincount(tmpPred, minlength=32)
                tmpCountEach = np.array(tmpCountEach) / (eachInputX.shape[0] * topAcc)
                confusion.append(tmpCountEach)

                if topAcc == 1:
                    print('Class: {0:<15} Size: {1:<10} Accuracy = {2:.4f}%'.format(printClassName(z), eachInputX.shape[0], np.mean(np.equal(predY, eachInputY)) * 100))
                    # Predict attribute for each class and plot
                    s = np.arange(eachInputX.shape[0])
                    np.random.shuffle(s)
                    eachInputX = eachInputX[s]
                    tmpPredAtt = model.getAttribute(eachInputX[:10])
                    tmpPredClass = ['' for x in range(tmpPredAtt.shape[0])]
                    top5Index = np.argsort(-tmpCountEach)[:5]
                    top5PredAtt = concatAtt_D[top5Index, :]
                    top5PredClass = [printClassName(x) for x in top5Index]
                    showAtt = np.concatenate((np.expand_dims(concatAtt_D[z], axis=0), top5PredAtt, tmpPredAtt), axis=0)
                    showName = [printClassName(z)] + top5PredClass + tmpPredClass
                    trace = go.Heatmap(z=showAtt,
                                       x=allClassAttName,
                                       y=showName,
                                       zmax=1.0,
                                       zmin=0.0
                                       )
                    data = [trace]
                    layout = go.Layout(title=globalV.FLAGS.KEY, width=1920, height=1080,
                                       yaxis=dict(
                                           ticktext=showName,
                                           tickvals=np.arange(len(showName))))
                    fig = go.Figure(data=data, layout=layout)
                    # py.image.save_as(fig, filename=globalV.FLAGS.DIR + '_' + printClassName(z) + '_Te.png')

            confusion = np.array(confusion)
            # Confusion Matrix
            tmpClassName = [printClassName(x) for x in range(globalV.FLAGS.numClass)]
            trace = go.Heatmap(z=confusion,
                               x=tmpClassName,
                               y=tmpClassName,
                               zmax=1.0,
                               zmin=0.0
                               )
            data = [trace]
            layout = go.Layout(title=globalV.FLAGS.KEY, width=1920, height=1080,
                               yaxis=dict(
                                   ticktext=tmpClassName,
                                   tickvals=np.arange(len(tmpClassName))))
            fig = go.Figure(data=data, layout=layout)
            # py.image.save_as(fig, filename=globalV.FLAGS.DIR + '_Confusion_' + str(topAcc) + '.png')

        tmpSupTitle = "Train Classes : "
        tmpSupTitle += " ".join(trainClass) + "\n"
        tmpSupTitle += "Validation Classes : "
        tmpSupTitle += " ".join(valClass) + "\n"
        tmpSupTitle += "Test Classes : "
        tmpSupTitle += " ".join(testClass) + "\n"
        print('\n'+tmpSupTitle)

        # plt.figure(figsize=(20, 20))
        # for i in range(20):
        #     plt.subplot(4, 5, i + 1)
        #     h = list(g[i])
        #     tmpStr = ' ' + b[i]
        #     for index, st in enumerate(h):
        #         if index % 5 == 0:
        #             tmpStr += '\n'
        #         tmpStr += ' ' + st
        #     plt.title(tmpStr, multialignment='left')
        #     plt.imshow(checkX[i])
        #     plt.axis('off')
        # plt.tight_layout()
        # plt.savefig(globalV.FLAGS.KEY + '_Predict_Class.png')
        # plt.clf()

        # Check Classes Heat map
        trace = go.Heatmap(z = concatAtt_D,
                           x = allClassAttName,
                           y = allClassName,
                           zmax=1.0,
                           zmin=0.0
                           )
        data = [trace]
        layout = go.Layout(title=globalV.FLAGS.KEY, width=1920, height=1080)
        fig = go.Figure(data=data, layout=layout)
        py.image.save_as(fig, filename=globalV.FLAGS.DIR+'_Heat.png')

    elif globalV.FLAGS.OPT == 5:
        print('\nTree Prediction')

        # Train Class Map
        mapTrain = [1, 1, 2, 2, 0, 0, 0, 3, 4, 6, 5, 7, 8, 9, 5]
        trYCluster70 = np.copy(trY70)
        trYCluster30 = np.copy(trY30)
        for i in range(trY70.shape[0]):
            trYCluster70[i] = mapTrain[trY70[i]]
        for i in range(trY30.shape[0]):
            trYCluster30[i] = mapTrain[trY30[i]]

        # Validation Class Map
        mapVal = [1, 2, 0, 3, 5]
        vYCluster = np.copy(vY)
        for i in range(vY.shape[0]):
            vYCluster[i] = mapVal[vY[i]-15]

        # Test Class Map
        mapTest = [1, 2, 0, 0, 0, 0, 3, 4, 6, 5, 5, 0]
        teYCluster = np.copy(teY)
        for i in range(teY.shape[0]):
            teYCluster[i] = mapTest[teY[i] - 20]

        # Find cluster with Graph
        returnIndex = [57, 11, 53, 12, 40, 51, 13, 43, 47, 52]
        returnValue = [1, 7, 0, 8, 6, 3, 9, 4, 5, 2]
        def FindCluster(att, pos):
            if pos in returnIndex:
                return returnValue[returnIndex.index(pos)]
            else:
                left = distanceFunc(tmpConcatAtt[treeMap[pos][0]], att)
                right = distanceFunc(tmpConcatAtt[treeMap[pos][1]], att)
                if left < right:
                    return FindCluster(att, treeMap[pos][0])
                else:
                    return FindCluster(att, treeMap[pos][1])

        # # Find cluster with closet distance
        # returnValue = [1, 1, 2, 2, 0, 0, 0, 3, 4, 6, 5, 7, 8, 9, 5, 1, 2, 0, 3, 5, 1, 2, 0, 0, 0, 0, 3, 4, 6, 5, 5, 0]
        # def FindCluster(att, pos):
        #     clusDistance = []
        #     for eachAtt in concatAtt_D:
        #         clusDistance.append(spatial.distance.euclidean(att, eachAtt))
        #     clusInd = np.argsort(clusDistance)[:1]
        #     return returnValue[clusInd[0]]

        g1 = tf.Graph()
        with g1.as_default():
            model = attribute()

        # Train Cluster
        attTmp = model.getAttribute(trX30)
        tmpPredCluster = []
        for i in range (attTmp.shape[0]):
            tmpPredCluster.append(FindCluster(attTmp[i], tmpConcatAtt.shape[0] - 1))
        tmpPredCluster = np.array(tmpPredCluster)
        print('Cluster Train Accuracy = {0:.4f}%'.format(np.mean(np.equal(tmpPredCluster, trYCluster30)) * 100))

        # Val Cluster
        attTmp = model.getAttribute(vX)
        tmpPredCluster = []
        for i in range(attTmp.shape[0]):
            tmpPredCluster.append(FindCluster(attTmp[i], tmpConcatAtt.shape[0] - 1))
        tmpPredCluster = np.array(tmpPredCluster)
        print('Cluster Validation Accuracy = {0:.4f}%'.format(np.mean(np.equal(tmpPredCluster, vYCluster)) * 100))

        # Test Cluster
        attTmp = model.getAttribute(teX)
        tmpPredCluster = []
        for i in range(attTmp.shape[0]):
            tmpPredCluster.append(FindCluster(attTmp[i], tmpConcatAtt.shape[0] - 1))
        tmpPredCluster = np.array(tmpPredCluster)
        print('Cluster Test Accuracy = {0:.4f}%'.format(np.mean(np.equal(tmpPredCluster, teYCluster)) * 100))

        # Accuracy for each class and Confusion matrix
        print('')
        # Loop each Train class
        confusion = []
        for z in range(0, 15):
            eachInputX = []
            eachInputY = []
            for k in range(0, trX30.shape[0]):
                if trY30[k] == z:
                    eachInputX.append(trX30[k])
                    eachInputY.append(trYCluster30[k])
            eachInputX = np.array(eachInputX)
            eachInputY = np.array(eachInputY)
            attTmp = model.getAttribute(eachInputX)
            tmpPredCluster = []
            for i in range(attTmp.shape[0]):
                tmpPredCluster.append(FindCluster(attTmp[i], tmpConcatAtt.shape[0] - 1))
            tmpPredCluster = np.array(tmpPredCluster)
            print('Class: {0:<15} Size: {1:<10} Accuracy = {2:.4f}%'.format(printClassName(z), eachInputX.shape[0], np.mean(np.equal(tmpPredCluster, eachInputY)) * 100))

            # Confusion matrix
            tmpCountEach = np.bincount(tmpPredCluster, minlength=10)
            tmpCountEach = np.array(tmpCountEach)/eachInputX.shape[0]
            confusion.append(tmpCountEach)


        # Loop each Validation class
        for z in range(15, 20):
            eachInputX = []
            eachInputY = []
            for k in range(vX.shape[0]):
                if vY[k] == z:
                    eachInputX.append(vX[k])
                    eachInputY.append(vYCluster[k])
            eachInputX = np.array(eachInputX)
            eachInputY = np.array(eachInputY)
            attTmp = model.getAttribute(eachInputX)
            tmpPredCluster = []
            for i in range(attTmp.shape[0]):
                tmpPredCluster.append(FindCluster(attTmp[i], tmpConcatAtt.shape[0] - 1))
            tmpPredCluster = np.array(tmpPredCluster)
            print('Class: {0:<15} Size: {1:<10} Accuracy = {2:.4f}%'.format(printClassName(z), eachInputX.shape[0], np.mean(np.equal(tmpPredCluster, eachInputY)) * 100))

            # Confusion matrix
            tmpCountEach = np.bincount(tmpPredCluster, minlength=10)
            tmpCountEach = np.array(tmpCountEach)/eachInputX.shape[0]
            confusion.append(tmpCountEach)

        # Loop each Test class
        for z in range(20, 32):
            eachInputX = []
            eachInputY = []
            for k in range(teX.shape[0]):
                if teY[k] == z:
                    eachInputX.append(teX[k])
                    eachInputY.append(teYCluster[k])
            eachInputX = np.array(eachInputX)
            eachInputY = np.array(eachInputY)
            attTmp = model.getAttribute(eachInputX)
            tmpPredCluster = []
            for i in range(attTmp.shape[0]):
                tmpPredCluster.append(FindCluster(attTmp[i], tmpConcatAtt.shape[0] - 1))
            tmpPredCluster = np.array(tmpPredCluster)
            print('Class: {0:<15} Size: {1:<10} Accuracy = {2:.4f}%'.format(printClassName(z), eachInputX.shape[0], np.mean(np.equal(tmpPredCluster, eachInputY)) * 100))

            # Confusion matrix
            tmpCountEach = np.bincount(tmpPredCluster, minlength=10)
            tmpCountEach = np.array(tmpCountEach)/eachInputX.shape[0]
            confusion.append(tmpCountEach)

        confusion = np.array(confusion)
        tmpClassName = [printClassName(x) for x in range(globalV.FLAGS.numClass)]
        trace = go.Heatmap(z=confusion,
                           y=tmpClassName,
                           zmax=1.0,
                           zmin=0.0
                           )
        data = [trace]
        layout = go.Layout(title=globalV.FLAGS.KEY, width=1920, height=1080,
                           yaxis=dict(
                               ticktext=tmpClassName,
                               tickvals=np.arange(len(tmpClassName))))
        fig = go.Figure(data=data, layout=layout)
        py.image.save_as(fig, filename=globalV.FLAGS.DIR + '_Confusion_Cluster' + '.png')



