# -*- coding: utf-8 -*-

import requests
from re import findall, search
from uuid import uuid4
from datetime import datetime
from os import mkdir, name, system
from threading import Semaphore, Thread
from rich.text import Text
from rich.console import Console
from random import shuffle
from time import sleep

hit, bad, error, cpm, done = 0, 0, 0, 0, 0

console = Console()
screen_lock = Semaphore(value=1)

def clear(): system('cls' if name == 'nt' else 'clear')
def title():
    while True:
        system("title " + f"Url Leecher By: @Tufaah -- ( Urls: {done} -- Hits: {hit} -- Bad: {bad} -- Errors: {error} -- CPM: {cpm} ) ")
        sleep(1.2)

def counter():
    global cpm
    while True:
        oldchecked = hit + bad;sleep(1);newchecked = hit + bad
        cpm = (newchecked - oldchecked) * 60

def output(msg):
    screen_lock.acquire()
    console.print(msg)
    screen_lock.release()

system("title " + f"Url Leecher By: @Tufaah")
logo = '''
    ╦ ╦┬─┐┬  
    ║ ║├┬┘│  
    ╚═╝┴└─┴─┘     [cyan]@Tufaah[/]
    ╦  ┌─┐┌─┐┌─┐┬ ┬┌─┐┬─┐
    ║  ├┤ ├┤ │  ├─┤├┤ ├┬┘
    ╩═╝└─┘└─┘└─┘┴ ┴└─┘┴└─

'''
console.print(logo, style="bold blue")
output('[bold][on white]  [black]Output  [/][/] [blue]Separate multi keywords with a space![/][/]')
console.print('[bold][on white]  [black]Input   [/][/] [cyan]Enter one or more keywords: [/][/]', end='');keywords = input('')
keywords = keywords.split()
clear()

try: mkdir('./results')
except FileExistsError: pass
time = datetime.now();date = f'{time.month}_{time.day}_{time.hour}_{time.minute}_{time.second}'
mkdir(f'./results/{date}')

engines = ['DuckDuckGo', 'Yahoo', 'StartPage', 'Ask']
for i in engines: mkdir(f'./results/{date}/{i}')

try: domains_file = open('./domains.txt')
except FileNotFoundError: clear();console.print(logo, style="bold blue");output(f'[bold][on white]   [black]Output   [/][/] domains.txt not found![/]');sleep(3)
domains = domains_file.read().splitlines()
domains = [f'https://{i}/' for i in domains]

user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36'
pages = 10

class Main:
    def __init__(self, url):
        self.url = url

    def sort(self, response):
        returned = []
        for i in response:
            if search(r'\/([^.]+)', self.url).group(1) in i and len(i) < 111: returned.append(i)
        return returned

    @classmethod
    def save(cls, fileName: str, data, type, keyword):
        with open(rf'./results/{date}/{type}/{keyword}/{fileName}', "a+", encoding='utf-8', errors='ignore') as save_file:
            save_file.write(str(data) + '\n')


class DuckDuckGo:
    def __init__(self, url, keyword):
        self.url = url
        self.keyword = keyword

    def dorks(self):
        global error
        try:
            vqd = search("vqd='([^']+)", requests.get('https://duckduckgo.com/',
                       params={'q': f'site:{self.url} "{self.keyword}"', 't': 'h_', 'ia': 'web'},
                       headers={'user-agent': user_agent}).text).group(1)

            response = requests.get('https://links.duckduckgo.com/d.js',
                       params={
                        'q': f'site:{self.url} "{self.keyword}"', 'l': 'us-en', 's': '0', 'a': 'h_',
                        'dl': 'en', 'vqd': vqd, 'ct': 'US', 'ss_mkt': 'us', 'msvrtexp': 'b', 'deepsprts': 'b',
                        'wrap': '1', 'p_ent': '', 'ex': '-1', 'sp': '1', 'biaexp': 'b'},
                       headers={'referer': 'https://duckduckgo.com/', 'user-agent': user_agent}).text
            return list(set(findall('"(https?://[^"]+)', response)[1:]))
        except:
            output('[bold][on white]  [black]Error  [/][/]   [red]while finding links in DuckDuckGo[/][/]');error+=1
            return [0]


