"""
mysql工具类
"""
import datetime
import json
import pymysql

host = '127.0.0.1'
user = 'root'
password = 'ak47m4a1though'
database = 'sbike'

"""建立数据库表连接，返回连接对象conn和光标对象cursor"""
def connect_database(host: str, user: str, password: str, database: str):
    conn = pymysql.connect(host=host, user=user, password=password, database=database, charset='utf8')
    cursor = conn.cursor()
    return conn, cursor

"""关闭数据库表连接，传入连接对象conn和光标对象cursor"""
def close_database(conn, cursor):
    conn.close()
    cursor.close()

"""登录验证"""
def login_valid(user_web, password_web):
    conn, cursor = connect_database(host, user, password, database)
    sql = 'select * from user_administer where account =\'{}\''.format(user_web)
    cursor.execute(sql)
    result = cursor.fetchall()
    password_true = ''
    uid = ''
    status = -1
    for i in result:
        password_true = i[2]
        uid = i[0]
        status = i[3]
    close_database(conn, cursor)

    if password_true == password_web:
        return uid, status
    return '', -1

"""登录后初始化用户数据 (uid, fund, phone, sex, nickname)"""
def initial_data(uid):
    conn, cursor = connect_database(host, user, password, database)
    sql = 'select * from user where uid = \'{}\''.format(uid)
    cursor.execute(sql)
    result1 = []
    for i in cursor.fetchall()[0]:
        result1.append(i)

    result2 = {}
    count = 1
    sql = 'select * from trace where uid = \'{}\''.format(uid)
    cursor.execute(sql)

    total_distance = 0

    for i in cursor.fetchall():
        result2['trace'+str(count)] = i
        total_distance += i[6]
        count += 1

    result1.append(len(result2))
    result1.append(total_distance)

    close_database(conn, cursor)
    print(result2)
    return result1, result2

def initial_data_root():
    conn, cursor = connect_database(host, user, password, database)
    sql = 'select * from user natural join user_administer left join pledge on user.uid = pledge.uid'
    cursor.execute(sql)
    user_info = cursor.fetchall()

    sql = 'select * from trace'
    cursor.execute(sql)
    trace_info = cursor.fetchall()

    sql = 'select * from bike'
    cursor.execute(sql)
    bike_info = cursor.fetchall()

    sql = 'select * from pledge'
    cursor.execute(sql)
    pledge_info = cursor.fetchall()

    close_database(conn, cursor)
    return user_info, trace_info, bike_info, pledge_info

"进入钱包管理界面"
def wallet_data(uid):
    conn, cursor = connect_database(host, user, password, database)
    sql = 'select * from pledge where uid = \'{}\''.format(uid)
    cursor.execute(sql)
    result = cursor.fetchall()

    close_database(conn, cursor)

    if result != ():
        return result[0]

    return ()

"获取用户骑行轨迹相关信息"
def trace_data(uid):
    conn, cursor = connect_database(host, user, password, database)

    sql = 'select * from trace where uid=\'{}\''.format(uid)
    cursor.execute(sql)
    result = cursor.fetchall()

    sql = 'select sum(distance) from trace where uid = \'{}\' group by uid'.format(uid)
    cursor.execute(sql)
    total_distance = cursor.fetchall()

    sql = 'select count(*) from trace where uid = \'{}\' group by uid'.format(uid)
    cursor.execute(sql)
    total_count = cursor.fetchall()

    close_database(conn, cursor)
    return result, total_count, total_distance

"""通过tid获取轨迹json数据"""
def get_trace_json(tid):
    conn, cursor = connect_database(host, user, password, database)

    sql = 'select trace_data from trace where tid = \'{}\''.format(tid)
    cursor.execute(sql)
    result = cursor.fetchall()

    close_database(conn, cursor)
    return result

"""单车位置数据"""
def bike_position():
    conn, cursor = connect_database(host, user, password, database)

    sql = 'select type, position from bike'
    cursor.execute(sql)
    data = cursor.fetchall()

    result = {}
    count = 1

    close_database(conn, cursor)

    for i in data:
        result[str(count)] = json.loads(i[1])
        count += 1

    count = 1
    for i in data:
        result[str(count)]['type'] = i[0]

    return json.dumps(result)

"""查询用户骑行轨迹账单数据"""
def get_pay(uid):
    conn, cursor = connect_database(host, user, password, database)
    sql = 'select * from trace where uid = \'{}\''.format(uid)
    cursor.execute(sql)
    result = cursor.fetchall()

    close_database(conn, cursor)
    return result

"""处理main函数修改用户信息的请求"""
def root_modify_user(uid, nickname, phone, state):
    conn, cursor = connect_database(host, user, password, database)

    sql = 'update user set nickname = \'{}\' where uid = \'{}\''.format(nickname, uid)
    cursor.execute(sql)
    conn.commit()

    sql = 'update user set phone = \'{}\' where uid = \'{}\''.format(phone, uid)
    cursor.execute(sql)
    conn.commit()

    sql = 'update user_administer set status = \'{}\' where uid = \'{}\''.format(state, uid)
    cursor.execute(sql)
    conn.commit()

    close_database(conn, cursor)

"""管理员删除用户"""
def root_delete_user(uid):
    conn, cursor = connect_database(host, user, password, database)

    sql = 'delete from user where uid = \'{}\''.format(uid)
    cursor.execute(sql)
    print("从user表删除成功")
    # conn.commit()

    sql = 'delete from user_administer where uid = \'{}\''.format(uid)
    cursor.execute(sql)
    print("从user_administer表删除成功")
    # conn.commit()

    close_database(conn, cursor)

