from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from tkinter import *
import requests
import cv2
import numpy as np
import pyautogui
import json
import os
import re
import time
import configparser

# 验证码处理
def verification(raw_image, color):
    image = cv2.imdecode(np.frombuffer(raw_image, np.uint8), cv2.IMREAD_COLOR)
    if color == "红":
        mask = cv2.inRange(cv2.cvtColor(image, cv2.COLOR_RGB2HSV), np.array([115, 100, 0]), np.array([135, 255, 255]))
    elif color == "绿":
        mask = cv2.inRange(cv2.cvtColor(image, cv2.COLOR_BGR2HSV), np.array([45, 100, 0]), np.array([90, 255, 255]))
    elif color == "黄":
        mask = cv2.inRange(cv2.cvtColor(image, cv2.COLOR_BGR2HSV), np.array([15, 100, 0]), np.array([45, 255, 255]))
    elif color == "蓝":
        mask = cv2.inRange(cv2.cvtColor(image, cv2.COLOR_BGR2HSV), np.array([90, 50, 0]), np.array([150, 255, 255]))
    contours, hierarchy = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    index = 1
    area_ = 0
    offset_x = 0
    offset_y = 0
    for contour in contours:
        area = cv2.contourArea(contour)
        if area < 100:
            continue
        if index == 1:
            area_ = area
        if area < area_ or index == 1:
            area_ = area
            moment = cv2.moments(contour)
            offset_x = moment["m10"] / moment["m00"]
            offset_y = moment["m01"] / moment["m00"]
        index += 1
    offset_x = verification_position_x + offset_x / 2 * system_zoom
    offset_y = verification_position_y + offset_y / 2 * system_zoom
    return offset_x, offset_y

# 检测验证是否通过
def is_verified():
    try:
        driver.find_element(By.XPATH, '//*[@id="root"]/div[1]/div[2]/main/main/div/div/h2')
        return True
    except NoSuchElementException:
        return False

# 开启网站
def open_web():
    button_open_web.config(state="disabled")
    driver.get('https://www.yooc.me/mobile/dashboard/my_group')
    # 载入Cookies
    if not os.path.exists('cookies.json'):
        with open('cookies.json', 'w') as f:
            json.dump({}, f, indent=4)
    with open('cookies.json', 'r') as f:
        cookies = json.load(f)
    for cookie in cookies:
        driver.add_cookie(cookie)
    # 刷新
    driver.get('https://www.yooc.me/mobile/dashboard/my_group')
    # driver.refresh()
    # 判断Cookies是否失效
    if driver.current_url != 'https://www.yooc.me/mobile/dashboard/my_group':
        # 等待人机验证
        input("Cookies失效，请重新登陆：登陆成功后任意回复")
        # 保存Cookies
        cookies = driver.get_cookies()
        with open('cookies.json', 'w') as f:
            json.dump(cookies, f, indent=4)
        print("Cookies已更新")
    button_cycle_add.config(state="normal")
    button_cycle_remove.config(state="normal")
    button_start.config(state="normal")

