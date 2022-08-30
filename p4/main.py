# project:p4

# submitter:mkornely

# partner:none 

# hours:7




#https://www.kaggle.com/komalkhetlani/out-of-school-rates-global-data?select=Primary.csv
#out of school rates for students in primary school around the world 

import pandas as pd
from flask import Flask, request, jsonify,Response
import re 
import matplotlib
import matplotlib.pyplot as plt
from io import BytesIO
import time


matplotlib.use('Agg')
app = Flask(__name__)

#global counters 
n=0 
visits=0
a_counter=0
b_counter=0


@app.route('/')
def home():
    global visits
    visits+=1
    with open("index.html") as f:
        html = f.read()
    if(visits<=10):
        if(visits%2==0):
            with open("indexalternate.html") as f:
                html = f.read()
    else:
        if(b_counter>a_counter):
            with open("indexalternate.html") as f:
                html = f.read()
       
          
    return html


@app.route("/primary_school.svg")
def primary():
    c= request.args.get("c")
    fig, ax = plt.subplots()
    dataframe=pd.read_csv("main.csv")
    dataframe.plot.scatter(x='Male', y='Female',c=c,cmap='plasma', ax=ax)
    ax.set_xlabel("Percentage of Males not in Primary School")
    ax.set_ylabel("Percentage of Females not in Primary School")
    ax.set_title("Male vs Female percentages not in Primary School ")
    fake_file = BytesIO()
    ax.get_figure().savefig(fake_file, format="svg", bbox_inches="tight")
    plt.close(fig)
    return Response(fake_file.getvalue(),
                    headers={"Content-Type": "image/svg+xml"})
    
    
@app.route("/development_regions.svg")
def regions():
    fig, ax = plt.subplots()
    dataframe=pd.read_csv("main.csv")
    dataframe["Development Regions"].value_counts().plot(kind='bar',ax=ax)
    ax.set_xlabel("Development Regions")
    ax.set_ylabel("Frequency")
    ax.set_title("Frequency of Development Regions")
    fake_file = BytesIO()
    ax.get_figure().savefig(fake_file, format="svg", bbox_inches="tight")
    plt.close(fig)
    return Response(fake_file.getvalue(),
                    headers={"Content-Type": "image/svg+xml"})


@app.route('/browse.html')
def browse_handler():
    f=pd.read_csv("main.csv")
    return "<html><body><h1>Data</h1></body>"+ f.to_html()


@app.route('/email', methods=["POST"])
def email():
    global n
    email = str(request.data, "utf-8")
    if re.match(r"\w+@{1}\w+\.{1}\w+", email): # 1
        n=n+1
        with open("emails.txt", "a") as f: # open file in append mode
            f.write(email + "\n") # 2
        return jsonify(f"thanks, you're subscriber number {n}!")
    return jsonify("Enter a valid email!!!!") # 3


@app.route('/donate.html')
def donate_handler():
    global a_counter, b_counter
    index_page=request.args.get("from")
    if(index_page!=None):
        if index_page== 'A':
            a_counter+=1
        if index_page== 'B':
            b_counter+=1
    
    
    with open("donate.html") as f:
        html = f.read()

    return html


@app.route('/robots.txt')
def robot():
     return Response("\n".join(["User-Agent: busyspider", "Disallow: / \n", "User-Agent: hungrycaterpillar", "Disallow: /browse.html"]) ,
                   headers={"Content-Type": "text/plain"})

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True, threaded=False) # don't change this line!


  


    
# NOTE: app.run never returns (it runs for ever, unless you kill the process)
# Thus, don't define any functions after the app.run call, because it will
# never get that far.
