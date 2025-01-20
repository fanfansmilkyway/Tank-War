import math

def cross_product(x1, y1, x2, y2, x3, y3):
    return (x2 - x1) * (y3 - y1) - (y2 - y1) * (x3 - x1)

def distance(A:tuple, B:tuple):
    """
    Calculate the distance between two points A,B.
    """
    return math.sqrt((A[0]-B[0])**2 + (A[1]-B[1])**2)

def if_intersect(A:tuple, B:tuple, C:tuple, D:tuple):
    """
    Determine whether two line segment intersects(AB, CD)
    """
    d1 = cross_product(C[0], C[1], D[0], D[1], A[0], A[1])
    d2 = cross_product(C[0], C[1], D[0], D[1], B[0], B[1])
    d3 = cross_product(A[0], A[1], B[0], B[1], C[0], C[1])
    d4 = cross_product(A[0], A[1], B[0], B[1], D[0], D[1])

    if d1 * d2 < 0 and d3 * d4 < 0:
        return True
    return False

def if_point_in_polygon(point:tuple, polygon_vertices:list):
    """
    To determine whether a point is in a polygon. True for the point is in the polygon. False for the point is not in it.
    """
    Intersection_Count = 0
    RAY_END = (30000, point[1])
    vertices = [polygon_vertices[i:i+2] for i in range(0, len(polygon_vertices), 2)]
    SIDES = []
    index = 0
    for vertice in vertices:
        if index == len(vertices) - 1:
            SIDES.append([(vertices[0][0],vertices[0][1]), (vertices[index][0], vertices[index][1])])
        else:
            SIDES.append([(vertice[0],vertice[1]), (vertices[index+1][0], vertices[index+1][1])])
        index += 1

    for side in SIDES:
        if if_intersect(point, RAY_END, side[0], side[1]):
            Intersection_Count += 1
    
    if Intersection_Count % 2 == 0:
        return False
    else:
        return True
    
def if_sight_blocked_by_obstacle(A:tuple, B:tuple, polygon_vertices:list):
    """
    To determine whether a sight line(which is a line segment called AB) is blocked by a bunker or an obstacle.
    The return is a bool. True for sight blocked, False for not blocked.
    """
    vertices = [polygon_vertices[i:i+2] for i in range(0, len(polygon_vertices), 2)]
    SIDES = []
    index = 0
    for vertice in vertices:
        if index == len(vertices) - 1:
            SIDES.append([(vertices[0][0],vertices[0][1]), (vertices[index][0], vertices[index][1])])
        else:
            SIDES.append([(vertice[0],vertice[1]), (vertices[index+1][0], vertices[index+1][1])])
        index += 1

    for side in SIDES:
        if if_intersect(A, B, side[0], side[1]):
            return True # The sight is blocked
        
    return False

def if_tank_spotted(sight_range:int, A:tuple, B:tuple, all_bunkers:list):
    """
    To determine whether a tank can be spotted. A is the observer coordinate, while B is the target coordinate.
    The return is a bool. True for tank spotted, False for tank not spotted.
    """
    if distance(A, B) > sight_range:
        return False
    for bunker in all_bunkers:
        if if_sight_blocked_by_obstacle(A, B, bunker.vertices) == True:
            return False
    return True