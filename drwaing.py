class Node:
    connectedNode = []

    def __init__(self, address, tx, spent) -> None:
        self.address = address
        self.transaction = tx
        self.spented = spent

    def setNodaData(self, )

    def addNewNode(self, nextNode : 'Node'):
        self.connectedNode.append(nextNode)