from tabulate import tabulate
textFile = 'textfiles/test3.txt'

def readNodes(line):
    global nodesList
    newNodes = line.split(',')
    for node in newNodes:
        node = node.rstrip('\n')
        nodesList.append(createNode(node))

def readLanguage(line):
    global language
    newChars = line.split(',')
    for char in newChars:
        char = char.rstrip('\n')
        language.append(char)

def readInitialStates(line):
    global nodesList
    initialNodes = line.split(',')
    nodeNames = getNodeNames(nodesList)
    for node in initialNodes:
        node = node.rstrip('\n')
        if(node in nodeNames):
            nodesList[searchNodeIndex(node, nodesList)]['isInitialState'] = True

def readFinalStates(line):
    global nodesList
    finalNodes = line.split(',')
    nodeNames = getNodeNames(nodesList)
    for node in finalNodes:
        node = node.rstrip('\n')
        if(node in nodeNames):
            nodesList[searchNodeIndex(node, nodesList)]['isFinalState'] = True

def getNodeNames(nodesList):
    nodeNames = []
    for node in nodesList:
        nodeNames.append(node['name'])
    return nodeNames

def searchNodeIndex(nodeName, nodesList):
    position = 0
    found = False
    while(not found and position < len(nodesList)):
        if(nodesList[position].get('name') == nodeName):
            return position
        position = position + 1
    return -1

def searchTransitionIndex(transitionId, processor):
    position = 0
    found = False
    while(not found and position < len(processor)):
        if(processor[position].get('id') == transitionId):
            return position
        position = position + 1
    return -1


def readTransitions(lines):
    global processor
    global nodesList
    for line in lines:
        line = line.rstrip('\n')
        x = line.split('=>')
        initialNodeStr, char = x[0].split(',')
        initialNode = nodesList[(searchNodeIndex(initialNodeStr, nodesList))]
        transitions = x[1].split(',')
        actualTransitions = getTransitionNames(processor)
        for transitionNodeStr in transitions:
            transitionNode = nodesList[(searchNodeIndex(transitionNodeStr, nodesList))]
            testId = initialNode['name'] + transitionNode['name']
            if(testId in actualTransitions):
                processor[searchTransitionIndex(testId, processor)]['chars'].append(char)
            else:
                processor.append(createTransition(initialNode, char, transitionNode))
                

    
def getTransitionNames(processor):
    transitionIDs = []
    for transition in processor:
        transitionIDs.append(transition['id'])
    return transitionIDs          

def createNode(name):
    node =	{
    'name': name,
    'isInitialState': False,
    'isFinalState': False,
    }
    return node

def createTransition(initialNode, char, finalNode):
    transition = {
    'id': initialNode['name'] + finalNode['name'],
    'initialNode': initialNode,
    'chars': [char],
    'finalNode': finalNode,
    }
    return transition

def printNodes(nodesList):
    for node in nodesList:
        print(node['name'], end=",")

def printLanguage(language):
    for char in language:
        print(char)

def printTransitions(processor):
    for transition in processor:
        for char in transition['chars']:
            print(transition['initialNode']['name'] + ' to ' +  transition['finalNode']['name'] + ' with ' + char)

def printTransition(transition):
    print(transition['initialNode']['name'] + ' to ' +  transition['finalNode']['name'])

def readFile(textFile):
    f = open(textFile, 'r')
    fileText = f.readlines()
    getFileData(fileText)

def getFileData(file):
    readNodes(file[0])
    file.pop(0)
    readLanguage(file[0])
    file.pop(0)
    readInitialStates(file[0])
    file.pop(0)
    readFinalStates(file[0])
    file.pop(0)
    readTransitions(file)

def generateHeader(language):
    header = ["node"]
    for char in language:
        header.append(char)
    return header

def generateRow(node, processor, language):
    row = []
    nodeName = node['name']
    if node['isInitialState']:
        nodeName = '->' + nodeName
    if node['isFinalState']:
        nodeName = nodeName + '*'
    row.append(nodeName)
    for char in language:
        charNodes = []
        for transition in processor:
            if transition['initialNode'] == node:
                if char in transition['chars']:
                    charNodes.append(transition['finalNode']['name'])
        destinationStr = ''
        for endNode in charNodes:
            destinationStr = destinationStr + endNode + ', '
        destinationStr = destinationStr[:-2]
        row.append(destinationStr)
    return row



def printTable(language, processor, nodesList):
    table= []
    table.append(generateHeader(language))
    for node in nodesList:
        table.append(generateRow(node, processor, language))
    print()
    print(tabulate(table, headers="firstrow"))
    print()

def getInitialState(nodesList):
    for node in nodesList:
        if node['isInitialState']:
            return node

def processACharachterNDFA(node, thisChar, processor):
    finalNodes = []
    for transition in processor:
            if transition['initialNode']['name'] == node['name']:
                for char in transition['chars']:
                    if thisChar == char:
                        finalNodes.append(transition['finalNode'])
    return finalNodes
                    

def convertToNDFA(language, processor, nodesList):
    ndfaProcessor = []
    language.remove('l')
    for char in language:
        for node in nodesList:
            childNodes = []
            lambdaNodes = processACharachterNDFA(node, 'l', processor)
            if lambdaNodes:
                for child in lambdaNodes:
                    if child['isFinalState'] and node['isInitialState']:
                        nodesList[searchNodeIndex(node, nodesList)]['isFinalState'] = True
                        node['isFinalState'] = True
                    if child not in childNodes:
                        childNodes.append(child)
            thisCharNodes = processACharachterNDFA(node, char, processor)
            for newChild in thisCharNodes:
                if newChild not in childNodes:
                    childNodes.append(newChild)          
            for child in childNodes:
                lambdaCharNodes = processACharachterNDFA(child, char, processor)
                for newChild in lambdaCharNodes:
                    if newChild not in childNodes:
                        childNodes.append(newChild)
            for child in childNodes:
                if child['isFinalState'] and node['isInitialState']:
                    nodesList[searchNodeIndex(node, nodesList)]['isFinalState'] = True
                    node['isFinalState'] = True
                lambdaNodes = processACharachterNDFA(child, 'l', processor)
                for newChild in lambdaNodes:
                    if newChild not in childNodes:
                        childNodes.append(newChild)
            for child in childNodes:
                ndfaProcessor.append(createTransition(node, char, child))
    convertToDFA(language, ndfaProcessor, nodesList)



def convertToDFA(language, processor, nodesList):
    if("l" in language):
        print("NDFA with Lambda")
        printTable(language, processor, nodesList)
        convertToNDFA(language, processor, nodesList)
    else:
        print("NDFA")
        printTable(language, processor, nodesList)
        #Convert to DFA below
        
        
        
        








nodesList = [] #Lista de Nodos
language = [] #Lista de caracacteres
processor = [] #Procesador(Lista de transiciones)
readFile(textFile)
print()
print()
convertToDFA(language, processor, nodesList)








