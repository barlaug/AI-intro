import Map

### Av Eirik Runde Barlaug og Jon Torgeir Grini (Gruppe 256) ifm. AI-intro øving 2. Overkommentert for stud-ass' skyld.


#Oppretter en class Node 
class Node(): 
    def __init__(self,state=None, g=None, h=None, f=None, parent=None, children=[]):
        self.state = tuple(state) #x,y koordinater til noden som er en tuple
        self.g = g
        self.h = h
        self.f = f
        self.parent = parent 
        self.children = children #liste med barna til den aktuelle noden
    
    def print_node(self): #til testing
        return f'{self.state[0]}, {self.state[1]}'

#regner ut et estimat på avstanden fra en node til et mål på et kart map_obj. 
#Type bestemmer om euclidean eller manhattan utregning skal tas i bruk
def h_calculation(state, map_obj, type):
    goal = map_obj.get_goal_pos()
    if type == "manhattan": 
        return abs(goal[0]-state[0]) + abs(goal[1]-state[1])
    elif type == "euclidean":
        return ((goal[0] - state[0])**2 + (goal[1] - state[1])**2)**0.5
    else:
        print("Type må være enten manhattan eller euclidean")
        return 0

#cost_function returnerer kosten å gå fra en celle til en annen,
#er f eks høyere hvis man går opp trapper enn ned trapper
def cost_function(to_state, map_obj):
    return map_obj.get_cell_value(to_state)

#Sjekke om en node sin state er vår goal-node sin state også
def is_at_goal(state, goal_state): 
    return (state[0] == goal_state[0]) and (state[1] == goal_state[1])

#Initialiserer en start node
def init_start_node(start_state, h_value):
    start_node = Node(
        state = start_state,
        parent = None #root-/start-noden har ingen forelder
    )
    start_node.g = 0
    start_node.h = h_value
    start_node.f = start_node.h + start_node.g
    return start_node

#Initialiserer en ny node
def init_child_node(parent, child_state, h_function, map_obj):
    child_node = Node(
        parent=parent,
        state=child_state
    )
    #Tilegner den nye node g, h og f verdi
    child_node.g = parent.g + cost_function(child_node.state, map_obj) 
    child_node.h = h_calculation(child_node.state, map_obj, h_function)
    child_node.f = child_node.g + child_node.h
    return child_node

#Rekurserer gjennom children og potensielt sett mange andre etterkommere til en parent P.
#Dersom noen etterkommere ikke har P som sin beste forelder må dette endres og forplante seg til alle etterkommere av denne child
#Forplantningen av beste forelder vil også kunne spre seg til children i OPEN-lista
def propagate_path_improvements(parent, map_obj, h_function):
    for child in parent.children:
        new_g = parent.g + cost_function(child.state)
        if new_g < child.g:
            child.parent = parent
            child.g = new_g
            child.f = child.g + h_calculation(child.state, map_obj, h_function)

#Genererer en liste med children til en gitt node
def generate_children(parent, map_obj):
    children_list = []
    for adjacent_tiles in [(0, -1), (0, 1), (-1, 0), (1, 0)]: #finner nabo. Skal kun ta hensyn til nord, sør, øst, vest
        child_pos_x = parent.state[0] + adjacent_tiles[0]
        child_pos_y = parent.state[1] + adjacent_tiles[1]
        
        (w, h) = map_obj.int_map.shape #henter width og height for å sørge for at vi holder oss innenfor mappet

        #sjekke at child_pos er innenfor grensene på map_obj
        if (child_pos_x < 0) or (child_pos_x > w) or (child_pos_y < 0) or (child_pos_y > h):
            continue #hvis noden er utenfor bryr vi oss ikke om den og sjekker neste
        
        child_pos = tuple((child_pos_x, child_pos_y))

        #sjekker om child_pos er en hindring, alle hindringer har verdi -1 i .csv-filene
        if map_obj.get_cell_value(child_pos) == -1:
            continue

        new_node = Node(child_pos) #lager ny node av child, alle andre variabler beholder default verdiene fra Node-klassen
        children_list.append(new_node) #legger til new_node i en liste av children
    return children_list

