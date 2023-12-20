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
    print('Connect to ' + args.name)

    conn = psycopg2.connect(database=args.name,
                            host=args.host,
                            user=args.user,
                            password=args.pwd,
                            port=args.port)
