from httpx import AsyncClient as Client
import re
import json
import asyncio

async def get_uma_data():
    async with Client() as client:
        
        response = await client.get ("https://umatwdb.com")
        if response.status_code!= 200:
            print("Failed to get data")
            return
        page_source = response.text
        match = re.search (r"static/js/main\.\w+\.js", page_source)
        if match:
            file_name = match.group()
        else:
            print ("File not found")
            return
        response = await client.get(f"https://umatwdb.com/{file_name}")
        if response.status_code!= 200:
            print("Failed to get data")
            return
        main = response.text
    
    data = re.findall(r"=JSON.parse\('(.*?)'\)",main)
    skill = data[0]
    umaname = data[1]
    support = data[2]
    skill = skill.encode("utf-8").decode("unicode_escape")
    support = support.encode("utf-8").decode("unicode_escape")
    umaname = umaname.encode("utf-8").decode("unicode_escape")

    skill_new = json.loads(skill)
    umaname_new = json.loads(umaname)
    support_new = json.loads(support)

    
    with open("./data/uma_name.json",'r',encoding='utf8') as f:
        umaname_old = json.load(f)
    for i in umaname_new:
        if str(i["value"]) not in umaname_old:
            umaname_old[str(i["value"])] = [i["label"]]
            print(f'append{i["label"]}')
    with open("./data/uma_name.json", "w", encoding="utf-8") as f:
        json.dump(umaname_old, f, indent=4, ensure_ascii=False)

    with open("./data/support.json",'r',encoding='utf8') as f:
        support_old = json.load(f)
    for i in support_new:
        if str(i["value"]) not in support_old:
            support_old[str(i["value"])] = [i["label"]]
            print(f'append{i["label"]}')
    with open("./data/support.json", "w", encoding="utf-8") as f:
        json.dump(support_old, f, indent=4, ensure_ascii=False)

    with open('./data/skill.json','r',encoding='utf8') as f:
        skill_w_old = json.load(f)
    with open('./data/skill0.json','r',encoding='utf8') as f:
        skill_g_old = json.load(f)
    for i in skill_new:
        if i["c"] == "g":
            if str(i["value"]) not in skill_g_old:
                skill_g_old[str(i["value"])] = [i["label"]]
                print(f'append{i["label"]}')
        elif i["c"] == "w":
            if str(i["value"]) not in skill_w_old:
                skill_w_old[str(i["value"])] = [i["label"]]
                print(f'append{i["label"]}')

    with open("./data/skill0.json", "w", encoding="utf-8") as f:
        json.dump(skill_g_old, f, indent=4, ensure_ascii=False)
    with open("./data/skill.json", "w", encoding="utf-8") as f:
        json.dump(skill_w_old, f, indent=4, ensure_ascii=False)

if __name__ == '__main__':
    asyncio.run(get_uma_data())