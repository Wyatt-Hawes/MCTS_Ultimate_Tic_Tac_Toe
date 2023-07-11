
from mcts_node import MCTSNode
from random import choice
from math import sqrt, log

num_nodes = 1000
explore_faction = 2.

global no_child_nodes
no_child_nodes = 0

def traverse_nodes(node, board, state, identity):
    """ Traverses the tree until the end criterion are met.

    Args:
        node:       A tree node from which the search is traversing.
        board:      The game setup.
        state:      The state of the game.
        identity:   The bot's identity, either 'red' or 'blue'.

    Returns:        A node from which the next stage of the search can proceed.

    """
    #Unsure where board, state, and identity should be included

    #node.visits =  node.visits + 1
    if board.is_ended(state) == True:
        #print("Path lead to game end, returning None in traverse_node()")
        return (node, state)

    #                                               C is exploration factor
    #weight = child_node_wins / child_node_visits   +    C * sqrt( ln(current_node_visits) / child_node_visits )


    if len(node.untried_actions) != 0:
        return (node, state)

    if node.child_nodes is {}:
        no_child_nodes+=1
        #node.untried_actions = board.legal_actions(state)
        print("*" * 1000)
        return (node, state)


    '''
    print("\n---------------------------------")
    print("ALL ACTION ATTEMPTED, CHOOSE CHILD")
    print(node.child_nodes)
    print("----------------------------------")
    '''

    max_weight = None
    max_node   = None
    max_state  = state



    for key in node.child_nodes.keys():
        curr_child = node.child_nodes[key]
        #print("LOOKING:",curr_child)
        winRate = (curr_child.wins/curr_child.visits)
        if board.current_player(state) != identity:
            winRate = 1 - winRate

        curr_weight = winRate  +   (explore_faction * sqrt( log(node.visits) / curr_child.visits ))

        if (max_weight is None) or (curr_weight > max_weight):
            max_weight = curr_weight
            max_node = curr_child
            max_state = board.next_state(state,curr_child.parent_action)


    if max_node is None:
        print("Woah no max child was found at all")
        print(node)
        print(node.child_nodes)
        print(state)
        print(board.display(state, node.parent_action))
        print(board.is_ended(state))
        print(node.untried_actions)
        exit()



    return traverse_nodes(max_node,board,max_state,identity)
    #return traverse_nodes(max_node, board, state, identity)


    # Hint: return leaf_node


def expand_leaf(node, board, state):
    """ Adds a new leaf to the tree by creating a new child node for the given node.

    Args:
        node:   The node for which a child will be added.
        board:  The game setup.
        state:  The state of the game.

    Returns:    The added child node.

    """

    if board.is_ended(state):
        #print("Node Cant be expanded, game is over")
        return

    #Choose a random untried action
    chosen_action = choice(node.untried_actions)
    #remove it from the untried action list
    node.untried_actions.remove(chosen_action)

    new_state = board.next_state(state, chosen_action)

    #create node
    new_node = MCTSNode(parent=node,parent_action=chosen_action, action_list=board.legal_actions(new_state))
    #new_node.visits = 1

    '''
    if board.legal_actions(new_state) == []:
        print(node)
        print(new_node)
        print(board.display(state, new_node.parent_action))
    '''

    #Add new child to parent's dictionary
    node.child_nodes[chosen_action] = new_node

    # Hint: return new_node
    return new_node


def rollout(board, state):
    """ Given the state of the game, the rollout plays out the remainder randomly.

    Args:
        board:  The game setup.
        state:  The state of the game.

    """

    while board.is_ended(state) == False:
        random_choice = choice(board.legal_actions(state))
        state = board.next_state(state,random_choice)

    return state


def backpropagate(node, won):
    """ Navigates the tree from a leaf node to the root, updating the win and visit count of each node along the path.

    Args:
        node:   A leaf node.
        won:    An indicator of whether the bot won or lost the game.

    """
    if node is None:
        return

    #Increment the value, won is 1 for win and 0 for loss
    node.visits = node.visits + 1
    if won > 0:
        node.wins   = node.wins + won

    #print("New ratio: ", node.wins,"/",node.visits)
    #recurse
    backpropagate(node.parent, won)
    return


def think(board, state):
    """ Performs MCTS by sampling games and calling the appropriate functions to construct the game tree.

    Args:
        board:  The game setup.
        state:  The state of the game.

    Returns:    The action to be taken.

    """
    identity_of_bot = board.current_player(state)
    root_node = MCTSNode(parent=None, parent_action=None, action_list=board.legal_actions(state))
    #print(identity_of_bot)
    #Temporary redeclaration
    #num_nodes = 100
    
    for step in range(num_nodes):
        # Copy the game for sampling a playthrough
        sampled_game = state

        # Start at root
        node = root_node

        # Do MCTS - This is all you!

        #Traverse nodes to get next node to be expanded and state at that node
        return_values = traverse_nodes(node,board, sampled_game, identity_of_bot)


        if return_values is None:
            print("TRAVERSE RETURNED NONE")
            continue




        node,sampled_game = return_values

        #Expand the node and add it to graph
        new_node = expand_leaf(node,board,sampled_game)
        if new_node is None:
            backpropagate(node, board.points_values(sampled_game)[identity_of_bot])
            continue

        #Simulate remainder (or evaluate heuristic)
        new_node_state = board.next_state(sampled_game,new_node.parent_action)

        #print(new_node_state)
        new_node_state = rollout(board,new_node_state)
        #print(new_node_state)

        #1 for win, 0 for tie, -1 for loss
        backpropagate(new_node, board.points_values(new_node_state)[identity_of_bot])


    #Now choose child node from parent with highest win/visited ratio
    best_move       = None
    best_move_ratio = None

    #print("Possible Moves: \n", root_node.child_nodes)
    #print("Children:", root_node.child_nodes)
    for key in root_node.child_nodes.keys():
        curr_node = root_node.child_nodes[key]
        #print("looking at: ", curr_node, "  \t its parent is", root_node)

        curr_ratio = curr_node.wins/curr_node.visits

        if best_move_ratio is None or (curr_ratio > best_move_ratio):
            best_move = curr_node.parent_action
            best_move_ratio = curr_ratio


    # Return an action, typically the most frequently used action (from the root) or the action with the best
    # estimated win rate.
    #return None
    print("MCTS_vanilla calculated move ", best_move, ":%.0f"%(best_move_ratio * 100) + "%", "(",no_child_nodes,")")
    return best_move
