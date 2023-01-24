import sys
import time
from os.path import exists, isdir
import sqlite3
import pickle
import concurrent.futures


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
            number_of_iters = line


    return save_directory, from_basemap, run_type, number_of_iters

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
    :type save_directory: str"""

    source = sqlite3.connect(save_directory+"//temp_file_sql_input.sqlite")
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

def makeBasemap(conn, cursor, dict_rule_tree, dict_nest_rule):
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
    for key in dict_rule_tree:
        print(f"basegroup is {dict_rule_tree[key][4]}") #test
    list_base_group_ids.sort()
    for item in list_base_group_ids:
        print(f"rule name is {dict_rule_tree[item][3]}") #test
        assignVegCom(dict_nest_rule, conn, cursor, "basemap", dict_rule_tree[item][3]) #3 is rule name
    #save a temp basemap sql file if necessary
    cursor.execute(f'VACUUM INTO "{save_directory}//temp_file_basemap.sqlite";')
    conn.commit()


def assignVegCom(dict_nest_rule, conn, cursor, map_name, rule):
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

    print(f"assigning veg_com for {map_name} using rule {rule} at {time.time()} in subprocess")
    pass




##Main code

#check if save input is correct. If not will automatically error and quit
save_directory, from_basemap, run_type, number_of_iters= checkInput()
print("save directory", save_directory)
print("from_basemap", from_basemap)
print("run_type", run_type)
print("number of iters ", number_of_iters)
#Open pickled files
dict_nest_rule, dict_rule_tree = loadFiles(save_directory)
for key in dict_nest_rule:
    print("dict of nested rules ", key )
for key in dict_rule_tree:
    print("dict rule tree ", key)

# Create the basemap if necessary
if from_basemap == "0": #No basemap has been made yet, make basemap.
    if run_type == "2" or run_type == "3": #Create the basemap, save basemap, then quit
        conn = copySqlitetoMem(save_directory) #Make sqlite connection and copy to memory
        cursor = conn.cursor()

        if run_type == "2":
            #save basemap,then quit
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
