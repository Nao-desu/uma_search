import requests
import json
import os
import random
from requests.adapters import HTTPAdapter
from hoshino import Service, priv, R
import zhconv
from .get import get_uma_data
from .config import *

s = requests.Session()
s.mount('http://', HTTPAdapter(max_retries=5))
s.mount('https://', HTTPAdapter(max_retries=5))

false = False

url="https://umatwdb.com/api/user/list"
idata={"wins":0,"selectSupports":[],"selectUmas":[],"selectUmasExclude":[],"selectFactors":[]}
sv = Service('搜种马', enable_on_default = True,help_='''
从繁中服DB获取种马数据
---使用方法---
[搜种马 n因子(支持多个) 马娘名]
ps：部分因子支持别名(如春,东京,地固,逃直等),部分马娘支持外号
    示例：
    [搜种马 10胜九力5u3地固星云]
[支援卡列表 属性] 查看对应属性支援卡的编号
[搜支援卡 编号 突破数(可不写)]搜索支援卡
[uma别名 马娘名/因子名 别名]为马娘或因子添加别名,用于简化搜索
[更新种马数据]更新数据
'''.strip())

uma_name_dir = os.path.join(os.path.dirname(__file__), 'data/uma_name.json')
support_dir = os.path.join(os.path.dirname(__file__), 'data/support.json')
status_dir = os.path.join(os.path.dirname(__file__), 'data/status.json')
skill0_dir = os.path.join(os.path.dirname(__file__), 'data/skill0.json')
skill_dir = os.path.join(os.path.dirname(__file__), 'data/skill.json')
nsup_dir = os.path.join(os.path.dirname(__file__), 'data/n_support.json')

ch2num = {"一":1,"二":2,"三":3,"四":4,"五":5,"六":6,"七":7,"八":8,"九":9}

def uma2data(text):
    with open(uma_name_dir, 'r', encoding = 'UTF-8') as f:
        uma_name = json.load(f)
    s = []
    for n,v in uma_name.items():
        for i in v:
            if i in text:
                num = int(n)
                s = [{"selectRange":2,"umaType":num}]
    return s

def text2support(text):
    resupport = []
    with open(support_dir,'r',encoding = 'UTF-8') as f:
        support = json.load(f)
    if len(text.split(' ')) == 1:
        if text.split(' ')[0] in support:
            resupport = [{"support_level": 1, "support": int(text.split(' ')[0]), "supportLevel": 4}]
    elif len(text.split(' ')) == 2:
        if text.split(' ')[0] in support:
            if int(text.split(' ')[1]) in range(1,5):
                resupport = [{"support_level": 1, "support": int(text.split(' ')[0]), "supportLevel": int(text.split(' ')[1])}]
    return resupport    

def text2status(text):
    with open(status_dir, 'r', encoding = 'UTF-8') as f:
        status = json.load(f)
    s = []
    numlist = [] 
    for num in status:
        for ern in status[num]:
            if ern in text:
                for i in range(1,10):
                    if f"{str(i)}{ern}" in text:
                        if num in numlist:
                            print(f"适性因子{status[num][0]}已添加！")
                        else:
                            s += [{"factorTypeLevel": i,"factorTypeRange": 1,"factorType": int(num)}]
                            numlist = numlist+[num]
    return s

def text2skill0(text):
    with open(skill0_dir, 'r', encoding = 'UTF-8') as f:
        skill0 = json.load(f)
    s = []
    numlist = []
    for num in skill0:
        for s0n in skill0[num]:
            if s0n in text:
                for n in range(1,10):
                    if f"{str(n)}{s0n}" in text:
                        if num in numlist:
                            print(f"固有技能因子{skill0[num][0]}已添加！")
                        else:
                            s += [{"factorTypeLevel": n,"factorTypeRange": 1,"factorType": int(num)}]
    return s
            
