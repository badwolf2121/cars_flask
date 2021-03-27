import psycopg2

class Car:
    avaialbility=True
    def __init__(self,car_id,ppd,fuel_efficency,car_brand,car_make,is_aval,number_plate):
        self.car_id=car_id
        self.ppd=ppd
        self.fuel_efficency=fuel_efficency
        self.car_brand=car_brand
        self.car_make=car_make
        self.is_aval=str(is_aval)
        self.number_plate=number_plate
    def __str__(self):
        self_str="ID = "+str(self.car_id)+"\n ppd = "+str(self.ppd)
        self_str+="\n feff="+str(self.fuel_efficency)+("\nname = ")+str(self.car_brand)+("\nmake = ")+str(self.car_make)
        self_str+=("\navail = ")+str(self.is_aval)+("\n numberplate =")+str(self.number_plate)
        return self-str



def add_car_to_db(My_car,owner_id):
    '''
    My_car is a car object
    insert into db
    return if unsuccesful(duplicate) 0
    any other issue return 1
    if success return 2    
    '''
    print("Adding a car under owner",owner_id)
    query1=format(f"insert into cars values( '{My_car.car_id}','{My_car.fuel_efficency}' ,'{My_car.car_make}','{My_car.car_brand}','{My_car.ppd}','{My_car.is_aval}','{My_car.number_plate}');")
    print(query1)
    con = psycopg2.connect(database="testdb", user="abdullahalshaiabani", password="", host="127.0.0.1", port="5432")
    cur=con.cursor()
    try:
        cur.execute(query1)
        con.commit()
        print("Added to cars table, now adding to fico table")
        # insert into the for_inventory_car_owner user_table
        query2=format(f"insert into for_inventory_car_owner values( '{My_car.car_id}','{owner_id}');")
        cur.execute(query2)
        con.commit()
        print("Added succesfully")

        return 2
    except psycopg2.errors.UniqueViolation: 
        print("Duplicate car")
        return 0
    except:
        print("Some Error while inserting into db")
        return 1




def old_or_new(old_cars,new_car):
    for index,row in old_cars.iterrows():
        print("Comparing",new_car.car_id,"and",row["car_id"])
        print(type(new_car.car_id))
        print(type(row["car_id"]))
        print("****")
        if str(new_car.car_id)==str(row["car_id"]):
            return False
    return True          

def get_all_cars(all_cars):
    dic={}
    for index,row in all_cars.iterrows():
        current_id=row["car_id"]
        current_ppd=row["ppd"]
        current_feff=row["fuel_efficency"]
        current_cbrand=row["car_brand"]
        current_aval=row["is_aval"]
        dic[current_id]=(current_cbrand,current_ppd,current_feff,current_aval)
    return dic
        

def get_all_available_cars(all_cars):
    dic=get_all_cars(all_cars) 
    ids_to_remove=[]
    for key,val in dic.items():
        if val[3]==0:
            ids_to_remove.append(key)
    for i in range (len(ids_to_remove)):
        del dic[ids_to_remove[i]]

    return dic


def get_one_car(all_cars,car_id):

    car_id=int(car_id)
    dic=get_all_cars(all_cars)
    print("All cars dictionary  = ",dic)
    if car_id not in dic:
        return {}
    result_dic={}
    result_dic[car_id]=dic[car_id]
    print("Filtered car dictionary = ",result_dic)
    #return("number of synonyms = "+str(len(big_dict.keys())))
    return result_dic




def modify_one_car(all_cars,car_object):
    message="Car not found, create a new car with this id"
    for index,row in all_cars.iterrows():
        current_id=row["car_id"]
        print("ids are ",current_id)
        print("searching for ",car_object.car_id)
        if str(current_id)==str(car_object.car_id):
            all_cars.at[index, 'ppd'] = car_object.ppd
            all_cars.at[index, 'fuel_efficency'] = car_object.fuel_efficency
            print("new status ",str(car_object.is_aval))
            all_cars.at[index, 'is_aval'] = str(car_object.is_aval)
            all_cars.to_csv("data/cars.csv",index=False)
            message="Succesfully modified"
            break
    return message



