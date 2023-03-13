import sys
import time
import sqlite3
from os.path import exists, isdir
from pickle import load
from multiprocessing import Process
from random import randint
from re import split
import csv
from math import sqrt
from numpy import random

def SqlSqrt(real_number): # TODO this function is also in MSA_QGIS_custom_sql_methods.py, but I cannot import it here.
    """Used to import the numpy sqrt function to sqlite.

    :param real_number: The number of which the square root will be calculated.
    :type real_number: float"""
    return sqrt(real_number)

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
            spacing = line[:-1]
            count += 1
        elif count == 6:
            windrose = line[:-1]
            count+=1
        elif count == 7:
            likelihood_threshold = line[:-1]
            count += 1
        elif count == 8:
            cumulative_likelihood_threshold = line[:-1]
            count+=1
        elif count == 9:
            fit_formula = line[:-1]
            count +=1
        elif count == 10:
            keep_fitted = line[:-1]
            count +=1
        elif count == 11:
            keep_two = line[:-1]
            count +=1
        elif count == 12:
            number_of_entries = int(line[:-1])
            count +=1
        elif count == 13:
            nested = line[:-1]
            count +=1
        elif count == 14:
            n_of_sites = int(line[:-1])
            count +=1
        elif count == 15:
            n_of_taxa = int(line[:-1])
            count +=1
        else:
            n_of_vegcom = int(line)




    return save_directory, from_basemap, run_type, number_of_iters, spacing, windrose, [likelihood_threshold, cumulative_likelihood_threshold, fit_formula, keep_fitted, keep_two], number_of_entries, nested, n_of_sites, n_of_taxa, n_of_vegcom

def loadFiles(save_directory):
    """Loads the files required for running the MSA.

    :param save_directory: URL location of the SQlite file containing the point sampled vector point layer
    as created in MSA_QGIS.py
    :type save_directory: str"""
    with open(save_directory+"/temp_save_rule_dict.pkl", 'rb') as pkl_file:
        dict_nest_rule = load(pkl_file)

    with open(save_directory + "/temp_save_ruletree_dict.pkl", 'rb') as pkl_file:
        dict_rule_tree = load(pkl_file)

    return dict_nest_rule, dict_rule_tree

def copySqlitetoMem(save_directory, file):
    """Copies the temp file made for communicating with MSA_QGIS.py to an in-memory database.

    :param save_directory: URL location of the SQlite file containing the point sampled vector point layer
    as created in MSA_QGIS.py
    :type save_directory: str

    :return: Sqlite connection in memory that contains the set of tables built in MSA_QGIS.py
    """

    source = sqlite3.connect(save_directory+file)
    #TODO check for existence of required tables
    conn = sqlite3.connect(":memory:")
    source.backup(conn)
    source.close()
    return conn

def prepareMSA(dict_rule_tree):

    """ Writes a dict based on dict_rule_tree that is keyed by scenario, with a list of all previous rules and itself.
    The dict is ordered by key. List associated with containsL
    [0]: start_point (str)
    [1]: is_final_rule (bool)
    [2]: run_list (list)

    :param dict_rule_tree: Simplefied version of the dictionary of the order the user has given to complete rules
    :type dict_rule_tree: dict"""

    # remove all of the basegroup rules
    list_base_group_ids = [key for key in dict_rule_tree if dict_rule_tree[key][4]] #4 is isBaseGroup bool
    list_branch_points_ids = [key for key in dict_rule_tree if len(dict_rule_tree[key][0])>1]
    # identify final rules, make a dict with final rules as keys and all prev rules, minus those of basegroup, as list
    for item in list_base_group_ids:
        dict_rule_tree.pop(item)
    start_point = "basemap"
    scenario_dict = {}
    for key in dict_rule_tree:
        if len(dict_rule_tree[key][0]) > 1: #is branch point
            is_final_rule = False
            list_possible_start_points = []
            for entry in dict_rule_tree[key][1]:
                if entry in list_branch_points_ids:
                    list_possible_start_points.append(int(entry))
            if list_possible_start_points != []:
                start_point = max(list_possible_start_points)
                run_list = [item for item in dict_rule_tree[key][1] if
                            item not in list_base_group_ids and int(item) > start_point]
            else:
                run_list = [item for item in dict_rule_tree[key][1] if
                            item not in list_base_group_ids]
            run_list.append(key)
            scenario_dict[key] = [str(start_point),is_final_rule, run_list]

        if dict_rule_tree[key][0] == []: #is final rule
            is_final_rule = True
            list_possible_start_points = []
            if list_branch_points_ids == []:
                run_list = [item for item in dict_rule_tree[key][1] if item not in list_base_group_ids]
                run_list.append(key)
            else:
                for entry in dict_rule_tree[key][1]:
                    if entry in list_branch_points_ids:
                        list_possible_start_points.append(int(entry))
                start_point = max(list_possible_start_points)
                run_list = [item for item in dict_rule_tree[key][1] if item not in list_base_group_ids and int(item) > start_point]
                run_list.append(key)
            scenario_dict[key] = [str(start_point),is_final_rule, run_list]
    #sort the dictionary by key
    scenario_dict= dict(sorted(scenario_dict.items()))

    return scenario_dict

