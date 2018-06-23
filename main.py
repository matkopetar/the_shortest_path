import xml.etree.ElementTree  as ET  
import time
import sys
import json

class MapHelper:
    def __init__(self, xmlRoot):
        self.xmlRoot = xmlRoot
        self.unvisitedPoints = []
        self.initMatrix()

    def initMatrix(self):
        maxRow = 0
        maxCol = 0
        
        for cell in self.xmlRoot.iter("cell"):
            row = self.getRow(cell)
            col = self.getCol(cell)
            point = [row, col]

            if maxRow < row:
                maxRow = row
            if maxCol < col:
                maxCol = col

            self.unvisitedPoints.append(point)

        self.matrix = [0] * (maxRow + 1)
        for i in range(maxRow + 1):
            self.matrix[i] = [0] * (maxCol + 1)

        self.parent = [-1] * (maxRow + 1)
        for i in range(maxRow + 1):
            self.parent[i] = [-1] * (maxCol + 1)

        for point in self.unvisitedPoints:
            self.matrix[point[0]][point[1]] = 1

    @staticmethod
    def getRow(xmlElem):
        return int(xmlElem.get("row")) - 1

    @staticmethod
    def getCol(xmlElem):
        return int(ord(xmlElem.get("col")) - ord('A'))

    @staticmethod
    def getPoint(xmlElem):
        return [MapHelper.getRow(xmlElem), MapHelper.getCol(xmlElem)]
        
    def upperCellExists(self, row_num, col_num):
        upper_cell = self.matrix[row_num - 1][col_num]
        return (row_num is not 0) and (upper_cell is 1)
        
    def bottomCellExists(self, row_num, col_num):
        bottom_cell = self.matrix[row_num + 1 - len(self.matrix)][col_num]
        return (row_num is not len(self.matrix) - 1) and (bottom_cell is 1)

    def leftCellExists(self, row_num, col_num):
        left_cell = self.matrix[row_num][col_num - 1]
        return (col_num is not 0) and (left_cell is 1)

    def rightCellExists(self, row_num, col_num):
        right_cell = self.matrix[row_num][col_num + 1 - len(self.matrix[0])]
        return (row_num is not len(self.matrix[0])) and (right_cell is 1)

    def getNeighbours(self, point):
        res = []
        if self.upperCellExists(point[0], point[1]):
            upper_cell = [point[0] - 1, point[1]]
            res.append(upper_cell)
        if self.bottomCellExists(point[0], point[1]):
            bottom_cell = [point[0] + 1, point[1]]
            res.append(bottom_cell)
        if self.leftCellExists(point[0], point[1]):
            left_cell = [point[0], point[1] - 1]
            res.append(left_cell)
        if self.rightCellExists(point[0], point[1]):
            right_cell = [point[0], point[1] + 1]
            res.append(right_cell)
        return res

def format_path(path):
    new_path = []
    for point in path:
        new_path.append({
            "row": point[0] + 1,
            "col": chr(point[1] + ord('A'))
        })
    return new_path

def backtrace(parent, start, end):
    path = [end]
    while path[-1] != start:
        path.append(parent[path[-1][0]][path[-1][1]])
    path.reverse()
    return format_path(path)


def main(xmlFileName):
    paths = []

    xmlRoot = ET.parse(xmlFileName).getroot()
    
    mapHelper = MapHelper(xmlRoot)


    xmlStartCell = xmlRoot.find("start-point")
    startPoint = MapHelper.getPoint(xmlStartCell)

    xmlEndCell = xmlRoot.find("end-point")
    endPoint = MapHelper.getPoint(xmlEndCell)

    queue = [startPoint]
    mapHelper.unvisitedPoints.remove(startPoint)

    last_iteration = False

    while queue:
        currentPoint = queue.pop(0)
        neighbours = mapHelper.getNeighbours(currentPoint)

        for neighbour in neighbours:
            if neighbour in mapHelper.unvisitedPoints:
                mapHelper.parent[neighbour[0]][neighbour[1]] = currentPoint
                queue.append(neighbour)
                mapHelper.unvisitedPoints.remove(neighbour)
                if neighbour == endPoint:
                    paths.append({"points": backtrace(mapHelper.parent, startPoint, neighbour) })
                    last_iteration = True
        if last_iteration:
            while queue:
                currentPoint = queue.pop(0)
                neighbours = mapHelper.getNeighbours(currentPoint)

                for neighbour in neighbours:
                    if neighbour == endPoint:
                        mapHelper.parent[neighbour[0]][neighbour[1]] = currentPoint
                        if neighbour == endPoint:
                            paths.append({"points": backtrace(mapHelper.parent, startPoint, neighbour) })
            break
    return paths

def checkIfRequiredParameterExists():
    if len(sys.argv) < 2:
        print("Missing required .xml parameter!")
        sys.exit()
    elif len(sys.argv) > 3:
        print("You have more than two parameters!")
        sys.exit()

def checkIfRequiredParemeterIsXML(xmlFileName):
    if not xmlFileName.endswith(".xml"):
        print("Required .xml parameter is not specified as .xml!")
        sys.exit()

def xmlFormatError():
    print("Xml file is in the wrong format!")
    sys.exit()

def checkXmlContent(xmlRoot):
    if xmlRoot.tag != "map":
        xmlFormatError()

    checkArray = []
    for child in xmlRoot:
        checkArray.append(child.tag)
        if child.tag != 'cells':
            if ("col" not in child.attrib) or (child.attrib["col"] < 'A') or (child.attrib["col"] > 'Z'):
                xmlFormatError()
            if ("row" not in child.attrib) or (int(child.attrib["row"]) < 1) or (int(child.attrib["row"]) > 100):
                xmlFormatError()
                
    if not set(['start-point', 'end-point', 'cells']).issubset(checkArray):
        xmlFormatError()
    
    for cells in xmlRoot.findall("cells"):
        for cell in cells:
            if cell.tag != 'cell':
                xmlFormatError()
            if ("col" not in cell.attrib) or (cell.attrib["col"] < 'A') or (cell.attrib["col"] > 'Z'):
                xmlFormatError()
            if ("row" not in cell.attrib) or (int(cell.attrib["row"]) < 1) or (int(cell.attrib["row"]) > 100):
                xmlFormatError()

def getFileNameIfWithoutErrors():
    checkIfRequiredParameterExists()

    xmlFileName = sys.argv[1]
    checkIfRequiredParemeterIsXML(xmlFileName)

    xmlRoot = ET.parse(xmlFileName).getroot()
    checkXmlContent(xmlRoot)
    return xmlFileName


def getFilepath():
    filepath = "json.json"
    if len(sys.argv) == 3:
        filepath = sys.argv[2]
    return filepath

def writeJson(filepath, jsonData):
    with open(filepath, 'w') as outfile:
        outfile.write(json.dumps(jsonData, indent=4, sort_keys=True))
        outfile.close()
    print(filepath)

if __name__ == "__main__":
    start_time = time.clock()

    xmlFileName = getFileNameIfWithoutErrors()

    paths = main(xmlFileName)

    jsonData = {
        "execution_time_in_ms": round((time.clock() - start_time) * 1000, 2),	
        "paths": paths
    }

    filepath = getFilepath()
    writeJson(filepath, jsonData)
