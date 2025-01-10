import random

D360_TEAM_MEMBERS = [
    "Juan Garcia Bazan",
    "Aaron Niskode-Dossett",
    "Melanie Moy",
    "Swetha Baskaran",
    "Damani Philip",
    "Edgar Arenas",
    "Eileen Toomer",
    "Jeremy Pharo",
    "Yong-Jin Lee",
    "Juan Bages",
    "Sydney Hamilton",
    "Brian McGonigle",
    "Crist Scheye-Grover",
    "Edwin Jimenez",
    "Jorge Banuelos",
    "Kelly Zhou",
    "Jeena Lee",
    "Kevin Zeng",
    "Monica Senapati",
    "Rachel Hong",
    "Ryan Bertsche",
    "Vishal Shah",
    "Discovery - TBH"
     ]
ALREADY_HIGHLIGHTED = ["Kelly Zhou", "Monica Senapati", "Rachel Hong", "Juan Bages", "Jorge Banuelos"]

# Function to get a random value from A that's not in B
def select_newsletter_highlight():
    # Create a new list of elements in A that are not in B
    eligible = [elt for elt in D360_TEAM_MEMBERS if elt not in ALREADY_HIGHLIGHTED]

    # Check if there are any elements left in eligible
    if not eligible:
        raise Exception("No more eligible team members to highlight.  Reset the list!")

    # Randomly select and return an element from eligible
    return random.choice(eligible)


# Example usage
selected_value = select_newsletter_highlight()

print(f'This week\'s highlighted team member: {selected_value}')
