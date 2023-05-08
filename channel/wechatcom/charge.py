import datetime


def check_count(username):
    storage_str = redis_db.get(f"user:{username}")
    storage_str = str(storage_str, 'utf-8')
    userinfo = storage_str.split("|")
    left_count = userinfo[2]
    if int(left_count)<=0:
        return False,"您余额不足啦,需要充值次数后方可使用,谢谢"
    else:
        return True,"成功"

def reduce_count(username):
    try:
        storage_str = redis_db.get(f"user:{username}")
        storage_str = str(storage_str, 'utf-8')
        userinfo = storage_str.split("|")
        left_count = userinfo[2]
        password = userinfo[1]
        usertype = userinfo[3]
        registerDate = userinfo[4]
        recommender = userinfo[5]
        lastChargeDate = userinfo[6]
        new_left_count = int(left_count)-1
        if new_left_count<=0:
            new_left_count=0 # 以免出现负数
        storage_string = assemble_userinfo(username, password, new_left_count, usertype, registerDate, recommender,lastChargeDate)
        # storage_str = username+"|"+password+"|"+str(new_left_count)
        redis_db.set(f"user:{username}", storage_string)
        return True
    except:
        return False

def assemble_userinfo(username,password,count,userType,registerDate,recommender,lastChargeDate):
    # 组装用户string
    storage_str = username + "|" + password + "|" + str(count) + "|"+userType+"|" + registerDate + "|"+recommender+"|"+lastChargeDate
    return storage_str

def return_storage_userString_list(username):
    # 根据用户名返回他存储的string
    storage_str = redis_db.get(f"user:{username}")
    storage_str = str(storage_str, 'utf-8')
    userinfo = storage_str.split("|")
    return userinfo

def login(username,password):
    # 1 验证长度
    if len(username)>11:
        return gr.Textbox.update(visible=True),gr.Textbox.update(visible=True),gr.Button.update(visible=True),gr.Textbox.update(visible=True),gr.Textbox.update(visible=True),gr.Textbox.update(visible=True),gr.Button.update(visible=True),gr.Textbox.update(visible=True),gr.Markdown.update(value="用户名长度超出限制"),"Notlogin"
    if len(password)>20:
        return gr.Textbox.update(visible=True),gr.Textbox.update(visible=True),gr.Button.update(visible=True),gr.Textbox.update(visible=True),gr.Textbox.update(visible=True),gr.Textbox.update(visible=True),gr.Button.update(visible=True),gr.Textbox.update(visible=True),gr.Markdown.update(value="密码长度超出限制"),"Notlogin"
    # 2 查找用户是否存在
    if not redis_db.exists(f"user:{username}"):
        return gr.Textbox.update(visible=True),gr.Textbox.update(visible=True),gr.Button.update(visible=True),gr.Textbox.update(visible=True),gr.Textbox.update(visible=True),gr.Textbox.update(visible=True),gr.Button.update(visible=True),gr.Textbox.update(visible=True), gr.Markdown.update(value="用户不存在:"+username),"Notlogin"
    else:
        # 3 验证密码
        storage_str = redis_db.get(f"user:{username}")
        storage_str = str(storage_str,'utf-8')
        userinfo = storage_str.split("|")
        storage_password=userinfo[1]
        if password!=storage_password:
            return gr.Textbox.update(visible=True),gr.Textbox.update(visible=True),gr.Button.update(visible=True),gr.Textbox.update(visible=True),gr.Textbox.update(visible=True),gr.Textbox.update(visible=True),gr.Button.update(visible=True),gr.Textbox.update(visible=True), gr.Markdown.update(value="密码不对!"),"Notlogin"
        # 登录成功会吧用户名密码存在一个地方，用户每次询问的时候带上用户名和密码，以便查询剩余额度
        return gr.Textbox.update(visible=False),gr.Textbox.update(visible=False),gr.Button.update(visible=False),gr.Textbox.update(visible=False),gr.Textbox.update(visible=False),gr.Textbox.update(visible=False),gr.Button.update(visible=False),gr.Textbox.update(visible=False),gr.Markdown.update(value="登录成功，欢迎 " +" "+ username + "!"),username
        # return gr.Textbox.update(visible=False),gr.Textbox.update(visible=False),gr.Textbox.update(visible=False),gr.Button.update(visible=False),gr.Textbox.update(visible=False),gr.Textbox.update(visible=False),gr.Textbox.update(visible=False),gr.Button.update(visible=False),"Welcome" +" "+ username + "!",username

