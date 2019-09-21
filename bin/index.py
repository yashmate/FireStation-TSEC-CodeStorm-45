from flask import Flask,render_template,request
from geopy import Nominatim
from sqlite3 import *
import pandas as pd
from geopy.distance import geodesic
import reverse_geocoder as rg
import pprint
import collections
import requests, json
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

app = Flask(__name__)
api_key = 'AIzaSyCL0wx3UnODrwb51u4XxQFhmNNd20jhq1o'
url = "https://maps.googleapis.com/maps/api/place/textsearch/json?"
def reverseGeocode(coordinates):
    result = rg.search(coordinates)
    return result
@app.route('/')
def home():
   return render_template('home.html')
@app.route('/reportFire',methods=['GET','POST'])
def report():
    print('Done1')
    if(request.method=='POST'):
        print('Done')
        loc=request.form['location']
        print(loc)
        cause=request.form['cause']
        print(cause)
        intensity=int(request.form['intensity'])
        print(intensity)
        try:
            firest=[]
            phoneno=[]
            geolocator=Nominatim(timeout=5)
            print('Done2')
            location=geolocator.geocode(loc)
            p=location.longitude
            q=location.latitude

            coordinates =(q, p)
            z=reverseGeocode(coordinates)
            z=list(z[0].items())
            location=z[2][1]
            query = str(location)+' hospital'
            print(query)
            r = requests.get(url + 'query=' + query +'&key=' + api_key)
            print("Amazing")
            x = r.json()
            y = x['results']
            l2=[]
            for i in range(len(y)):
                print(y[i]['name'])
                l2.append(y[i]['name'])
            print("Done3")
            conn2=connect('firefighters.db')
            print("DOne4")
            conn2.execute("INSERT INTO reportfire(latitude,longitude,location,intensity,cause) VALUES(?,?,?,?,?)",(q,p,loc,intensity,cause) )
            print("Done5")
            conn2.commit()
            print("Report Datbase Connected successfully!")
            conn2.close()
            print("Done Inserting!")


            conn=connect('firestation.db')
            p1=conn.execute('Select * from Firesta')
            q1=p1.fetchall()
            print(q1)
            for i in q1:
                s=geodesic((i[1],i[2]), (p,q)).km
                if(s<6):
                    print(i[0])
                    if(str(i[3])!=None):
                        print('done')
                        firest.append(str(i[0])+'  :  '+str(i[3]))
                        print('done')
                        phoneno.append(str(i[3]))
                        print('done')
            conn.close()

            print('There')
            return render_template('n2.html',l1=firest,l2=l2)
        except:
            return render_template('reportfire.html')
    return render_template('reportfire.html')

@app.route('/safeguard')
def safeguard():
   return render_template('safeguard.html')
@app.route('/checkforfire',methods=['GET','POST'])
def firecheck():
    if(request.method=='POST'):
        loc=request.form['location']
        print(loc)
        try:
            fireloc=[]
            geolocator=Nominatim(timeout=15)
            print('Done1')
            location=geolocator.geocode(loc)
            p=location.longitude
            q=location.latitude
            print('Done2')
            conn=connect('firefighters.db')
            p1=conn.execute('Select * from adminfire where current_status="Ablaze"')
            print("Done3")
            q1=p1.fetchall()
            print("done4")
            for i in q1:
                s1=geodesic((p,q),(i[6],i[3])).km
                print(i)
                if(s1<5):
                    fireloc.append(str(i[1]))
                    print("done6")
            conn.close()
            print("done7")
            print(fireloc)
            return render_template('fireschecked.html',val1=fireloc)
        except:
            return render_template('checkforfire.html')
    return render_template('checkforfire.html')
@app.route('/dashboardadmin')
def dashboardadmin():
    con=connect('firefighters.db')
    con.row_factory = Row
    cur = con.cursor()
    cur.execute("select * from adminfire")
    rows = cur.fetchall();


    return render_template('dashboardadmin.html',rows = rows)
@app.route('/ablaze')
def ablaze():
    con=connect('firefighters.db')
    con.row_factory = Row
    cur = con.cursor()
    cur.execute("select * from adminfire")
    rows = cur.fetchall();
    return render_template('n3.html',rows=rows)
@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')
@app.route('/login')
def login():
   return render_template('login.html')
