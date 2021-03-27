from flask import Flask, request, session, redirect, url_for
from markupsafe import escape
import random
import requests
from flask import render_template
import json
from fuzzywuzzy import fuzz
import pandas as pd
from PyDictionary import PyDictionary 
import pickle
import os
import time
import copy

from utils.frame  import *



#import utils
app=Flask(__name__)
app.secret_key = "ke3"

@app.route('/')
def root():
    return render_template ("add_car.html")





@app.route('/add_car',methods=['POST'])
def add_car():
    car_id=request.form["ID"]
    ppd=request.form["ppd"]
    fuel_efficency=request.form["fuel_efficency"]
    car_brand=request.form["car_brand"]
    car_make=request.form ['car_make']
    Plate_no=request.form['car_plate_no']

    My_car=Car(car_id,ppd,fuel_efficency,car_brand,car_make,1,Plate_no)
    status_val=add_car_to_db(My_car,session["username"])
    if status_val==0:
        return "Duplicate Car"
    elif status_val==1:
        return "Some error"
    elif status_val==2:
        # return to the page owner sees after logging in
        username=session["username"]
        dic=all_cars_under_owner(username) 
        return render_template("all_cars_under_owner.html",data=dic) 
        # return "Added to two tables successfully"


@app.route('/show_all_cars')
def show_all_cars():
    all_cars=pd.read_csv("data/cars.csv")
    dic=get_all_cars(all_cars)    
    return render_template("all_cars.html",data=dic)



@app.route('/get_car/<car_id>')
def get_single_car(car_id):
    all_cars=pd.read_csv("data/cars.csv")
    result_dic=get_one_car(all_cars,car_id)
    return render_template("all_cars.html",data=result_dic)


@app.route('/show_car_modify',methods=['POST'])
def show_car_modify():
    all_cars=pd.read_csv("data/cars.csv")
    car_id=request.form["car_id"]
    result_dic=get_one_car(all_cars,car_id)
    print("obtained single car",result_dic)

    return render_template("show_car_modify.html",data=result_dic)



@app.route('/modify_car',methods=['POST'])
def modify_car():
    car_id=request.form["ID"]
    ppd=request.form["ppd"]
    fuel_efficency=request.form["fuel_efficency"]
    car_brand=request.form["car_brand"]
    is_aval=request.form["is_aval"]
    My_car=Car(car_id,ppd,fuel_efficency,car_brand,is_aval)
    print("New car object created ",My_car)
    all_cars=pd.read_csv("data/cars.csv")
    print(all_cars.head())
    message= modify_one_car(all_cars,My_car)
    return message


@app.route('/book_car',methods=['POST'])
def book_car():
    car_id=request.form["car_id"]
    username=session["username"]
    status= book_one_car(car_id,username)
    if status==1:

        dic=get_all_cars_from_db_for_renter()
        dic2=get_all_cars_rented_by_user(username)

        return_dic={}
        return_dic["cars_for_rent"]=dic
        return_dic["cars_already_rented"]=dic2


        print("obtained dictionary is ",dic)
        return render_template("Customer_all_cars.html",data=return_dic)        
    elif status==0:
        return "error"


@app.route('/return_to_shed',methods=['POST'])
def return_to_shed():
    car_id=request.form["car_id"]
    username=session["username"]
    status=submit_car_for_return(username,car_id)
    # 1 =>  succes
    # 0 => faiure
    if status == 1:
        dic=get_all_cars_from_db_for_renter()
        dic2=get_all_cars_rented_by_user(username)

        return_dic={}
        return_dic["cars_for_rent"]=dic
        return_dic["cars_already_rented"]=dic2


        print("obtained dictionary is ",dic)
        return render_template("Customer_all_cars.html",data=return_dic)           

    elif status==0:
        return "Your request to return could not be processed"

################################################################
#########################USER SECTION###########################
################################################################

@app.route('/add_user')
def add_user():
    return render_template ("add_user.html")