def setupMSA(dict_rule_tree, dict_nest_rule, spacing, save_directory, file_name,windrose, fit_stats,number_of_entries, nested,n_of_sites, n_of_taxa, n_of_vegcom, run_type):
    """ Sets up the multiprocessing environment for the various iterations of the MSA.

    :param spacing: resolution of the vector point grid
    :type spacing: int

    :param save_directory: URL location of the location where temp files and output files are stored.
    :type save_directory: str

    :param dict_nest_rule: nested dictionary of rules given by user
    :type dict_nest_rule: dict

    :param dict_rule_tree: nested, simplefied dictionary derived from rule tree widgets given by user
    :type dict_rule_tree: dict

    :param file_name: file name and extension of the file that contains either the basemap or point-sampled map, (depending on which exists)
    :type file_name: str"""
    # Create an output file
    output_conn = sqlite3.connect(save_directory + "//MSA_output.sqlite")
    conn = sqlite3.connect(save_directory + file_name)
    conn.backup(output_conn)
    conn.close()
    output_conn.close()

    # Run the multiple runs.
    scenario_dict = prepareMSA(dict_rule_tree)
    process_list = []
    for iteration in range(1, int(number_of_iters) + 1):
        process = Process(target=runMSA,
                          args=(
                              iteration, spacing, scenario_dict, save_directory,
                              dict_nest_rule,
                              dict_rule_tree, file_name, windrose, fit_stats,number_of_entries, nested,n_of_sites,
                              n_of_taxa, n_of_vegcom, run_type))
        process_list.append(process)

    for process in process_list:
        process.start()

    for process in process_list:
        process.join()

    # Save important tables
    output_conn = sqlite3.connect(save_directory + "//MSA_output.sqlite")
    cursor = output_conn.cursor()
    cursor.execute(f'SELECT * FROM "simulated_pollen"')
    with open(f'{save_directory}//simulated_pollen_output.csv', 'w', newline='') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow([i[0] for i in cursor.description])
        csv_writer.writerows(cursor)
    cursor.execute(f'SELECT * FROM "maps"')
    with open(f'{save_directory}//simulated_likelihood_and_landscape.csv', 'w', newline='') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow([i[0] for i in cursor.description])
        csv_writer.writerows(cursor)
    output_conn.close()