# 开始
def start():
    global current_times
    # 打开题库
    if not os.path.exists(entry_answer_path.get()):
        with open(entry_answer_path.get(), 'w', encoding='utf-8') as f:
            json.dump({}, f, indent=4)
    with open(entry_answer_path.get(), 'r', encoding='utf-8') as f:
        answer_dic = json.load(f)
    while current_times < total_times:
        if not first_time.get():
            driver.find_element(By.XPATH, entry_xpath1.get()).click()
            driver.find_element(By.XPATH, entry_xpath2.get()).click()
        # 获取题目数量
        question_number = int(re.findall(r'\d+', driver.find_element(By.XPATH,'//*[@id="root"]/div[1]/div[2]/main/article/div[1]/div[2]/div').text)[0])
        # 进入考试------------------------------------------------------------------------------------------------------------
        driver.find_element(By.XPATH, '//*[@id="root"]/div[1]/div[2]/main/article/div[3]/button').click()
        driver.find_element(By.XPATH, '//*[@id="root"]/div[1]/div[2]/main/article/div[3]/div/div/div[2]/button[2]').click()
        # 自动处理验证码
        if auto_verify.get():
            time.sleep(1)
            # 获取验证码图片
            image_element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'shumei_captcha_loaded_img_bg')))
            image_url = image_element.get_attribute('src')
            # 点击
            try:
                pyautogui.click(verification(requests.get(image_url).content, driver.find_element(By.CLASS_NAME, 'shumei_captcha_slide_tips').text.split("色")[0][-1]))
            except Exception as e:
                print("自动验证失败", e)
        else:
            input("等待通过验证码：任意输入以继续")
        while not is_verified():
            input("验证未通过：任意输入以继续")
        for i in range(question_number):
            # 判断题目类型
            question_type = driver.find_element(By.XPATH, '//*[@id="root"]/div[1]/div[2]/main/main/div/div/h2').text
            if question_type == "单选题":
                question = driver.find_element(By.XPATH, '//*[@id="root"]/div[1]/div[2]/main/main/div/div/div/div/h3/div').text
                if question in answer_dic:
                    a = driver.find_element(By.XPATH, '//*[@id="root"]/div[1]/div[2]/main/main/div/div/div/div/div/ul/li[1]/div[2]')
                    b = driver.find_element(By.XPATH, '//*[@id="root"]/div[1]/div[2]/main/main/div/div/div/div/div/ul/li[2]/div[2]')
                    c = driver.find_element(By.XPATH, '//*[@id="root"]/div[1]/div[2]/main/main/div/div/div/div/div/ul/li[3]/div[2]')
                    d = driver.find_element(By.XPATH, '//*[@id="root"]/div[1]/div[2]/main/main/div/div/div/div/div/ul/li[4]/div[2]')
                    options_list = [a, b, c, d]
                    for option in options_list:
                        if option.text.split('.')[1] == answer_dic[question][0]:
                            option.click()
                            break
                else:
                    # 无答案默认选A
                    driver.find_element(By.XPATH, '//*[@id="root"]/div[1]/div[2]/main/main/div/div/div/div/div/ul/li[1]/div[2]').click()
            elif question_type == "多选题":
                question = driver.find_element(By.XPATH, '//*[@id="root"]/div[1]/div[2]/main/main/div/div/div/div/h3/div').text
                if question in answer_dic:
                    a = driver.find_element(By.XPATH, '//*[@id="root"]/div[1]/div[2]/main/main/div/div/div/div/div/ul/li[1]/div[2]')
                    b = driver.find_element(By.XPATH, '//*[@id="root"]/div[1]/div[2]/main/main/div/div/div/div/div/ul/li[2]/div[2]')
                    c = driver.find_element(By.XPATH, '//*[@id="root"]/div[1]/div[2]/main/main/div/div/div/div/div/ul/li[3]/div[2]')
                    d = driver.find_element(By.XPATH, '//*[@id="root"]/div[1]/div[2]/main/main/div/div/div/div/div/ul/li[4]/div[2]')
                    options_list = [a, b, c, d]
                    for option in options_list:
                        if option.text.split('.')[1] in answer_dic[question]:
                            option.click()
                else:
                    # 无答案默认选A
                    driver.find_element(By.XPATH, '//*[@id="root"]/div[1]/div[2]/main/main/div/div/div/div/div/ul/li[1]/div[2]').click()
            elif question_type == "判断题":
                question = driver.find_element(By.XPATH, '//*[@id="root"]/div[1]/div[2]/main/main/div/div/div/div/h3/div').text
                if question in answer_dic:
                    a = driver.find_element(By.XPATH, '//*[@id="root"]/div[1]/div[2]/main/main/div/div/div/div/div/ul/li[1]/div[2]')
                    b = driver.find_element(By.XPATH, '//*[@id="root"]/div[1]/div[2]/main/main/div/div/div/div/div/ul/li[2]/div[2]')
                    options_list = [a, b]
                    for option in options_list:
                        if option.text.split('.')[1] == answer_dic[question][0]:
                            option.click()
                            break
                else:
                    # 无答案默认选A
                    driver.find_element(By.XPATH, '//*[@id="root"]/div[1]/div[2]/main/main/div/div/div/div/div/ul/li[1]/div[2]').click()
            elif question_type == "填空题":
                question = driver.find_element(By.XPATH, '//*[@id="root"]/div[1]/div[2]/main/main/div/div/div/div/h3/div/div').text
                input_blanks = driver.find_elements(By.CLASS_NAME, 'exam-input')
                if question in answer_dic:
                    index = 0
                    for input_blank in input_blanks:
                        input_blank.send_keys(answer_dic[question][index])
                        index += 1
                else:
                    for input_blank in input_blanks:
                        input_blank.send_keys(" ")
            # 下一题
            driver.find_element(By.XPATH, '//*[@id="root"]/div[1]/div[2]/main/main/div/ul/li[4]/button').click()
        # 交卷
        driver.find_element(By.XPATH, '//*[@id="root"]/div[1]/div[1]/div[3]/div/button').click()
        driver.find_element(By.XPATH, '//*[@id="root"]/div[1]/div[1]/div[3]/div/div/div/div[2]/button[2]').click()
        # 判断正确率
        accuracy = driver.find_element(By.XPATH, '//*[@id="root"]/div[1]/div[2]/main/article/div[1]/section[2]/div/b').text
        print(f"本次正确率{accuracy}")
        # 录入答案------------------------------------------------------------------------------------------------------------
        driver.find_element(By.XPATH, '//*[@id="root"]/div[1]/div[2]/main/article/div[2]/button').click()
        for i in range(question_number):
            # 判断题目类型
            question_type = driver.find_element(By.XPATH, '//*[@id="root"]/div[1]/div[2]/main/div/h2').text
            if question_type == "单选题":
                question = driver.find_element(By.XPATH, '//*[@id="root"]/div[1]/div[2]/main/div/div/div/h3/div').text
                answer = driver.find_element(By.XPATH, '//*[@id="root"]/div[1]/div[2]/main/div/div/div/div[2]/div').text
                if answer.split('：')[1] == "A":
                    answer_dic[question] = [driver.find_element(By.XPATH, '//*[@id="root"]/div[1]/div[2]/main/div/div/div/div[1]/ul/li[1]/div[2]').text.split('.')[1]]
                elif answer.split('：')[1] == "B":
                    answer_dic[question] = [driver.find_element(By.XPATH, '//*[@id="root"]/div[1]/div[2]/main/div/div/div/div[1]/ul/li[2]/div[2]').text.split('.')[1]]
                elif answer.split('：')[1] == "C":
                    answer_dic[question] = [driver.find_element(By.XPATH, '//*[@id="root"]/div[1]/div[2]/main/div/div/div/div[1]/ul/li[3]/div[2]').text.split('.')[1]]
                elif answer.split('：')[1] == "D":
                    answer_dic[question] = [driver.find_element(By.XPATH, '//*[@id="root"]/div[1]/div[2]/main/div/div/div/div[1]/ul/li[4]/div[2]').text.split('.')[1]]
                else:
                    print(f"第{i}题答案录入错误")
            elif question_type == "多选题":
                question = driver.find_element(By.XPATH, '//*[@id="root"]/div[1]/div[2]/main/div/div/div/h3/div').text
                answer = driver.find_element(By.XPATH, '//*[@id="root"]/div[1]/div[2]/main/div/div/div/div[2]/div').text
                answer_list = []
                for option in answer.split('：')[1].split('、'):
                    if option == "A":
                        answer_list.append(driver.find_element(By.XPATH, '//*[@id="root"]/div[1]/div[2]/main/div/div/div/div[1]/ul/li[1]/div[2]').text.split('.')[1])
                    elif option == "B":
                        answer_list.append(driver.find_element(By.XPATH, '//*[@id="root"]/div[1]/div[2]/main/div/div/div/div[1]/ul/li[2]/div[2]').text.split('.')[1])
                    elif option == "C":
                        answer_list.append(driver.find_element(By.XPATH, '//*[@id="root"]/div[1]/div[2]/main/div/div/div/div[1]/ul/li[3]/div[2]').text.split('.')[1])
                    elif option == "D":
                        answer_list.append(driver.find_element(By.XPATH, '//*[@id="root"]/div[1]/div[2]/main/div/div/div/div[1]/ul/li[4]/div[2]').text.split('.')[1])
                    else:
                        print(f"第{i}题答案录入错误")
                answer_dic[question] = answer_list
            elif question_type == "判断题":
                question = driver.find_element(By.XPATH, '//*[@id="root"]/div[1]/div[2]/main/div/div/div/h3/div').text
                answer = driver.find_element(By.XPATH, '//*[@id="root"]/div[1]/div[2]/main/div/div/div/div[2]/div').text
                if answer.split('：')[1] == "A":
                    answer_dic[question] = [driver.find_element(By.XPATH, '//*[@id="root"]/div[1]/div[2]/main/div/div/div/div[1]/ul/li[1]/div[2]').text.split('.')[1]]
                elif answer.split('：')[1] == "B":
                    answer_dic[question] = [driver.find_element(By.XPATH, '//*[@id="root"]/div[1]/div[2]/main/div/div/div/div[1]/ul/li[2]/div[2]').text.split('.')[1]]
                else:
                    print(f"第{i}题答案录入错误")
            elif question_type == "填空题":
                question = driver.find_element(By.XPATH, '//*[@id="root"]/div[1]/div[2]/main/div/div/div/h3/div').text
                answer = driver.find_element(By.XPATH, '//*[@id="root"]/div[1]/div[2]/main/div/div/div/div[2]/div').text
                answer_dic[question] = answer.split('：')[1].split('、')
            # 下一题
            driver.find_element(By.XPATH, '//*[@id="root"]/div[1]/div[2]/main/ul/li[3]/button').click()
        with open(entry_answer_path.get(), 'w', encoding='utf-8') as f:
            json.dump(answer_dic, f, ensure_ascii=False, indent=4)
        print(f"题库数量{len(answer_dic)}")
        # 返回
        driver.find_element(By.XPATH, '//*[@id="root"]/div[1]/div[1]/div[1]/span').click()
        if first_time.get():
            break
        current_times += 1
        print(f"进度{current_times}/{total_times}\n")
    label_cycle_times.config(text=f"{current_times}/{total_times}")

