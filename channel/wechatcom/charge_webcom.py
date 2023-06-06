import datetime
import math
import random
import redis
redis_db = redis.StrictRedis(host="localhost", port=6379, password="")

'''
user information:
0 username : user's name
1 password : username + str(random.randint(0, 100)) + str(random.randint(0, 9)) + str(random.randint(0, 9)) + str(random.randint(0, 9))
2 left_count: user left query count
3 usertype: free/paid
4 registerDate: user first login/send msg date
5 recommender: paid user's recommender , free user is recommender is "none"
6 lastChargeDate: paid user last charge date , free user date is "2000-01-01"
7 chargeMoney: user actually paid money , free user chargeMoney is "0"
8 lastChargeMoney: user last time charge money
'''


def check_count(username):
    storage_str = redis_db.get(f"user:{username}")
    storage_str = str(storage_str, 'utf-8')
    userinfo = storage_str.split("|")
    left_count = userinfo[2]
    chargeMoney = int(userinfo[8])

    errMsg1 = "您余额不足啦,需要充值次数后方可使用,谢谢,充值10元50次,50元400次,100元1000次,有效期均为一年。如果您推荐他人也充值,您可以获得他充值点数的20%,比如他充值10块,您作为推荐人可以获得50*0.2次免费回答。"
    if int(float(left_count))<=0:
        return False,errMsg1
    else:
        return True, "success"
        # compare date 看是否过期，3个月以后再启用
        if chargeMoney<=10: # 充值小于10块，可用3个月，充值小于100块，可用半年，充值大于100块，可用一年
            useable_days = 93
        elif chargeMoney<100:
            useable_days = 186
        elif chargeMoney>=100:
            useable_days = 365
        lastChargeDate = userinfo[6]
        date = datetime.datetime.strptime(lastChargeDate, "%Y-%m-%d")
        today = datetime.datetime.today()
        diff = (today - date).days
        errMsg2 = "您的充值已经超过一年,未使用的次数已经过期.需要重新充值次数后方可使用,谢谢,充值10元50次,50元400次,100元1000次,有效期均为一年。如果您推荐他人也充值,您可以获得他充值点数的20%,比如他充值10块,您作为推荐人可以获得50*0.2次免费回答。"
        if diff > useable_days:
            return False,errMsg2
        else:
            return True,"success"



def reduce_count(username,count=1):
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
        chargeMoney = userinfo[7]
        lastchargeMoney = userinfo[8]
        new_left_count = int(left_count)-count
        if new_left_count<=0:
            new_left_count=0 # 以免出现负数
        storage_string = assemble_userinfo(username, password, new_left_count, usertype, registerDate, recommender,lastChargeDate,chargeMoney,lastchargeMoney)
        redis_db.set(f"user:{username}", storage_string)
        return True
    except:
        return False

def assemble_userinfo(username,password,count,userType,registerDate,recommender,lastChargeDate,chargeMoney,lastchargeMoney):
    # 组装用户string
    storage_str = username + "|" + password + "|" + str(count) + "|"+userType+"|" + registerDate + "|"+recommender+"|"+lastChargeDate+"|"+str(chargeMoney)+"|"+str(lastchargeMoney)
    return storage_str

def return_storage_userString_list(username):
    # 根据用户名返回他存储的string
    storage_str = redis_db.get(f"user:{username}")
    storage_str = str(storage_str, 'utf-8')
    userinfo = storage_str.split("|")
    return userinfo

def check_account(username):
    # username|password|count|(free/paid)|registerDate|recommender|lastChargeDate
    password = username + str(random.randint(0, 100)) + str(random.randint(0, 9)) + str(
        random.randint(0, 9)) + str(random.randint(0, 9))
    if not redis_db.exists(f"user:{username}"):  # 新用户
        registerDate = datetime.datetime.today().strftime("%Y-%m-%d")
        storage_string = assemble_userinfo(username,password,3,"free",registerDate,"none","2000-01-01","0","0")
        redis_db.set(f"user:{username}", storage_string)
        return True,"success"
    else:
        # 检查次数
        return check_count(username)



def charge_count(username,actual_money,recommender="none"):
    import random
    import math
    try:
        money = int(actual_money)
    except ValueError:
        return "充值失败,您输入金额不是数字"
    money = math.ceil(money)  # 向上取整
    if money <= 0:
        return "充值失败,充值数额不能小于0"

    flag=5 # 默认5倍系数，也就是1块钱5次
    if money < 50:
        flag = 5
    elif money < 100:
        flag = 8
    elif money >= 100:
        flag = 10

    available_count = money * flag
    if not redis_db.exists(f"user:{username}"):  # 如果充值的用户不存在则创建该用户，并且设置随机默认密码
        return "用户不存在"
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
        usertype = 'paid'
        registerDate = userinfo[4]
        old_chargeMoney = userinfo[7]
        new_chargeMoney = int(old_chargeMoney)+int(actual_money)
        if recommender != "none":
            recommender_new = recommender
        else:
            recommender_new = userinfo[5]
        new_count = int(left_count) + available_count
        # 首先给充值人充值
        lastChargeDate = datetime.datetime.today().strftime("%Y-%m-%d")
        storage_string = assemble_userinfo(username, password, new_count, usertype, registerDate, recommender_new,lastChargeDate,new_chargeMoney,int(actual_money))
        redis_db.set(f"user:{username}", storage_string)
        return_message = f"充值成功，已经为账号{username}充值{str(available_count)}次数,充值后剩余的次数为{str(new_count)}次."
        message2 = ""
        if recommender != "none":
            # 首先检查推荐人在不在
            if not redis_db.exists(f"user:{recommender}"):
                message2 = ".由于推荐人不存在,未自动给该推荐人充值,请您检查名称后单独给他充值"
            else:
                # 如果推荐人字段有值，则推荐人也给充值，原则是充值人金额的20%
                available_count = money * flag * 0.2
                userinfo = return_storage_userString_list(recommender)
                password = userinfo[1]
                left_count = userinfo[2]
                usertype = 'paid'
                registerDate = userinfo[4]
                recommender_old = userinfo[5]
                old_chargeMoney = userinfo[7]
                lastchargeMoney2 = userinfo[8]
                new_count = int(left_count) + available_count
                new_storage_str = assemble_userinfo(recommender,password,new_count,usertype,registerDate,recommender_old,lastChargeDate,old_chargeMoney,lastchargeMoney2)
                redis_db.set(f"user:{recommender}", new_storage_str)
                message2 = f".推荐人{recommender}也充值成功，充值{str(available_count)}次数,充值后剩余的次数为{str(new_count)}次"
        charge_result = return_message + message2
        return charge_result