class Yahoo:
    def __init__(self, url, keyword):
        self.url = url
        self.keyword = keyword

    def dorks(self, page):
        global error
        try:
            response = requests.get('https://search.yahoo.com/search;_ylt=AwrJ_zuKJyBjTM8BNiVXNyoA;_ylu=Y29sbwNiZjEEcG9zAzEEdnRpZAMEc2VjA3BhZ2luYXRpb24-',
                       params= [
                        ('p', f'site:{self.url} "{self.keyword}"'),
                        ('pz', '7'), ('fr', 'sfp'), ('fr2', 'p:s,v:sfp,m:sb-top'),
                        ('bct', '0'), ('b', '1' if page == 1 else f'{(7*page)+1}'), ('pz', '7'), ('bct', '0'), ('xargs', '0')],
                       headers={'referer': 'https://search.yahoo.com/search;_ylt=AwrFADR.JyBjOKoBWVpXNyoA;_ylu=Y29sbwNiZjEEcG9zAzEEdnRpZAMEc2VjA3BhZ2luYXRpb24-?p=site%3Ahttps%3A%2F%2Fanonfiles.com%2F+%22combo%22&fr=sfp&fr2=p%3As%2Cv%3Asfp%2Cm%3Asb-top&b=8&pz=7&bct=0&xargs=0', 'user-agent': user_agent})
            return list(set(findall('(https:\/\/r.search.yahoo.com\/[^"]+)', response.text)))
        except:
            output('[bold][on white]  [black]Error  [/][/]   [red]while finding links in Yahoo[/][/]');error+=1
            return [0]

    def get_url(self, response):
        global error
        returned = []
        try:
            for i in response:
                try: returned.append(search(f'({self.url}[^"]+)', requests.get(i, headers={'User-Agent': user_agent}, allow_redirects =False).text).group(1))
                except: pass
            return returned
        except:
            output('[bold][on white]  [black]Error  [/][/]   [red]while finding links in Yahoo[/][/]');error+=1
            return [0]


class StartPage:
    def __init__(self, url, keyword):
        self.url = url
        self.keyword = keyword

    def dorks(self, page):
        global error
        try:
            response = requests.post('https://www.startpage.com/sp/search',
                       data={
                        'abp': '-1','language': 'english', 'lui': 'english',
                        'query': f'site:{self.url} "{self.keyword}"',
                        'cat': 'web', 'page': f'{page}', 'sc': 'MDrEds04V6aM20'},
                       headers={'Referer': 'https://www.startpage.com/', 'User-Agent': user_agent})
            return list(set(findall(f'({self.url}\w+)', response.text)))
        except:
            output('[bold][on white]  [black]Error  [/][/]   [red]while finding links in StartPage[/][/]');error+=1
            return [0]


class Ask:
    def __init__(self, url, keyword):
        self.url = url
        self.keyword = keyword

    def dorks(self, page):
        global error
        try:
            response = requests.get('https://www.ask.com/web',
                       params={
                        'q': f'site:{self.url} "{self.keyword}"',
                        'ad': 'SEO', 'o': '779176', 'ueid': uuid4(),
                        'qo': 'pagination', 'qsrc': '998', 'page': f'{page}'},
                       headers={'referer': 'https://www.ask.com/web?q=site:https://anonfiles.com/%20%22combo%22&ad=SEO&o=779176&ueid=f1d25714-c313-4012-9047-c871f4a2fc2d', 'user-agent': user_agent})
            return list(set(findall(f'({self.url}[^\']+)', response.text)))
        except:
            output('[bold][on white]  [black]Error  [/][/]   [red]while finding links in Ask[/][/]');error+=1
            return [0]


def when_done(response: list, domain, type, keyword):
    global hit, bad, done
    try:
        domain = search(":\/\/(www)?([^.]+)", domain).group(2)
        _len = len(response)
        if _len:
            done += _len
            output(f'[bold][on white]   [black]Hit   [/][/]   [green]{type} Found ( {_len} ) {keyword.capitalize()} Valid Links In {domain.capitalize()}[/][/]');hit+=1
            for i in response: Main.save(f'{domain}.txt', i, type=type, keyword=keyword)
        else: output(f'[bold][on white]   [black]Bad   [/][/]   [yellow]{type} Found Nothing In {keyword.capitalize()} In {domain.capitalize()}[/][/]');bad+=1
    except: pass


def start(domain):
    for keyword in keywords:
        try:
            for i in engines: mkdir(f'./results/{date}/{i}/{keyword}')
        except FileExistsError: pass

        ddg = DuckDuckGo(domain, keyword)
        try: when_done((Main(domain).sort(ddg.dorks())), domain=domain, type='DuckDuckGo', keyword=keyword)
        except TypeError: pass

        def _yh():
            for i in range(1, pages):
                yh = Yahoo(domain, keyword)
                try: when_done(Main(domain).sort(yh.get_url(yh.dorks(page=i))), domain=domain, type='Yahoo', keyword=keyword)
                except TypeError: pass

        def _sp():
            for i in range(1, pages):
                sp = StartPage(domain, keyword)
                try: when_done(Main(domain).sort(sp.dorks(page=i)), domain=domain, type='StartPage', keyword=keyword)
                except TypeError: pass

        def _ak():
            for i in range(1, pages):
                ak = Ask(domain, keyword)
                try: when_done(Main(domain).sort(ak.dorks(page=i)), domain=domain, type='Ask', keyword=keyword)
                except TypeError: pass

        to_start = [_ak, _sp, _yh]
        shuffle(to_start)
        for j in range(3): to_start[j]()


threads = []
ti = Thread(target=title);threads.append(ti);ti.start()
cp = Thread(target=counter);threads.append(cp);cp.start()
for domain in domains:
    th = Thread(target=start, args=(domain,))
    threads.append(th)
    th.start()

for thread in threads:
    thread.join()
    clear()
    console.print(logo, style="bold blue")
    output(f'[bold][on white]   [black]Output   [/][/] Done Checking![/]')





