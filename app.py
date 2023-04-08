"""
Author:Efe Akaröz
Date: 8th April 2023
"""


from flask import Flask, render_template, request, abort
import json
import os
import random
from werkzeug.utils import secure_filename
import time
from flask_cors import CORS
import sqlite3
import cv2

config = json.loads(open("config.json", "r").read())
ALLOWED_EXTENSIONS = config["allowed_extensions"]
alphabet = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l',
            'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS




app = Flask(__name__)
CORS(app)
con = sqlite3.connect("tr_adres.db", check_same_thread=False)
cur =con.cursor()

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
    return {"msg":"this is scaler"}
if __name__ == "__main__":
  app.run(debug=True,port="2012")