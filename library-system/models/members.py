from db_config import mysql

def add_member(name, contact):
    cursor = mysql.connection.cursor()
    query = "INSERT INTO Members (Name, Contact) VALUES (%s, %s)"
    cursor.execute(query, (name, contact))
    mysql.connection.commit()
    cursor.close()

def get_members():
    cursor = mysql.connection.cursor()
    query = "SELECT * FROM Members"
    cursor.execute(query)
    members = cursor.fetchall()
    cursor.close()
    return members

def get_member(member_id):
    cursor = mysql.connection.cursor()
    query = "SELECT * FROM Members WHERE MemberID = %s"
    cursor.execute(query, (member_id,))
    member = cursor.fetchone()
    cursor.close()
    return member