def book_one_car(car_id,user_id):
    
    query1=format(f"update cars set availability='0' where car_id='{car_id}';")
    con = psycopg2.connect(database="testdb", user="abdullahalshaiabani", password="", host="127.0.0.1", port="5432")
    cur=con.cursor()
    try:
        cur.execute(query1)
        con.commit()
        query2=format(f"insert into rented_by values ('{user_id}','{car_id}','u');")
        cur.execute(query2)
        con.commit()
    except:
        print("Some Error while inserting into db")
        return 0

    return 1
    

class User:
    def __init__(self,user_id,username,password,name,QID,telephone,email,address):
        self.user_id=user_id
        self.username=username
        self.password=password
        self.name=name
        self.QID=QID
        self.telephone=telephone
        self.email=email
        self.address=address
    def __str__(self):
        description="ID = "+str(self.user_id)+"\n username = "+str(self.username)
        description+="\n password="+str(self.password)+("\nname = ")+str(self.name)
        description+="\nQID = "+str(self.QID)+"\ntelephone = "+str(self.telephone)
        description+="\nemail = "+str(self.email)+"\naddress = "+str(self.address)
        return description

def user_old_or_new(old_users,new_user):
    for index,row in old_users.iterrows():
        
        if str(new_user.QID)==str(row["QID"]):
            return False
        if str(new_user.username)==str(row["username"]):
            return False    
    return True 
def match_user_password(username,password,All_users):
    for index,row in All_users.iterrows():
        
        if str(username)==str(row["username"]):
            if str(password)==str(row["password"]):
                return True
    return False




def insert_user_into_db(user):
    '''
    0,username,password,name,QID,telephone,email,address
    '''
    print("data  is ")
    print(user.username)
    print(user.password)
    # user_id , password, name, qid, email , address  ,telephone
    query1=format(f"insert into user_table values( '{user.username}','{user.password}' ,'{user.name}','{user.QID}','{user.email}','{user.address}','{user.telephone}');")
    print(query1)
    con = psycopg2.connect(database="testdb", user="abdullahalshaiabani", password="", host="127.0.0.1", port="5432")
    cur=con.cursor()
    try:
        cur.execute(query1)
        con.commit()
    except psycopg2.errors.UniqueViolation: 
        print("Duplicate user/QID")
        return False
    except:
        print("Some Error while inserting into db")
        return False


    return True

def insert_owner_into_db(user):
    '''
    0,username,password,name,QID,telephone,email,address
    '''
    print("data  is ")
    print(user.username)
    print(user.password)

    query1=format(f"insert into car_owner values( '{user.username}','{user.password}' ,'{user.name}','{user.QID}','{user.email}','{user.telephone}','{user.address}');")
    print(query1)
    con = psycopg2.connect(database="testdb", user="abdullahalshaiabani", password="", host="127.0.0.1", port="5432")
    cur=con.cursor()
    try:
        cur.execute(query1)
        con.commit()
    except psycopg2.errors.UniqueViolation: 
        print("Duplicate user/QID")
        return False
    except:
        print("Some Error while inserting into db")
        return False


    return True




def validate_owner_login(username,password):
    con = psycopg2.connect(database="testdb", user="abdullahalshaiabani", password="", host="127.0.0.1", port="5432")
    cur=con.cursor()
    query1=format(f"select count(*) from car_owner where user_id='{username}';")
    print(query1)
    try:
        cur.execute(query1)
        row = cur.fetchone()
        print(row)
        print(type(row))
        if row[0] ==0:
            print("user does not exist")
            return 0
        else:
            query2=format(f"select count(*) from car_owner where user_id='{username}' and password='{password}';")
            cur.execute(query2)
            row = cur.fetchone()
            if row[0]==0:
                print ("password is wrong")
                return 1
            else:
                return 2
    except:
        print("Some issue")


