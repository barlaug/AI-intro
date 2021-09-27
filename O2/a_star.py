import Map

class Node(): #må ha node klasse vettøøøøø
    def __init__(self,state=None, g=None, h=None, f=None, status = None, parent=None, children=None):
        self.state = state #x,y koordinater til noden
        self.g = g
        self.h = h
        self.f = f
        self.status = status #open or closed
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


def is_at_goal(state, map_obj): #sjekker om current node er i goal_pos
    goal = map_obj.get_goal_pos()
    return (state[0] == goal[0]) and (state[1] == goal[1])

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

def init_child_node(parent, child_state, h_function):
    child_node = Node(
        parent=parent,
        state=child_state,
        children=[]
    )
    child_node.g = parent.g + cost_function(child_node) 
    child_node.h = h_function(child_node)
    child_node.f = child_node.g + child_node.h
    return child_node


#A*-algoritme implementasjon
def a_star(start, goal, h_function, map_obj):
    start_node = init_start_node(start, h_calculation(start, map_obj, h_function))
    OPEN = []
    CLOSED = []

    OPEN.append(start_node)

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
        if is_at_goal(current_node.state, map_obj):
            #vi skal nå gå bakover langs alle barn->forelder->besteforelder til vi er ved startnoden og legge til alle koordinater i path slik at vi kan returnere den
            path = [] 
            now = current_node
            while now is not None: #det vil si at vi enda ikke har kommer til startnoden sin hadde en parent-peker til None
                path.append(now.state)
                now = now.parent
            return path[::-1] #returnerer baklengs path så de er i riktig rekkefølge

        
        #mangler å:
        #for noden vi er på nå, lag barn rundt og legg de til i childre-liste
        #loope gjennom barna og sjekke om de er i open-lista, hvis ikke så:
        #regn ut f-verdien deres og legg til i Open-lista
            







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
    for _ in solution:
        map_obj.set_cell_value(_,"O") #maler mappet med veien vi fant

    map_obj.show_map()

if __name__ == '__main__':
    main()
