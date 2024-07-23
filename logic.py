# Standard Library imports
import itertools
import json

# Champion class with name and traits
class Champion:
  def __init__(self, name, traits, cost):
    self.name = name
    self.traits = traits
    self.cost = cost

  def __repr__(self):
    return f"Champion(name={self.name}, traits={self.traits}, cost={self.cost})"

# Read and parse JSON file
with open('champions.json', 'r') as file:
  data = json.load(file)

# Creat the list of champions
champions = [
  Champion(champ['name'], 
           champ['traits'], 
           champ['cost']) for champ in data]

# Filter champions by their cost
def filter_by_cost(champions, allowed_costs):
  return [champ for champ in champions if champ.cost in allowed_costs]
  
# Checks team and returns the number of traits activated and the set of activated traits
def evaluate_team(team, activation_thresholds, headliner_trait=None):
    trait_counts = {}

    # Counting traits from team
    for champion in team:
        for trait in champion.traits:
            trait_counts[trait] = trait_counts.get(trait, 0) + 1

    # Adding +1 to the headliner trait, if selected
    if headliner_trait and headliner_trait in trait_counts:
        trait_counts[headliner_trait] += 1

    # Identifying activated traits
    activated_traits = {
        trait for trait in trait_counts 
        if trait in activation_thresholds and trait_counts[trait] >= activation_thresholds[trait]
    }

    return len(activated_traits), activated_traits


"""
# Checks all team variations and creates a list of solutions that activate the most traits 
def brute_force_solution2(champions, activation_thresholds, team_size, headliner_trait, mandatory_champs=[]):
  best_teams = []
  best_team_traits = set()
  max_activated = 0
  
  # Exclude mandatory champions from the pool to choose from
  remaining_champs = [champ for champ in champions if champ not in mandatory_champs]
  remaining_slots = team_size - len(mandatory_champs)
  
  for team_combination in itertools.combinations(remaining_champs, remaining_slots):
      # Add mandatory champions to the team
      team = mandatory_champs + list(team_combination)
      activated, traits = evaluate_team(team, activation_thresholds, headliner_trait)
  
      if activated > max_activated:
          max_activated = activated
          best_teams = [team]
          best_team_traits = traits
      elif activated == max_activated:
          best_teams.append(team)
          best_team_traits = traits
  
  return best_teams, best_team_traits, max_activated
"""

def brute_force_solution2(champions, activation_thresholds, team_size, headliner_trait, cancel_flag, mandatory_champs=[]):
    best_teams = []
    best_team_traits = set()
    max_activated = 0
    
    # Exclude mandatory champions from the pool to choose from
    remaining_champs = [champ for champ in champions if champ not in mandatory_champs]
    remaining_slots = team_size - len(mandatory_champs)
    
    for team_combination in itertools.combinations(remaining_champs, remaining_slots):
        # Check if cancellation is requested
        if cancel_flag.is_set():
            return [], set(), 0  # Early return on cancel
        
        # Add mandatory champions to the team
        team = mandatory_champs + list(team_combination)
        activated, traits = evaluate_team(team, activation_thresholds, headliner_trait)
    
        if activated > max_activated:
            max_activated = activated
            best_teams = [team]
            best_team_traits = traits
        elif activated == max_activated:
            best_teams.append(team)
            best_team_traits = traits
    
    return best_teams, best_team_traits, max_activated







                
