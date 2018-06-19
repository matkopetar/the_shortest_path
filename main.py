import xml.etree.ElementTree  as ET  
import time
import sys
import json

def checkRequiredParameter():
    if len(sys.argv) < 2:
        print("Nije prosledjen obavezan parametar!")
        sys.exit()
    elif len(sys.argv) > 3:
        print("Postoji visak parametara...")
        sys.exit()

def xmlFormatError():
    print("Greska u formatu .xml fajla")
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
                
    if 'start-point' not in checkArray:
        xmlFormatError()
    if 'end-point' not in checkArray:
        xmlFormatError()
    if 'cells' not in checkArray:
        xmlFormatError()
    if len(checkArray) != 3:
        xmlFormatError()
    for cells in xmlRoot.findall("cells"):
        for cell in cells:
            if cell.tag != 'cell':
                xmlFormatError()
            if ("col" not in cell.attrib) or (cell.attrib["col"] < 'A') or (cell.attrib["col"] > 'Z'):
                xmlFormatError()
            if ("row" not in cell.attrib) or (int(cell.attrib["row"]) < 1) or (int(cell.attrib["row"]) > 100):
                xmlFormatError()


def getRow(xmlElem):
    return int(xmlElem.get("row")) - 1

def getCol(xmlElem):
    return int(ord(xmlElem.get("col")) - ord('A'))

def getPoint(xmlElem):
    return [getRow(xmlElem), getCol(xmlElem)]
    
def upperCellExists(matrix, row_num, col_num):
    upper_cell = matrix[row_num - 1][col_num]
    return (row_num is not 0) and (upper_cell is 1)
    
def bottomCellExists(matrix, row_num, col_num):
    bottom_cell = matrix[row_num + 1 - len(matrix)][col_num]
    return (row_num is not len(matrix) - 1) and (bottom_cell is 1)

def leftCellExists(matrix, row_num, col_num):
    left_cell = matrix[row_num][col_num - 1]
    return (col_num is not 0) and (left_cell is 1)

def rightCellExists(matrix, row_num, col_num):
    right_cell = matrix[row_num][col_num + 1 - len(matrix[0])]
    return (row_num is not len(matrix[0])) and (right_cell is 1)


def getNeighbours(matrix, point):
    res = []
    if upperCellExists(matrix, point[0], point[1]):
        upper_cell = [point[0] - 1, point[1]]
        res.append(upper_cell)
    if bottomCellExists(matrix, point[0], point[1]):
        bottom_cell = [point[0] + 1, point[1]]
        res.append(bottom_cell)
    if leftCellExists(matrix, point[0], point[1]):
        left_cell = [point[0], point[1] - 1]
        res.append(left_cell)
    if rightCellExists(matrix, point[0], point[1]):
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

def parentPoint(parent, path):
    return parent[path[-1][0]][path[-1][1]]

def backtrace(parent, start, end):
    path = [end]
    while path[-1] != start:
        path.append(parentPoint(parent, path))
    path.reverse()
    return format_path(path)


def main():
    paths = []
    xmlRoot = ET.parse(sys.argv[1]).getroot()

    checkXmlContent(xmlRoot)

    xmlStartCell = xmlRoot.find("start-point")
    startPoint = getPoint(xmlStartCell)

    xmlEndCell = xmlRoot.find("end-point")
    endPoint = getPoint(xmlEndCell)
    
    maxRow = 0
    maxCol = 0

    unvisitedPoints = []

    for cell in xmlRoot.iter("cell"):
        row = getRow(cell)
        col = getCol(cell)
        point = [row, col]

        if maxRow < row:
            maxRow = row
        if maxCol < col:
            maxCol = col

        unvisitedPoints.append(point)

    matrix = [0] * (maxRow + 1)
    for i in range(maxRow + 1):
        matrix[i] = [0] * (maxCol + 1)

    parent = [-1] * (maxRow + 1)
    for i in range(maxRow + 1):
        parent[i] = [-1] * (maxCol + 1)

    for point in unvisitedPoints:
        matrix[point[0]][point[1]] = 1

    queue = [startPoint]
    unvisitedPoints.remove(startPoint)

    last_iteration = 0
    lenght_of_path = 0

    while queue:
        currentPoint = queue.pop(0)
        neighbours = getNeighbours(matrix, currentPoint)

        for neighbour in neighbours:
            if neighbour in unvisitedPoints:
                parent[neighbour[0]][neighbour[1]] = currentPoint
                queue.append(neighbour)
                unvisitedPoints.remove(neighbour)
                if neighbour == endPoint:
                    paths.append({"points": backtrace(parent, startPoint, neighbour) })
                    last_iteration = 1
        if last_iteration:
            while queue:
                currentPoint = queue.pop(0)
                neighbours = getNeighbours(matrix, currentPoint)

                for neighbour in neighbours:
                    if neighbour == endPoint:
                        parent[neighbour[0]][neighbour[1]] = currentPoint
                        if neighbour == endPoint:
                            paths.append({"points": backtrace(parent, startPoint, neighbour) })
            break
    return paths

def writeJson(filepath, jsonData):
    with open(filepath, 'w') as outfile:
        outfile.write(json.dumps(jsonData, indent=4, sort_keys=True))
        outfile.close()
    print(filepath)

def getFilepath():
    filepath = "json.json"
    if len(sys.argv) == 3:
        filepath = sys.argv[2]
    return filepath

if True:
    checkRequiredParameter()

    start_time = time.time()

    paths = main()
    jsonData = {
        "execution_time_in_ms": round((time.time() - start_time) / 1000, 2),	
        "paths": paths
    }

    filepath = getFilepath()
    writeJson(filepath, jsonData)
