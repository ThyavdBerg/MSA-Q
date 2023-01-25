import sys
import time
from os.path import exists, isdir
import sqlite3
import pickle
import concurrent.futures
import random
from re import split
import csv

def checkInput():
    """Checks whether the input received from MSA_QGIS.py via stdin is safe and functional.
    If not, the programme (subprocess) will quit."""
    count = 1

    for line in sys.stdin:
        if count == 1:
            if isdir(line[:-1]):
                save_directory = line[:-1]
                count += 1
            else:
                sys.exit("Error in subprocess, save directory not correct")
        elif count == 2:
            if line[:-1] == "0":
                from_basemap = line[:-1]
                count +=1
            else:
                if exists(from_basemap):
                    from_basemap = line[:-1]
                    count+=1
                else:
                    sys.exit("Error in subprocess, basemap file does not exist")
        elif count == 3:
            run_type = line[:-1]
            count +=1
        elif count == 4:
            number_of_iters = line[:-1]
            count +=1
        elif count == 5:
            spacing = line


    return save_directory, from_basemap, run_type, number_of_iters, spacing

def loadFiles(save_directory):
    """Loads the files required for running the MSA.

    :param save_directory: URL location of the SQlite file containing the point sampled vector point layer
    as created in MSA_QGIS.py
    :type save_directory: str"""
    with open(save_directory+"/temp_save_rule_dict.pkl", 'rb') as pkl_file:
        dict_nest_rule = pickle.load(pkl_file)

    with open(save_directory + "/temp_save_ruletree_dict.pkl", 'rb') as pkl_file:
        dict_rule_tree = pickle.load(pkl_file)

    return dict_nest_rule, dict_rule_tree

def copySqlitetoMem(save_directory):
    """Copies the temp file made for communicating with MSA_QGIS.py to an in-memory database.

    :param save_directory: URL location of the SQlite file containing the point sampled vector point layer
    as created in MSA_QGIS.py
    :type save_directory: str

    :return: Sqlite connection in memory that contains the set of tables built in MSA_QGIS.py
    """

    source = sqlite3.connect(save_directory+"//temp_file_sql_input.sqlite")
    #TODO check for existence of required tables
    conn = sqlite3.connect(":memory:")
    source.backup(conn)
    return conn


def mainMSA():
    """ This is where the main application of the MSA takes place, outside of QGIS, using SQLite3.
    Implements multiprocessing so that iterations of the MSA can be operated in parallel.

    :param directory: URL location of the SQlite file containing the point sampled vector point layer
    as created in MSA_QGIS.py
    :type directory: str """
    #remove all of the basegroup rules
    #identify final rules
    #make list per trajectory through the tree
    #run assignVegCom through the lists, start from basemap

    pass

def makeBasemap(conn, cursor, dict_rule_tree, dict_nest_rule,spacing):
    """ This deals with the order of rules in the dict_rule_tree for the making of a basemap, so that they can be dealt
    with correctly with assignVegetation.

    :param conn: Sqlite3 memory connection to the point_sampled_map
    :type conn: sqlite3.Connection

    :param cursor: Sqlite3 cursor of the connection above
    :type cursor: sqlite3.Cursor

    :param dict_rule_tree: Dictionary containing the UI-less version of the rule tree
    :type dict_rule_tree: dict

    :param dict_nest_rule: Dictionary containing the nested information on the user given rules. Given solely to be able
    to pass it on to assignVegCom.
    :type dict_nest_rule: dict
    """

    # create a list of all of the basegroup rules and run them from low to high
    list_base_group_ids = [key for key in dict_rule_tree if dict_rule_tree[key][4]] #4 is isBaseGroup bool
    list_base_group_ids.sort()
    for item in list_base_group_ids:
        assignVegCom(dict_nest_rule, conn, cursor, "basemap", dict_rule_tree[item][3], spacing) #3 is rule name
    #save a file with the basemap
    cursor.execute(f'VACUUM INTO "{save_directory}//output_basemap.sqlite";')
    conn.commit()