#Koble en parent til en child, og fyller inn verdier for g, h, f for child
def attach_child(parent, child, h_function, map_obj):
        child.parent = parent
        child.g = parent.g + cost_function(child.state, map_obj)
        child.h = h_calculation(child.state, map_obj, h_function)
        child.f = child.g + child.h


#A*-algoritme implementasjon
def a_star(start, goal, h_function, map_obj):
    #init:
    start_node = init_start_node(start, h_calculation(start, map_obj, h_function))
    OPEN = []
    CLOSED = []
    memo = {} #memory-dictionary på formen {state : node} 
    OPEN.append(start_node)
    memo[start_node.state] = start_node

    while len(OPEN) > 0: #looper så lenge det er elementer i OPEN

        #sjekker de cellene som skal åpnes om det er noen som har bedre f-verdi
        #setter den med best f-verdi til current_node
        current_node = OPEN[0]
        current_i = 0 #trengs for å poppe riktig element fra OPEN
        for i, node in enumerate(OPEN): #bruker enumerate siden vi vil ha med oss indeksen
            if node.f < current_node.f:
                current_node = node
                current_i = i
        #popper den beste noden og legger den i closed-lista
        OPEN.pop(current_i) 
        CLOSED.append(current_node)
        
        #sjekker om current_node er en mål-node
        if is_at_goal(current_node.state, goal):
            #går bakover langs alle barn->forelder->besteforelder osv. til vi er ved startnoden. Legger til alle koordinater i path slik at vi kan returnere den
            path = [] 
            now = current_node
            while now is not None: #det vil si at vi enda ikke har kommet til rotnoden som hadde en parent-peker til None
                path.append(now.state)
                now = now.parent
            return path[::-1] #returnerer baklengs path så elementene er i riktig rekkefølge


        #genererer barn til current_node
        children = generate_children(current_node, map_obj)

        #går gjennom alle children til current_node én etter én
        for child in children:

            #Dersom state til en child allerede eksisterer i en annen node betyr dette at vi noden er oppdaget fra før
            #Da må vi bruke den noden som er funnet tidligere, slik at vi kan undersøke om den gamle eller nye noden har best g-verdi
            if child.state in memo:
                child_node = memo[child.state]
            #Dersom noden sin state ikke eksisterer i en annen node oppretter vi en ny node med denne staten og legger til i memo
            else:
                child_node = init_child_node(current_node, child.state, h_function, map_obj) #hvis vi ikke har vært innom noden fra før og den finnes i memo, genererer vi en ny
                memo[child_node.state] = child_node
            
            #Legger til child_node som en child til current_node
            current_node.children.append(child_node)

            if child_node not in OPEN and child_node not in CLOSED: #Betyr at vi ikke har undersøkt denne noden enda
                attach_child(current_node, child_node, h_function, map_obj) #Fyller inn verdier for child
                OPEN.append(child_node) #Legger til child i OPEN, slik at den åpnes senere
            elif current_node.g + cost_function(child_node.state, map_obj) < child_node.g: #Betyr at kosten via current_node er billigere
                attach_child(current_node, child_node, h_function, map_obj) #Fyller inn verdier for child
                #dersom child_node ligger i CLOSED allerede må vi sjekke om vi kan forbedre g-verdien til child_node og 
                # andre etterkommer via veien gjennom current_node
                if child_node in CLOSED: 
                    propagate_path_improvements(child_node, map_obj, h_function)


def main():
    #setup:
    map_obj = Map.Map_Obj(task = 4)
    #map_obj.read_map('Samfundet_map_1.csv')
    #map_obj.read_map('Samfundet_map_2.csv')
    map_obj.read_map('Samfundet_map_Edgar_full.csv')
    map_obj.get_maps()
    start_state = map_obj.get_start_pos()
    goal_state = map_obj.get_goal_pos()
    h_function_type = "manhattan"

    solution = a_star(start_state, goal_state, h_function_type, map_obj) #astar returnerer en liste med koordinater til korteste vei
    for _ in solution[1:len(solution)-1]: #unnlater å male over start og goal så de kommer frem i visualiseringen
        map_obj.set_cell_value(_,"O") #maler mappet med veien vi fant
    map_obj.show_map()

if __name__ == '__main__':
    main()
