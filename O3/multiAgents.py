# multiAgents.py
# --------------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


from pacman import GameState
from util import manhattanDistance
from game import Directions
import random, util

from game import Agent

class ReflexAgent(Agent):
    """
    A reflex agent chooses an action at each choice point by examining
    its alternatives via a state evaluation function.

    The code below is provided as a guide.  You are welcome to change
    it in any way you see fit, so long as you don't touch our method
    headers.
    """


    def getAction(self, gameState):
        """
        You do not need to change this method, but you're welcome to.

        getAction chooses among the best options according to the evaluation function.

        Just like in the previous project, getAction takes a GameState and returns
        some Directions.X for some X in the set {NORTH, SOUTH, WEST, EAST, STOP}
        """
        # Collect legal moves and successor states
        legalMoves = gameState.getLegalActions()

        # Choose one of the best actions
        scores = [self.evaluationFunction(gameState, action) for action in legalMoves]
        bestScore = max(scores)
        bestIndices = [index for index in range(len(scores)) if scores[index] == bestScore]
        chosenIndex = random.choice(bestIndices) # Pick randomly among the best

        "Add more of your code here if you want to"

        return legalMoves[chosenIndex]

    def evaluationFunction(self, currentGameState, action):
        """
        Design a better evaluation function here.

        The evaluation function takes in the current and proposed successor
        GameStates (pacman.py) and returns a number, where higher numbers are better.

        The code below extracts some useful information from the state, like the
        remaining food (newFood) and Pacman position after moving (newPos).
        newScaredTimes holds the number of moves that each ghost will remain
        scared because of Pacman having eaten a power pellet.

        Print out these variables to see what you're getting, then combine them
        to create a masterful evaluation function.
        """
        # Useful information you can extract from a GameState (pacman.py)
        successorGameState = currentGameState.generatePacmanSuccessor(action)
        newPos = successorGameState.getPacmanPosition()
        newFood = successorGameState.getFood()
        newGhostStates = successorGameState.getGhostStates()
        newScaredTimes = [ghostState.scaredTimer for ghostState in newGhostStates]

        "*** YOUR CODE HERE ***"
        return successorGameState.getScore()

def scoreEvaluationFunction(currentGameState):
    """
    This default evaluation function just returns the score of the state.
    The score is the same one displayed in the Pacman GUI.

    This evaluation function is meant for use with adversarial search agents
    (not reflex agents).
    """
    return currentGameState.getScore()

class MultiAgentSearchAgent(Agent):
    """
    This class provides some common elements to all of your
    multi-agent searchers.  Any methods defined here will be available
    to the MinimaxPacmanAgent, AlphaBetaPacmanAgent & ExpectimaxPacmanAgent.

    You *do not* need to make any changes here, but you can if you want to
    add functionality to all your adversarial search agents.  Please do not
    remove anything, however.

    Note: this is an abstract class: one that should not be instantiated.  It's
    only partially specified, and designed to be extended.  Agent (game.py)
    is another abstract class.
    """

    def __init__(self, evalFn = 'scoreEvaluationFunction', depth = '2'):
        self.index = 0 # Pacman is always agent index 0
        self.evaluationFunction = util.lookup(evalFn, globals())
        self.depth = int(depth)

class MinimaxAgent(MultiAgentSearchAgent):
    """
    Your minimax agent (question 2)
    """

    def getAction(self, gameState):
        """
        Returns the minimax action from the current gameState using self.depth
        and self.evaluationFunction.

        Here are some method calls that might be useful when implementing minimax.

        gameState.getLegalActions(agentIndex):
        Returns a list of legal actions for an agent
        agentIndex=0 means Pacman, ghosts are >= 1

        gameState.generateSuccessor(agentIndex, action):
        Returns the successor game state after an agent takes an action

        gameState.getNumAgents():
        Returns the total number of agents in the game

        gameState.isWin():
        Returns whether or not the game state is a winning state

        gameState.isLose():
        Returns whether or not the game state is a losing state
        """
        "*** YOUR CODE HERE ***"
        #util.raiseNotDefined()

        #make a call to minimax()
        action, score = self.minimax(self.depth, self.index, gameState, gameState.getNumAgents())
        return action

    def minimax(self, depth, agentIndex, gameState, nr_of_agents):

        #if we have gone through all the agents we decrement the depth and reset the agent index
        if agentIndex >= nr_of_agents:
            agentIndex = 0
            depth -= 1

        #if we have searched through all the layers of nodes or game is over we return with no action and current score 
        if depth == 0 or gameState.isWin() or gameState.isLose():
            return None, self.evaluationFunction(gameState)
        
        best_action = None
        legal_actions = gameState.getLegalActions(agentIndex)
        
        if agentIndex == 0: #we have maximizing player (pacman)
            best_score = float('-inf')
            for action in legal_actions: #we check every action for the current game state to find the best move
                gs_child = gameState.generateSuccessor(agentIndex, action) #next GameState given an action and agent
                temp, score = self.minimax(depth, agentIndex+1, gs_child, nr_of_agents) #recursive call to search through all the layers
                #if our new score is higher than any previous score found for maximizing player we want to update our variables best_score and best_action
                if score > best_score:
                    best_score = score
                    best_action = action      
        else: #then we have minimizing player (ghost)
            best_score = float('inf')
            for action in legal_actions: #we check every action for a given ghost-state to find the best move
                gs_child = gameState.generateSuccessor(agentIndex, action) #next GameState given a action and agent
                temp, score = self.minimax(depth, agentIndex+1, gs_child, nr_of_agents) #recursive call to search through all the layers
                #if our new score is lower than any previous score found for minimizing player we want to update our variables best_score and best_action
                if score < best_score:
                    best_score = score
                    best_action = action
        return best_action, best_score