def assignVegCom(dict_nest_rule, conn, cursor, map_name, rule, spacing):
    """ Edits veg_com in the SQLite database version of the map based on a single given rule.

    :param conn: sqlite3 memory connection
    :type conn: sqlite3.Connection

    :param cursor: sqlite3 cursor of the connection above
    :type cursor: sqlite3.Cursor

    :param map_name: name of the sqlite3 table that will be edited
    :type map_name: str

    :param rule: rule number that corresponds to a key in dict_nest_rule and determines which rule will be
    used to change veg_com.
    :type rule: str or int
    """
    vegcom_start_time = time.time()
    print(f"{vegcom_start_time}: Assigning veg_com for {map_name} using rule {rule}")

    veg_com = dict_nest_rule[rule][2]
    rule_type = dict_nest_rule[rule][3]
    list_of_prev_vegcom = dict_nest_rule[rule][9]
    chance = dict_nest_rule[rule][4]

    #TODO see if this can be moved somewhere else so that it only needs to happen once
    cursor.execute(f"SELECT * FROM {map_name}")
    number_of_entries = len(cursor.fetchall())

    #set chance, if necessary
    if chance == 100:
        pass
    else:
        chance = chance * 10000  # in order to avoid using decimals
        cursor.execute('BEGIN TRANSACTION')
        for msa_id in range(1, number_of_entries + 1):
            random_number = random.randint(1, 10000)
            cursor.execute(f'UPDATE "{number_of_entries}" SET "chance_to_happen" = {random_number}' \
                                   f' WHERE (msa_id = {msa_id});')
        cursor.execute('COMMIT')
    pass


    start_string = f'UPDATE "{map_name}" SET "veg_com" = "{veg_com}" WHERE '
    #create conditional update string
    string_condition_prev_veg_com = ''
    if rule_type == '(Re)place':
        # Implement limitation previous veg_com
        if dict_nest_rule[rule][8]:  # Check if all veg coms was checked
            string_condition_prev_veg_com = ''
        elif dict_nest_rule[rule][9][0] == 'Empty':
            string_condition_prev_veg_com = '"veg_com" = "Empty" AND '
        else:
            for prev_veg_com in list_of_prev_vegcom:
                string_condition_prev_veg_com = string_condition_prev_veg_com+f'"veg_com" = "{prev_veg_com}" AND '
    elif rule_type == 'Encroach':
        # Get n_of_points and calculate the distance within which the encroachable points must be. Should be very clear in the manual what is included per encroach!
        n_of_points = dict_nest_rule[rule][5]
        encroachable_distance = n_of_points * spacing
        # Select the points that are next to the chosen veg com. Requires creating a temporary table that has all the entries from the veg_com to encroach,
        # as otherwise the table will update while running and increase the number of points while running, which changes the entire map to the encroaching veg_com.
        string_create_temp_table = f'CREATE TEMPORARY TABLE temp AS SELECT * FROM "{map_name}" WHERE veg_com = "{veg_com}"'
        cursor.execute(string_create_temp_table)
        string_condition_prev_veg_com = f'"veg_com" <> "{veg_com}" AND EXISTS ' \
                                        f'(SELECT 1 FROM "temp" WHERE ' \
                                        f'"{map_name}".geom_x BETWEEN temp.geom_x - {str(encroachable_distance)} ' \
                                        f'AND temp.geom_x + {str(encroachable_distance)} AND' \
                                        f'"{map_name}".geom_y BETWEEN temp.geom_y - {str(encroachable_distance)} ' \
                                        f'AND temp.geom_y + {str(encroachable_distance)}) AND'
    elif rule_type == 'Adjacent':  # TODO needs significant changes to the UI. Postpone as a workaround by creating buffer maps in QGIS is possible.
        return
    elif rule_type == 'Extent':  # TODO needs significant changes to the UI. Postpone as a workaround by drawing the extent in QGIS is possible.
        return

    string_chance = f'("chance_to_happen" >= "{str(chance)}") AND '

    # Find the conditions that apply to the same column, add them to a dict by column name
    dict_env_var = {}
    for key in dict_nest_rule[rule][10]:
        if key == 'Empty':
            dict_env_var['Empty'] = [None]

        elif isinstance(dict_nest_rule[rule][10][key][0], str):  # categorical constraint
            # Get the column name
            list_split_name_ui_env_var = split(' - ', key)
            env_var = list_split_name_ui_env_var[1]
            env_var_layer = list_split_name_ui_env_var[0]
            if env_var[:5] == 'Band ':
                associated_column_name = env_var_layer[0:8] + env_var[5]
            else:
                associated_column_name = env_var[0:10]
            # Check if dict entry for column name exists
            if associated_column_name in dict_env_var:
                dict_env_var[associated_column_name].append(dict_nest_rule[rule][10][key])
            else:
                dict_env_var[associated_column_name] = [dict_nest_rule[rule][10][key]]

        else:  # Range constraint
            # Get the column name
            list_split_name_ui_env_var = split(' - ', key)
            env_var = list_split_name_ui_env_var[1]
            env_var_layer = list_split_name_ui_env_var[0]
            if env_var[:5] == 'Band ':
                associated_column_name = env_var_layer[0:8] + env_var[5]
            else:
                associated_column_name = env_var[0:10]
            # Check if dict entry for column name exists
            if associated_column_name in dict_env_var:
                dict_env_var[associated_column_name].append(dict_nest_rule[rule][10][key][0])
                dict_env_var[associated_column_name].append(dict_nest_rule[rule][10][key][1])
            else:
                dict_env_var[associated_column_name] = [dict_nest_rule[rule][10][key][0],
                                                        dict_nest_rule[rule][10][key][1]]

    # Create the conditional update string(take into account that having multiple of the same env_var need to be treated as OR not AND
    string_condition_env_var = ''
    for key in dict_env_var:
        if len(dict_env_var[key]) == 1:
            if key == 'Empty':
                break  # Leaves string_condition_env_var empty
            else:  # Column with 1 category to select for
                string_condition_env_var = f'{string_condition_env_var}("{key}" = "{dict_env_var[key][0]}") AND '
        else:
            if isinstance(dict_env_var[key][0], str):  # Column with multiple categories to select for
                string_to_insert = f'("{key}" = "'
                for entry in dict_env_var[key]:
                    string_to_insert = f'{string_to_insert}{entry}" OR "'
                string_to_insert = string_to_insert + '") AND '
                string_condition_env_var = string_condition_env_var + string_to_insert
            elif len(dict_env_var[key]) == 2:  # Column with a single range to select between
                string_condition_env_var = f'{string_condition_env_var}("{key}" BETWEEN {str(dict_env_var[key][0])} ' \
                                                                      f'AND {str(dict_env_var[key][1])}) AND '
            else:  # Column with multiple ranges to select between
                string_to_insert = '("'
                for index in range(len(dict_env_var[key]), 2):
                    string_to_insert = f'{string_to_insert}{key}" BETWEEN {str(dict_env_var[key][index])} AND ' \
                                                          f'{str(dict_env_var[key][index + 1])} OR "'

                string_to_insert = string_to_insert[:-4] + ') AND'
                string_condition_env_var = string_condition_env_var + string_to_insert

    string_condition_env_var = string_condition_env_var
    string_condition_rule = start_string + string_condition_prev_veg_com + string_chance + string_condition_env_var
    string_condition_rule = string_condition_rule[:-4] + ';'
    cursor.execute(string_condition_rule)
    conn.commit()

    # If the enroach rule was run, the temp table needs to be dropped
    cursor.execute('DROP TABLE IF EXISTS "temp";')

    # Temporarily create csv to check if correct
    cursor.execute(f'select * from "{map_name}"')
    with open (save_directory+ '//' + map_name + '_test.csv', 'w', newline = '') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow([i[0] for i in cursor.description])
        csv_writer.writerows(cursor)
    print(f"{time.time()} assigning vegcom for {map_name} with {rule} took {vegcom_start_time-time.time()}")


