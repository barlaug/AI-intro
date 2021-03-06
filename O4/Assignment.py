import copy
import itertools


class CSP:
    def __init__(self):
        # self.variables is a list of the variable names in the CSP
        self.variables = []

        # self.domains[i] is a list of legal values for variable i
        self.domains = {}

        # self.constraints[i][j] is a list of legal value pairs for
        # the variable pair (i, j)
        self.constraints = {}

        ##Variables to keep track of the success and failure count:
        self.successes = 0
        self.failures = 0

        ##We also keep track of how many times backtrack() is called:
        self.backtrack_calls = 0

    def add_variable(self, name, domain):
        """Add a new variable to the CSP. 'name' is the variable name
        and 'domain' is a list of the legal values for the variable.
        """
        self.variables.append(name)
        self.domains[name] = list(domain)
        self.constraints[name] = {}

    def get_all_possible_pairs(self, a, b):
        """Get a list of all possible pairs (as tuples) of the values in
        the lists 'a' and 'b', where the first component comes from list
        'a' and the second component comes from list 'b'.
        """
        return itertools.product(a, b)

    def get_all_arcs(self):
        """Get a list of all arcs/constraints that have been defined in
        the CSP. The arcs/constraints are represented as tuples (i, j),
        indicating a constraint between variable 'i' and 'j'.
        """
        return [(i, j) for i in self.constraints for j in self.constraints[i]]

    def get_all_neighboring_arcs(self, var):
        """Get a list of all arcs/constraints going to/from variable
        'var'. The arcs/constraints are represented as in get_all_arcs().
        """
        return [(i, var) for i in self.constraints[var]]

    def add_constraint_one_way(self, i, j, filter_function):
        """Add a new constraint between variables 'i' and 'j'. The legal
        values are specified by supplying a function 'filter_function',
        that returns True for legal value pairs and False for illegal
        value pairs. This function only adds the constraint one way,
        from i -> j. You must ensure that the function also gets called
        to add the constraint the other way, j -> i, as all constraints
        are supposed to be two-way connections!
        """
        if not j in self.constraints[i]:
            # First, get a list of all possible pairs of values between variables i and j
            self.constraints[i][j] = self.get_all_possible_pairs(self.domains[i], self.domains[j])

        # Next, filter this list of value pairs through the function
        # 'filter_function', so that only the legal value pairs remain
        self.constraints[i][j] = list(filter(lambda value_pair: filter_function(*value_pair), self.constraints[i][j]))

    def add_all_different_constraint(self, variables):
        """Add an Alldiff constraint between all of the variables in the
        list 'variables'.
        """
        for (i, j) in self.get_all_possible_pairs(variables, variables):
            if i != j:
                self.add_constraint_one_way(i, j, lambda x, y: x != y)

    def backtracking_search(self):
        """This functions starts the CSP solver and returns the found
        solution.
        """
        # Make a so-called "deep copy" of the dictionary containing the
        # domains of the CSP variables. The deep copy is required to
        # ensure that any changes made to 'assignment' does not have any
        # side effects elsewhere.
        assignment = copy.deepcopy(self.domains)

        # Run AC-3 on all constraints in the CSP, to weed out all of the
        # values that are not arc-consistent to begin with
        self.inference(assignment, self.get_all_arcs())

        # Call backtrack with the partial assignment 'assignment'
        return self.backtrack(assignment)

    def assignment_is_complete(self, assignment):
        """
        Returns True if every variable of the CSP-problem only has one possible 
        value in it's domain. Otherwise it returns False
        """
        for key, value in assignment.items(): 
            if len(value) != 1: 
                return False
        return True

    def backtrack(self, assignment):
        """The function 'Backtrack' from the pseudocode in the
        textbook.

        The function is called recursively, with a partial assignment of
        values 'assignment'. 'assignment' is a dictionary that contains
        a list of all legal values for the variables that have *not* yet
        been decided, and a list of only a single value for the
        variables that *have* been decided.

        When all of the variables in 'assignment' have lists of length
        one, i.e. when all variables have been assigned a value, the
        function should return 'assignment'. Otherwise, the search
        should continue. When the function 'inference' is called to run
        the AC-3 algorithm, the lists of legal values in 'assignment'
        should get reduced as AC-3 discovers illegal values.

        IMPORTANT: For every iteration of the for-loop in the
        pseudocode, you need to make a deep copy of 'assignment' into a
        new variable before changing it. Every iteration of the for-loop
        should have a clean slate and not see any traces of the old
        assignments and inferences that took place in previous
        iterations of the loop.
        """
        #increase bactrack-call number by one
        self.backtrack_calls += 1

        #if assigment is complete we have found a solution to our CSP-problem
        if self.assignment_is_complete(assignment):
            return assignment

        #var becomes a unassigned variable
        var = self.select_unassigned_variable(assignment)

        #we visit every possible value in the domain of variable var and assign it to val
        for val in assignment[var]:
            #we make a deep copy of assignments because we want do not want to see any of the
            #  changes made in the previous iterations of the loop
            assignment_copy = copy.deepcopy(assignment)
            assignment_copy[var] = [val]
            #edges becomes a list of tuples of all arcs neighbour to variable var
            edges = self.get_all_neighboring_arcs(var)
            if self.inference(assignment_copy, edges):
                #inference returns true for the edges so we recursively backtrack
                #increase success number by one
                self.successes += 1
                result = self.backtrack(assignment_copy)
                #if result is a non-empty dictionary we return it
                if result: return result
        
        #increase fail number by one
        self.failures += 1
        return {}        

    def select_unassigned_variable(self, assignment):
        """The function 'Select-Unassigned-Variable' from the pseudocode
        in the textbook. Should return the name of one of the variables
        in 'assignment' that have not yet been decided, i.e. whose list
        of legal values has a length greater than one.
        """
        #we return any unassigned variable. A variable is unassigned if the number of values it can take is higher than 1
        for key,value in assignment.items():
            if len(value) > 1:
                return key

    def inference(self, assignment, queue):
        """The function 'AC-3' from the pseudocode in the textbook.
        'assignment' is the current partial assignment, that contains
        the lists of legal values for each undecided variable. 'queue'
        is the initial queue of arcs that should be visited.
        """
        
        while queue:
            #AC-3 pops off an arbitrary arc (i, j) from the queue
            i, j = queue.pop(0)
            #revise returns true if and only if we change (revise) the domain of i
            if self.revise(assignment, i, j):
                #if domain of variable i is empty, we do not change it and return False
                if not assignment[i]:
                    return False
                #we iterate over every neighbouring arc of variable i and add it to queue, the list of arcs that should be visited
                for k, var in self.get_all_neighboring_arcs(i):
                    #do not add to queue if k = j, i.e. it is the arc we just visited
                    if k != j:
                        queue.append((k, i))
        return True

    def revise(self, assignment, i, j):
        """The function 'Revise' from the pseudocode in the textbook.
        'assignment' is the current partial assignment, that contains
        the lists of legal values for each undecided variable. 'i' and
        'j' specifies the arc that should be visited. If a value is
        found in variable i's domain that doesn't satisfy the constraint
        between i and j, the value should be deleted from i's list of
        legal values in 'assignment'.
        """
        #initially we have not revised the domain of i
        revised = False
        #we visit every possible value in the domain of i
        for x in assignment[i]:
            #get all possible pairs of the value of x and the domain of variable j as a list of tuples
            edges = list(self.get_all_possible_pairs(x,assignment[j]))
            tmp = True
            #iterate over every possible pair stored as edge
            for edge in edges:
                #if edge exists as one of the constraints in the csp problem we do not want to revise it
                if edge in self.constraints[i][j]:
                    tmp = False
            #if edge do not exist as a constraint, 
            # we can safely remove the current domain-value x from our list of possible domain-values for variable i
            # then variable i is also revised. i.e we have shrunk the domain of possible values for variable i
            if tmp:
                revised = True
                if x in assignment[i]:
                    assignment[i].remove(x)        
        return revised



