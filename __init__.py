from flask import Flask,url_for,render_template,redirect,request,session,Markup
from flask_pymongo import PyMongo
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
import datetime
from plotly.offline import plot
from plotly.graph_objs import Scatter
app=Flask(__name__)
crypt=Bcrypt()
app.config['MONGO_DBNAME']='online_attendance'
app.config['MONGO_URI']='mongodb://AjishKalia99:Ajish123!@ds123513.mlab.com:23513/online_attendance'
Client=PyMongo(app)
StuBase=Client.db.online_attendance['StudentFinal1']
TeachBase=Client.db.online_attendance['TeacherFinal1']
app.secret_key="MySecret"
Date1=""

def Create_Register(Name):
    NewBase=Client.db.online_attendance[Name]
    return NewBase

def Logout():
    session.pop('Username',None)
    session.pop('Password',None)

Register={}

@app.route("/")
def Home():
    Logout()
    return render_template("main.html",Logout=True)

@app.route("/Teacher_Login")
def Teach_Login():
    return render_template("Teacher_Login.html",Logout=True)

@app.route("/Student_Login")
def Stu_Login():
    return render_template("Student_Login.html",Logout=True)

@app.route("/Add_Stu")
def Add():
    Temp=TeachBase.find_one({'Teach_Id':session['username']})
    return render_template("Add_Student.html",Logout=False,Data=Temp['Name'])

@app.route("/Update_Rec")
def Update():
    Temp=TeachBase.find_one({'Teach_Id':session['username']})
    return render_template("Update_Rec.html",Logout=False,Data=Temp['Name'],Success=False)


@app.route("/Teacher",methods=['POST','GET'])
def Teach_Res():
    global Register
    session['username']=request.form['TeachID']
    session['Password']=request.form['TeachPass']
    Temp=TeachBase.find_one({'Teach_Id':session['username']})
    if(Temp==None):
        Logout()
        return render_template("Teacher_Login.html",User_Found=False,Logout=True)
    if(crypt.check_password_hash(Temp['Password'],session['Password'])):
        Value=Register[Temp['Teach_Id']].find()
        return render_template("Teacher_Result.html",Data=Temp['Name'],Logout=False,Value=Value)
    else:
        Logout()
        return render_template("Teacher_Login.html",Login=False,Logout=True)

@app.route("/TeacherSgnup",methods=['POST','GET'])
def Teach_Sign():
    global Register
    Name=request.form['TeachName']
    Id=request.form['TeachID']
    Phone=request.form['Phone']
    Pass=request.form['TeachPass']
    HashPass=crypt.generate_password_hash(Pass)
    Temp=TeachBase.find_one({'Teach_Id':Name})
    if (Temp==None):
        TeachBase.insert_one({'Name':Name,'Teach_Id':Id,'Phone':Phone,'Password':HashPass})
        Register[Id]=Create_Register(Name)
        return render_template("Succ_Sign.html",Name=Name,Logout=True)
    else:
        return render_template("Teacher_Login.html",User_Exists=True,Logout=True)

@app.route("/Student",methods=['POST','GET'])
def Stu_Res():
    global Register
    session['username']=request.form['StuID']
    session['Password']=request.form['StuPass']
    Temp=StuBase.find_one({'Stu_Id':session['username']})
    Results=[]
    if(Temp==None):
        Logout()
        return render_template("Student_Login.html",User_Found=False,Logout=True)
    if(crypt.check_password_hash(Temp['Password'],session['Password'])):
        val=Temp['Subjects']
        for i in val:
            Value=Register[i].find_one({'name':Temp['Name']})
            Results.append(Value)
        return render_template("Student_Subjects.html",Data=Temp['Name'],Logout=False,val=val,Dis=True)
    else:
        Logout()
        return render_template("Student_Login.html",Login=False,Logout=True)



@app.route("/StuSgnup",methods=['POST','GET'])
def Stu_Sign():
    Name=request.form['StuName']
    Id=request.form['StuID']
    Phone=request.form['StuPhone']
    Pass=request.form['StuPass']
    HashPass=crypt.generate_password_hash(Pass)
    Subs=[]
    Temp=StuBase.find_one({'Stu_Id':Id})
    if (Temp==None):
        StuBase.insert_one({'Name':Name,'Stu_Id':Id,'Phone':Phone,'Password':HashPass,'Subjects':Subs})
        return render_template("Succ_Sign.html",Name=Name,Logout=False)
    else:
        return render_template("Student_Login.html",User_Exists=True,Logout=True)

