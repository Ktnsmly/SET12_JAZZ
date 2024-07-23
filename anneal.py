import random
import itertools
import json
import math
from traits import activation_thresholds
from champions_loader import champions

def get_initial_solution(champions, team_size, mandatory_champs = []):
    """
    Generate an initial random solution for the team composition.

    :param champions: List of available champions.
    :param team_size: Size of the team to be formed.
    :param mandatory_champs: List of champions that must be included in the team.
    :return: List of champions representing an initial team composition.
    """
    # Include mandatory champions first
    initial_team = mandatory_champs.copy()

    # Determine the number of additional champions needed
    remaining_slots = team_size - len(initial_team)

    # Choose random unique champions from the remaining pool
    remaining_champs = [champ for champ in champions if champ not in initial_team]
    initial_team.extend(random.sample(remaining_champs, remaining_slots))

    return initial_team

"""
def get_neighbor(current_team, champions, mandatory_champs = []):

    new_team = current_team.copy()

    # Select a random champion to replace
    champ_to_replace = random.choice(new_team)

    # Select a new champion that is not in the current team
    possible_new_champs = [champ for champ in champions if champ not in new_team]
    new_champ = random.choice(possible_new_champs)

    # Replace the champion
    new_team[new_team.index(champ_to_replace)] = new_champ

    return new_team
"""

def get_neighbor(current_team, champions, mandatory_champs):
    """
    Generate a neighboring solution by making a small change to the current solution,
    while keeping mandatory champions intact.

    :param current_team: The current solution, a list of champions.
    :param champions: List of all available champions.
    :param mandatory_champs: List of champions that must not be replaced.
    :return: A new team composition, slightly different from the current one.
    """
    new_team = current_team.copy()

    # Filter the replaceable champions: those not in mandatory_champs
    replaceable_champions = [champ for champ in new_team if champ not in mandatory_champs]

    # If all champions are mandatory or no replaceable champions, return the current team
    if not replaceable_champions:
        return new_team

    # Select a random champion to replace from those not mandatory
    champ_to_replace = random.choice(replaceable_champions)

    # Potential new champions are those not in the current team or in mandatory_champs
    # This assumes that champions in mandatory_champs are already in new_team and shouldn't be duplicated
    potential_new_champs = [champ for champ in champions if champ not in new_team]

    # If there are no potential new champions (unlikely but could occur with small pools), return the team as is
    if not potential_new_champs:
        return new_team

    # Select a new champion and replace the chosen one
    new_champ = random.choice(potential_new_champs)
    replace_index = new_team.index(champ_to_replace)
    new_team[replace_index] = new_champ

    return new_team

def evaluate_solution(team, activation_thresholds, headliner_trait=None):
    trait_counts = {}

    # Counting traits from team
    for champion in team:
        for trait in champion.traits:
            trait_counts[trait] = trait_counts.get(trait, 0) + 1

    if headliner_trait and headliner_trait in trait_counts:
        trait_counts[headliner_trait] += 1

    # Identifying activated traits
    activated_traits = {
        trait for trait in trait_counts 
        if trait in activation_thresholds and trait_counts[trait] >= activation_thresholds[trait]
    }

    return len(activated_traits), activated_traits

def acceptance_probability(old_cost, new_cost, temperature):
    """
    Calculate the probability of accepting a worse solution at the current temperature.

    :param old_cost: Evaluation metric of the current solution.
    :param new_cost: Evaluation metric of the new solution.
    :param temperature: Current temperature in simulated annealing.
    :return: Probability of accepting the new solution.
    """
    if new_cost > old_cost:
        # If the new solution is better, always accept it
        return 1.0
    else:
        # If the new solution is worse, accept it with a certain probability
        return math.exp((new_cost - old_cost) / temperature)

def decrease_temperature(current_temperature, alpha):
    """
    Decrease the temperature based on the cooling schedule.

    :param current_temperature: Current temperature in the simulated annealing process.
    :param alpha: Cooling rate, a factor between 0 and 1 by which the temperature is multiplied.
    :return: New temperature after cooling.
    """
    return current_temperature * alpha

#Variables
initial_temperature = 1
final_temperature = 0.001
alpha = 0.9999 # Cooling rate

def calculate(champions, team_size, activation_thresholds, initial_temperature, final_temperature, alpha, mandatory_champs = [], headliner_trait=None):
    current_solution = get_initial_solution(champions, team_size, mandatory_champs)
    best_solution = current_solution
    current_cost, current_traits = evaluate_solution(current_solution, activation_thresholds, headliner_trait)
    best_cost = current_cost
    best_traits = current_traits
    temperature = initial_temperature

    while temperature > final_temperature:
        neighbor_solution = get_neighbor(current_solution, champions, mandatory_champs)
        neighbor_cost, neighbor_traits = evaluate_solution(neighbor_solution, activation_thresholds, headliner_trait)

        if neighbor_cost > current_cost or random.uniform(0, 1) < acceptance_probability(current_cost, neighbor_cost, temperature):
            current_solution = neighbor_solution
            current_traits = neighbor_traits
            current_cost = neighbor_cost

            if current_cost > best_cost:
                best_solution = current_solution
                best_cost = current_cost
                best_traits = current_traits

        temperature = decrease_temperature(temperature, alpha)
    return best_solution, best_cost

#calculate(champions, 9, [], activation_thresholds, initial_temperature, final_temperature, alpha)