"""付款完成后进行数据库信息修改"""
def pay_ok(tid):
    conn, cursor = connect_database(host, user, password, database)

    sql = 'update trace set pay = 1 where tid=\'{}\''.format(tid)
    cursor.execute(sql)
    conn.commit()
    print("执行成功")
    close_database(conn, cursor)

"""退还押金"""
def pledge_withdraw_database(uid):
    conn, cursor = connect_database(host, user, password, database)
    sql = 'delete from pledge where uid = \'{}\''.format(uid)
    cursor.execute(sql)
    conn.commit()
    print(uid + "退还押金执行成功")

    close_database(conn, cursor)

"""押金支付完成"""
def pledge_ok(uid, trade_no):
    conn, cursor = connect_database(host, user, password, database)

    d_info = datetime.datetime.now()
    sql = 'insert into pledge values (\'{}\', \'支付宝\', \'{}-{}-{} {}:{}:{}\', 90.0, {})'.format(
        uid, d_info.year, d_info.month, d_info.day, d_info.hour, d_info.minute, d_info.second, trade_no)
    cursor.execute(sql)
    conn.commit()
    print(uid + "押金支付成功")

    close_database(conn, cursor)

"""jy币使用并修改"""
def modify_jy(uid: str, jy: float):
    conn, cursor = connect_database(host, user, password, database)
    sql = 'update user set JY = JY - {} where uid = \'{}\''.format(jy, uid)
    cursor.execute(sql)
    conn.commit()
    print("jy币修改完成" + str(jy))

    close_database(conn, cursor)

"""用户修改信息"""
def user_modify_info(uid, nickname, phone):
    print(type(phone))

    conn, cursor = connect_database(host, user, password, database)
    if nickname != '':
        sql = 'update user set nickname = \'{}\' where uid = \'{}\''.format(nickname, uid)
        cursor.execute(sql)
        conn.commit()

    if phone != '':
        sql = 'update user set phone = \'{}\' where uid = \'{}\''.format(phone, uid)
        cursor.execute(sql)
        conn.commit()

    close_database(conn, cursor)

"""处理main函数修改单车信息的请求"""
def root_modify_bike(bid, lat, lng, s):
    conn, cursor = connect_database(host, user, password, database)

    sql = 'update bike set state = {}, position = '.format(s) + '\'{' + '{}:{}, {}:{}'.format("\"x\"", lat, "\"y\"", lng) + '}\'' + ' where bid = \'{}\''.format(bid)
    cursor.execute(sql)
    print('单车信息修改成功')
    conn.commit()

    close_database(conn, cursor)

"""写入管理员日志"""
def log(uid, oid, date, info):
    conn, cursor = connect_database(host, user, password, database)

    lid = 'L{}'.format(getlid())

    sql = 'insert into log values(\'{}\', \'{}\', \'{}\', \'{}\', \'{}\')'.format(lid, uid, oid, info, date)
    cursor.execute(sql)
    print('日志写入成功')
    conn.commit()

    close_database(conn, cursor)

"""获取下一个日志记录的lid"""
def getlid():
    conn, cursor = connect_database(host, user, password, database)

    sql = 'select lid from log'
    cursor.execute(sql)
    count = cursor.rowcount

    close_database(conn, cursor)
    return count + 1

"""查询log并返回页面数据"""
def log_data():
    conn, cursor = connect_database(host, user, password, database)

    sql = 'select * from log'
    cursor.execute(sql)
    result = cursor.fetchall()

    close_database(conn, cursor)
    return result

"""上传头像后修改user.blob"""
def user_blob(uid, blob):
    conn, cursor = connect_database(host, user, password, database)

    sql = 'update user set pic = \'{}\' where uid = \'{}\''.format(blob, uid)
    cursor.execute(sql)
    conn.commit()
    print("blob修改成功")

    close_database(conn, cursor)

"""管理员删除单车"""
def root_delete_bike(bid):
    conn, cursor = connect_database(host, user, password, database)

    sql = 'delete from bike where bid = \'{}\''.format(bid)
    print(sql)
    cursor.execute(sql)
    conn.commit()
    print("单车删除成功")

    close_database(conn, cursor)

"""处理main函数增加单车信息的请求"""
def root_add_bike(bid, lat, lng, type_):
    conn, cursor = connect_database(host, user, password, database)

    sql = 'insert into bike values (\'{}\', 0, \'{}\', \''.format(bid, type_) + '{' + '\"x\":{}, \"y\":{}'.format(lat, lng) + '}\')'
    print(sql)
    cursor.execute(sql)
    print('单车增加成功')
    conn.commit()

    close_database(conn, cursor)

"""单独查询头像pic,因为太大了不能放入cookie"""
def get_pic(uid):
    conn, cursor = connect_database(host, user, password, database)

    sql = 'select pic from user where uid = \'{}\''.format(uid)
    cursor.execute(sql)
    result = str(cursor.fetchall()[0][0], encoding='UTF-8')

    close_database(conn, cursor)
    return result.strip("\"")

def pay_jy(uid, amount):
    conn, cursor = connect_database(host, user, password, database)
    sql = 'update user set jy = jy + {} where uid = \'{}\''.format(amount, uid)
    cursor.execute(sql)
    conn.commit()
    close_database(conn, cursor)

def withdraw_jy(uid, amount):
    conn, cursor = connect_database(host, user, password, database)
    sql = 'update user set jy = jy - {} where uid = \'{}\''.format(amount, uid)
    cursor.execute(sql)
    conn.commit()
    close_database(conn, cursor)

"""main函数用于测试"""
if __name__ == '__main__':
    pass
