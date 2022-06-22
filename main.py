import telebot
from telebot import types
from constants import API_KEY
import prettytable as pt
from telegram import ParseMode
from telegram.ext import *

import requests
import json
bot = telebot.TeleBot(API_KEY,parse_mode=None)
headersdict={}
corses=['giktreeevevedulaaa']
session = requests.Session()
user_id_pas={}




def loginn(user,pas,msg):
    params = {'user_name': user, 'password': pas}
    s = session.post('http://10.240.1.89/api/auth/sign_in', params)
    tg_user_name = msg.from_user.username
    global header
    x = s.headers
    header = {"Accept": "*/*",
              "Accept-Encoding": "gzip, deflate",
              "Accept-Language": "en-US,en;q=0.5",
              "Connection": "keep-alive",
              "Content-Length": "625",
              "content-type": "application/json",
              "expiry": "1644831505",
              "Host": "10.240.1.89",
              "Origin": "http://10.240.1.89",
              "Referer": "http://10.240.1.89/",
              "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:96.0) Gecko/20100101 Firefox/96.0"
              }
    headersdict[tg_user_name]=header
    try:
        headersdict[tg_user_name]["access-token"] = x["access-token"]
    except:
        bot.send_message(chat_id=msg.chat.id, text="Invalid Credentials please enter username",)
        headersdict.pop(tg_user_name)
        print(user_id_pas)
        user_id_pas.pop(msg.from_user.id)
        print(user_id_pas)
        
        return 5
    headersdict[tg_user_name]["client"] = x["client"]
    headersdict[tg_user_name]["expiry"] = x["expiry"]
    headersdict[tg_user_name]["uid"] = x["uid"]
    bot.delete_message(chat_id=msg.chat.id, message_id=msg.message_id)
def generate_corurse(msg):
    x=msg.from_user.username
    try:
        header=headersdict[x]
    except:
        start_keyboards(msg)
        return 0
    s = session.post('http://10.240.1.89/api//graphql', headers=header, json={"operationName": None, "variables": {},"query": "{\n  studentCourseEnrollments {\n    id\n    course {\n      id\n      titleAndCode\n      __typename\n    }\n    __typename\n  }\n}\n"})
    asseskey = {}
    res = json.loads(s.text)

    for j in res["data"]['studentCourseEnrollments']:
        asseskey[j['course']['titleAndCode'].replace(" ", "")] = j['id']
    return asseskey


def see_course_assesment(gh,msg):
    x=msg.from_user.username
    header=headersdict[x]
    a = session.post('http://10.240.1.89/api//graphql', headers=header,
                     json={"operationName": "assessmentResultForEnrollment", "variables": {"id": gh},
                           "query": "query assessmentResultForEnrollment($id: ID!) {\n  assessmentResultForEnrollment(id: $id) {\n    id\n    instructorName\n    sumOfMaximumMark\n    sumOfResults\n    course {\n      id\n      courseTitle\n      courseCode\n      __typename\n    }\n    studentGrade {\n      id\n      letterGrade\n      __typename\n    }\n    assessmentResults {\n      id\n      result\n      assessment {\n        id\n        assessmentName\n        maximumMark\n        assessmentType\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}\n"})
    
    res = json.loads(a.text)
    myassesmentout = {}

    for j in res['data']['assessmentResultForEnrollment']['assessmentResults']:
        a= j['result']
        if not a :
            a=' '

        myassesmentout[j['assessment']['assessmentName']] = [j['assessment']['maximumMark'],a]
    try:
        myassesmentout['total'] = [res["data"]['assessmentResultForEnrollment']['studentGrade']['letterGrade'],res["data"]['assessmentResultForEnrollment']['sumOfResults']]
    except:
        myassesmentout['total'] = [' ',res["data"]['assessmentResultForEnrollment']['sumOfResults']]
        

    return myassesmentout

@bot.message_handler(commands=["start"])
def start_keyboards(msg,xy=0):
    markup=types.ReplyKeyboardRemove(selective=False)
    markup = types.ReplyKeyboardMarkup(row_width=1)
    btn1 = types.KeyboardButton("/login")
    btn3 = types.KeyboardButton("/help")
    markup.add(btn1, btn3)
    if xy:
        bot.send_message(chat_id=xy,text="Invalid credentials please enter ID ",reply_markup=markup)
    return True
    


@bot.message_handler(commands=["login"])
def send_help_message(msg):
    markup = types.ReplyKeyboardMarkup(row_width=1)
    bot.send_message(chat_id=msg.chat.id, text="please enter user name")
    btn1 = types.KeyboardButton("/cancel")
    markup.add(btn1)
    return True










@bot.message_handler(commands=corses)
def send_hello_message(msg):
    table = pt.PrettyTable(['res', 'type', 'max'])
    table.align['Symbol'] = 'l'
    table.align['Price'] = 'l'
    table.align['Change'] = 'l'
    data = [
    ]
    y = generate_corurse(msg)
    if y and msg.text.replace('/', '') in y :
        a = y[msg.text.replace('/', '')]
        x = see_course_assesment(a, msg)
        c = ""
        for j in x:
            data.append((x[j][1] ,j,x[j][0]))
        for symbol, price, change in data:
            table.add_row([symbol, price[:3],change])

        bot.reply_to(msg,f'<pre>{table}</pre>', parse_mode=ParseMode.HTML)


@bot.message_handler(commands=["help"])
def send_help_message(msg):
    bot.reply_to(msg,"i will help you")
   
@bot.message_handler(commands=["go"])
def select_course(msg):
    global corses
    y=generate_corurse(msg)
    l=list(y.keys())
    corses=l[:]
    markup=types.ReplyKeyboardMarkup(row_width=1)
    btn3 = types.KeyboardButton("/logout")
    markup.add(btn3)
    for k in l:
        btn2 = types.KeyboardButton("/"+k)
        markup.add(btn2)
    bot.send_message(chat_id=msg.chat.id,text="please select a course ",reply_markup=markup)

@bot.message_handler(commands=["logout"])
def send_command_messa(msg):
    markup=types.ReplyKeyboardRemove(selective=False)
    bot.send_message(chat_id=msg.chat.id,text="logged_out",reply_markup=markup)
    headersdict.pop(msg.from_user.username)
    start_keyboards(msg)




@bot.message_handler(content_types=['text'])
def function_name(message):
    x=message.text
    stut=message.from_user.id
    if stut in user_id_pas:
        if len(user_id_pas[stut])==1:
            user_id_pas[stut].append(x)
            ree=loginn(user_id_pas[stut][0],x,message)
        else :
            bot.send_message(chat_id=message.chat.id,text="Enter Password")

            user_id_pas[stut]=[x]
            return 1
    else:
        user_id_pas[stut]=[x]
        bot.send_message(chat_id=message.chat.id,text="Enter Password else")
        return 1
        
    username=message.from_user.username
    if x[0]=='/':
        send_hello_message(message)
        return 1
   
    
    if ree != 5:
        y=generate_corurse(message)
        select_course(message)
    else:
        bot.send_message(chat_id=message.chat.id,text="Invalid credentials")
        bot.send_message(chat_id=message.chat.id,text="Enter ID")
        


bot.polling()
