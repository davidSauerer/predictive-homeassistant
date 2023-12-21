import argparse
import psycopg2
import tensorflow as tf
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

# Make NumPy printouts easier to read.
np.set_printoptions(precision=3, suppress=True)


def sql_enitity_states(entity):
    return (f"SELECT s.state, s.last_updated_ts from states s JOIN states_meta es ON es.metadata_id = s.metadata_id "
            f"WHERE es.entity_id LIKE '{entity}';")

# Converts a unix timestamp into a date-time object
def convert_timestamp_to_datetime(timestamp):
    return datetime.utcfromtimestamp(float(timestamp))

# Sort array to have the events in the right order
def sort_events(unsorted):
    return sorted(unsorted, key=lambda x: x[1])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Personal information')
    parser.add_argument('--name', dest='name', type=str, help='Database name of DB to analyze')
    parser.add_argument('--host', dest='host', type=str, help='The database host')
    parser.add_argument('--user', dest='user', type=str, help='The database user')
    parser.add_argument('--pass', dest='pwd', type=str, help='The database password')
    parser.add_argument('--port', dest='port', type=int, help='The database port')

    args = parser.parse_args()

    conn = psycopg2.connect(database=args.name,
                            host=args.host,
                            user=args.user,
                            password=args.pwd,
                            port=args.port)
    print(conn)
    print("TensorFlow version:", tf.__version__)

    ##---gen trainings data

    cur = conn.cursor()
    cur.execute(sql_enitity_states("light.badschrabklampe"))
    light = cur.fetchall()

    cur.execute(sql_enitity_states("binary_sensor.badezimmer_motion"))
    motion = cur.fetchall()

    # sort array
    sorted_array = np.array(sort_events(motion))

    # Motion state
    motion_state = sorted_array[:, 0]
    # Time of change
    motion_time = sorted_array[:, 1]

    # Replace strings with numbers using list comprehension
    string_to_number_mapping = {"off": 0, "on": 1}
    motion_state_replaced = [string_to_number_mapping[item] for item in motion_state]
    # Replace unix timestamp with date_time object
    motion_time_date_time = [convert_timestamp_to_datetime(timestamp) for timestamp in motion_time]

    # Plot the time series
    plt.figure(figsize=(10, 6))
    plt.plot(motion_time_date_time, motion_state_replaced, marker='o', linestyle='-')

    # Add labels and title
    plt.xlabel('Date')
    plt.ylabel('Value')
    plt.title('Time Series Example')

    # Display the plot
    plt.grid(True)
    plt.show()

    conn.close()
