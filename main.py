import xml.etree.ElementTree  as ET  
import time
import sys
import json

def getRow(xmlElem):
    return int(xmlElem.get("row")) - 1

def getCol(xmlElem):
    return int(ord(xmlElem.get("col")) - ord('A'))

def getPoint(xmlElem):
    return [getRow(xmlElem), getCol(xmlElem)]
    
def getNeighbours(matrix, point):
    res = []
    if (point[0] != 0) and (matrix[point[0] - 1][point[1]] == 1):
        res.append([point[0] - 1, point[1]])
    if (point[0] + 1 != len(matrix)) and (matrix[point[0] + 1][point[1]] == 1):
        res.append([point[0] + 1, point[1]])
    if (point[1] != 0) and (matrix[point[0]][point[1] - 1] == 1):
        res.append([point[0], point[1] - 1])
    if (point[1] + 1 != len(matrix[0])) and (matrix[point[0]][point[1] + 1] == 1):
        res.append([point[0], point[1] + 1])
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


def main(paths):
    xmlRoot = ET.parse(sys.argv[1]).getroot()

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

    end = 0

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
                    end = 1
        if end:
            while queue:
                currentPoint = queue.pop(0)
                neighbours = getNeighbours(matrix, currentPoint)

                for neighbour in neighbours:
                    if neighbour == endPoint:
                        parent[neighbour[0]][neighbour[1]] = currentPoint
                        if neighbour == endPoint:
                            paths.append({"points": backtrace(parent, startPoint, neighbour) })


    return paths

if __name__ == "__main__":
    start_time = time.time()
    paths = main([])
    returnJsonData = {
        "execution_time_in_ms": round((time.time() - start_time) / 1000, 2),	
        "paths": paths
    }
    filepath = "json.json"
    if len(sys.argv) == 3:
        filepath = sys.argv[2]

    with open(filepath, 'w') as outfile:
        outfile.write(json.dumps(returnJsonData, indent=4, sort_keys=True))
        outfile.close()

    print(filepath)