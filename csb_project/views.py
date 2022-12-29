from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse
from django.shortcuts import render, redirect
import json
import bcrypt
from hashlib import md5
import sqlite3
import string


class View:
    def __init__(self):
        pass

    def home(self,request):
        return render(request, "register.html")

    def register(self,request):
        db=sqlite3.connect("db.sqlite3")
        user=request.POST.get("username")
        passwd = request.POST.get("password")

        #weak password fix:
        # new_passwd = str(passwd)
        # if not self.check_password_allowed(new_passwd):
        #     return TemplateResponse(request, "register.html", 
        #     {
        #         "error_message":"Password must include lowercase letters, capital letters, numbers and symbols and be at least 8 characters long"
        #     })

        encrypted_password= md5(passwd.encode()).hexdigest()

        #Fix md5 hashing to bcrypt with salt:
        #encrypted_password= bcrypt.hashpw(passwd.encode("utf8"), bcrypt.gensalt()).decode()

        id=db.cursor().execute("insert into users (username, password, admin) values ('{}', '{}', 0) returning id;".format(user, encrypted_password)).fetchone()[0]
        db.commit()

        #fix stack trace exposure:
        # try:
        #     id=db.cursor().execute("insert into users (username, password, admin) values ('{}', '{}', 0) returning id;".format(user, encrypted_password)).fetchone()[0]
        #     db.commit()
        # except Exception:
        #     return TemplateResponse(request, "register.html", {"error_message": "Username taken"})

        #fix sql injection 1:
        # id=db.cursor().execute("insert into users (username, password, admin) values (?, ?, 0) returning id;", [user, encrypted_password]).fetchone()[0]

        res=HttpResponseRedirect("/app")
        res.set_cookie("id",id)

        #cookie fix
        # request.session["id"]=id

        return res

    ##weak password fix:
    def check_password_allowed(self, password):
        special_characters="!#€%&/()=;:_"

        if len(password)<8:
            return False

        has_special_character=False
        has_capital_letter=False
        has_number=False
        has_lower_case_letter=False

        for char in password:
            if char in special_characters:
                has_special_character=True
            if char in string.ascii_uppercase:
                has_capital_letter=True
            if char in "1234567890":
                has_number=True
            if char in string.ascii_lowercase:
                has_lower_case_letter=True

        return has_special_character and has_capital_letter and has_number and has_lower_case_letter
        
        
        
    def app(self, request):
        keyword=request.GET.get("keyword")
        if keyword==None:
            keyword=""
        db=sqlite3.connect("db.sqlite3")
        try:
            id = request.COOKIES["id"]
            #cookie fix
            # id=request.session["id"]
            names = db.cursor().execute("select username, id from users").fetchall()
            user=[user for user in names if user[1]==int(id)][0][0]
            names = [user for user in names if user[1]!=int(id)]
        except Exception:
            return redirect("/")
        db.commit()

        messages=db.cursor().execute(
            """
            select username, title, content 
            from messages join users on messages.sender_id = users.id  where receiver_id='{}'
            and title like '%{}%'"""
        .format(id, keyword)).fetchall()

        #fix to sql injection part 2:
        # messages=db.cursor().execute(
        #     """
        #     select username, title, content 
        #     from messages join users on messages.sender_id = users.id  where receiver_id=?
        #     and title like ?""", (id, "%"+keyword+"%")).fetchall()

        return TemplateResponse(request, "app.html", 
        {"names":names, "user":user, 
        "messages":messages})

    def logout(self, request):
        res = HttpResponseRedirect("/")
        res.delete_cookie("id")
        res.delete_cookie("username")
        #cookie fix
        #Destroy session:
        # request.session.flush()
        return res

    def login(self, request):
        if request.method=="GET":
            return render(request, "login.html")

        db=sqlite3.connect("db.sqlite3")
        username=request.POST.get("username")
        cursor = db.cursor()
        passwd = request.POST.get("password")
        encrypted_password= md5(passwd.encode()).hexdigest()

        #fix - change md5 to bcrypt with salt part 2:
        # data=db.cursor().execute("select id, password from users where username=?",[username]).fetchone()
        # if (data==None):
        #     return redirect("/login")
        # result = bcrypt.checkpw(passwd.encode(), data[1].encode())
        # if not result:
        #     redirect("/login")

        data=cursor.execute(
            """
            select id from users where username=? and password=?
            """, 
            [username, encrypted_password]).fetchone()

        if data==None:
            return redirect("/login")

        res=HttpResponseRedirect("/app")

        res.set_cookie("id",data[0])

        #cookie fix
        # set session variable rather than cookie:
        # request.session["id"]=data[0]

        return res

    def send_message(self, request):
        db=sqlite3.connect("db.sqlite3")
        sender_id = request.COOKIES["id"]

        #cookie fix
        # sender_id=request.session["id"]

        content=request.POST.get("content")
        title=request.POST.get("title")
        receiver_id=request.POST.get("receiver_id")
        print(receiver_id)
        db.cursor().execute(
        """
        insert into messages (sender_id, receiver_id, title, content) values (?, ?, ?, ?)
        """,
        [sender_id, receiver_id, title, content])
        db.commit()
        return redirect("/app")




    
