"""
Author:Efe Akaröz
Date: 8th April 2023
"""

import io
from flask import Flask, render_template, request, abort,send_file,make_response
import json
import os
import random
from werkzeug.utils import secure_filename
import time
import requests
from flask_cors import CORS
import sqlite3
import cv2
import socks
import socket


socks.set_default_proxy(socks.SOCKS5, "45.155.125.74", 1447, True, 'prox1','7ft339lWrI')
socket.socket = socks.socksocket



config = json.loads(open("config.json", "r").read())
ALLOWED_EXTENSIONS = config["allowed_extensions"]
alphabet = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l',
            'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']


app = Flask(__name__)
CORS(app)
con = sqlite3.connect("tr_adres.db", check_same_thread=False)
cur =con.cursor()

#Forgot to add it
listNotWorking = []

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def getwithproxy(lat,long):
    proxies = open("proxies.txt")
    allReadlines = proxies.readlines()
    for ar in allReadlines:
        if ar.replace("\n","") in listNotWorking:
            allReadlines.pop(allReadlines.index(ar))
    ip_proxy = random.choice(allReadlines)
    proxy = ip_proxy.replace("\n","")
    proxyDict = {
            "http":proxy,
            "https":proxy,
    }
    try:

        page = requests.get("https://cbsapi.tkgm.gov.tr/megsiswebapi.v3/api/parsel/{}/{}".format(lat,long),verify=False)
    except Exception as e :
        return {"SCC":False,"err":"Invalid Proxy","err_detailed":str(e)}
    try:
        data = json.loads(page.content)
    except:
        listNotWorking.append(ip_proxy)
    return data


@app.route("/get_coordinates")
def get_coordinates():
    """
    Format: City,District
    """
    search = request.args.get("q")
    data = json.loads(open("data/final_tr.json","r").read())
    if search == None:
        return {"SCC":False,"msg":"You need to specify search"}
    city = search.split(",")[0].strip()
    try:
        district = search.split(",")[1].strip()
    except:
        return {"SCC":False,"msg":"İlçe girin, şehir ismini merkez için yineleyin: Ankara,Ankara"}
    allcities = list(data.keys())
    for a in allcities:
        al = a.lower()
        if city.lower() == al:
            alldistricts = data[a]
            dkeys = list(alldistricts.keys())
            for d in dkeys:
                if district.lower() == d.lower():
                    return alldistricts[d]

            return data[a]
    return {"SCC":False,"msg":"Sonuç bulunamadı"}

@app.route("/demo/2")
def second_demo():
    return render_template("demo2.html")


@app.route("/parsel_sorgu")
def parselSorgu():
    output = {}
    lat = request.args.get("lat")
    long = request.args.get("long")
    if lat == None or long == None:
        return {"SCC":False,"err":"Need to specify lat and long"}

    page = getwithproxy(lat,long)
    return page


@app.route("/")
def index():

    return render_template(config["homepage"],allowed_extensions=ALLOWED_EXTENSIONS)


@app.route("/upload", methods=["POST"])
def uploadIt():
    logger = open("file.log", "a")
    if request.method == "POST":
        try:
            ip = request.environ['REMOTE_ADDR'].split(",")[0]
            # ip=request.remote_addr
        except:
            ip = request.environ['HTTP_X_FORWARDED_FOR'].split(",")[0]
        try:
          file = request.files['file']
        except:
          return {"err":"Please specify 'file'."}
        if file and allowed_file(file.filename):
            originalFile = secure_filename(file.filename)
            ext = originalFile.split(".")[1]
            ext = originalFile.split(".")[-1]

            filename = ""
            for i in range(10):
                ca = random.choice(alphabet)
                filename = filename+ca
                addNorNot = random.randint(0, 1)
                if addNorNot == 1:
                    filename = filename + str(random.randint(12, 120))

            try:
                file.save("static/"+filename+"."+ext)
                logger.write(f"UPLOAD {ip} | "+originalFile+" @" +
                             str(time.time())+" as "+filename+"."+ext+"\n")
                return {"file": filename+"."+ext, "time": time.time(), "ctime": time.ctime(time.time())}

            except Exception as e:
                return {"err": str(e)}
        else:
          return {"err":"File type is not allowed in this server","allowedFileTypes":ALLOWED_EXTENSIONS,"maxSize":"10MB"}
    logger.close()
