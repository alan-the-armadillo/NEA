import json

class BehaviourTree:
    def __init__(self, root_node):
        self.root_node = root_node
        self.left_branch_len = BehaviourTree.get_len_left_branch(self.root_node)
        self.current_behaviour = self.reset_behaviour()
        self.pause_cycles = 0
    def reset_behaviour(self):
        """Returns the reset current behaviour index list."""
        return [0 for _ in range(self.left_branch_len)]
    @staticmethod
    def get_len_left_branch(node):
        """Recursively finds the length of the left child branch."""
        if hasattr(node, "children"):
            return BehaviourTree.get_len_left_branch(node.children[0]) + 1
        else:
            return 0
    def update(self):
        if self.pause_cycles > 0:
            self.pause_cycles -= 1
        else:
            self.current_behaviour = self.root_node.update(self.current_behaviour)
            print(self.current_behaviour)

class Node:
    def __init__(self):
        self.children = []
    def update(self):
        raise Exception (f"{self.__class__} does not have an update function.")


class SequenceNode(Node):
    """Moves focus if the child node is resolved/returns True."""
    def update(self, indexes):
        child = self.children[indexes[0]]
        if type(child) == SelectorNode:
            result = child.update(indexes[1:])
            if result == "move":
                new_index = indexes[0]+1
                if len(self.children) == new_index: #At end of tree
                    return "reset behaviour"
                return [new_index]+[0 for _ in range(BehaviourTree.get_len_left_branch(self.children[new_index]))]
            elif result == "return":
                return [0]+[indexes[1:]] #################
            elif type(result) == list:
                return result
            else:
                raise Exception (f"Result {result} could not be resolved by SequenceNode.")
        else:
            raise Exception (f"Have not made SequenceNode - {child.__class__} relations yet.")
            

class SelectorNode(Node):
    """If a child condition is met, this node returns.
    If the child condition is false, focus moves to the next child along."""
    def update(self, indexes):
        child = self.children[indexes[0]]
        if type(child) == ConditionNode:
            condition_result = child.update()
            if condition_result:
                result = "move" #Move focus to the right of the parent's children ##PARENT LEVEL
            else: #Move focus right to next child
                new_index = indexes[0]+1
                if len(self.children) == new_index:
                    raise Exception ("SelectorNode has no action node to the right of a condition node.")
                return [new_index]+[indexes[1:]]
        elif type(child) == ActionNode:
            action_result = child.update()
            if action_result:
                result = "return" #Move to the left-most of the parent of this node's children ##PARENT LEVEL
            else:
                return indexes #Current action has not completed, so do not move on ##CURRENT LEVEL
        else:
            raise Exception (f"You haven't implemented SelectorNode child resolution for {child.__class__}.")
        
        return result


class ConditionNode(Node):
    def __init__(self, condition_func):
        self.condition = condition_func
    def update(self):
        return self.condition()

class ActionNode(Node):
    def __init__(self, action_func):
        self.action = action_func


class AIModules:
    pass

class AIParser:
    with open("enemy_behaviours.json", "r") as file: ###############<- change "enemy behaviours"
        behaviours = json.load(file)

    behaviour_translator = {
        "no damage":"a",
        "wait":"b",
        "distance to player >":"c",
        "move from player":"d",
        "attack":"e"
    }
    node_type_translator = {
        "SEL":SelectorNode,
        "CON":ConditionNode,
        "ACT":ActionNode
    }

    
    @staticmethod
    def create_node(node_behaviour):
        node_type = node_behaviour[0]
        behaviour = node_behaviour[1]
        if type(behaviour[0]) != list: #Pre-defined ##########If you don't implement composites, can change this to check for CON and ACT
            behaviour_func = AIParser.behaviour_translator[behaviour[0]]
            node = AIParser.node_type_translator[node_type](behaviour_func)
        else:
            node = AIParser.node_type_translator[node_type]()
            for child_node in behaviour:
                node.children.append(AIParser.create_node(child_node))
        return node


    @staticmethod
    def parse_AI(id):
        behaviour = AIParser.behaviours[id]
        root_node = SequenceNode()
        for child_node in behaviour:
            root_node.children.append(AIParser.create_node(child_node))
        return BehaviourTree(root_node)

bt = AIParser.parse_AI("e0")
print(bt)
print(bt.left_branch_len)