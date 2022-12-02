
import json
from flask import *

# import mysql.connector
from mysql.connector import Error
from mysql.connector import pooling


import os
from dotenv import load_dotenv
load_dotenv()

host = os.getenv("host")
user = os.getenv("user")
database = os.getenv("database")
password = os.getenv("password")

import jwt
import time

def jwt_encode(name, username):
  payload = {
    "iss": "ben.127",  # 字串 或 uri 表示這個 JWT 的唯一識別發行方 
    "iat": int(time.time()), # issued at (time)，JWT 的發行時間
    "exp": int(time.time() + 86400 * 7), # 設定 JWT 被視為無效的時間
    "aud": "www.ben.127", # audience，這個 JWT 唯一識別的預期接收者，與 iss 和 sub 要求的情況一樣，該權利要求是專用的
    "sub": username, # subject，用字串 或 uri 表示這個 JWT 所夾帶的唯一識別訊息
    "name": name,
  }
  token = jwt.encode(payload, "secret", algorithm="HS256")
  return token

def jwt_verify(token):
  payload = jwt.decode(token, "secret", audience="www.ben.127", algorithms="HS256")
  if payload:
    return payload
  return None



app = Flask(__name__, static_folder="public", static_url_path="/")

# app.secret_key="anytxt"

def connectPool():
  connection_pool = pooling.MySQLConnectionPool(pool_name="pynative_pool",
                                                pool_size=5,
                                                pool_reset_session=True,
                                                host=host,
                                                user=user,
                                                database=database,
                                                password=password)
  connection_object = connection_pool.get_connection()   
  return connection_object                                          

# # mycursor = connection_pool.cursor()
insertSql = "INSERT INTO users (name, username, password) VALUES (%s, %s, %s)"
signUpSelectSql = "SELECT * FROM users WHERE username=%s"
# msgSql = "INSERT INTO message (name_id, msg) VALUES (%s, %s)"
# showMsgSql = "SELECT u.name, m.msg, m.time FROM users AS u INNER JOIN message As m ON u.uid=m.name_id ORDER BY m.time DESC"
# showMsgParamsSql = ()
signInSelectSql = "SELECT * FROM users WHERE username=%s and password=%s"
# msgUidSelectSql = "SELECT uid FROM users WHERE name=%s"

# 首頁
@app.route("/")
def index():
  return render_template("index.html")

# 會員頁
@app.route("/member", methods=["get", "post"])
def member():
  try:
    payload = jwt_verify(request.cookies.get("key"))
    name = payload["name"]
    username = payload["sub"]
    return render_template("member.html", len=0, user=name)
  except:
    return redirect("/")

  
  # if request.method == 'POST':
    # LocalStore.post_body = request.json["name"]
    # print("POST request stored.")
    # return {"result": "Thanks for your POST!"}
  # else:
    # name = session["name"]
    # print("POST body was    :", LocalStore.post_body)
    # name = LocalStore.post_body
    # if not name:
    #   return redirect("/")
    
    # db = connectPool()
    # mycursor = db.cursor()
    # mycursor.execute(showMsgSql)
    # msgs = mycursor.fetchall()
    # mycursor.close()
    # db.close()

    # msgs = connectDB(None, None, False, True, False, False)
    # time = []
    # for i in msgs:
    #   s = str(i[2]).split(" ")[1][:5]
    #   time.append(s)


    # return render_template("member.html", user=name, msgs=msgs, time=time, len=len(time))


# 錯誤頁
@app.route("/error")
def error():
  err = request.args.get("message", "輸入錯誤") 
  return render_template("error.html", message=err)


# 註冊
@app.route("/signup", methods=["post"])
def signup():
  name = request.json["name"]
  username = request.json['username']
  password = request.json['password']

  if not name or not username or not password:
    return {"result": "請輸入註冊資訊"}

  db = connectPool()
  mycursor = db.cursor()
  mycursor.execute(signUpSelectSql, (username, ))
  exists = mycursor.fetchone()

  if exists:
    mycursor.close()
    db.close()
    return {"result": "帳號已存在"}
  else:
    val = (name, username, password)
    mycursor.execute(insertSql, val)
    db.commit()
    mycursor.close()
    db.close()
    print("用戶 {} 帳戶創建成功！".format(name))
    return {"result": "OK"}


# 登入
@app.route("/signin", methods=["post"])
def sign():
  username = request.json['username']
  password = request.json['password']
  if username == "" or password == "":
    return {"result": "請輸入登入資訊"}
  params = (username, password)

  db = connectPool()
  mycursor = db.cursor(dictionary=True) 
  mycursor.execute(signInSelectSql, params)
  exists = mycursor.fetchone()
  mycursor.close()
  db.close()

  if not exists:
    return {"result": "帳號或密碼輸入錯誤"}

  # jwt
  token = jwt_encode(exists["name"], exists["username"])
  
  # cookie
  resp = make_response({"result": "OK", "name": exists["name"]})
  resp.set_cookie("key", token)

  return resp
  


# 登出
@app.route("/signout")
def signout():
  resp = make_response(redirect("/"))
  resp.set_cookie('key', '', 0)
  return resp


# # 留言
# @app.route("/message", methods=["post"])
# def message():
#   msg = request.json["msg"]
#   clicked = request.json["click"]
#   if not clicked:
#     db = connectPool()
#     mycursor = db.cursor()
#     mycursor.execute(showMsgSql)
#     msgs = mycursor.fetchall()
#     mycursor.close()
#     db.close()
#     # msgs = connectDB(None, None, False, True, False, False)
#     return {"result": msgs}
#   if not msg:
#     return {"result": "請留言"}
  
#   name = session["name"]
  
#   db = connectPool()
#   mycursor = db.cursor()
#   # 紀錄使用者及留言
#   mycursor.execute(msgUidSelectSql, (name, ))
#   uid = mycursor.fetchone()[0]
#   val = (uid, msg)
#   # 寫入
#   mycursor.execute(msgSql, val)
#   db.commit()
#   # 抓所有留言
#   mycursor.execute(showMsgSql)
#   msgs = mycursor.fetchall()
#   mycursor.close()
#   db.close()
#   # msgs = connectDB(msgUidSelectSql, (name, msg), False, False, False, True)

#   # for i in msgs:
#   #   print(i[0], i[1], i[2])
#   return {"result": msgs}




app.run(port=3000, debug=True)




# ##

# import base64
# import hmac
# import hashlib 
# import binascii

# def jwt(name):
#   header	='{"alg":"HS256","typ":"JWT"}'
#   print(name)
#   payload = '{' + f'"name":"{name}","timestamp":"1234567"' + '}'
#   print(payload)
#   key	= "fji234j;raewr823423"

#   #convert utf-8 string to byte format
#   def toBytes(string):
#     return bytes(string,'utf-8')

#   def encodeBase64(text):
#     #remove "=" sign, 
#     #P.S. "=" sign is used only as a complement in the final process of encoding a message. 
#     return base64.urlsafe_b64encode(text).replace(b'=',b'')

#   #signature = HMAC-SHA256(key, unsignedToken)
#   def create_sha256_signature(key, unsignedToken):
#     signature = hmac.new(toBytes(key), unsignedToken, hashlib.sha256).digest()
#     return encodeBase64(signature)

#   unsignedToken = encodeBase64(toBytes(header)) + toBytes('.') + encodeBase64(toBytes(payload))

#   signature	= create_sha256_signature(key,unsignedToken)


#   jwt_token = unsignedToken.decode("utf-8") +'.'+signature.decode("utf-8")
#   print(jwt_token)


# ##






