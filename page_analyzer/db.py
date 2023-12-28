import psycopg2
import requests
from page_analyzer import app
from page_analyzer.enums import Statuses
from page_analyzer.find_tags import find_tags
from psycopg2.extras import NamedTupleCursor


def connect_database():
    conn = psycopg2.connect(app.app.config['DATABASE_URL'])
    return conn


def insert_url(website_url):
    status = Statuses.SUCCESS
    conn = connect_database()
    try:
        conn.cursor().execute("INSERT INTO urls (name) "
                              "VALUES (%s)", (website_url,))
        conn.commit()
    except Exception:
        status = Statuses.NOT_SUCCESS
    conn = connect_database()
    with conn.cursor(cursor_factory=NamedTupleCursor) as cur:
        cur.execute(f"SELECT * FROM urls WHERE name='{website_url}'")
        result = cur.fetchone()
    conn.close()
    return {'id': result.id, 'status': status}


def get_all_urls():
    conn = connect_database()
    with conn.cursor(cursor_factory=NamedTupleCursor) as cur:
        cur.execute("SELECT urls.id, urls.name, url_checks.status_code, "
                    "MAX(url_checks.created_at) FROM urls "
                    "LEFT JOIN url_checks ON urls.id = url_checks.url_id "
                    "GROUP BY urls.id, url_checks.status_code "
                    "ORDER BY urls.id DESC;")
        result = cur.fetchall()
    conn.close()
    return result


def get_url_data_view(id):
    conn = connect_database()
    with conn.cursor(cursor_factory=NamedTupleCursor) as cur:
        cur.execute(f"SELECT * FROM urls WHERE id = {id};")
        website_data = cur.fetchone()
        cur.execute(f"SELECT * FROM url_checks "
                    f"WHERE url_id = {id} ORDER BY id DESC;")
        checks_website_data = cur.fetchall()
    conn.close()
    return website_data, checks_website_data

'''
def check_url_view(id):
    conn = connect_database()
    cur = conn.cursor(cursor_factory=NamedTupleCursor)
    cur.execute(f"SELECT * FROM urls WHERE id = {id}")
    result = cur.fetchone()
    url = result.name
    try:
        response = requests.get(url)
        status_code = response.status_code
        if status_code != 200:
            return Statuses.ERROR
        tags = find_tags(response)
        title = tags['title']
        h1 = tags['h1']
        description = tags['description']
        cur.execute("INSERT INTO url_checks (url_id, status_code, h1, "
                    "title, description) "
                    "VALUES (%s, %s, %s, %s, %s)",
                    (id, status_code, h1, title, description))
        conn.commit()
        cur.close()
        conn.close()
        return Statuses.SUCCESS
    except Exception:
        return Statuses.ERROR
'''    

def get_url_name(id):
    conn = connect_database()
    with conn.cursor(cursor_factory=NamedTupleCursor) as cur:
        cur.execute(f"SELECT * FROM urls WHERE id = {id}")
        result = cur.fetchone()
    conn.close()
    print(result.name)
    return result.name


def check_url_view(id, status_code, title, h1, description):
    conn = connect_database()
    cur = conn.cursor(cursor_factory=NamedTupleCursor)
    try:
        cur.execute("INSERT INTO url_checks (url_id, status_code, h1, "
                    "title, description) "
                    "VALUES (%s, %s, %s, %s, %s)",
                    (id, status_code, h1, title, description))
        conn.commit()
        cur.close()
        conn.close()
        return Statuses.SUCCESS
    except Exception:
        print('дошло')
        return Statuses.ERROR