def create_map_coloring_csp():
    """Instantiate a CSP representing the map coloring problem from the
    textbook. This can be useful for testing your CSP solver as you
    develop your code.
    """
    csp = CSP()
    states = ['WA', 'NT', 'Q', 'NSW', 'V', 'SA', 'T']
    edges = {'SA': ['WA', 'NT', 'Q', 'NSW', 'V'], 'NT': ['WA', 'Q'], 'NSW': ['Q', 'V']}
    colors = ['red', 'green', 'blue']
    for state in states:
        csp.add_variable(state, colors)
    for state, other_states in edges.items():
        for other_state in other_states:
            csp.add_constraint_one_way(state, other_state, lambda i, j: i != j)
            csp.add_constraint_one_way(other_state, state, lambda i, j: i != j)
    return csp


def create_sudoku_csp(filename):
    """Instantiate a CSP representing the Sudoku board found in the text
    file named 'filename' in the current directory.
    """
    csp = CSP()
    board = list(map(lambda x: x.strip(), open(filename, 'r')))

    for row in range(9):
        for col in range(9):
            if board[row][col] == '0':
                csp.add_variable('%d-%d' % (row, col), list(map(str, range(1, 10))))
            else:
                csp.add_variable('%d-%d' % (row, col), [board[row][col]])

    for row in range(9):
        csp.add_all_different_constraint(['%d-%d' % (row, col) for col in range(9)])
    for col in range(9):
        csp.add_all_different_constraint(['%d-%d' % (row, col) for row in range(9)])
    for box_row in range(3):
        for box_col in range(3):
            cells = []
            for row in range(box_row * 3, (box_row + 1) * 3):
                for col in range(box_col * 3, (box_col + 1) * 3):
                    cells.append('%d-%d' % (row, col))
            csp.add_all_different_constraint(cells)

    return csp


def print_sudoku_solution(solution):
    """Convert the representation of a Sudoku solution as returned from
    the method CSP.backtracking_search(), into a human readable
    representation.
    """
    for row in range(9):
        for col in range(9):
            print(solution['%d-%d' % (row, col)][0], end=" "),
            if col == 2 or col == 5:
                print('|', end=" "),
        print("")
        if row == 2 or row == 5:
            print('------+-------+------')

def main():
    name_to_path = {'Easy' : 'easy.txt', 'Medium' : 'medium.txt', 'Hard' : 'hard.txt', 'Very Hard' : 'veryhard.txt'}
    for name in name_to_path:
        curr_file = name_to_path[name]
        csp = create_sudoku_csp(curr_file)
        answer = csp.backtracking_search()
        print(f'{name}:')
        print_sudoku_solution(answer)
        print(f'Solved with {csp.failures} failures, and {csp.successes} successes, with {csp.backtrack_calls} calls to the backtrack() function')
        print('___________________________________________________________________________________\n')

main()