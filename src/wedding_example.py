import pulp

max_tables = 10
max_table_size = 8
guests = "A B C D E F G H I J K L M N O P Q R S T U V W X Y Z".split()


def happiness(table):
    """
    Find the happiness of the table
    - by calculating the maximum distance between the letters
    """
    return abs(ord(table[0]) - ord(table[-1]))


# create list of all possible tables
possible_tables = [tuple(c) for c in pulp.allcombinations(guests, max_table_size)]

# create a binary variable to state that a table setting is used
x = pulp.LpVariable.dicts(
    "table", possible_tables, lowBound=0, upBound=1, cat=pulp.LpInteger
)

seating_model = pulp.LpProblem("Wedding Seating Model", pulp.LpMinimize)

seating_model += pulp.lpSum([happiness(table) * x[table] for table in possible_tables])

# specify the maximum number of tables
seating_model += (
    pulp.lpSum([x[table] for table in possible_tables]) <= max_tables,
    "Maximum_number_of_tables",
)

# A guest must seated at one and only one table
for guest in guests:
    seating_model += (
        pulp.lpSum([x[table] for table in possible_tables if guest in table]) == 1,
        f"Must_seat_{guest}",
    )

seating_model.solve()

print(f"The chosen tables are out of a total of {len(possible_tables)}:")
for table in possible_tables:
    if x[table].value() == 1.0:
        print(table)