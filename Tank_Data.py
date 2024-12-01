"""
This file is specially designed for storing basic data of tanks.
The source of the data is from the Internet. Maybe there're some mistakes and flaws.
"""

# Brief descriptions of the tanks
TANK_DESCRIPTION = {"T34":"Soviet Medium Tank. Equipped with F-34 76.2mm tank gun.",
                    "PzIII J":"German Medium Tank",
                    "PzIV H":"German Medium Tank. Equipped with 7.5 cm KwK 40 L/48.",
                    "Matilda II":"British Infantry Tank. Equipped with QF 2-pounder tank gun."}

"""
Note about penetration:
The penetration written here is the penetration to vertical armor using AP or APCBC ammunition.
"""
# "Tank Name": [Attack(0m, 100m, 300m, 500m, 1000m, 1500m, 2000m, 3000m)mm, Relative Armor(front, side, rear), Speed(pixel / sec)]
TANK_DATA = {"T34-76": [[100, 85, 80, 73, 68, 62, 57, 45], [52, 52, 46], 9.7],
             "PzIII J": [[60, 55, 50, 57, 47, 28, 21, 15, 5], [50, 30, 45], 8.4],
             "PzIV H": [[140, 135, 130, 123, 109, 97, 86, 68], [80, 30, 20], 8.33],
             "Matilda II": [[60, 53, 50, 47, 40, 34, 20, 5], [78, 70, 50], 5.56]}