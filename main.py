import argparse
import psycopg2
import tensorflow as tf
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import csv
import os

# Make NumPy printouts easier to read.
np.set_printoptions(precision=3, suppress=True)


def sql_enitity_states(entity):
    return (f"SELECT s.state, s.last_updated_ts from states s JOIN states_meta es ON es.metadata_id = s.metadata_id "
            f"WHERE es.entity_id LIKE '{entity}' AND s.state not like 'unavailable';")


def sql_enitity_states_with_start_stop(entity, start, end):
    return (f"SELECT s.state, s.last_updated_ts from states s JOIN states_meta es ON es.metadata_id = s.metadata_id "
            f"WHERE es.entity_id LIKE '{entity}' AND s.state not like 'unavailable' AND s.last_updated_ts >= "
            f"{start} AND s.last_updated_ts <= {end};")


# Converts a unix timestamp into a date-time object
def convert_timestamp_to_datetime(timestamp):
    return datetime.utcfromtimestamp(float(timestamp))


# Sort array to have the events in the right order
def sort_events(unsorted):
    return sorted(unsorted, key=lambda x: x[1])


# This method is cleaning the data, it could replace on off with numbers and is splitting this multidimensional array
# into two single ones
def clean_data(array):
    # sort array
    sorted_array = np.array(sort_events(array))
    # states
    states_only = sorted_array[:, 0]
    # Time of change
    timestamps = sorted_array[:, 1]

    # Replace strings with numbers using list comprehension
    # Could also add here more for other states like "pause"
    string_to_number_mapping = {"off": 0, "on": 1}
    if states_only[0] in {'on', 'off'}:
        state_replaced = [string_to_number_mapping[item] for item in states_only]
    else:
        state_replaced = states_only
    # Replace unix timestamp with date_time object
    date_times = [convert_timestamp_to_datetime(timestamp) for timestamp in timestamps]
    return date_times, state_replaced


def write_into_csv(data):
    # Name of CSV-File
    csvfile = "learningdata.csv"

    if os.path.exists(csvfile):
        os.remove(csvfile)
        print(f'The existing CSV-File {csvfile} is deleted now.')

    for f in data:
        # CSV-Datei zum Schreiben öffnen
        with open(csvfile, mode='w', newline='') as file:
            # CSV-Writer erstellen
            schreiber = csv.writer(file, delimiter=';')

            # Daten in die CSV-Datei schreiben
            schreiber.writerows(data)


def generate_list_of_all_states_and_display(database, host, user, password, port, start, end, entities):
    # Specify the format of the date string
    date_format = "%Y-%m-%d-%H:%M:%S"

    list_all_states = []
    counter = -1

    conn = psycopg2.connect(database=database, host=host, user=user, password=password, port=port)
    cur = conn.cursor()
    print(conn)

    plt.figure(figsize=(10, 6))

    for e in entities:
        counter = counter + 1
        if args.start is not None and args.end is not None:
            cur.execute(sql_enitity_states_with_start_stop(e, datetime.strptime(start, date_format).timestamp(),
                                                           datetime.strptime(end, date_format).timestamp()))
        else:
            cur.execute(sql_enitity_states(e))
        states = cur.fetchall()
        result_array1, result_array2 = clean_data(states)
        list_all_states.append(result_array1)
        list_all_states.append(result_array2)

        # Plot the time series
        plt.plot(result_array1, result_array2, markersize=5, marker='o', linestyle='-', linewidth=1,
                 label=args.entities[counter])
        print(f"For the entity{args.entities[counter]} we found {len(result_array1)} valid datapoints")
    # Add labels and title
    plt.xlabel('Date')
    plt.ylabel('State')
    plt.title('Time Series')
    plt.legend()

    # Display the plot
    plt.grid(True)
    plt.show()
    conn.close()
    return list_all_states


def find_latest_value(key, position):
    latest_next = all_states[position][0]
    for index_next, time_next in enumerate(all_states[position-1]):
        if time_next > key:
            if index_next - 1 >= 0:
                latest_next = all_states[position][index_next - 1]
            break
        if index_next == len(all_states[position-1]) - 1:
            latest_next = all_states[position][index_next]
    return latest_next


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Personal information')
    parser.add_argument('--database', dest='database', type=str, help='Database name of DB to analyze')
    parser.add_argument('--host', dest='host', type=str, help='The database host')
    parser.add_argument('--user', dest='user', type=str, help='The database user')
    parser.add_argument('--pass', dest='pwd', type=str, help='The database password')
    parser.add_argument('--port', dest='port', type=int, help='The database port')
    parser.add_argument('--start', dest='start', type=str, help='Defines the start time of the data in the format '
                                                                '%Y-%m-%d %H:%M:%S')
    parser.add_argument('--end', dest='end', type=str, help='Defines the end time of the data in the format '
                                                            '%Y-%m-%d %H:%M:%S')
    parser.add_argument('--entities', dest='entities', nargs="+", type=str,
                        help='List of entities which should be used as trainings data')

    args = parser.parse_args()
    print("TensorFlow version:", tf.__version__)

    all_states = generate_list_of_all_states_and_display(args.database, args.host, args.user, args.pwd, args.port,
                                                         args.start, args.end, args.entities)
    print(all_states)
    allFeatures = []
    feature = []
    index2 = 3
    for index, time_key in enumerate(all_states[0]):
        feature.append(all_states[1][index])
        while index2 <= len(all_states)-1:
            f = find_latest_value(time_key, index2)
            index2 += 2
            feature.append(f)
        allFeatures.append(feature.copy())
        feature.clear()
        index2 = 3
    write_into_csv(allFeatures)
