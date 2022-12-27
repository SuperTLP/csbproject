from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse
from django.shortcuts import render, redirect
from hashlib import md5
import sqlite3
import string
class View:
    def __init__(self):
        pass

    def home(self,request):
        return render(request, "register.html")

    def encrypt_message(self,password):
        password_letters = list(password)
        ascii_letters=string.ascii_letters+"1234567890!!#€%&/()=?"
        print(ascii_letters)
        for i in range(0,len(password_letters)):
            index=ascii_letters.index(password_letters[i])
            password_letters[i]=ascii_letters[index-1]
        return ''.join(password_letters)

    def register(self,request):
        db=sqlite3.connect("db.sqlite3")
        user=request.POST.get("username")
        cursor = db.cursor()
        passwd = request.POST.get("password")
        encrypted_password= md5(passwd.encode()).hexdigest()
        cursor.execute("insert into users (username, password, admin) values ('{}', '{}', 0) returning id;".format(user, encrypted_password))
        id=cursor.fetchone()[0]
        cursor.close()
        db.commit()
        res=HttpResponseRedirect("/app")
        res.set_cookie("id",id)
        return res

    def app(self, request):
        keyword=request.GET.get("keyword")
        if keyword==None:
            keyword=""
        db=sqlite3.connect("db.sqlite3")
        try:
            id = request.COOKIES["id"]
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
        return TemplateResponse(request, "app.html", {"names":names, "user":user, "messages":messages})

    def logout(self, request):
        res = HttpResponseRedirect("/")
        res.delete_cookie("id")
        res.delete_cookie("username")
        return res

    def login(self, request):
        if request.method=="GET":
            return render(request, "login.html")

        db=sqlite3.connect("db.sqlite3")
        user=request.POST.get("username")
        cursor = db.cursor()
        passwd = request.POST.get("password")
        encrypted_password= md5(passwd.encode()).hexdigest()
        user_id=cursor.execute(
            """
            select id from users where username=? and password=?
            """, 
            [user, encrypted_password]).fetchone()
        if user_id==None:
            return redirect("/login")
        res=HttpResponseRedirect("/app")
        res.set_cookie("id",user_id[0])
        return res

    def send_message(self, request):
        db=sqlite3.connect("db.sqlite3")
        sender_id = request.COOKIES["id"]
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




    
