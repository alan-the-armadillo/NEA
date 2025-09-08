import json
from random import randint, uniform
from hitbox import Hitbox

GAME = None

class Behaviours:
    def no_damage(entity):
        print("no damage")
        return True

    def wait(entity, time):
        print(f"wait {time}")
        return []

    def distance_to_player_gt(entity, smaller_dist):
        pos1, pos2 = entity.collider.rect.center, GAME.player.collider.rect.center
        distance = Hitbox.get_distance(pos1, pos2)
        print(distance)
        return distance > smaller_dist

    def move_from_player(entity, time):
        def moving_behaviour():
            epos, ppos = entity.collider.rect.center, GAME.player.collider.rect.center
            entity.update_motion_vector([epos[0]-ppos[0], epos[1]-ppos[1]])
            entity.move()
        #Set entity current behaviour
        entity.behaviour = moving_behaviour
        #Update entity behaviour tree pause time
        entity.AI.pause = time
        print(f"move from player {time}")
        return []

    def attack(entity, attack_id):
        print(f"attack {attack_id}")
        return []

    def wander(entity, time):
        x,y = entity.collider.rect.center
        boundaries = GAME.renderer.display.get_size()
        new_vector = [uniform(0, boundaries[0])-x, uniform(0, boundaries[0])-y]
        entity.update_motion_vector(new_vector)
        def moving_behaviour():
            entity.move()
        #Set entity current behaviour
        entity.behaviour = moving_behaviour
        #Update entity behaviour tree pause time
        entity.AI.pause = time
        print(f"wander {time}")
        return []

    translator = {
        "no damage":no_damage,
        "wait": wait,
        "distance to player >": distance_to_player_gt,
        "move from player" : move_from_player,
        "attack" : attack,
        "wander" : wander
    }

class BehaviourTree:
    with open("enemy_behaviours.json", "r") as file:
        behaviours = json.load(file)
    
    def get_relative_left_branch_len(self, parent_node):
        if parent_node[0] in ["CON", "ACT"]: #Leaf
            return 0
        else:
            return 1 + self.get_relative_left_branch_len(parent_node[1][0])

    def get_relative_left_leaf_index(self, parent_node):
        #-1 as to not include the current node
        return [0 for _ in range(self.get_relative_left_branch_len(parent_node))]

    def parse_node_data(self, node_data):
        """Recreates the node data but replaces the behaviour name with the function.
        """
        node_type = node_data[0]
        if node_type in ["CON", "ACT"]: #Check leaf
            behaviour = node_data[1]
            #Use get rather than indexing to allow for better error handling if there is a typo or function not implemented
            behaviour_function = Behaviours.translator.get(behaviour[0])
            if behaviour_function == None:
                raise ValueError (f"Unknown behaviour '{behaviour[0]}'")
            parameters = behaviour[1:]
            #Return formatted node data
            if parameters:
                return [node_type, [behaviour_function] + parameters]
            else:
                return [node_type, [behaviour_function]]
        else: #Check parent nodes
            #Recursively check children
            children_data = node_data[1]
            children = [self.parse_node_data(c) for c in children_data]
            return [node_type, children]

    def __init__(self, entity, ai_id):
        self.entity = entity
        tree_data = BehaviourTree.behaviours.get(ai_id)
        if tree_data == None:
            raise ValueError (f"Uknown ai_id '{ai_id}'")
        self.tree = self.parse_node_data(tree_data)
        self.initial_index = self.get_relative_left_leaf_index(self.tree)
        self.index = self.initial_index.copy()
        self.pause = 0
        print(self.tree, self.initial_index, "\n")

    def resolve_SEQ(self, node, relative_index):
        """Resolves child node.
        If it returns True the child is not the right-most, then this node adds to the relative index and returns the index since the child has succeeded.
        If the child is the rightmost and returns True, this node returns True.
        If it returns False, then this node will not update the relative index but will return it.
        If it returns a list, then this node returns the relative index.
        This will occur if the child that was resolved is not a direct child of this node."""
        children = node[1]
        child = children[relative_index[0]]
        result = self.traverse(child, relative_index[1:])
        if result == True:
            new_relative_index = []
            new_relative_index.append(relative_index[0] + 1)
            if new_relative_index[0] == len(children):
                return True
            #Index adapts to the length of the new branch, so there is no indexing issues:
            new_child = children[new_relative_index[0]]
            new_relative_index = [new_relative_index[0]]+self.get_relative_left_leaf_index(new_child)
            return new_relative_index
        elif result == False:
            return relative_index
        elif type(result) == list:
            return [relative_index[0]] + result
        else:
            raise Exception(f"Unknown result {result} from child of SEQ node.")
    
    def resolve_SEL(self, node, relative_index):
        """Resolves child node.
        If it returns False, then this node adds to the relative index and returns the index since the child failed.
        If it returns True, then this node returns True as the child succeeded.
        If it returns a list, then this node returns the relative index.
        This will return if the child that was resolved is not a direct child of this node."""
        children = node[1]
        child = children[relative_index[0]]
        result = self.traverse(child, relative_index[1:])
        if result == False:
            new_relative_index = []
            new_relative_index.append(relative_index[0] + 1)
            #Check not at the right end
            if len(children) == new_relative_index[0]:
                return True
            else:
                #Index adapts to the length of the new branch, so there is no indexing issues:
                new_child = children[new_relative_index[0]]
                new_relative_index = [new_relative_index[0]]+self.get_relative_left_leaf_index(new_child)
                return new_relative_index
        elif result == True:
            return True
        elif type(result) == list:
            return [relative_index[0]] + result
        else:
            raise Exception(f"Unknown result {result} from child {child[0]} of SEL node.")

    def resolve_PSEQ(self, node, _):
        """Repeatedly resolves like a SEQ node, but stops when a child fails or all children have been completed.
        """
        relative_index = self.get_relative_left_leaf_index(node)
        failed = False
        while not failed:
            result = self.resolve_SEQ(node, relative_index)
            next_child_index = relative_index[0]+1
            if type(result) == bool or result[0] != next_child_index: #Cannot move on
                failed = True
            else:
                relative_index = result
        return result

    def resolve_PSEL(self, node, _):
        """Repeatedly resolves like a SEL node, but stops when a child fails.
        """
        relative_index = self.get_relative_left_leaf_index(node)
        failed = False
        while not failed:
            result = self.resolve_SEL(node, relative_index)
            next_child_index = relative_index[0]+1
            if result == True or result[0] != next_child_index: #Cannot move on
                failed = True
            else:
                relative_index = result
        return result

    def resolve_CON(self, node, _):
        return node[1][0](self.entity, *node[1][1:])

    def resolve_ACT(self, node, _):
        return node[1][0](self.entity, *node[1][1:])

    node_resolvers = {
        "PSEQ":resolve_PSEQ,
        "PSEL":resolve_PSEL,
        "SEQ":resolve_SEQ,
        "SEL":resolve_SEL,
        "CON":resolve_CON,
        "ACT":resolve_ACT
    }

    def traverse(self, node, relative_index):
        """
        Arguments:
            relative_index (list): list of indexes of children that lead from this node to the leaf node."""
        print(node[0], end="--|")
        node_type = node[0]
        return BehaviourTree.node_resolvers[node_type](self, node, relative_index)

    def update(self):
        if self.pause > 0:
            self.pause -= 1
        else:
            value = self.traverse(self.tree, self.index)
            if value == True:
                self.index = self.initial_index.copy()
            else:
                self.index = value
        print(f"INDEX:  {self.index}")