import json


print("This program allows you as a user to add items to the item json file.\n\
If a question asks for an answer form a set of options, respond with the relevant number.\n")

def input_options(start:str, options:list, end:str):
    """Prints options for the user to pick. Will ask until one options is picked.
    Options are numbered as to allow any options and require few characters."""
    if len(options) < 2:
        raise ValueError (f"Length of options '{options}' should be greater than 1.")
    options_indexed = [f"[{n+1}]{o}" for n, o in enumerate(options)]
    options_string = start + ", ".join(options_indexed[:-1]) + " or " + options_indexed[-1] + end
    found = False
    while not found:
        result = input(options_string)
        try:
            int_result = int(result)
            float_result = float(result)
            if int_result != float_result or int_result < 1 or int_result > len(options):
                print(f"Not an integer between 1 and {len(options)}. Try again.")
            else:
                return options[int(result)-1]
        except:
            print(f"Not an integer between 1 and {len(options)}. Try again.")

#Lists of options
item_types = ["Limb", "Weapon"]
item_type_ids = ["l", "w"]
stats = ["HP", "Melee", "Ranged", "Magic", "Defense", "Speed", "End Boosts"]
slots = ["Head", "Torso", "Hand", "Foot"]
weapon_types = ["Melee", "Ranged", "Magic"]

#Data storage
main_dict = {}

#Load old item data
item_data_file = "item_data.json"
try:
    with open(item_data_file, "r") as file:
        old_data = json.load(file)
except:
    old_data = {}

#Work out where ids should start
next_item_id_nums = [0, 0, 0]
for item_id in old_data.keys():
    item_id_num = int(item_id[1:])
    item_type_index = item_type_ids.index(item_id[0])
    next_item_id_nums[item_type_index] = max(next_item_id_nums[item_type_index], item_id_num+1)

#Get data from user for items:
#Main loop:
running = True
while running:
    item_type = input_options("item type; ", item_types, ": ")
    #Work out item ids
    item_type_index = item_types.index(item_type)
    id = item_type_ids[item_type_index]+str(next_item_id_nums[item_type_index])
    next_item_id_nums[item_type_index] += 1
    name = input("Name: ")
    got_boosts = False
    stat_boosts = []
    while not got_boosts:
        boost = input_options("stat boosts; ", stats, ": ")
        if boost != "End Boosts":
            amount = input("stat boost amount [float|int]: ")
            try:
                amount = float(amount)
                stat_boosts.append([boost, amount])
                continue
            except:
                print("Not a number. Try again.")
                continue
        else:
            got_boosts = True
    
    item_data = {
        "type" : item_type,
        "name" : name,
        "stat boosts" : stat_boosts,
    }

    if item_type == "Limb":
        slot = input_options("slot; ", slots, ": ")
        denies = input_options("denies relevant hand; ", ["Yes", "No"], ": ")
        item_data.update({"slot" : slot})
        if denies == "Yes":
            item_data.update({"denies" : True})
    elif item_type == "Weapon":
        size = input_options("slots size; ", ["1", "2"], ": ")
        found = False
        while not found:
            damage = input("base damage: ")
            try:
                damage = float(damage)
                if damage < 0:
                    print("Damage must be positive.")
                else:
                    found = True
            except:
                print("Not a number. Try again.")
        weapon_type = input_options("weapon type; ", weapon_types, ": ")
        item_data.update({"base damage" : damage, "weapon type" : weapon_type, "slot size" : size})

    main_dict.update({id : item_data})
    end = input_options("", ["End", "continue"], "? ")
    if end == "End":
        running = False
    else:
        print("\n")

#Ask user to save or discard data
print(main_dict)
save = input_options(f"\nAdd this to '{item_data_file}'? ", ["Add", "Discard changes"], ": ")

if save == "Add":
    #Put the dicts together
    new_data = old_data | main_dict
    #Sort the dicts by id
    new_data = dict(sorted(new_data.items()))
    #Save the dict to the JSON file
    with open(item_data_file, "w") as file:
        json.dump(new_data, file, indent = 4)