def runMSA(iteration, spacing, scenario_dict,save_directory,dict_nest_rule, dict_rule_tree, file,windrose, fit_stats,number_of_entries, nested,n_of_sites, n_of_taxa, n_of_vegcom, run_type):
    """ This is where rules are initiated in order of the rule tree. It is a single iteration of the MSA. Can be
    multiprocessed.

    :param iter: iteration being run
    :type iter: int

    :param spacing: resolution of the vector point grid
    :type spacing: int

    :param scenario_dict: sorted dictionary of ruletreewidget ids to be processed
    :type scenario_dict: dict

    :param save_directory: URL location of the location where temp files and output files are stored.
    :type save_directory: str

    :param dict_nest_rule: nested dictionary of rules given by user
    :type dict_nest_rule: dict

    :param dict_rule_tree: nested, simplefied dictionary derived from rule tree widgets given by user
    :type dict_rule_tree: dict """
    retries = 100 # number of times the connection will retry to save the table to file.
    # Open a connection to the basemap to copy everything.
    try:
        conn = copySqlitetoMem(save_directory,file)
    except Exception as e:
        error_statement = f"{e}\nFor run {iteration}"
        print(error_statement, flush = True)
        return error_statement
    cursor = conn.cursor()
    for key in scenario_dict:
        map_name = f"{key}_{iteration}"
        if scenario_dict[key][0] == "basemap":
            start_point = scenario_dict[key][0]
        else:
            start_point = f'{scenario_dict[key][0]}_{iteration}'
        cursor.execute(f'CREATE TABLE "{map_name}" AS SELECT * FROM "{start_point}";')
        conn.commit()
        cursor.execute(f'CREATE INDEX "{map_name}_idx" ON "{map_name}"(msa_id);')
        conn.commit()
        print(f'{map_name} was created, start_point was {start_point}', flush=True)
        for item in scenario_dict[key][2]:
            assignVegCom(dict_nest_rule, conn, cursor, map_name, dict_rule_tree[item][3], spacing, number_of_entries)
        if scenario_dict[key][1]:
            if nested == True:
                cursor.execute(f'CREATE INDEX "{map_name}_idx_res" on "{map_name}"(resolution);')
            simulatePollen(map_name, iteration, conn,cursor, windrose, fit_stats, nested,n_of_sites, n_of_taxa, n_of_vegcom)
            if run_type == "3":
                calculateFit(map_name,n_of_sites, n_of_taxa, conn, cursor, iteration,fit_stats)

    #Save what needs to be saved
    cursor.execute(f"ATTACH DATABASE '{save_directory}/MSA_output.sqlite' as file_db")
    #Save all the simulated pollen
    for increment in range(retries):
        try:
            cursor.execute('BEGIN TRANSACTION')
            for row in range(n_of_sites):
                cursor.execute(f'SELECT site_name FROM "sampling_sites" WHERE rowid IS {row + 1}')
                site_name = cursor.fetchone()[0]
                insert_simulated_pollen = (f'INSERT INTO file_db.[simulated_pollen](map_id, site_name, ')
                for row2 in range(n_of_taxa):
                    cursor.execute(f'SELECT taxon_code FROM "taxa" WHERE rowid IS {row2 + 1}')
                    taxon = cursor.fetchone()[0]
                    # Add all columns of taxon percent
                    if row2 + 1 == n_of_taxa:
                        insert_simulated_pollen += f'sim_{taxon}_percent)'
                    else:
                        insert_simulated_pollen += f'sim_{taxon}_percent, '
                # Add all values
                insert_simulated_pollen += f'VALUES("{map_name}", "{site_name}", '
                for row2 in range(n_of_taxa):
                    cursor.execute(f'SELECT taxon_code FROM "taxa" WHERE rowid IS {row2 + 1}')
                    taxon = cursor.fetchone()[0]
                    if row2 + 1 == n_of_taxa:
                        insert_simulated_pollen += f'(SELECT sim_{taxon}_percent FROM simpol_{map_name}_{iteration} WHERE "site_name" = "{site_name}"))'
                    else:
                        insert_simulated_pollen += f'(SELECT sim_{taxon}_percent FROM simpol_{map_name}_{iteration} WHERE "site_name" = "{site_name}"),'
                cursor.execute(insert_simulated_pollen)
                cursor.execute('COMMIT')
            break
        except sqlite3.OperationalError:
            print("retry connection (simulated pollen)...", flush=True)
            time.sleep(increment)

    if fit_stats[3] == 'True':
        # Only save maps that made fit
        cursor.execute(f'SELECT map_id FROM maps WHERE (likelihood_met = "Yes")')
        maps_to_save = cursor.fetchall()
    elif fit_stats[4] == 'True':
        # Keep all maps
        cursor.execute(f'SELECT map_id FROM maps')
        maps_to_save = cursor.fetchall()
    else:
        #Keep maps and also save loadings
        cursor.execute(f'SELECT map_id FROM maps')
        maps_to_save = cursor.fetchall()
        cursor.execute(f'SELECT site_name FROM "sampling_sites"')
        sampling_sites = cursor.fetchall()
        for map in maps_to_save:
            for site in sampling_sites:
                for increment in range(retries):
                    try:
                        cursor.execute(f'CREATE TABLE file_db.[{site[0]}{map[0]}] AS SELECT * FROM [{site[0]}{map[0]}]')
                        break
                    except sqlite3.OperationalError: # TODO needs to catch only database locked
                        print("retry connection 3...", flush=True)
                        time.sleep(increment)
                conn.commit()
    for map in maps_to_save:
        for increment in range(retries):
            try:
                cursor.execute(f"CREATE TABLE file_db.[{map[0]}] AS SELECT * FROM [{map[0]}]")
                break
            except sqlite3.OperationalError: # TODO needs to catch only database locked
                print("retry connection 2...", flush=True)
                time.sleep(increment)
        conn.commit()
        cursor.execute(f'SELECT * FROM "{map[0]}"')
        with open(f'{save_directory}//{map[0]}.csv', 'w', newline='') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow([i[0] for i in cursor.description])
            csv_writer.writerows(cursor)
    for increment in range(retries):
        try:
            cursor.execute(f'INSERT INTO file_db.[maps] SELECT * FROM [maps]')
            conn.commit()
            break
        except Exception as e: # TODO needs to catch only database locked
            print(f"retry connection 1 for {map_name}...\n{e}", flush=True)
            cursor.execute(f"DETACH DATABASE file_db")
            conn.commit()
            time.sleep(increment)
            cursor.execute(f"ATTACH DATABASE '{save_directory}/MSA_output.sqlite' as file_db")
            conn.commit()


    cursor.execute(f"DETACH DATABASE file_db")
    conn.commit()
    conn.close()