@app.route("/delete/<filename>", methods=["DELETE"])
def deleteit(filename):
    logger = open("file.log", "a")
    try:
        ip = request.environ['REMOTE_ADDR'].split(",")[0]
        # ip=request.remote_addr
    except:
        ip = request.environ['HTTP_X_FORWARDED_FOR'].split(",")[0]

    if "*" in filename or ".." in filename or "/" in filename:
        return abort(403)
    try:
        open(f"static/{filename}", "r")
    except:
        return {"err": "File does not exist"}
    os.system(f"rm static/{filename}")
    logger.write(f"DELETE {ip} | {filename} {time.time()}  \n")
    return {"message": "Delete Successfull", "filename": filename}

    logger.close()


@app.route("/cities")
def cities():
    res = cur.execute("SELECT il_adi FROM iller")
    out = {"res": res.fetchall()}
    return out
@app.route("/api")
def apithing():
    city = request.args.get("city")
    apikey = request.args.get("key")
    if apikey=="AHSJMI21234998":
        if city == None:
            res = cur.execute("SELECT il_adi FROM iller")
            out = {"sehirler":res.fetchall()}
            return out
        else:
            district = request.args.get("district")
            if district == None:
                alldata = cur.execute("SELECT * FROM ilceler WHERE il_adi IN ('{}')".format(city)).fetchall()
                return {"res":alldata}
            else:
                nh= request.args.get("nh")
                if nh == None:
                    alldata = cur.execute(f"SELECT * FROM mahalleler WHERE ilce_adi='{district}' AND il_adi='{city}' ").fetchall()
                    return {"res":alldata}
                else:
                    alldata = cur.execute(f"SELECT * FROM sokaklar WHERE ilce_adi='{district}' AND il_adi='{city}' AND mahalle_adi='{nh}' ").fetchall()
                    return {"res":alldata}

    return{"SCC":False,"err":"Didn't specify any keys."}

@app.route("/static/scaler")
def scaler():
    filename = request.args.get("filename")
    if filename == None:
        return {"SCC":False,"err":"Filename required"}
    try:
        img = cv2.imread('static/{}'.format(filename), cv2.IMREAD_UNCHANGED)
    except:
        return {"SCC":False,"err":"file not found or could not be opened by cv2"}

    try:
        scale_percent = int(request.args.get("scalePer"))
    except:
        scale_percent = 60
    width = int(img.shape[1] * scale_percent / 100)
    height = int(img.shape[0] * scale_percent / 100)
    dim = (width, height)
    resized = cv2.resize(img, dim, interpolation=cv2.INTER_AREA)
    retval, buffer = cv2.imencode('.png', resized)
    response = make_response(buffer.tobytes())
    response.headers['Content-Type'] = 'image/png'
    return response

@app.route("/demo")
def demoit():
    return render_template("demo.html")



@app.route("/get_cities")
def getCities():

    page = open("data/cityNames.json","r")
    output = json.loads(page.read())
    return output

@app.route("/getDistricts/<province>")
def getDistricts_(province):
    listOutput = []
    page = requests.get("https://cbsapi.tkgm.gov.tr/megsiswebapi.v3/api/IdariYapi/ilceliste/"+province,verify=False)
    output = json.loads(page.content)
    output = output["features"]
    for o in output:
        listOutput.append(o["properties"])

    return listOutput

@app.route("/nh/<district>")
def getnh(district):
    page = requests.get("https://cbsapi.tkgm.gov.tr/megsiswebapi.v3/api/idariYapi/mahalleListe/"+district,verify=False)
    listOutput = []

    output = json.loads(page.content)
    output = output["features"]
    for o in output:
        listOutput.append(o["properties"])
    return listOutput

@app.route("/idari/<id_>/<ada_>/<parsel>")
def idariSorgu(id_,ada_,parsel):
    try:
        page = requests.get(f"https://cbsapi.tkgm.gov.tr/megsiswebapi.v3/api/parsel/{id_}/{ada_}/{parsel}",verify=False)
    except Exception as e :
        print(e)
        return {"SCC":False,"err":"Couldn't load page"}
    
    return json.loads(page.content)
    


if __name__ == "__main__":
  app.run(debug=True,port="2012")