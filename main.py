import argparse
import psycopg2

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

    cur = conn.cursor()
    cur.execute("SELECT es.entity_id, s.state, s.last_updated_ts from states s JOIN states_meta es ON es.metadata_id = s.metadata_id WHERE es.entity_id LIKE 'input_boolean.sleeping';")
    rows = cur.fetchall()
    for row in rows:
        print("State = ", row[1], "Updated", row[2])

    conn.close()