@app.route('/insert_user',methods=['POST'])
def insert_user():
    username=request.form["username"]
    password=request.form["password"]
    name=request.form["name"]
    QID=request.form["QID"]
    telephone=request.form["telephone"]
    email=request.form["email"]
    address=request.form["address"]

    new_user=User(0,username,password,name,QID,telephone,email,address)

    status=insert_user_into_db(new_user)
    if status == False:
        return "Duplicate user or QID"
    
    session["username"]=username
    print("Session modified")
    all_cars=pd.read_csv("data/cars.csv")
    dic=get_all_available_cars(all_cars)
    print("returnd dict is ",dic)
    # return "Newuser saved"
    return render_template("Customer_all_cars.html",data=dic)

@app.route('/user_login')
def user_login():
    return render_template("login.html") 
    # if 'username' in session:
    #     all_cars=pd.read_csv("data/cars.csv")
    #     dic=get_all_available_cars(all_cars)
    #     print("modified dictionary is ",dic)
    #     return render_template("Customer_all_cars.html",data=dic)

    # else:    
        # return render_template("login.html") 






@app.route('/post_user_login',methods=['POST'])
def post_user_login():
    print("At logging in",request)
    username=request.form['username']
    password=request.form['password']
    user_type=request.form['typeuser']
    if user_type=='renter':
        validation_value=validate_renter_login(username,password)

        print("The value is ",validation_value)
        # 0 - user not exist
        # 1 - wrong password
        # 2 - success
        if validation_value==0:
            return "User doesnot exist"
        elif validation_value==1:
            return "Wrong password"
        elif validation_value==2: 
            session["username"]=username
            # show al the cars to the user from db which are available
            dic=get_all_cars_from_db_for_renter()
            dic2=get_all_cars_rented_by_user(username)

            return_dic={}
            return_dic["cars_for_rent"]=dic
            return_dic["cars_already_rented"]=dic2


            print("obtained dictionary is ",dic)
            return render_template("Customer_all_cars.html",data=return_dic)        
        else:
            print("Error logging in")
            return render_template("login.html") 
    elif user_type=="owner":
        validation_value=validate_owner_login(username,password)
        print("The value is ",validation_value)
        # 0 - user not exist
        # 1 - wrong password
        # 2 - success
        if validation_value==0:
            return "User doesnot exist"
        elif validation_value==1:
            return "Wrong password"
        elif validation_value==2: 
            session["username"]=username
            print("Session modified")
            dic=all_cars_under_owner(username) 
            print(dic)

            return render_template("all_cars_under_owner.html",data=dic) 
    elif user_type=="admin" and username=="admin":
        validation_value=validate_owner_login(username,password)
        print("The value is ",validation_value)
        # 0 - user not exist
        # 1 - wrong password
        # 2 - success
        if validation_value==0:
            return "Admin doesnot exist"
        elif validation_value==1:
            return "Wrong admin password"
        elif validation_value==2: 
            session["username"]=username
            print("Session modified")
            dic=get_return_pending_cars()            
            print(dic)
            return render_template("admin_return_cars.html",data=dic) 




@app.route('/accept_return',methods=['POST'])
def accept_return():
    if request.method == "POST":
        selected_cars = request.form.getlist("cars")
        print(selected_cars)
        status=accept_cars_for_return_in_db(selected_cars)
        if status==0:
            print("Some issue in accepting return, please try again")
        elif status==1:
            dic=get_return_pending_cars()            
            print(dic)
            return render_template("admin_return_cars.html",data=dic) 


    




@app.route('/add_owner')
def add_owner():
    return render_template ("add_owner.html")



@app.route('/insert_owner',methods=['POST'])
def insert_owner():
    username=request.form["username"]
    password=request.form["password"]
    name=request.form["name"]
    QID=request.form["QID"]
    telephone=request.form["telephone"]
    email=request.form["email"]
    address=request.form["address"]

    new_user=User(0,username,password,name,QID,telephone,email,address)

    status=insert_owner_into_db(new_user)
    if status == False:
        return "Duplicate user or QID"
    
    session["username"]=username
    print("Session modified")
    all_cars=pd.read_csv("data/cars.csv")
    dic=get_all_available_cars(all_cars)
    print("returnd dict is ",dic)
    # return "Newuser saved"
    return render_template("Customer_all_cars.html",data=dic)


if __name__ == '__main__':
    
    app.run(host="0.0.0.0",debug=True)
    
