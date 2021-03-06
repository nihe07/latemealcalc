from flask import Flask, render_template
import os
import psycopg2
import subprocess

import os
import csv
import datetime

app = Flask(__name__, static_url_path = "", static_folder = "static")

#'heroku config:get DATABASE_URL -a calculatemeal' to get the name of the database
DATABASE_URL = 'postgres://gniojkvxziujuu:1c53b1d388891669097c66f2e618d42e31ffffa249aaaef45ccf72034503106c@ec2-184-73-153-64.compute-1.amazonaws.com:5432/d1ipk1vqr3fslq'

#READING CSV FILE FOR DATA #####################################################


conn = psycopg2.connect(DATABASE_URL, sslmode='require')
cursor = conn.cursor()

##ADDED CODE ###################################################################################
cursor.execute("""DROP TABLE IF EXISTS food""")
conn.commit()
#################################################################################################

cursor.execute(
  """
  CREATE TABLE food (
    name VARCHAR(50) NOT NULL PRIMARY KEY,
    price REAL NOT NULL,
    category VARCHAR(50) NOT NULL,
    count INTEGER NOT NULL,
    time VARCHAR(50) NOT NULL,
    packaged VARCHAR(50) NOT NULL
  )
  """)

with open('fooddb.csv', 'r') as f:
  next(f)
  cursor.copy_from(f, 'food', sep=',')
conn.commit()

#cursor.execute(
 #   """
  #  \copy food(name, price, category, count, time, packaged)
   # FROM 'fooddb.csv' DELIMITER ',' CSV HEADER
    #""")
dt = datetime.datetime.now()
if dt.hour < 17:
    time = 'lunch'
else:
    time = 'dinner'

@app.route("/")
def main():
    return render_template("index.html")

@app.route("/contact")
def getContact():
    return render_template("contact.html")

@app.route("/favorites")
def getFavorites():
    cursor.execute("SELECT name FROM food ORDER BY count DESC LIMIT 3")
    results = cursor.fetchall()
    retVal = ""
    for re in results:
      retVal += str(re[0]) + ", "

    return render_template("favorites.html", resultStr=retVal)

@app.route("/info")
def getInfo():
    return render_template("info.html")

@app.route("/search/item/<item>")
def getItem(item):
  if dt.hour < 17:
      cursor.execute("SELECT name FROM food WHERE (time = 'both' OR time='dinner')")
      results = cursor.fetchall()
  else:
      cursor.execute("SELECT name FROM food WHERE (time = 'both' OR time='lunch')")
      results = cursor.fetchall()
  retVal = ""
  if len(results) == 0:
    return "No results found."
  for re in results:
      if item.lower() in str(re[0]).lower():
          retVal = retVal + str(re[0]) + "\n"
          cursor.execute("UPDATE food SET count=count+1 WHERE name='%s'" % re)

  return render_template("results.html", resultStr = retVal)


@app.route("/search/category/<catg>")
def getItemsFromCategory(catg):
  catg = str(catg)
  if dt.hour < 17:
      cursor.execute("SELECT name, category FROM food WHERE (category ='%s' AND (time = 'both' OR time = 'dinner'))" % catg)
      results = cursor.fetchall()
  else:
      cursor.execute("SELECT name, category FROM food WHERE (category ='%s' AND (time = 'both' OR time = 'lunch'))" % catg)
      results = cursor.fetchall()
  if len(results) == 0:
    return "No results found."
  retVal = "Category: " + catg + '\n'
  for re in results:
      retVal += str(re[0]) + " "

  return render_template("category.html", resultStr = retVal)

if __name__ == "__main__":
    PORT = int(os.environ.get("PORT", 5000))
    app.run(debug=False, port=PORT, host='0.0.0.0')
