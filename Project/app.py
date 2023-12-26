from flask import Flask, render_template, request, redirect, url_for, session, flash
# import pymongo
import os
from pymongo import MongoClient


app = Flask(__name__)

app.secret_key='user-client'


cluster = MongoClient("mongodb+srv://sharanalwarswamy:sharanalwarswamy@cluster0.tu1qjxp.mongodb.net/?retryWrites=true&w=majority")
db = cluster['CloudWallet']
collection = db['users-collection']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/create_account',methods=['POST','GET'])
def create_account():
    if request.method == 'POST': 
        data = {
            "username":request.form['username'],
            "gmail":request.form['gmail'],
            "password":request.form['password'],
            "fileNames":[],
            "staticFileNames":[]
        }
        user = collection.find_one({"username":data['username']})
        if user:
            flash("Account already exists")
            return render_template('login.html')
        collection.insert_one(data)
        print(request.form['username'] + "data inserted to database")
        flash("Account is created!!")
        # alert message kudakanum that account is created nu 
        return render_template('login.html')
    return render_template('create_account.html')

@app.route("/login",methods=['POST','GET'])
def login():
    if request.method == 'POST':
        session['username'] = request.form['username']
        session['gmail'] = request.form['gmail']
        session['password'] = request.form['password']
        user = collection.find_one({"username":session['username'] ,"gmail":session['gmail'] , "password":session['password']})
        if user :
            user = collection.find_one({"username":session['username'] ,"gmail":session['gmail'] , "password":session['password']})
            return redirect(url_for('home'))
        else:
            flash("Wrong Credentials!!")
            return render_template("login.html")
    return render_template("login.html")

@app.route("/home",methods=['POST','GET'])
def home():
    user = collection.find_one({"username":session['username'] ,"gmail":session['gmail'] , "password":session['password']})
    yourFilesArray = user['fileNames']
    staticFilesArray = user['staticFileNames']
    return render_template('home.html', files=yourFilesArray , staticFiles=staticFilesArray )

@app.route("/addYourFiles",methods=['POST','GET'])
def addYourFiles():
    if request.method == 'POST':
            if 'file' not in request.files:
                return 'No file part'

            file = request.files['file']

            if file.filename == '':
                return 'No selected file'

            if file:
                destination_folder = './uploads'
                if not os.path.exists(destination_folder):
                    os.makedirs(destination_folder)
                file = request.files['file']
                filename = os.path.join(destination_folder,file.filename)
                file.save(filename)
                print("file saved: "+file.filename)
                #add file name to mongo
                user1 = collection.find_one({"username": session['username'], "password": session['password']})
                fileArray = user1['fileNames']
                temp = session['username']+"-"+file.filename
                if temp not in fileArray: 
                    fileArray.append(temp)
                    collection.update_one({"username": session['username'], "password": session['password']},{"$set": {"fileNames": fileArray}})
                    flash("file added to your account!!")
                    # AWS code to send to send file to s3
                    # while adding to s3 add username before it <temp>
                    os.remove('./uploads/'+file.filename)
                    # request.method = 'GET'
                    return redirect(url_for('home'))
                else:
                    flash("File already exists!!")
                    return redirect(url_for('home'))
            return redirect(url_for('home'))
    return render_template('addYourFiles.html')

@app.route('/remove/<button_id>')
def remove(button_id):
    user = collection.find_one({"username":session['username'] ,"gmail":session['gmail'] , "password":session['password']})
    tempArray = user['fileNames']
    # data = request.get_json()
    # button_id = data.get('button_id')
    print(f"Received button ID: {button_id}")
    print(tempArray)
    tempArray.remove(button_id)
    print(tempArray)
    collection.update_one({"username": session['username'], "password": session['password']},{"$set": {"fileNames": tempArray}})
    print("inside")
    return redirect(url_for('home'))
    # return redirect(url_for('home'))

@app.route("/removeYourFiles",methods=['POST','GET'])
def removeYourFiles():
    user = collection.find_one({"username":session['username'] ,"gmail":session['gmail'] , "password":session['password']})
    tempArray = user['fileNames']
    # if request.method == 'POST':
    #     data = request.get_json()
    #     button_id = data.get('buttonId')
    #     print(f"Received button ID: {button_id}")
    #     print(tempArray)
    #     tempArray.remove(button_id)
    #     print(tempArray)
    #     collection.update_one({"username": session['username'], "password": session['password']},{"$set": {"fileNames": tempArray}})
    #     print("not returning")
    #     return redirect(url_for('home'))
    return render_template('removeYourFiles.html',files=tempArray)

@app.route('/removeStatic/<button_id>')
def removeStatic(button_id):
    user = collection.find_one({"username":session['username'] ,"gmail":session['gmail'] , "password":session['password']})
    tempArray = user['staticFileNames']
    # data = request.get_json()
    # button_id = data.get('button_id')
    print(f"Received button ID: {button_id}")
    print(tempArray)
    tempArray.remove(button_id)
    print(tempArray)
    collection.update_one({"username": session['username'], "password": session['password']},{"$set": {"staticFileNames": tempArray}})
    print("inside")
    return redirect(url_for('home'))
    # print("outside")
    # return redirect(url_for('home'))

@app.route("/addStaticFiles",methods=['POST','GET'])
def addStaticFiles():
    if request.method == 'POST':
            if 'file' not in request.files:
                return 'No file part'

            file = request.files['file']

            if file.filename == '':
                return 'No selected file'

            if file:
                destination_folder = './staticUploads'
                if not os.path.exists(destination_folder):
                    os.makedirs(destination_folder)
                file = request.files['file']
                filename = os.path.join(destination_folder,file.filename)
                file.save(filename)
                print("file saved: "+file.filename)
                #add file name to mongo
                user1 = collection.find_one({"username": session['username'], "password": session['password']})
                fileArray = user1['staticFileNames']
                temp = session['username']+"-"+file.filename
                if temp not in fileArray: 
                    fileArray.append(temp)
                    collection.update_one({"username": session['username'], "password": session['password']},{"$set": {"staticFileNames": fileArray}})
                    flash("file added to your account!!")
                    # AWS code to send to send file to s3
                    # while adding to s3 add username before it <temp>
                    os.remove('./staticUploads/'+file.filename)
                    # request.method = 'GET'
                    return redirect(url_for('home'))
                else:
                    flash("File already exists!!")
                    return redirect(url_for('home'))
            return redirect(url_for('home'))
    return render_template('addStaticFiles.html')

@app.route("/removeStaticFiles",methods=['POST','GET'])
def removeStaticFiles():
    user = collection.find_one({"username":session['username'] ,"gmail":session['gmail'] , "password":session['password']})
    tempArray = user['staticFileNames']
    # if request.method == 'POST':
    #     data = request.get_json()
    #     button_id = data.get('buttonId')
    #     print(f"Received button ID: {button_id}")
    #     print(tempArray)
    #     tempArray.remove(button_id)
    #     print(tempArray)
    #     collection.update_one({"username": session['username'], "password": session['password']},{"$set": {"fileNames": tempArray}})
    #     print("not returning")
    #     return redirect(url_for('home'))
    return render_template('removeStaticFiles.html',files=tempArray)


@app.route("/signout",methods=['POST','GET'])
def signout():
    if request.method == 'POST':
        flash("you have loggedOUT!!")
        session.pop('username',None)
        session.pop('gmail',None)
        session.pop('password',None)
        return redirect(url_for('index'))
    return redirect(url_for('index'))

    

if __name__=="__main__":
    app.run(host='0.0.0.0',port=8080,debug=True)

    # sessions proper ah implement pannanum 