def text2skill(text):
    with open(skill_dir, 'r', encoding = 'UTF-8') as f:
        skill = json.load(f)
    s = []
    numlist = []
    for num in skill:
        for s1n in skill[num]:
            if s1n in text or zhconv.convert(s1n,'zh-cn') in text:
                for n in range(1,10):
                    if f"{str(n)}{s1n}" in text or f"{str(n)}{zhconv.convert(s1n,'zh-cn')}"in text:
                        if num in numlist:
                            print(f"技能因子{skill[num][0]}已添加！")
                        else:
                            s += [{"factorType":int(num),"factorTypeLevel":n,"factorTypeRange":1}]
                            numlist.append(num)
    return s
    
def num2wins(text):
    wins = 0
    for i in range(1,64):
        win=f"{str(i)}胜"
        if win in text:
           wins = i
    return wins
            
def num2support(n):
    with open(support_dir, 'r', encoding = 'UTF-8') as f:
        support = json.load(f)
    support_name=support[str(n)][0]
    return support_name
    
def num2uma(n):
    with open(uma_name_dir, 'r', encoding = 'UTF-8') as f:
        uma = json.load(f)
    uma_name=uma[str(n)][0]
    return uma_name

def num2skill(n):
    with open(status_dir, 'r', encoding = 'UTF-8') as f1:
        status = json.load(f1)
    with open(skill0_dir, 'r', encoding = 'UTF-8') as f2:
        skill0 = json.load(f2)
    with open(skill_dir, 'r', encoding = 'UTF-8') as f3:
        skill = json.load(f3)
    f_skill = {}
    f_skill.update(status)
    f_skill.update(skill0)
    f_skill.update(skill)
    s_skill=f_skill[str(n)][0]
    return s_skill

def re2status(d):
    with open(status_dir, 'r', encoding = 'UTF-8') as f1:
        status = json.load(f1)
    con = ""
    for i in status:
        inn = 0
        self = 0
        for n in (0,1,2):
            for typ in d["umas"][n]["factors"]:
                if typ["type"] == int(i):
                    inn += typ["level"]
        if inn != 0:
            for typ in d["umas"][0]["factors"]:
                if typ["type"] == int(i):
                    self = typ["level"]
                    break
            if self != 0:
                con += f"★{str(inn)}{status[i][0]}(本体★{str(self)})"
            else:
                con += f"★{str(inn)}{status[i][0]}"
    return con

def re2skill0(d):
    con = ""
    with open(skill0_dir, 'r', encoding = 'UTF-8') as f2:
        skill0 = json.load(f2)
    for i in skill0:
        for n in (0,1,2):
            for typ in d["umas"][n]["factors"]:
                if typ["type"] == int(i):
                    skill0level = typ["level"]
                    con += f"★{str(skill0level)}{skill0[i][0]}\n"
    return con

def re2skill(d):
    con = ""
    with open(skill_dir, 'r', encoding = 'UTF-8') as f3:
        skill = json.load(f3)  
    skilllist={}
    for n in (0,1,2):
        onelist=[]
        for typ in d["umas"][n]["factors"]:
            if str(typ["type"]) in skill:
                if typ["type"] in onelist:
                   trashbin=1
                else:
                    onelist += [typ["type"]]
                    if typ["type"] in skilllist:
                        skilllist[typ["type"]] += typ["level"]
                    else:
                        skilllist[typ["type"]] = typ["level"]
    selfskill={}
    for i in skilllist:
        for typ in d["umas"][0]["factors"]:
            if typ["type"] == i:
                selfskill[i] = typ["level"]
                break
    for i in skilllist:
        if i in selfskill:
            con += f"★{str(skilllist[i])}{skill[str(i)][0]}(本体★{str(selfskill[i])})\n"
        else:
            con += f"★{str(skilllist[i])}{skill[str(i)][0]}\n"
    return con
    
