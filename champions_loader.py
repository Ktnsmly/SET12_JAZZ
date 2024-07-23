import json
#from traits import activation_thresholds

class Champion:
    def __init__(self, name, traits, cost):
        self.name = name
        self.traits = traits
        self.cost = cost

    def __repr__(self):
        return f"Champion(name={self.name}, traits={self.traits}, cost={self.cost})"

def load_champions(filepath='champions.json'):
    with open(filepath, 'r') as file:
        data = json.load(file)
    return [
        Champion(champ['name'], champ['traits'], champ['cost']) for champ in data
    ]

champions = load_champions()
