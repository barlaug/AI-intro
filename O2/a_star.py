import Map

class Node(): #må ha node klasse vettøøøøø
    def __init__(self,state=None, g=None, h=None, f=None, parent=None, children=[]):
        self.state = tuple(state) #x,y koordinater til noden
        self.g = g
        self.h = h
        self.f = f
        self.parent = parent #den beste forelderen til noden
        self.children = children #liste med barn til noden
    
    def print_node(self): #vet ikke om denne er nødvendig
        return f'{self.state[0]}, {self.state[1]}'

def h_calculation(state, map_obj, type): #regner ut avstand til mål enten manhattan eller euclidean, basert på input, state er x,y til current node
    goal = map_obj.get_goal_pos()
    if type == "manhattan": 
        return abs(goal[0]-state[0]) + abs(goal[1]-state[1]) #se internett
    if type == "euclidean":
        return ((goal[0] - state[0])**2 + (goal[1] - state[1])**2)**0.5 #se internett
    else:
        print("Type må være enten manhattan eller euclidean")
        return 0

def cost_function(to_state, map_obj): #tror kansekj vi trenger denne i del 2
    #returnerer kosten fra å gå fra en celle til en annen, er f eks høyere hvis man går opp trapper enn ned trapper
    return map_obj.get_cell_value(to_state)


def is_at_goal(state, goal_state): #sjekker om current node er i goal_pos
    return (state[0] == goal_state[0]) and (state[1] == goal_state[1]) #må ikke funk vite hvilken node det er?

def init_start_node(start_state, h_function):
    start_node = Node(
        state = start_state,
        parent = None, #første karen hakke no pappa
        children = []
    )
    start_node.g = 0
    start_node.h = h_function
    start_node.f = start_node.h + start_node.g
    return start_node

def init_child_node(parent, child_state, h_function, map_obj): #skjønner ikke hva child-state skal være
    child_node = Node(
        parent=parent,
        state=child_state,
        children=[]
    )
    child_node.g = parent.g + cost_function(child_node.state, map_obj) 
    child_node.h = h_calculation(child_node.state, map_obj, h_function)
    child_node.f = child_node.g + child_node.h
    return child_node

def propagate_path_improvements(parent, map_obj, h_function):
    for child in parent.children:
        new_g = parent.g + cost_function(child.state)
        if new_g < child.g:
            child.parent = parent
            child.g = new_g
            child.f = child.g + h_calculation(child.state, map_obj, h_function)

def generate_children(parent, map_obj, h_function):
    children_list = []
    for adjacent_tiles in [(0, -1), (0, 1), (-1, 0), (1, 0)]: #finner nabo
        child_pos_x = parent.state[0] + adjacent_tiles[0]
        child_pos_y = parent.state[1] + adjacent_tiles[1]
        print("child pos x,y:", child_pos_x, child_pos_y)
        (w, h) = map_obj.int_map.shape 
        print("w,h:", w,h)
        #sjekke at child_pos er innenfor grensene på map_obj
        if (child_pos_x < 0) or (child_pos_x > w) or (child_pos_y < 0) or (child_pos_y > h):
            continue #hopper av resten av koden for-løkken skal kjøre og begynner på neste iterasjon
        
        child_pos = tuple((child_pos_x, child_pos_y))
        print("child_pos. ", child_pos)
        #sjekke om child_pos er en hindring
        if map_obj.get_cell_value(child_pos) == -1:
            continue

        new_node = Node(child_pos) #lager ny node av child
        children_list.append(new_node)
    return children_list

def attach_child(parent, child, h_function, map_obj):
        child.parent = parent
        child.g = parent.g + cost_function(child.state, map_obj)
        child.h = h_calculation(child.state, map_obj, h_function)
        child.f = child.g + child.h


#A*-algoritme implementasjon
def a_star(start, goal, h_function, map_obj):
    start_node = init_start_node(start, h_calculation(start, map_obj, h_function))
    OPEN = []
    CLOSED = []
    memo = {}

    OPEN.append(start_node)
    memo[start_node.state] = start_node

    while len(OPEN) > 0: #går helt til vi har funnet goal-node

        #sjekker de åpna cellene om det er noen som har bedre f-verdi, setter denn til current node
        current_node = OPEN[0]
        current_i = 0 #trengs for å poppe riktig element fra OPEN
        for i, node in enumerate(OPEN): #må ha enumerate siden vi itererer over rare objekter
            if node.f < current_node.f:
                current_node = node
                current_i = i
        OPEN.pop(current_i)
        CLOSED.append(current_node)
        
        #sjekker om vi har truffet mål
        if is_at_goal(current_node.state, goal):
            #vi skal nå gå bakover langs alle barn->forelder->besteforelder til vi er ved startnoden og legge til alle koordinater i path slik at vi kan returnere den
            path = [] 
            now = current_node
            while now is not None: #det vil si at vi enda ikke har kommet til startnoden sin hadde en parent-peker til None
                path.append(now.state)
                now = now.parent
            return path[::-1] #returnerer baklengs path så de er i riktig rekkefølge
        #generate children
        children = generate_children(current_node, map_obj, h_function)

        print("children: ", children)

        for child in children:
            if child.state in memo:
                child_node = memo[child.state]
            else:
                child_node = init_child_node(current_node, child.state, h_function, map_obj)
                memo[child_node.state] = child_node
            
            current_node.children.append(child_node)

            if child_node not in OPEN and child_node not in CLOSED:
                attach_child(current_node, child_node, h_function, map_obj)
                OPEN.append(child_node)
            elif current_node.g + cost_function(child_node.state, map_obj) < child_node.g:
                attach_child(current_node, child_node, h_function, map_obj)
                if child_node in CLOSED:
                    propagate_path_improvements(child_node, map_obj, h_function)


def main():
    print("main")
    map_obj = Map.Map_Obj(task = 1)
    map_obj.read_map('Samfundet_map_1.csv')
    map_obj.get_maps()

    #kjør a* på map-objekter osvosv
    start_state = map_obj.get_start_pos()
    goal_state = map_obj.get_goal_pos()
    h_function_type = "manhattan"
    solution = a_star(start_state, goal_state, h_function_type, map_obj) #astar returnerer en liste med koordinater til korteste vei
    print(solution)
    for _ in solution:
        map_obj.set_cell_value(_,"O") #maler mappet med veien vi fant
    #map_obj.set_cell_value((3, 18),"O")

    map_obj.show_map()

if __name__ == '__main__':
    main()
