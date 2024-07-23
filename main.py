import tkinter as tk
import logic
import importlib
from traits import activation_thresholds
import anneal
import threading

importlib.reload(logic)


class ChampionGrid:
    def __init__(self, master, champions):
        self.master = master
        self.champions = champions
        self.team = []
        self.buttons = []
        self.frame = tk.Frame(self.master)
        self.frame.pack()
        self.create_grid()
        self.create_text_input()
        self.create_clear_button()
        self.create_filter_by_text_button()

    def update_grid_with_new_data(self, new_champions):
        # Clear existing buttons
        for button in self.buttons:
            button.destroy()
        self.buttons.clear()

        # Update the champions list with the new data
        self.champions = new_champions

        # Recreate the grid with the new champions data
        self.create_grid()

    # Creates a UI grid with one button for each champion, labeled with their name 
    def create_grid(self):
        for i, champ in enumerate(self.champions):
            button = tk.Button(self.frame, text=champ.name, command=lambda champ=champ: self.champion_click(champ), width=7, height =1)
            button.grid(row=i // 13, column=i % 13, sticky='w', padx=5)  # Arrange buttons in a grid
            self.buttons.append(button)

    # Updates Current Team Text Window after clicking Champion button
    def champion_click(self, champ):
        self.team.append(champ) # Adds champion to current team
        count, traits = logic.evaluate_team(self.team, activation_thresholds, selected_option.get())
        header = f"Team has {len(self.team)} Units\n"
        current = format_team_info([self.team], count, header)
        update_output(current, current_team)

    # UI Button for clearing team
    def create_clear_button(self):
        clear_button = tk.Button(self.frame, text='Clear Team', command=self.clear_team)
        clear_button.grid(row=6, column=4)

    # Clears the Current team window
    def clear_team(self):
        self.team = []
        update_output("", current_team)

    # Text input box for filtering Champion Buttons
    def create_text_input(self):
        self.input_text = tk.Entry(self.frame)  # Create an Entry widget for text input
        self.input_text.grid(row=6, column =0, columnspan=13)
        self.input_text.bind("<Return>", self.filter_by_text)  # Bind the Enter key to the filter_by_text method

    def create_filter_by_text_button(self):
        filter_button = tk.Button(text = 'Filter', command = self.filter_by_text)
        filter_button.pack()
    
    # Takes Input Text and Greys out Champion Buttons with non-matching trait/names   
    def filter_by_text(self, event=None):
        inp = self.input_text.get()
        input_words = inp.split() if inp else []

        # Reset all buttons to original color if the text field is blank
        if inp.strip() == '':
            for button in self.buttons:
                button.config(bg='#f0f0f0')
            return  # Exit the function early

        for i, champ in enumerate(self.champions):
            match_found = False
            # Check if any input word matches the champion's name
            if any(word.lower() in champ.name.lower() for word in input_words):
                match_found = True

        # Check if any input word matches any of the champion's traits
            if not match_found:
                for trait in champ.traits:
                    if any(word.lower() in trait.lower() for word in input_words):
                        match_found = True
                        break

        # Update button color based on match found
            if match_found:
                self.buttons[i].config(bg='#f0f0f0')  # Set to original color if match is found
            else:
                self.buttons[i].config(bg='grey')  # Grey out if no match is found

# Takes List of teams and formats strings for output
def format_team_info(best_teams, max_activated, header, headliner_trait=None):
    if not isinstance(best_teams[0], list):
        best_teams = [best_teams]
    info_str = header
    for i, team in enumerate(best_teams):
        info_str += f'Team: {i+1} Activates: {max_activated} traits\n'
        for champ in team:
            # Append an asterisk to headliner trait
            traits_with_asterisk = [trait + ('**' if trait == headliner_trait else '') for trait in champ.traits]
            info_str += f"{champ.name:12} ({champ.cost}) (Traits: {', '.join(traits_with_asterisk)})\n"
        info_str += "\n"
    return info_str


# Takes some string and writes it to a specified text box
def update_output(info, endpoint):
	endpoint.delete('1.0', 'end')
	endpoint.insert(tk.END, info + "\n")
	endpoint.see(tk.END)  # Auto-scrolls to the end

"""
def calculate_best_teams(champion_grid):
    method = calculation_method_var.get()
    # Gets max team size from slider
    headliner_trait = selected_option.get()
    team_size = team_size_slider.get()
    # Gets allowed Champion costs from check boxes
    selected_costs = [cost for cost, var in cost_vars.items() if var.get() == 1]
    # Filters out Champions by cost
    filtered_champions = logic.filter_by_cost(logic.champions, selected_costs)

    # Calls Function to check for number of activated traits
    if method == "Brute Force":
        best_teams, traits, max_activated = logic.brute_force_solution2(
            filtered_champions, activation_thresholds, team_size, selected_option.get(), champion_grid.team)


    else:
        best_teams, max_activated = anneal.calculate(
            filtered_champions, team_size, activation_thresholds, anneal.initial_temperature, anneal.final_temperature, anneal.alpha, champion_grid.team, selected_option.get())

    # Updates output_text with team(s) 
    header = f"There are {len(best_teams)} Teams that Activate {max_activated} Traits\n\n"
    info_str = format_team_info(best_teams, max_activated, header, selected_option.get())
    update_output(info_str, output_text)
"""
cancel_flag = threading.Event()

def start_calculation_thread(app):
    cancel_flag.clear()  # Reset the cancel flag when starting a new calculation
    calculation_thread = threading.Thread(target=calculate_best_teams, args=(app,))
    calculation_thread.start()

def calculate_best_teams(champion_grid):
    method = calculation_method_var.get()
    # Gets max team size from slider
    headliner_trait = selected_option.get()
    team_size = team_size_slider.get()
    # Gets allowed Champion costs from check boxes
    selected_costs = [cost for cost, var in cost_vars.items() if var.get() == 1]
    # Filters out Champions by cost
    filtered_champions = logic.filter_by_cost(logic.champions, selected_costs)

    # Calls Function to check for number of activated traits
    if method == "Brute Force":
        best_teams, traits, max_activated = logic.brute_force_solution2(
            filtered_champions, activation_thresholds, team_size, selected_option.get(),cancel_flag, champion_grid.team)


    else:
        best_teams, max_activated = anneal.calculate(
            filtered_champions, team_size, activation_thresholds, anneal.initial_temperature, anneal.final_temperature, anneal.alpha, champion_grid.team, selected_option.get())

    # Updates output_text with team(s) 
    header = f"There are {len(best_teams)} Teams that Activate {max_activated} Traits\n"
    info_str = format_team_info(best_teams, max_activated, header, selected_option.get())
    update_output(info_str, output_text)

def cancel_calculation():
    cancel_flag.set()  # Signal the calculation to cancel




# GUI Layout
root = tk.Tk()
root.title("Team Builder")

# How many units are on the team
label = tk.Label(text='Set Max Team Size:')
label.pack()

# Slider for setting team size *Checking 7+ empty positions can take a very long time*
team_size_slider = tk.Scale(root, from_=1, to=12, orient='horizontal', length =200)
team_size_slider.set(7)
team_size_slider.pack()

# Calculation Method Selection
method_label = tk.Label(text="Select Calculation Method:")
method_label.pack()

calculation_method_var = tk.StringVar(value="Brute Force")  # Default value

brute_force_rb = tk.Radiobutton(root, text="Brute Force", variable=calculation_method_var, value="Brute Force")
brute_force_rb.pack()

annealing_rb = tk.Radiobutton(root, text="Simulated Annealing", variable=calculation_method_var, value="Simulated Annealing")
annealing_rb.pack()

# Create a frame for the dropdown and label
dropdown_frame = tk.Frame(root)
dropdown_frame.pack()

# Create and pack the label to the left in the frame
headliner_label = tk.Label(dropdown_frame, text="Headliner Trait:")
headliner_label.pack(side=tk.LEFT)

# Create and pack the dropdown menu to the right of the label in the frame
selected_option = tk.StringVar(root)
headliner_options = ["No Headliner"] + list(activation_thresholds.keys())
selected_option.set(headliner_options[0])
headliner_trait = tk.OptionMenu(dropdown_frame, selected_option, *headliner_options)
headliner_trait.pack(side=tk.LEFT)

# Creates check boxes that are used for filtering what champion costs to include
cost_label = tk.Label(text = 'Include Costs:')
cost_label.pack()
cost_vars = {i: tk.IntVar(value=1) for i in range(1, 6)}  # Create a dictionary of IntVar for costs 1-5

cost_checkboxes_frame = tk.Frame(root)
cost_checkboxes_frame.pack()

for cost, var in cost_vars.items():
    checkbox = tk.Checkbutton(cost_checkboxes_frame, text=str(cost), variable=var)
    checkbox.pack(side=tk.LEFT)

# What is this
#button_frame = tk.Frame(root)
#button_frame.pack()

# Uses ChampionGrid class to create grid of buttons with Champion names
app = ChampionGrid(root, logic.champions)
    
# Button to calculate best teams based on trait activation
get_value_button = tk.Button(root, text="Calculate", command=lambda: calculate_best_teams(app))
get_value_button.pack()

# Updates when Champion buttons clicked to show current team
current_team = tk.Text(root, height=10, width = 65)
current_team.pack()

# Updates when new teams are calculated to show best teams
output_text = tk.Text(root, height=30, width=65)
output_text.pack()

cancel_button = tk.Button(root, text="Cancel", command=cancel_calculation)
cancel_button.pack()



root.mainloop()






