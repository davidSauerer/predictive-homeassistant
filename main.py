import argparse
import psycopg2
import tensorflow as tf
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

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
    string_to_number_mapping = {"off": 0, "on": 1}
    if states_only[0] in {'on', 'off'}:
        state_replaced = [string_to_number_mapping[item] for item in states_only]
    else:
        state_replaced = states_only
    # Replace unix timestamp with date_time object
    date_times = [convert_timestamp_to_datetime(timestamp) for timestamp in timestamps]
    return date_times, state_replaced


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Personal information')
    parser.add_argument('--name', dest='name', type=str, help='Database name of DB to analyze')
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

    conn = psycopg2.connect(database=args.name,
                            host=args.host,
                            user=args.user,
                            password=args.pwd,
                            port=args.port,
                            )

    # Specify the format of the date string
    date_format = "%Y-%m-%d-%H:%M:%S"

    print(conn)
    print("TensorFlow version:", tf.__version__)

    plt.figure(figsize=(10, 6))

    cur = conn.cursor()
    counter = -1
    for e in args.entities:
        counter = counter + 1
        if args.start is not None and args.end is not None:
            cur.execute(sql_enitity_states_with_start_stop(e, datetime.strptime(args.start, date_format).timestamp(),
                                                           datetime.strptime(args.end, date_format).timestamp()))
        else:
            cur.execute(sql_enitity_states(e))
        states = cur.fetchall()
        result_array1, result_array2 = clean_data(states)
        # Plot the time series
        plt.plot(result_array1, result_array2, markersize=1, marker='o', linestyle='-', linewidth=1,
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