##Main code

#check if save input is correct. If not will automatically error and quit
save_directory, from_basemap, run_type, number_of_iters, spacing = checkInput()
#Open pickled files
dict_nest_rule, dict_rule_tree = loadFiles(save_directory)

# Create the basemap if necessary
if from_basemap == "0": #No basemap has been made yet, make basemap.
    if run_type == "2" or run_type == "3": #Create the basemap, save basemap, then quit
        conn = copySqlitetoMem(save_directory) #Make sqlite connection and copy to memory
        cursor = conn.cursor()
        makeBasemap(conn, cursor, dict_rule_tree,dict_nest_rule, spacing)

        if run_type == "2":
            #basemap is saved as part of makeBasemap, quit
            pass
        else:
            #continue with full MSA
            pass
        pass
    else: # Some error occurred in setting up the run, this code should not be reached
        sys.exit(f"Error in subprocess, run_type is incorrect for full run or basemap run, \n run_type = {run_type}")

    pass
else: #A basemap exists
    if run_type == "2":
        sys.exit(f"Error in subprocess, run_type is make basemap, but a basemap already exists. Quitting run")
    elif run_type == "3":
        pass
        #load basemap and run full MSA
    else:
        sys.exit(f"Error in subprocess, run_type is incorrect for full run, \n run_type = {run_type}")



# Run the multiple runs.
with concurrent.futures.ProcessPoolExecutor() as executor:
    for iter in number_of_iters:
        pass

#vacuum at the end
cursor.execute(f'VACUUM INTO "{save_directory}//temp_file_sql_output.sqlite";')
conn.commit()

try:
    conn.close()
except:
    #connection already closed, do nothing
    pass