# 添加循环
def cycle_add():
    global total_times
    total_times += 1
    label_cycle_times.config(text=f"{current_times}/{total_times}")

# 减少循环
def cycle_remove():
    global total_times
    if current_times < total_times:
        total_times -= 1
        label_cycle_times.config(text=f"{current_times}/{total_times}")

# 保存配置
def save_configs():
    config.set("default", "system_zoom", str(system_zoom))
    config.set("default", "verification_position_x", str(verification_position_x))
    config.set("default", "verification_position_y", str(verification_position_y))
    config.set("default", "answer_path", entry_answer_path.get())
    config.set("default", "auto_login", str(auto_login.get()))
    config.set("default", "auto_verify", str(auto_verify.get()))
    config.set("default", "first_time", str(first_time.get()))
    config.set("default", "xpath1", entry_xpath1.get())
    config.set("default", "xpath2", entry_xpath2.get())
    with open("config.ini", "w", encoding="utf-8") as f:
        config.write(f)
    window.destroy()

# 初始化
options = Options()
options.add_argument('--disable-blink-features=AutomationControlled')
options.add_argument('ignore-ssl-errors')
options.add_argument('ignore-certificate-errors')
options.add_experimental_option('excludeSwitches', ['enable-automation'])
driver = webdriver.Edge(options=options)
driver.implicitly_wait(10)
current_times = 0
total_times = 1
system_zoom = 1.0
verification_position_x = 0
verification_position_y = 0

