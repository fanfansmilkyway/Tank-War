"""
This file is specially designed for storing basic data of tanks.
The source of the data is from the Internet. Maybe there're some mistakes and flaws.
"""

# Brief descriptions of the tanks
TANK_DESCRIPTION = {"T34-76":"Soviet Medium Tank. Equipped with F-34 76.2mm tank gun.",
                    "PzIII J":"German Medium Tank",
                    "PzIV H":"German Medium Tank. Equipped with 7.5 cm KwK 40 L/48.",
                    "Matilda II":"British Infantry Tank. Equipped with QF 2-pounder tank gun.",
                    "BT-7":"Soviet Light Tank",
                    "M4 Sherman":"American Medium Tank",
                    "T26":"Soviet Light Tank. Also be used by Finns."}

"""
Note about penetration:
The penetration written here is the penetration to vertical armor using AP or APCBC ammunition.
"""
# "Tank Name": [Attack(0m, 100m, 300m, 500m, 1000m, 1500m, 2000m, 3000m)mm, Relative Armor(front, side, rear), Speed(pixel / sec), Reloading Time(sec)]
TANK_CAPABILITY = {"T34-76": [[100, 85, 80, 73, 68, 62, 57, 45], [52, 52, 46], 9.7, 11],
             "PzIII J": [[60, 55, 50, 57, 47, 28, 21, 15, 5], [50, 30, 45], 8.4, 5],
             "PzIV H": [[140, 135, 130, 123, 109, 97, 86, 68], [80, 30, 20], 8.33, 8],
             "Matilda II": [[60, 53, 50, 47, 40, 34, 20, 5], [78, 70, 50], 5.56, 3],
             "BT-7": [[50, 45 ,43 ,40, 38, 35, 25, 20], [18, 10, 6], 18.1, 2.5],
             "M4 Sherman": [[90, 88, 83, 81, 73, 65, 59, 47], [75, 38, 38], 11.1, 6],
             "T26": [[60, 59, 50, 45, 35, 29, 26, 20], [15, 15, 6], 6.1, 7]}