def validate_renter_login(username,password):


    con = psycopg2.connect(database="testdb", user="abdullahalshaiabani", password="", host="127.0.0.1", port="5432")
    cur=con.cursor()
    query1=format(f"select count(*) from user_table where user_id='{username}';")
    print(query1)
    try:
        cur.execute(query1)
        row = cur.fetchone()
        print(row)
        print(type(row))
        if row[0] ==0:
            print("user does not exist")
            return 0
        else:
            query2=format(f"select count(*) from user_table where user_id='{username}' and password='{password}';")
            cur.execute(query2)
            row = cur.fetchone()
            if row[0]==0:
                print ("password is wrong")
                return 1
            else:
                return 2
    except:
        print("Some issue")



    # check if user exists
def all_cars_under_owner(username):

    con = psycopg2.connect(database="testdb", user="abdullahalshaiabani", password="", host="127.0.0.1", port="5432")
    cur=con.cursor()
    query1=format(f"select * from cars c,for_inventory_car_owner f where c.car_id = f.car_id and f.user_id='{username}';")
    print(query1)
    cur.execute(query1)
    row = cur.fetchone()
    owner_cars_dic={}
    owner_cars_dic["rows"]=[]
    while row:
        print(row)
        owner_cars_dic["rows"].append(row)
        row=cur.fetchone()

    return owner_cars_dic
    




def get_return_pending_cars():
    con = psycopg2.connect(database="testdb", user="abdullahalshaiabani", password="", host="127.0.0.1", port="5432")
    cur=con.cursor()
    query1= "select r.user_id , c.car_id ,c.make, c.model,c.number_plate from cars c,returned_cars r where r.car_id=c.car_id;"
    cur.execute(query1)
    row=cur.fetchone()
    cars_to_return={}
    cars_to_return["row"]=[]
    while row:
        cars_to_return["row"].append(row)
        row=cur.fetchone()
    return cars_to_return

    
def accept_cars_for_return_in_db(selected_cars):
    for car_id in selected_cars:
        con = psycopg2.connect(database="testdb", user="abdullahalshaiabani", password="", host="127.0.0.1", port="5432")
        cur=con.cursor()
        query1= format(f"update cars set availability ='1' where car_id='{car_id}';")    
        try:
            cur.execute(query1)
            con.commit()    
            query2=format(f"delete from returned_cars where car_id='{car_id}';")
            cur.execute(query2)
            con.commit()
        except:
            print("Some Error while inserting/updating into db")
            return 0

    return 1
    


def get_all_cars_from_db_for_renter():


    con = psycopg2.connect(database="testdb", user="abdullahalshaiabani", password="", host="127.0.0.1", port="5432")
    cur=con.cursor()
    query1= "select * from cars where availability='1';"
    cur.execute(query1)
    row=cur.fetchone()
    
    all_aval_cars_dic={}
    all_aval_cars_dic["rows"]=[]

    while row:
        print(row)
        all_aval_cars_dic["rows"].append(row)
        row=cur.fetchone()
    return all_aval_cars_dic

def get_all_cars_rented_by_user(user_id):    
    # query1=format(f"select * from rented_by r, cars c  where user_id='{user_id}' and r.car_id=c.car_id and r.status='u';") 
    query1=format(f"select r.car_id, r.date, c.make,c.model ,c.number_plate from rented_by r, cars c  where user_id='{user_id}' and r.car_id=c.car_id and r.status='u';")
    
    con = psycopg2.connect(database="testdb", user="abdullahalshaiabani", password="", host="127.0.0.1", port="5432")
    cur=con.cursor()
    cur.execute(query1)
    row=cur.fetchone()
    all_rented_cars_dic={}
    all_rented_cars_dic["rows"]=[]

    while row:
        print(row)
        all_rented_cars_dic["rows"].append(row)
        row=cur.fetchone()
    return all_rented_cars_dic


    return dic2   

def submit_car_for_return(user_id,car_id):    
    query1=format(f"insert into returned_cars values( '{user_id}','{car_id}');")
    con = psycopg2.connect(database="testdb", user="abdullahalshaiabani", password="", host="127.0.0.1", port="5432")
    cur=con.cursor()
    try:
        cur.execute(query1)
        con.commit()    
        query2=format(f"update rented_by set status ='n' where user_id='{user_id}' and car_id='{car_id}';")
        cur.execute(query2)
        con.commit()

    except:
        print("Some Error while inserting/updating into db")
        return 0

    return 1