# 用户窗口
window = Tk()
window.title("Yiban Yooc Auto")
window.geometry("600x300")
first_time = BooleanVar(window)
auto_login = BooleanVar(window)
auto_verify = BooleanVar(window)
button_open_web = Button(window, text="打开网页", command=open_web)
button_open_web.grid(column=0, row=0)
button_cycle_add = Button(window, text="增加循环",state="disabled", command=cycle_add)
button_cycle_add.grid(column=0, row=2)
button_cycle_remove = Button(window, text="减少循环",state="disabled", command=cycle_remove)
button_cycle_remove.grid(column=1, row=2)
button_start = Button(window, text="开始", state="disabled", command=start)
button_start.grid(column=2, row=2)
label_cycle_times = Label(font=('', 20))
label_cycle_times.config(text=f"{current_times}/{total_times}")
label_cycle_times.grid(column=0, row=1, padx=60, pady=30)
checkbutton_auto_login = Checkbutton(window, text="自动登录", variable=auto_login, onvalue=True, offvalue=False)
checkbutton_auto_login.grid(column=1, row=0)
checkbutton_auto_verify = Checkbutton(window, text="自动验证", variable=auto_verify, onvalue=True, offvalue=False)
checkbutton_auto_verify.grid(column=1, row=1)
checkbutton_first_time = Checkbutton(window, text="首次启动", variable=first_time, onvalue=True, offvalue=False)
checkbutton_first_time.grid(column=2, row=1)
entry_answer_path = Entry(window)
entry_answer_path.grid(column=2, row=0)
entry_xpath1 = Entry(window)
entry_xpath1.grid(column=0, row=3, columnspan=3, pady=15, ipadx=190)
entry_xpath2 = Entry(window)
entry_xpath2.grid(column=0, row=4, columnspan=3, ipadx=190)

# 配置文件
config = configparser.ConfigParser()
config.read('config.ini', encoding='utf-8')
try:
    system_zoom = config.getfloat('default', 'system_zoom')
    verification_position_x = config.getint('default', 'verification_position_x')
    verification_position_y = config.getint('default', 'verification_position_y')
    entry_answer_path.insert(0, config.get('default', 'answer_path'))
    auto_login.set(config.getboolean('default', 'auto_login'))
    auto_verify.set(config.getboolean('default', 'auto_verify'))
    first_time.set(config.getboolean('default', 'first_time'))
    entry_xpath1.insert(0, config.get('default', 'xpath1'))
    entry_xpath2.insert(0, config.get('default', 'xpath2'))
except configparser.NoSectionError:
    config.add_section('default')

window.protocol("WM_DELETE_WINDOW", save_configs)
window.mainloop()