@app.route("/AddStudent",methods=['POST','GET'])
def Add_Student():
    global Register
    Temp=TeachBase.find_one({'Teach_Id':session['username']})
    Add=request.form['Student']
    emp=StuBase.find_one({'Name':Add})
    Already=Register[session['username']].find_one({'Name':Add})
    if(Already==None):
        if(emp!=None):
            List=emp['Subjects']
            List.append(session['username'])
            StuBase.update({'Name':Add},{'$set':{'Subjects':List}})
            Register[Temp['Teach_Id']].insert_one({'name':Add})
            val=Register[Temp['Teach_Id']].find()
            return render_template("Teacher_Result.html",Data=Temp['Name'],Found=True,Logout=False,Val=val)
        else:
            return render_template("Add_Student.html",Data=Temp['Name'],Found=False,Logout=False)
    else:
        return render_template("Add_Student.html",Data=Temp['Name'],Already=True,Logout=False,Found=True)

@app.route('/Update_Attendance',methods=['POST','GET'])
def Update_Attend():
    Name=request.form['Name']
    Attend=request.form['Attendance']
    Temp=TeachBase.find_one({'Teach_Id':session['username']})
    date=datetime.date.today()
    date=str(date)
    print(date)
    date=datetime.datetime.strptime(date,"%Y-%m-%d")
    date=str(date)
    Register[Temp['Teach_Id']].update({'name':Name},{'$set':{date:Attend}})
    val=Register[Temp['Teach_Id']].find()
    return render_template("Teacher_Result.html",Data=Temp['Name'],Logout=False,Val=val)

@app.route("/UpdateRecord",methods=['POST','GET'])
def Record_Up():
    global Register
    global Date1
    Temp=TeachBase.find_one({'Teach_Id':session['username']})
    Date=request.form['Date']
    Today=datetime.date.today()
    Today=str(Today)
    Today=datetime.datetime.strptime(Today,"%Y-%m-%d")
    try:
        date=datetime.datetime.strptime(Date,"%Y-%m-%d")
        if (date<Today):
            Val=Register[Temp['Teach_Id']].find()
            Date1=str(date)
            return render_template("Update_Rec.html",Data=Temp['Name'],Logout=False,Success=True,Date=Date1,Val=Val)
        else:
            return render_template("Update_Rec.html",Data=Temp['Name'],Logout=False,Valid=False,Success=False)
    except:
        return render_template("Update_Rec.html",Data=Temp['Name'],Logout=False,Valid=False,Success=False)


@app.route('/Attend_up',methods=['POST','GET'])
def Attend_Up():
    global Date1
    Name=request.form['Name']
    Attend=request.form['Attendance']
    Temp=TeachBase.find_one({'Teach_Id':session['username']})
    Register[Temp['Teach_Id']].update({'name':Name},{'$set':{Date1:Attend}})
    val=Register[Temp['Teach_Id']].find()
    return render_template("Update_Rec.html",Data=Temp['Name'],Logout=False,Success=True,Date=Date1,Val=val)


@app.route("/Students_Attendance/<Subject>")
def Attendance(Subject):
    global Register
    Dates=[]
    DatesF=[]
    No=['_id','name']
    AttF=[]
    Att=[]
    attended=0
    total=0
    per=0
    Temp=StuBase.find_one({'Stu_Id':session['username']})
    Attendance=Register[Subject].find_one({'name':Temp['Name']})
    for i in Attendance:
            Dates.append(i)
            total=total+1
            Att.append(Attendance[i])
            if(Attendance[i]==1):
                attended=attended+1
    for j in Dates:
        if(j in No):
            continue
        else:
            AttF.append(Attendance[j])
            DatesF.append(j)
    per=len(AttF)*100/len(DatesF)
    graph=plot([Scatter(x=DatesF,y=AttF,mode="markers")],output_type='div')
    return render_template("Student_Subjects.html",Data=Temp['Name'],Logout=False,Dates=Dates,Att=Att,Percent=per,Dis=False,graph=Markup(graph))


@app.route('/Subject')
def Subject():
    Temp=StuBase.find_one({'Stu_Id':session['username']})
    val=Temp['Subjects']
    return render_template("Student_Subjects.html",Data=Temp['Name'],Logout=False,val=val,Dis=True)

@app.route('/Teacher_Home')
def Back():
    Temp=TeachBase.find_one({'Teach_Id':session['username']})
    val=Register[Temp['Teach_Id']].find()
    return render_template("Teacher_Result.html",Data=Temp['Name'],Logout=False,Val=val)


@app.route("/Logout")
def Out():
    Logout()
    return render_template("main.html",Logout=True)


if __name__=="__main__":
    app.run(debug=True)