def makeBasemap(conn, cursor, dict_rule_tree, dict_nest_rule,spacing, save_directory, number_of_entries):
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
        assignVegCom(dict_nest_rule, conn, cursor, "basemap", dict_rule_tree[item][3], spacing, number_of_entries) #3 is rule name
    #save a file with the basemap
    cursor.execute(f'VACUUM INTO "{save_directory}//output_basemap.sqlite";')
    conn.commit()

def assignVegCom(dict_nest_rule, conn, cursor, map_name, rule, spacing, number_of_entries):
    """ Edits veg_com in the SQLite database version of the map based on a single given rule.

    :param conn: sqlite3 memory connection
    :type conn: sqlite3.Connection

    :param cursor: sqlite3 cursor of the connection above
    :type cursor: sqlite3.Cursor

    :param map_name: name of the sqlite3 table that will be edited
    :type map_name: str or int

    :param rule: rule number that corresponds to a key in dict_nest_rule and determines which rule will be
    used to change veg_com.
    :type rule: str or int
    """
    vegcom_start_time = time.time()
    print(f"{vegcom_start_time}: Assigning veg_com for {map_name} using rule {rule}", flush = True)

    veg_com = dict_nest_rule[rule][2]
    rule_type = dict_nest_rule[rule][3]
    list_of_prev_vegcom = dict_nest_rule[rule][9]
    chance = dict_nest_rule[rule][4]

    save_time = time.time()

    if chance == 100 or chance == 100.0:
        string_chance = ''
    else:
        cursor.execute(f'UPDATE "{map_name}" SET "chance_to_happen" = 0')
        conn.commit()
        string_chance = f'("chance_to_happen" = "1") AND '
        chance *=100 # to make compatible with integers despite 2 decimals
        timer = time.time()
        random_numbers = random.randint(1, 10000, size=number_of_entries)
        #print(f'generating {time.time()-timer}')
        timer = time.time()
        tuple_ids_above_chance = tuple([msa_id+1 for msa_id in range(number_of_entries) if random_numbers.item(msa_id) <chance])
        if tuple_ids_above_chance == (): # None of the random numbers were above chance, so the rule does not happen
            print(f'Random chance application resulted in no assigned points for rule {rule}, with {veg_com} '
                  f'for map {map_name}. Rule ignored')
            print(f"assigning vegcom for {map_name} with {rule} took {time.time() - vegcom_start_time}", flush=True)
            return
        if len(tuple_ids_above_chance) ==1:
            cursor.execute(f'UPDATE "{map_name}" SET "chance_to_happen" = 1 WHERE (msa_id == {tuple_ids_above_chance[0]})')
        else:
            cursor.execute(f'UPDATE "{map_name}" SET "chance_to_happen" = 1 WHERE (msa_id IN {tuple_ids_above_chance})')
        conn.commit()
        #print(f'applying {time.time()-timer}')

    #print(f'chance time {map_name} took {time.time()-save_time} to run', flush=True)
    save_time = time.time()

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
                string_condition_prev_veg_com +=f'"veg_com" = "{prev_veg_com}" AND '
    elif rule_type == 'Encroach':
        # Get n_of_points and calculate the distance within which the encroachable points must be. Should be very clear in the manual what is included per encroach!
        encroachable_distance = dict_nest_rule[rule][5]
        # Select the points that are next to the chosen veg com. Requires creating a temporary table that has all the entries from the veg_com to encroach,
        # as otherwise the table will update while running and increase the number of points while running, which changes the entire map to the encroaching veg_com.
        string_create_temp_table = f'CREATE TEMPORARY TABLE temp AS SELECT * FROM "{map_name}" WHERE veg_com = "{veg_com}"'
        cursor.execute(string_create_temp_table)
        string_condition_prev_veg_com = f'"veg_com" <> "{veg_com}" AND EXISTS ' \
                                        f'(SELECT 1 FROM "temp" WHERE ' \
                                        f'"{map_name}".geom_x BETWEEN temp.geom_x - {encroachable_distance} ' \
                                        f'AND temp.geom_x + {encroachable_distance} AND' \
                                        f'"{map_name}".geom_y BETWEEN temp.geom_y - {encroachable_distance} ' \
                                        f'AND temp.geom_y + {encroachable_distance}) AND'
    elif rule_type == 'Adjacent':  # TODO needs significant changes to the UI. Postpone as a workaround by creating buffer maps in QGIS is possible.
        return
    elif rule_type == 'Extent':  # TODO needs significant changes to the UI. Postpone as a workaround by drawing the extent in QGIS is possible.
        return
    #print(f'rule type {map_name} took {time.time()-save_time} to run', flush=True)
    save_time = time.time()
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

    #print(f'condition dict {map_name} took {time.time()-save_time} to run', flush=True)
    save_time = time.time()
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
                string_to_insert +='") AND '
                string_condition_env_var +=string_to_insert
            elif len(dict_env_var[key]) == 2:  # Column with a single range to select between

                string_condition_env_var += f'("{key}" BETWEEN {str(dict_env_var[key][0])} ' \
                                                                      f'AND {str(dict_env_var[key][1])}) AND '
            else:  # Column with multiple ranges to select between
                string_to_insert = '("'
                for index in range(len(dict_env_var[key]), 2):

                    string_to_insert += f'{key}" BETWEEN {str(dict_env_var[key][index])} AND ' \
                                                          f'{str(dict_env_var[key][index + 1])} OR "'

                string_to_insert = string_to_insert[:-4] + ') AND'
                string_condition_env_var += string_to_insert
    string_condition_rule = start_string + string_condition_prev_veg_com + string_chance + string_condition_env_var
    string_condition_rule = string_condition_rule[:-4] + ';'
    #print(f'condition string {map_name} took {time.time()-save_time} to run', flush=True)
    save_time = time.time()
    cursor.execute(string_condition_rule)
    conn.commit()
    #print(f'running rule {map_name} took {time.time()-save_time} to run', flush=True)

    # If the enroach rule was run, the temp table needs to be dropped
    cursor.execute('DROP TABLE IF EXISTS "temp";')
    print(f"assigning vegcom for {map_name} with {rule} took {time.time()-vegcom_start_time}", flush = True)

