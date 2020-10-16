import mysql.connector

db = mysql.connector.connect(user="root", password="root", database="tester3")
cursor = db.cursor()

query = "INSERT INTO termXurlXkeywords (term, url, keywords) VALUES (%s, %s, %s)"

url = 'http://www.calstatela.edu/ecst/cs-lecturers'

k = 'Cervantes, Cross, Firpo, Gean, Hurley, Knaur, Lim, Macias, Moss, Sargent, Thomas, Yu, Email'

terms = k.split(", ")

for term in terms:
    cursor.execute(query, (term, url, k))

db.commit()