@app.route('/notifications',methods=['GET','POST'])
def notifications():
    if request.method == "POST":
        email=request.form['email']
        phone_number=request.form['phone_number']
        url = "https://www.fast2sms.com/dev/bulk"
        msg='Fire has been detected near your vicinity!'
        payload = "sender_id=FSTSMS&message={}&language=english&route=p&numbers={}".format(msg,phone_number)
        headers = {
        'authorization': "mGtxiRuLCkVlXjW4eJw3KDSrvynh8YFIqZgPa7TQ1UA6Hf92BMYaSJKyh1UbDTOs8C9Azncr5pEL0jXV",
        'Content-Type': "application/x-www-form-urlencoded",
        'Cache-Control': "no-cache",
        }
        response = requests.request("POST", url, data=payload, headers=headers)

        fromaddr = "nihar.kalsekar@yahoo.com"
        toaddr = str(email)
        msg = MIMEMultipart()
        msg['From'] = fromaddr
        msg['To'] = toaddr
        msg['Subject'] = "Fire Notification"

        body = "A fire has been alarmed at location ABC!Please send relief!"
        msg.attach(MIMEText(body, 'plain'))
        s = smtplib.SMTP('smtp.mail.yahoo.com', 465)
        s.starttls()
        s.login(fromaddr, "shubhangi")
        text = msg.as_string()
        s.sendmail(fromaddr, toaddr, text)
        s.quit()
        return render_template('notifications.html')
    return render_template('notifications.html')
@app.route('/predictFireFighters',methods=['GET','POST'])
def predictff():
    if(request.method=='POST'):
        intensity=int(request.form['intensity'])
        cause=int(request.form['cause'])
        if(cause==1):
            xm=[1,0,0,0,0,0,intensity]
        elif(cause==2):
            xm=[0,1,0,0,0,0,intensity]
        elif(cause==3):
            xm=[0,0,1,0,0,0,intensity]
        elif(cause==4):
            xm=[0,0,0,1,0,0,intensity]
        elif(cause==5):
            xm=[0,0,0,0,1,0,intensity]
        elif(cause==6):
            xm=[0,0,0,0,0,1,intensity]
        df=pd.read_csv('fire.csv')
        x11=df.iloc[1:,3:10].values
        y11=df.iloc[1:,2].values
        z11=df.iloc[1:,10].values
        #np.ravel(y)
        from sklearn.linear_model import LogisticRegression
        #from sklearn.model_selection import train_test_split
        #_train, x_test, y_train, y_test = train_test_split(x, y, test_size = 1/3, random_state = 0)
        lin=LogisticRegression()
        lin.fit(x11,y11)
        ans=lin.predict([xm])
        lin.fit(x11,z11)
        ans2=lin.predict([xm])
        return render_template('predict.html',val2=ans[0],val1="The Estimated No. of Fire Fighters Required are: ",val3=ans2[0],val4='The estimated No. of Fire Brigades Required are: ')

    return render_template('predict.html')
@app.route('/updatedb',methods=['GET','POST'])
def updatedb():
    if(request.method=="POST"):
            #try:
            loc=request.form['location']
            print(loc)
            cas=int(request.form['casualties'])
            print(cas)
            conn=connect('firefighters.db')
            print('done')
            conn.execute('UPDATE adminfire SET casualities=? where current_status="Ablaze" and location=?',(cas,loc,))
            conn.commit()
            conn.execute('UPDATE adminfire SET current_status="PutOff" where current_status="Ablaze" and location=?',(loc,))
            print('done')
            conn.commit()
            p1=conn.execute('Select * from adminfire')
            q1=p1.fetchall()
            print(q1)
            conn.close()
            return ("Thank You")
            #except:
            #return render_template('update.html')
    return render_template('update.html')
@app.route('/notifyme',methods=['POST','GET'])
def notifyme():
    if request.method == 'POST':
        try:
            username=request.form['username']
            email=request.form['email']
            phone=request.form['phone_number']
            location=request.form['location']
            print(username)
            print(email)
            print(phone)
            print(location)
            con=connect("firefighters.db")


            con.execute("INSERT INTO users(name,phone_number,email,address) VALUES(?,?,?,?)",(username,email,phone,location) )
            con.commit()
            msg = "Record successfully added"
            print(msg)
            con.close()
        except:
            con.rollback()
            print("Error Message")
        finally:
            con.close()

    return render_template('notifyme.html')

@app.route('/safeguard/causesoffire')
def causesoffire():
   return render_template('causesoffire.html')
@app.route('/safeguard/inchargetable')
def inchargetable():
   return render_template('inchargetable.html')
@app.route('/safeguard/safetymeasures')
def safetymeasures():
   return render_template('safetymeasures.html')
@app.route('/safeguard/tutorials')
def tutorials():
   return render_template('tutorials.html')
@app.route('/insert',methods=['GET','POST'])
def insert():
    if request.method == 'POST':

        try:

            lat=request.form['latitude']
            long=request.form['longitude']
            loc=request.form['location']
            cause=request.form['cause']
            intensity=request.form['intensity']
            cas=request.form['casualities']
            status=request.form['current_status']
            firefighter=request.form['firefighter']
            print(lat)
            print(long)
            print(cas)
            con=connect("firefighters.db")
            con.execute("INSERT INTO adminfire(cause,location,intensity,latitude,firefighter,casualities,longitude,current_status) VALUES(?,?,?,?,?,?,?,?)",(cause,loc,intensity,lat,firefighter,cas,long,status) )
            con.commit()
            msg = "Record successfully added"
            print(msg)
            con.close()
        except:
            con.rollback()
            print("Error Message")
        finally:
            con.close()

    return render_template('insert.html')

if __name__ == '__main__':
   app.run()