def simulatePollen(map_name,iteration, conn, cursor, windrose, fit_stats, nested,n_of_sites, n_of_taxa, n_of_vegcom):
    """Simulates the pollen per map, per site and determines whether the fit between the simulated pollen and actual
     pollen is close enough to retain the map if the user selected to retain only fitted maps.

     :class params: self.dlg

     :param output_map: Name of the map/SQlite table for which the pollen need to be simulated
     :type output_map: str

     :param iteration: Iteration being computed
     :type iteration: int

     :param conn: SQLite connection
     :type conn: SQLite connection

     :param cursor: SQLite cursor attached to the connection
     type cursor: SQLite cursor"""

    start_time = time.time()
    print(f"Simulation of pollen for {map_name} started", flush=True)
    time_polload = time.time()
    # Calculate the pollen loadings
    for row in range(n_of_sites):
        # Create a new table per site
        cursor.execute(f'SELECT site_name FROM "sampling_sites" WHERE rowid IS {row+1}')
        site_name = cursor.fetchone()[0]
        create_table_str = f'CREATE TABLE {site_name}{map_name}(msa_id INT, pseudo_id INT, '
        for row2 in range(n_of_taxa):
            cursor.execute(f'SELECT taxon_code FROM "taxa" WHERE rowid IS {row2+1}')
            taxon = cursor.fetchone()[0]
            if row2+1 == n_of_taxa:
                create_table_str = f'{create_table_str}{taxon}_PL REAL)'
            else:
                create_table_str = f'{create_table_str}{taxon}_PL REAL, '
        cursor.execute(create_table_str)
        conn.commit()
        #fill table
        cursor.execute('BEGIN TRANSACTION')
        cursor.execute(f'INSERT INTO {site_name}{map_name}(msa_id) '
                       f'SELECT "msa_id" FROM "dist_dir" WHERE ("site_name" = "{site_name}") AND ("distance" != 0)')
        cursor.execute(f'INSERT INTO {site_name}{map_name}(pseudo_id) '
                       f'SELECT "pseudo_id" FROM "pseudo_points" WHERE "site_name" = "{site_name}"')
        cursor.execute(f'UPDATE "{site_name}{map_name}" SET "msa_id" = '
                       f'(SELECT "msa_id" FROM "pseudo_points" WHERE "site_name" = "{site_name}") '
                       f'WHERE pseudo_id >= 0')
        cursor.execute('COMMIT')
        #calculate pollen load
        cursor.execute('BEGIN TRANSACTION')
        for row2 in range(n_of_taxa):  #FIXME: This part of the code is a speed bottleneck, but I don't see how it could be improved.
            cursor.execute(f'SELECT taxon_code FROM "taxa" WHERE rowid IS {row2+1}')
            taxon = cursor.fetchone()[0]
            if nested == "True":
                update_table_str = f'UPDATE {site_name}{map_name} SET "{taxon}_PL" = (SELECT(' \
                                   f'SELECT "RelPP" FROM taxa WHERE "taxon_code" = "{taxon}") * (' \
                                   f'SELECT "resolution" FROM "{map_name}" WHERE ("msa_id" = {site_name}{map_name}.msa_id)) * ('\
                                   f'SELECT "vegcom_percent" FROM vegcom WHERE "taxon_code" = "{taxon}" ' \
                                   f'AND "veg_com" = (SELECT "veg_com" FROM "{map_name}" WHERE (' \
                                   f'msa_id = {site_name}{map_name}.msa_id))) * (' \
                                   f'SELECT "{taxon}_DW" FROM PollenLookup WHERE PollenLookup.distance = (' \
                                   f'SELECT "distance" FROM dist_dir WHERE (msa_id = {site_name}{map_name}.msa_id) ' \
                                   f'AND (site_name = "{site_name}"))) * (' \
                                   f'SELECT "distance" FROM dist_dir WHERE (msa_id = {site_name}{map_name}.msa_id) ' \
                                   f'AND (site_name = "{site_name}")'
            else:
                update_table_str = f'UPDATE {site_name}{map_name} SET "{taxon}_PL" = (SELECT(' \
                                   f'SELECT "RelPP" FROM taxa WHERE "taxon_code" = "{taxon}") * (' \
                                   f'SELECT "vegcom_percent" FROM vegcom WHERE "taxon_code" = "{taxon}" ' \
                                   f'AND "veg_com" = (SELECT "veg_com" FROM "{map_name}" WHERE (' \
                                   f'msa_id = {site_name}{map_name}.msa_id))) * (' \
                                   f'SELECT "{taxon}_DW" FROM PollenLookup WHERE PollenLookup.distance = (' \
                                   f'SELECT "distance" FROM dist_dir WHERE (msa_id = {site_name}{map_name}.msa_id) ' \
                                   f'AND (site_name = "{site_name}"))) * (' \
                                   f'SELECT "distance" FROM dist_dir WHERE (msa_id = {site_name}{map_name}.msa_id) ' \
                                   f'AND (site_name = "{site_name}")'
            if windrose == "True":
                find_windrose_str=(f') * ( SELECT "windrose_weight" FROM windrose WHERE('
                                   f'CASE WHEN {site_name}{map_name}.pseudo_id is NULL THEN "direction" = ('
                                   f'SELECT "direction" FROM dist_dir WHERE ((msa_id = {site_name}{map_name}.msa_id) AND ('
                                   f'site_name = "{site_name}"))) '
                                   f'ELSE "direction" = (SELECT "direction" FROM pseudo_points WHERE (pseudo_id = {site_name}{map_name}.pseudo_id)) END)))')
                update_table_str += find_windrose_str
            else:
                update_table_str += '))'
            cursor.execute(update_table_str)
        cursor.execute('COMMIT')
        # conn.commit()
        #Adjust pollen load by 0.25 for pseudopoints (which contain 0.25 of the area of a "normal" point)
        for row2 in range(n_of_taxa):
            cursor.execute(f'SELECT taxon_code FROM "taxa" WHERE rowid IS {row2+1}')
            taxon = cursor.fetchone()[0]
            cursor.execute(f'UPDATE {site_name}{map_name} SET {taxon}_PL = ('
                           f'SELECT "{taxon}_PL" * 0.25) WHERE pseudo_id IS NOT NULL')
        conn.commit()
    print(f'calculating pollen loadings for {map_name}took {time.time()-time_polload} to run', flush=True)

    # Create table for calculating pollen percentages
    create_table_str = f'CREATE TABLE simpol_{map_name}_{iteration}(site_name TEXT, '
    for row in range(n_of_taxa):
        cursor.execute(f'SELECT taxon_code FROM "taxa" WHERE rowid IS {row + 1}')
        taxon = cursor.fetchone()[0]
        if row+1 == n_of_taxa:
            create_table_str += f'sim_{taxon}_percent REAL)'
        else:
            create_table_str += f'sim_{taxon}_percent REAL,'
    cursor.execute(create_table_str)
    conn.commit()

    #calculate pollen percentages
    for row in range(n_of_sites):
        cursor.execute(f'SELECT site_name FROM "sampling_sites" WHERE rowid IS {row+1}')
        site_name = cursor.fetchone()[0]
        total_pollen_load_str = 'SELECT '
        for row2 in range(n_of_taxa):
            cursor.execute(f'SELECT taxon_code FROM "taxa" WHERE rowid IS {row2+1}')
            taxon = cursor.fetchone()[0]
            if row2+1 == n_of_taxa:
                total_pollen_load_str += f'(SELECT SUM({taxon}_PL) FROM {site_name}{map_name}) '
            else:
                total_pollen_load_str += f'(SELECT SUM({taxon}_PL) FROM {site_name}{map_name}) + '
        cursor.execute(total_pollen_load_str)
        total_pollen_load = cursor.fetchone()[0]

        insert_pollen_percent_str = f'INSERT INTO simpol_{map_name}_{iteration}(site_name, '
        for row2 in range(n_of_taxa):
            cursor.execute(f'SELECT taxon_code FROM "taxa" WHERE rowid IS {row2+1}')
            taxon = cursor.fetchone()[0]
            # Add all columns of taxon percent
            if row2+1 == n_of_taxa:
                insert_pollen_percent_str += f'sim_{taxon}_percent)'
            else:
                insert_pollen_percent_str += f'sim_{taxon}_percent,'
        # Add all values
        insert_pollen_percent_str += f' VALUES("{site_name}", '
        for row2 in range(n_of_taxa):
            cursor.execute(f'SELECT taxon_code FROM "taxa" WHERE rowid IS {row2+1}')
            taxon = cursor.fetchone()[0]
            if row2+1 == n_of_taxa:
                insert_pollen_percent_str += f'(SELECT ((SELECT SUM({taxon}_PL) FROM {site_name}{map_name})/' \
                                             f'{total_pollen_load}) * 100))'
            else:

                insert_pollen_percent_str += f'(SELECT ((SELECT SUM({taxon}_PL) FROM {site_name}{map_name})/' \
                                             f'{total_pollen_load}) * 100), '
        cursor.execute(insert_pollen_percent_str)
        conn.commit()
    # Insert map in to maps table
    cursor.execute(f'INSERT INTO maps(map_id, iteration, like_thres_sites, like_thres_cumul) '
                   f'VALUES("{map_name}", "{iteration}", "{fit_stats[0]}", "{fit_stats[1]}")')
    conn.commit()

    # Set percent vegcom per map
    for row in range(n_of_vegcom):
        cursor.execute(f'SELECT veg_com FROM "vegcom_list" WHERE rowid IS {row + 1}')
        veg_com = cursor.fetchone()[0]
        cursor.execute(
            f'UPDATE maps SET "percent_{veg_com}" = (SELECT (SELECT(SELECT COUNT(*) FROM "{map_name}" WHERE veg_com = "{veg_com}")*1.0)/' \
            f'(SELECT(SELECT COUNT(*) FROM "{map_name}")*1.0)* 100.0)')
    conn.commit()

    end_time_pol = time.time() - start_time
    print(f'calculating pollen percentages for {map_name} took {str(end_time_pol)} to run', flush=True)