def re2msg(d):
    uman1 = num2uma(d["umas"][0]["type"])
    uid = d["uuid"]
    win = str(d["wins"])
    uman2 = num2uma(d["umas"][1]["type"])
    uman3 = num2uma(d["umas"][2]["type"])
    con=f"{uman1}({win}胜)\nid:{uid}\n祖辈：{uman2}\n       {uman3}\n"
    if d["support"] != 0:
        support = num2support(d["support"])
        supportlevel = str(d["supportLevel"])
        con += f"支援卡:{support}({supportlevel}破)\n"
    con += re2status(d)
    con += "\n"
    con += re2skill0(d)
    con += re2skill(d)
    memo = d["memo"]
    if memo != "":
        con += f"备注：{memo}"
    mes = {"type": "node","data": {"name": name,"user_id": avatar,"content": con}}
    return mes

def resmaker(r,l):
    mes=[]
    if l==0 :
        mes += [re2msg(r[0])]
    else:
        for i in l:
            mes += [re2msg(r[i])]
    return mes



@sv.on_prefix('搜种马')
async def umasr(bot, ev):
    global false
    try:
        text = ev.message.extract_plain_text()
        for i,n in ch2num.items():
            if i in text:
                text = text.replace(i,str(n))
        data = {"wins":0,"selectSupports":[],"selectUmas":[],"selectUmasExclude":[],"selectFactors":[]}
        data["wins"] = num2wins(text)
        data["selectUmas"] = uma2data(text)
        data["selectFactors"] = text2status(text)+text2skill0(text)+text2skill(text)
        print(data)
        if data == {"wins":0,"selectSupports":[],"selectUmas":[],"selectUmasExclude":[],"selectFactors":[]}:
            await bot.send(ev,"条件为空，请重试",at_sender=True)
            return
        txtre = "搜索条件：\n"
        if data["wins"] !=  0:
            txtre += f"{str(num2wins(text))}胜\n"
        if data["selectUmas"] != []:
            uma = data["selectUmas"][0]["umaType"]
            txtre += f"{num2uma(uma)}\n"
        if data["selectFactors"] != []:
            for i in data["selectFactors"]:
                skill_level = str(i["factorTypeLevel"])
                skill_name = num2skill(i["factorType"])
                txtre += f"★{skill_level}{skill_name}\n"
        txtre = txtre.rstrip("\n")
        await bot.send(ev,txtre)
        r = eval(s.post(url,json=data,timeout=20).text)
        num = len(r)
        if num == 0:
            await bot.send(ev,"未找到结果，请尝试放宽条件",at_sender=True)
            return
        if num == 1:
            await bot.send(ev,f"已找到{num}个结果",at_sender=True)
            chos = 0
        if num <= 10 and num >= 2:
            await bot.send(ev,f"已找到{num}个结果",at_sender=True)
            chos = []
            for i in range(0,num):
                chos += [i]
        if num > 10:
            await bot.send(ev,f"已找到{num}个结果",at_sender=True)
            chos = random.sample(range(0,num), num)
        msg=resmaker(r,chos)
        await bot.send_group_forward_msg(group_id=ev['group_id'], messages=msg)
    except requests.exceptions.ConnectTimeout:
        await bot.send(ev,"请求超时...",at_sender=True)
        return
    except Exception as e:
        await bot.send(ev,f"发送失败,{e}",at_sender=True)

@sv.on_prefix('搜支援卡')
async def umacardsr(bot, ev):
    global false
    try:
        text = ev.message.extract_plain_text()
        data = {"wins":0,"selectSupports":[],"selectUmas":[],"selectUmasExclude":[],"selectFactors":[]}
        data["selectSupports"]=text2support(text)
        print(data)
        if data == {"wins":0,"selectSupports":[],"selectUmas":[],"selectUmasExclude":[],"selectFactors":[]}:
            await bot.send(ev,"格式错误，应为[搜支援卡 卡编号 突破数(可不写)]\n发送[支援卡列表 种类]可查看支援卡编号",at_sender=True)
            return
        txtre = "搜索条件：\n"
        txtre += f"{str(data['selectSupports'][0]['supportLevel'])}破 "
        txtre += num2support(data["selectSupports"][0]["support"])
        await bot.send(ev,txtre)
        r = eval(s.post(url,json=data,timeout=20).text)
        num = len(r)
        if num == 0:
            await bot.send(ev,"未找到结果，请尝试放宽条件",at_sender=True)
            return
        if num == 1:
            await bot.send(ev,f"已找到{num}个结果",at_sender=True)
            chos = 0
        if num <= 10 and num >= 2:
            await bot.send(ev,f"已找到{num}个结果",at_sender=True)
            chos = []
            for i in range(0,num):
                chos += [i]
        if num > 10:
            await bot.send(ev,f"已找到{num}个结果",at_sender=True)
            chos = random.sample(range(0,num), num)
        msg=resmaker(r,chos)
        await bot.send_group_forward_msg(group_id=ev['group_id'], messages=msg)
    except requests.exceptions.ConnectTimeout:
        await bot.send(ev,"请求超时...",at_sender=True)
        return
    except Exception as e:
        await bot.send(ev,f"发送失败,{e}",at_sender=True)
