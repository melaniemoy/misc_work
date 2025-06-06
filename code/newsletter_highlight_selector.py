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
    "Insha Lakhani",
    "Jorge Banuelos",
    "Kelly Zhou",
    "Jeena Lee",
    "Farman Pirzada",
    "Kevin Zeng",
    "Monica Senapati",
    "Rachel Hong",
    "Ryan Bertsche",
    "Vishal Shah"
]
ALREADY_HIGHLIGHTED = ["Kelly Zhou", "Monica Senapati", "Rachel Hong", "Juan Bages", "Jorge Banuelos", "Kevin Zeng", "Jeena Lee", "Brian McGonigle", "Swetha Baskaran", "Insha Lakhani", "Sydney Hamilton", "Ryan Bertsche"]

# Function to get a random value from A that's not in B
def select_newsletter_highlight():
    # Create a new list of elements in A that are not in B
    eligible = [elt for elt in D360_TEAM_MEMBERS if elt not in ALREADY_HIGHLIGHTED]

    # Check if there are any elements left in eligible
    if not eligible:
        raise Exception("No more eligible team members to highlight.  Reset the list!")

    # Shuffle eligible people
    random.shuffle(eligible)
    return eligible


# Example usage
members_randomized = select_newsletter_highlight()

print(f'Highlighted members in order: {members_randomized}')