def calculateFit(map_name,n_of_sites, n_of_taxa, conn, cursor, iteration, fit_stats):
    """When running a full MSA reconstruction, calculates the fit in comparison to the actual pollen."""
    start_time = time.time()
    conn.create_function("SQRT", 1, SqlSqrt)


    cumul_fit = 0
    # Fit calculation: squared chord distance
    like_thres_met = 'Yes'
    for row_sites in range(n_of_sites):
        cursor.execute(f'SELECT site_name FROM "sampling_sites" WHERE rowid IS {row_sites + 1}')
        site_name = cursor.fetchone()[0]
        if fit_stats[2] == 'Square Chord Distance':
            square_chord_str = 'SELECT '
            for row_taxa in range(n_of_taxa):
                cursor.execute(f'SELECT taxon_code FROM "taxa" WHERE rowid IS {row_taxa + 1}')
                taxon = cursor.fetchone()[0]
                cursor.execute(f'SELECT taxon_percentage FROM "{site_name}" WHERE taxon_code = "{taxon}"')
                real_taxon_total = cursor.fetchone()[0]
                cursor.execute(f'SELECT sim_{taxon}_percent FROM "simpol_{map_name}_{iteration}" WHERE site_name = "{site_name}"')
                sim_taxon_total = cursor.fetchone()[0]
                if row_taxa + 1 == n_of_taxa:
                    square_chord_str += f'(SELECT (SELECT SQRT({real_taxon_total})-SQRT({sim_taxon_total}))' \
                                        f'*(SELECT SQRT({real_taxon_total})-SQRT({sim_taxon_total})))'
                else:
                    square_chord_str += f'(SELECT (SELECT SQRT({real_taxon_total})-SQRT({sim_taxon_total}))' \
                                        f'*(SELECT SQRT({real_taxon_total})-SQRT({sim_taxon_total})))+'
            cursor.execute(square_chord_str)
            fit = cursor.fetchone()[0]
            update_table = f'UPDATE maps SET likelihood_{site_name} = {fit} WHERE map_id = "{map_name}"'
            try:
                cursor.execute(update_table)
                conn.commit()
            except Exception as e:
                print(f"Exception raised \n{e}", flush=True)
            # Add to cumulative fit (both for SQLite statement and for the log
            cumul_fit += fit
            # Determine whether likelihood threshold for site was met
            if like_thres_met == 'Yes' and fit > float(fit_stats[0]):
                like_thres_met = 'No'
            print(f"Fit for {map_name} site {site_name} is {fit}", flush=True)
    # Calculate cumulative fit
    cursor.execute(f'UPDATE maps SET "likelihood_cumul" = {cumul_fit} WHERE map_id = "{map_name}"')

    # Determine whether cumulative likelihood threshold was met
    if like_thres_met == 'Yes' and cumul_fit > float(fit_stats[1]):
        like_thres_met = 'No'
    # Set likelihood met
    cursor.execute(f'UPDATE maps SET likelihood_met = "{like_thres_met}" WHERE map_id = "{map_name}"')
    conn.commit()

    end_time_pol = time.time() - start_time
    print(f'Assigning fit for {map_name} took {str(end_time_pol)} to run', flush=True)