@sv.on_prefix('支援卡列表')
async def sup_list(bot,ev):
    text = ev.message.extract_plain_text()
    text = text.strip("卡")
    with open(nsup_dir,'r',encoding = 'UTF-8') as f:
        support = json.load(f)
    if text in ["速","速度"]:
        text = "速度"
    elif text in ["力","力量"]:
        text = "力量"
    elif text in ["耐","耐力","体","体力","持久力"]:
        text = "持久力"
    elif text in ["根","根性","意志力"]:
        text = "意志力"
    elif text in ["智力","智"]:
        text = "智力"
    elif text in ["友","友人","同伴"]:
        text = "同伴"
    else:
        await bot.send(ev,"请选择支援卡类型(速/力/耐/根/智/友)",at_sender = True)
        return
    msg = text + "卡列表："
    for i in support:
        if i["type"] == text:
            msg += f'\n{i["value"]}\t{i["label"]}\t{i["rank"]}'
    await bot.send(ev,msg)
    
@sv.on_prefix('uma别名')
async def uma_alias(bot,ev):
    text = ev.message.extract_plain_text()
    with open(uma_name_dir,'r',encoding = 'UTF-8') as f:
        uma = json.load(f)
    with open(skill0_dir,'r',encoding = 'UTF-8') as f:
        skill0 = json.load(f)
    with open(skill_dir,'r',encoding = 'UTF-8') as f:
        skill = json.load(f)
    name,alias = text.split(" ")[:2]
    for i in uma:
        for j in uma[i]:
            if j == name:
                uma[i].append(alias)
                with open(uma_name_dir,'w',encoding = 'UTF-8') as f:
                    json.dump(uma,f,ensure_ascii=False,indent=4)
                await bot.send(ev,f"成功为{name}添加别名{alias}")
                return
    for i in skill0:
        for j in skill0[i]:
            if j == name:
                skill0[i].append(alias)
                with open(skill0_dir,'w',encoding = 'UTF-8') as f:
                    json.dump(skill0,f,ensure_ascii=False,indent=4)
                await bot.send(ev,f"成功为{name}添加别名{alias}")
                return
    for i in skill:
        for j in skill[i]:
            if j == name:
                skill[i].append(alias)
                with open(skill_dir,'w',encoding = 'UTF-8') as f:
                    json.dump(skill,f,ensure_ascii=False,indent=4)
                await bot.send(ev,f"成功为{name}添加别名{alias}")
                return
    await bot.send(ev,f"未找到马娘名或因子名：{name}，请检查名称是否正确")
    
@sv.on_prefix('更新种马数据')
async def update_uma_data(bot,ev):
    await bot.send(ev,"正在更新种马娘数据，请稍后...")
    try:
        await get_uma_data()
        await bot.send(ev,"更新成功！")
    except Exception as e:
        await bot.send(ev,f"更新失败，{e}")
        
@sv.scheduled_job('cron', hour='10')
async def update_uma_data_cron():
    if not auto_update:
        return
    print("uma data update cron job running")
    try:
        await get_uma_data()
        print("uma data updated")
    except Exception as e:
        print(f"uma data update failed, {e}")