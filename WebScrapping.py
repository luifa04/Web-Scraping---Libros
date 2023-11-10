import pymysql
import requests
from bs4 import BeautifulSoup
from time import sleep
from config import db_config

#delete tables if exist
sqlDropTable = "drop table if exists book;"
sqlDropTable2 = "drop table if exists audit_error_book;"

#Create tables if do not exist
createTableBook = 'CREATE TABLE book(id_local int auto_increment,title_book varchar(70),url varchar(100),price_pesos_arg double,price_official_dollar double,price_blue_dollar double,date date,primary key (id_local));'
createTableError = 'CREATE TABLE audit_error_book(id_local  integer PRIMARY KEY AUTO_INCREMENT,title_book varchar(70),url varchar(100),date date);'

#conecct to the DataBase
conexion = pymysql.connect(**db_config)
cursor = conexion.cursor()

#Create the schema and the tables
cursor.execute(sqlDropTable)
cursor.execute(sqlDropTable2)
cursor.execute(createTableBook)
cursor.execute(createTableError)
conexion.commit()

#take the html from the books web page and search titles 
web = 'https://cuspide.com/100-mas-vendidos/'
result = requests.get(web)
sleep(2)
html = BeautifulSoup(result.text, 'html.parser')
titles = html.find_all(class_="name product-title woocommerce-loop-product__title")

# #take the html from the web page and the price of the dollar blue 
web_dollar_blue = 'https://dolarhoy.com/cotizaciondolarblue'
result2 = requests.get(web_dollar_blue)
html2 = BeautifulSoup(result2.content, 'html.parser')
price_blue_dollar = float(html2.find_all('div', class_="value")[1].text[1:])

#iterate all titles to extract the important data
for title in titles:
    titleBook = title.a.text.strip()
    urlBook = title.a.get('href')
    try:
        #use the url of each book and take the prices
        result_price = requests.get(urlBook)
        sleep(0.5)
        result_price.encoding = 'utf-8'
        html_price = result_price.text
        dom_precio = BeautifulSoup(html_price, features = 'html.parser')
        #take the price in pesos.    
        price_arg_pesos =float(dom_precio.find(class_="price product-page-price").bdi.text.strip('$').replace('.','').replace(',','.'))
        #take the price in dollars
        price_official_dolar =float(dom_precio.find('span',style="font-size: 1.3em").text.strip('$').replace('.','').replace(',','.'))
        #make the price for each book in blue dollar
        price_blue_dollar_book = round(float(price_arg_pesos / price_blue_dollar),2)
        #insert data into the table
        cursor.execute("INSERT INTO book(title_book,url,price_pesos_arg,price_official_dollar,price_blue_dollar,date) VALUES(%s,%s,%s,%s,%s,curdate())",(titleBook,urlBook,price_arg_pesos,price_official_dolar,price_blue_dollar_book))
    except:
        #if there are errors this part catch that ones
        requests.exceptions.HTTPError
        #insert data into the audit book table
        cursor.execute("INSERT INTO audit_error_book(title_book, url, fecha) VALUES(%s,%s,curdate())", (titleBook, urlBook))
    
conexion.commit()