def register(username,password1,password2):
    # username|password|count|(free/paid)|registerDate|recommender
    # 0 验证是否输入为空
    if not bool(username) or not bool(password1):
        return gr.Textbox.update(visible=True),gr.Textbox.update(visible=True),gr.Textbox.update(visible=True),gr.Button.update(visible=True),gr.Markdown.update(value="用户名密码不能为空!")
    # 1 验证密码是否一致
    if password1!=password2:
        return gr.Textbox.update(visible=True),gr.Textbox.update(visible=True),gr.Textbox.update(visible=True),gr.Button.update(visible=True),gr.Markdown.update(value="两次输入的密码不匹配!")
    # 2.1 验证长度
    if len(username)>20 or len(password1)>20:
        return gr.Textbox.update(visible=False),gr.Textbox.update(visible=True),gr.Textbox.update(visible=True),gr.Button.update(visible=True),gr.Markdown.update(value="用户名或密码长度超出限制!")
    # 2.2 验证长度
    if len(username) < 6 or len(password1) < 6:
        return gr.Textbox.update(visible=False),gr.Textbox.update(visible=True),gr.Textbox.update(visible=True),gr.Button.update(visible=True),gr.Markdown.update(value="用户名或密码长度太短")
    # 3 查找是否存在
    if not redis_db.exists(f"user:{username}"):  # 新用户
        registerDate = datetime.datetime.today().strftime("%Y-%m-%d")
        storage_string = assemble_userinfo(username,password1,3,"free",registerDate,"none")
        redis_db.set(f"user:{username}", storage_string)
        return gr.Textbox.update(visible=False),gr.Textbox.update(visible=False),gr.Textbox.update(visible=False),gr.Button.update(visible=False),gr.Markdown.update(value="注册成功:"+username+" 请登录后使用,您有三次免费咨询的机会")
    else:
        return gr.Textbox.update(visible=True),gr.Textbox.update(visible=True),gr.Textbox.update(visible=True),gr.Button.update(visible=True),gr.Markdown.update(value="用户已经存在,请输入一个用户名!")

def charge_count(username,money,recommender="none"):
    import random
    import math
    try:
        money = int(money)
    except ValueError:
        return "充值失败,您输入金额不是数字"
    money = math.ceil(money)  # 向上取整
    if money <= 0:
        return "充值失败,充值数额不能小于0"

    flag=5 # 默认5倍系数，也就是1块钱5次
    if money < 50:
        flag = 5
    elif money < 100:
        flag = 7
    elif money >= 100:
        flag = 1000

    available_count = money * flag
    if not redis_db.exists(f"user:{username}"):  # 如果充值的用户不存在则创建该用户，并且设置随机默认密码
        password = username + str(random.randint(0, 100)) + str(random.randint(0, 9)) + str(
            random.randint(0, 9)) + str(random.randint(0, 9))
        storage_string = username + "|" + password + "|" + str(available_count)
        # storage_str(username)
        redis_db.set(f"user:{username}", storage_string)
        return f"充值成功，因为您输入的账号不存在，已经为您自动创建{username}的账号，密码是{password},您可以使用的次数为{str(available_count)}次"
    else:
        userinfo = return_storage_userString_list(username)
        password = userinfo[1]
        left_count = userinfo[2]
        usertype = userinfo[3]
        registerDate = userinfo[4]
        recommender_old = userinfo[5]
        new_count = int(left_count) + available_count
        # 首先给充值人充值
        storage_string = assemble_userinfo(username, password, new_count, usertype, registerDate, recommender_old)
        redis_db.set(f"user:{username}", storage_string)
        return_message = f"充值成功，已经为账号{username}充值{str(available_count)}次数,充值后剩余的次数为{str(new_count)}次."
        message2 = ""
        if recommender != "none":
            # 如果推荐人字段有值，则推荐人也给充值，原则是充值人金额的20%
            available_count = money * flag * 0.2
            userinfo = return_storage_userString_list(username)
            password = userinfo[1]
            left_count = userinfo[2]
            usertype = userinfo[3]
            registerDate = userinfo[4]
            recommender_old = userinfo[5]
            new_count = int(left_count) + available_count
            new_storage_str = assemble_userinfo(username,password,new_count,usertype,registerDate,recommender_old)
            redis_db.set(f"user:{username}", new_storage_str)
            message2 = f"推荐人{username}也充值成功，充值{str(available_count)}次数,充值后剩余的次数为{str(new_count)}次"
        charge_result = return_message + message2
        return charge_result