if __name__ == "__main__":
    ##Main code
    # check if save input is correct. If not will automatically error and quit
    save_directory, from_basemap, run_type, number_of_iters, spacing, windrose, fit_stats,number_of_entries, nested, n_of_sites, n_of_taxa, n_of_vegcom = checkInput()
    # Open pickled files
    dict_nest_rule, dict_rule_tree = loadFiles(save_directory)
    # Create the basemap if necessary
    if from_basemap == "0": #No basemap has been made
        list_is_base_group = []
        for key in dict_rule_tree:
            if dict_rule_tree[key][4]:
                list_is_base_group.append(dict_rule_tree[key][4])
        if list_is_base_group == []: #No entries were designated as basegroup
            if run_type == "1":
                sys.exit("Error in subprocess, run_type = 2 (make only basemap), but no entries in rule tree were designated as base group")
            else: #Carry on to do a full MSA, but start from point_sampled_map
                setupMSA(dict_rule_tree,dict_nest_rule, spacing,save_directory, "//temp_file_sql_input.sqlite", windrose, fit_stats,number_of_entries, nested, n_of_sites, n_of_taxa, n_of_vegcom, run_type)
        else: #some entries were designated as basegroup
             if run_type == "1" or run_type == "2" or run_type == "3":
                 # Create the basemap
                 conn = copySqlitetoMem(save_directory, "//temp_file_sql_input.sqlite") #Make sqlite connection and copy to memory
                 cursor = conn.cursor()
                 makeBasemap(conn, cursor, dict_rule_tree,dict_nest_rule, spacing, save_directory, number_of_entries)
                 try:
                     conn.close()
                 except:
                     pass
                 if run_type == "1":
                     #basemap is saved as part of makeBasemap, move on to end subprocess
                     pass
                 elif run_type == "2" or run_type == "3": #continue with full MSA
                     setupMSA(dict_rule_tree,dict_nest_rule, spacing,save_directory, "//output_basemap.sqlite", windrose, fit_stats, number_of_entries, nested,n_of_sites, n_of_taxa, n_of_vegcom,run_type)
             else: # Some error occurred in setting up the run, this code should not be reached
                 sys.exit(f"Error in subprocess, run_type is incorrect, \n run_type = {run_type}")
    else: #A basemap exists
        if run_type == "1":
            sys.exit(f"Error in subprocess, run_type is make basemap, but a basemap already exists. Quitting run")
        elif run_type == "2" or run_type == "3":
            setupMSA(dict_rule_tree,dict_nest_rule, spacing,save_directory, "//temp_file_sql_input.sqlite", windrose, fit_stats, number_of_entries, nested,n_of_sites, n_of_taxa, n_of_vegcom, run_type)
        else:
            sys.exit(f"Error in subprocess, run_type is incorrect for full run, \n run_type = {run_type}")


    try:
        conn.close()
    except:
        #connection already closed, do nothing
        pass
    print(f'end reached', flush=True)

