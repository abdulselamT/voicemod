import telebot
from telebot import types,custom_filters
from constants import API_KEY
import prettytable as pt
from telebot.handler_backends import State,StatesGroup
from telebot.storage import StateMemoryStorage
import requests
import json
headersdict={}
corses=['giktreeevevedulaaa']
session = requests.Session()
user_id_pas={}
state_storage = StateMemoryStorage()
bot = telebot.TeleBot(API_KEY,state_storage=state_storage)


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
        #bot.send_message(chat_id=msg.chat.id, text="Invalid Credentials please enter username",)
        #headersdict.pop(tg_user_name)

        #user_id_pas.pop(msg.from_user.id)
    
        
        return False
    headersdict[tg_user_name]["client"] = x["client"]
    headersdict[tg_user_name]["expiry"] = x["expiry"]
    headersdict[tg_user_name]["uid"] = x["uid"]
    bot.delete_message(chat_id=msg.chat.id, message_id=msg.message_id)
    bot.send_message(msg.chat.id, 'you have successfully logged in ')

    return True

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
            table.add_row([symbol, price[:],change])

        bot.reply_to(msg,f'{table}')







class MyStates(StatesGroup):
    useername=State()
    password=State()
    assesment=State()





@bot.message_handler(state='*',commands=['start','login'])
def start_ex(message):
    bot.delete_state(message.from_user.id,message.chat.id)
    bot.set_state(message.from_user.id, MyStates.useername, message.chat.id)
    bot.send_message(message.chat.id, 'Hi, write me a username')

@bot.message_handler(state=MyStates.useername)
def name_get(message):
    
    bot.send_message(message.chat.id, 'Enter Password')
    bot.set_state(message.from_user.id, MyStates.password, message.chat.id)
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['username'] = message.text


@bot.message_handler(state=MyStates.password)
def name_get(message):
    
    bot.set_state(message.from_user.id, MyStates.assesment, message.chat.id)
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['password'] = message.text
    flag=loginn(data['username'],data['password'],message)
    if flag:

        select_course(message)
    else:
        bot.send_message(message.chat.id, 'username or password is incorrect')
        bot.set_state(message.from_user.id, MyStates.useername, message.chat.id)
        bot.send_message(message.chat.id, 'Enter username')


@bot.message_handler(state=MyStates.assesment)
def assesmen(msg):

    send_hello_message(msg)

@bot.message_handler(state='*',commands=['logout'])
def cancelled(msg):
    bot.send_message(msg.chat.id,"you are logged out")
    bot.delete_state(msg.from_user.id,msg.chat.id)


bot.add_custom_filter(custom_filters.StateFilter(bot))
bot.polling()