class AlphaBetaAgent(MultiAgentSearchAgent):
    """
    Your minimax agent with alpha-beta pruning (question 3)
    """

    def getAction(self, gameState):
        """
        Returns the minimax action using self.depth and self.evaluationFunction
        """
        "*** YOUR CODE HERE ***"
        #util.raiseNotDefined()

        #make a call to minimaxalphabeta()
        #we set alpha to -inf and beta to +inf at initialization
        action, score = self.minimaxalphabeta(self.depth, 0, gameState, gameState.getNumAgents(), float('-inf'), float('inf'))
        return action

    def minimaxalphabeta(self, depth, agentIndex, gameState, nr_of_agents, alpha, beta):

        #if we have gone through all the agents we decrement the depth and reset the agent index
        if agentIndex >= nr_of_agents:
            agentIndex = 0
            depth -= 1

        #if we have searched through all the layers of nodes or game is over we return with no action and current score 
        if depth == 0 or gameState.isWin() or gameState.isLose():
            return None, self.evaluationFunction(gameState)
        
        best_action = None
        legal_actions = gameState.getLegalActions(agentIndex)

        if agentIndex == 0: #we have maximizing player (pacman)
            best_score = float('-inf')
            for action in legal_actions: #we check every action for the current game state to find the best move
                gs_child = gameState.generateSuccessor(agentIndex, action) #next GameState given an action and agent
                temp, score = self.minimaxalphabeta(depth, agentIndex+1, gs_child, nr_of_agents, alpha, beta) #recursive call to search through all the layers
                #if our new score is higher than any previous score found for maximizing player we want to update our variables best_score and best_action
                if score > best_score:
                    best_score = score
                    best_action = action
                #if the new score is higher than any previous score found among the pacmans successor, we must update alpha with this value
                alpha = max(alpha, score)
                #if beta is less than alpha, then pacman has already found another action which is guaranteed to be better than the current action
                #we can then prune the tree
                if beta < alpha:
                    break
        else: #then we have minimizing player (ghost)
            best_score = float('inf')
            for action in legal_actions: #we check every action for a given ghost-state to find the best move
                gs_child = gameState.generateSuccessor(agentIndex, action) #next GameState given a action and agent
                temp, score = self.minimaxalphabeta(depth, agentIndex+1, gs_child, nr_of_agents, alpha, beta) #recursive call to search through all the layers
                if score < best_score:
                    best_score = score
                    best_action = action
                #if the new score is lower than any previous score found among the ghosts successor, we must update beta with this value 
                beta = min(beta, score)
                #if beta is less than alpha, then the ghost has already found another action which is guaranteed to be better than the current action
                #we can then prune the tree
                if beta < alpha:
                    break
        return best_action, best_score
    
class ExpectimaxAgent(MultiAgentSearchAgent):
    """
      Your expectimax agent (question 4)
    """

    def getAction(self, gameState):
        """
        Returns the expectimax action using self.depth and self.evaluationFunction

        All ghosts should be modeled as choosing uniformly at random from their
        legal moves.
        """
        "*** YOUR CODE HERE ***"
        util.raiseNotDefined()

def betterEvaluationFunction(currentGameState):
    """
    Your extreme ghost-hunting, pellet-nabbing, food-gobbling, unstoppable
    evaluation function (question 5).

    DESCRIPTION: <write something here so we know what you did>
    """
    "*** YOUR CODE HERE ***"
    util.raiseNotDefined()

# Abbreviation
better = betterEvaluationFunction
