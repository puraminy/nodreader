#v2 tehran
import requests
from time import sleep
import sys, os 
import datetime
import shlex
import re
import textwrap
import json
from termcolor import colored
import getch as gh
from utility import *
import curses as cur
from curses import wrapper
cW = 0
cR = 2
cG = 3
cY = 4
cB = 5
cPink = 14
cC = 7
clC = 15
clY = 12
cGray = 9
clGray = 249
clG = 11
cllC = 82
cO = 209
cW_cB = 250

def err(msg):
    print("")
    print(""+msg)
    ch = get_key(std)
    return ch
def switch(d, art, ch):
    key = art["id"]
    sects = 'abstract introduction conclusion'
    if not key in d:
        if ch == ord('s'):
           d[key] = sects.split(' ')
        else:
           d[key] = [s["title"].lower() for s in art["sections"]]
    else: 
        del d[key]

def request(std, query, page = 1, size=40, filters = None):
    global cW, cR, cG ,cY ,cB ,cPink ,cC ,clC ,clY ,cGray ,clGray ,clG , cllC ,cO, cW_cB
     

    page = int(page)
    page -= 1

    clear_screen(std)
    opts = {"output":"","text_color":246, "head_color":cGray, "merge":True}
    ranges = {}
    ind = {}
    #if not query and task == "All":
    #    return "query is mandatory!"
    headers = {
        'Connection': 'keep-alive',
        'Accept': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Mobile Safari/537.36',
        'Content-Type': 'application/json',
        'Origin': 'https://dimsum.eu-gb.containers.appdomain.cloud',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Dest': 'empty',
        'Referer': 'https://dimsum.eu-gb.containers.appdomain.cloud/',
        'Accept-Language': 'en-US,en;q=0.9',
    }
    size = int(size)
    filters_str = json.dumps(filters)
    data = f'{{"query":"{query}","filters":{filters_str},"page":{page},"size":{size},"sort":null,"sessionInfo":""}}'
    #data ='{"query":"reading comprehension","filters":{},"page":0,"size":30,"sort":null,"sessionInfo":""}'

    # print(data)
    rows, cols = std.getmaxyx()
    win_help = cur.newwin(1, cols, rows-1,0) 
    show_info("Getting articles...", win_help)
    try:
        response = requests.post('https://dimsum.eu-gb.containers.appdomain.cloud/api/scholar/search', headers=headers, data=data)
    except requests.exceptions.HTTPError as errh:
        print ("Http Error:",errh)
    except requests.exceptions.ConnectionError as errc:
        print ("Error Connecting:",errc)
    except requests.exceptions.Timeout as errt:
        print ("Timeout Error:",errt)
    except requests.exceptions.RequestException as err:
        print ("OOps: Something Else",err)

    clear_screen(std)
    conference = ''
    if "conference" in filters:
        conference = filters['conference']
    task = ''
    if "task" in filters:
        task = filters['task']
    dataset = ''
    if "dataset" in filters:
        dataset = filters['dataset']
    year = ''
    if "year" in filters:
        year = filters['year']
    folder = query + '_' + str(year) + '_' + str(page) + '_' + conference + '_' + task + '_' + dataset
    folder = folder.replace(' ','_')
    folder = folder.replace('__','_')
    folder = folder.replace('__','_')

    articles = response.json()['searchResults']['results']
    ch = ''
    sels = {}
    start = 0
    sects_num,frags_num = 0,0
    k,fc,sc  = 0,0,0
    N = len(articles)
    mode = 'list'
    ls = True
    fast_read = False
    cend = '\x1b[0m'
    cend2 = '\033[0m'
    cgray = '\033[90m'
    begin_x = 10; begin_y = 1 
    height = 4; width = 80
    title_win = cur.newwin(height, width, begin_y, begin_x)
    text_win = cur.newwin(rows - 5, 80, 3, 5)
    sect_win = cur.newwin(rows - 5, 20, 3, 0)
    # text_win = std
    if N == 0:
        return "No result fond!"
    while ch != ord('q') and ch != ord('g'):
        clear_screen(text_win)
        k = max(k, 0)
        k = min(k, size-1)
        art = articles[k]
        art_id = art['id']
        if mode == 'd':
           a = art
           clear_screen(std)
           sn = 0
           sects_num = len(a["sections"])
           sc = max(sc, 0)
           sc = min(sc, sects_num)
           title = "\n".join(textwrap.wrap(a["title"], 80)) # wrap at 60 characters
           top =  "["+str(k)+"] " + title
           print_there(0, 0, top,  title_win, cC) 
           for b in a["sections"]:
               if sn != sc:
                   sect_title = b["title"]
                   if art_id in sels and b["title"].lower() in sels[art_id]:
                       # print_there(sn,0, b["title"], sect_win, 7)
                       mprint(sect_title, text_win, cW_cB, True)
                   else:
                       # print_there(sn, 0, b["title"], sect_win, 10)
                       mprint(sect_title, text_win, cGray, True)
               else:
                   frags_num = len(b['fragments'])
                   frags_text = ""
                   for c in b['fragments']:
                       frags_text += '\n\n' + c['text']
                   if False: #fast_read:
                       words = frags_text.split()                
                       for word in words:
                          print_there(20, 40, colored(word + ' '.join([10*' ']), 'green') + cend, std)
                          sleep(len(word)*0.05)
                   sents = split_into_sentences(frags_text)    
                   frags_num = len(sents)
                   sect_title = b["title"] + f"({fc+1}/{frags_num})" 
                   if art_id in sels and b["title"].lower() in sels[art_id]:
                       # print_there(sn,0, sect_title, sect_win, 7)
                       mprint(sect_title, text_win, cW_cB)
                   else:
                       # print_there(sn,0, sect_title, sect_win, 10)
                       mprint(sect_title, text_win, int(opts["head_color"]), True)
                   # mprint(frags_text, text_win, 4)
                   for fn, text in enumerate(sents):
                       if fn == fc:
                          frag = "\n".join(textwrap.wrap(text, 76)) 
                          frag =  textwrap.indent(frag, " "*2) 
                          mprint(frag, text_win, int(opts["text_color"]))
                          # print_there(0,0, frag, text_win, 3)


               sn += 1
        else:
            for j,a in enumerate(articles[start:start + 15]): 
                i = start + j
                paper_title =  a['title']
                dots = ""
                if len(paper_title) > 80:
                   dots = "..."
                item = "{}{} {}".format(i, ":", paper_title[:73] + dots)               
                color = 0
                if a["id"] in sels:
                    color = clG
                if i == k:
                    color = clC

                mprint(item, text_win, color)

        #print(":", end="", flush=True)
        ch = get_key(std)
        if ch == ord('q') and mode == 'd':
            mode = 'list'
        if ch == ord('x'):
            fast_read = not fast_read
        if ch == ord('f') or ch == ord('s'):
            switch(sels, art, ch)

        if ch == ord('a'):
            for ss in range(start,start+15):
                  rr = articles[ss]
                  switch(sels, rr, 's')

        if ch == ord('c') and mode == 'd':
            cur_sect = art["sections"][sc]["title"].lower()
            if art_id in sels:
                if cur_sect in sels[art_id]:
                    sels[art_id].remove(cur_sect)
                else:
                    sels[art_id].append(cur_sect)
            else:
                sels[art_id] = [cur_sect]
        if ch == ord('p'):
            k-=1
        if ch == ord(":"):
            cmd = minput(win_help, 0, 0, ":")
            cmd = cmd.strip()
            if len(cmd) == 1:
                ch = cmd
            cmd = cmd.split('=')
            if len(cmd) > 1:
                key = cmd[0].strip()
                val = cmd[1].strip()
                if key not in opts:
                    show_err(key + " is an invalid option, press any key...", win_help)
                else:
                   mi = list(opts.keys()).index(key)
                   if key not in ranges:
                       opts[key] = val
                   else:
                        if val in ranges[key]:
                            opts[key] = val
                            ind[key] = ranges[key].index(val)
                        else:
                            show_err(val + " is invalid for " + key + ", press any key ...", win_help)
            else:
                cmd = re.split(r'\s(?=")', cmd) 
                if len(cmd) > 1:
                    cmd = cmd[0].strip()
                    arg = cmd[1].strip()
                    if cmd == 'w':
                        folder = arg
        if ch == ord('n'):
            k+=1
        if ch == cur.KEY_RIGHT and mode == 'd': 
                fc += 1
        if ch == ord('l') or ch == 127:
            mode = 'list'
        if ch == ord('d') or ch == cur.KEY_RIGHT or ch == 10 or ch == 9:
            if mode == 'list':
                mode = 'd'
                fc = 0
                sc = 0
        elif ch == cur.KEY_LEFT:
            if mode == 'd':
                fc -= 1
        elif ch == cur.KEY_UP:
            if mode == 'd': 
                sc -= 1
                fc = 0
            else:
                k -=1
        elif ch == cur.KEY_DOWN:
            if mode == 'd':
                sc += 1
                fc = 0
            else:
                k +=1
        elif ch == cur.KEY_HOME:
            if mode == 'd':
                sc = 0
                fc = 0
            else:
                k = start
        elif ch == cur.KEY_END:
            if mode == 'd':
                sc = sects_num
                fc = 0
            else:
                k = start + 14

        if mode == 'd':
            if fc < 0:
                fc = 0
                if sc > 0:
                    sc -=1
                else:
                    mode = 'list'
            elif fc >= frags_num:
                fc = 0
                if sc < sects_num - 1:
                    sc +=1
                else:
                    k +=1
                    sc = 0
        if k >= start + 15:
            ch = cur.KEY_NPAGE
        if k < start:
            ch = "prev_pg"
        if ch == cur.KEY_NPAGE:
            if mode == 'list':
                start += 15
                start = min(start, N - 15)
                k = start
            else:
                k +=1
        if ch == cur.KEY_PPAGE or ch == 'prev_pg':
            if mode == 'list':
                start -= 15
                start = max(start, 0)
                k = start + 14 if ch == 'prev_pg' else start
            else:
                k -= 1
        if ch == ord('w') or ch == ord('m'):
            merge = ch == 'm'
            if not sels:
                print_there(80,10,colored("No article selected!!",'red'), std)
            else:
                if merge:
                    f = open(folder + '.html', "w")
                    print("<!DOCTYPE html>\n<html>\n<body>", file=f)
                elif not os.path.exists(folder):
                    os.makedirs(folder)
                num = 0
                for j,a in enumerate(articles): 
                    i = start + j
                    _id = a["id"]
                    if  _id not in sels:
                        continue
                    num += 1
                    paper_title = a['title']
                    print_there(80,10, paper_title + '...', std)
                    file_name = paper_title.replace(' ','_').lower()
                    if not merge:
                       f = open(folder + '/' + file_name + '.html', "w")
                       print("<!DOCTYPE html>\n<html>\n<body>", file=f)
                    print("<h1>" +  "New Paper" + "</h1>", file=f)
                    print("<h1>" +  paper_title + "</h1>", file=f)
                    for b in a['sections']:
                        title =  b['title']
                        _sects = sels[_id]
                        if not title.lower() in _sects:
                            continue
                        print("<h2>", file=f)
                        print(title, file=f)
                        print("</h2>", file=f)
                        for c in b['fragments']:
                                text= c['text']
                                f.write("<p>" + text + "</p>")

                        print("<p> Paper was:" +  paper_title + "</p>", file=f)
                    print("</body>\n</html>", file=f)
                    if not merge:
                      f.close()
                #for
                if merge:
                    f.close()
                print_there(80,10, str(num)+ " articles were downloaded and saved into:" + folder, std)
            ch = get_key(std)
    return "" 

def refresh_menu(opts, menu_win, sel):
    global clG
    clear_screen(menu_win)
    for k, v in opts.items():
       if k == sel:
           mprint("{:<15}:{}".format(k, v), menu_win, clG)
       else:
           mprint("{:<15}:{}".format(k, v), menu_win)

def get_sel(opts, mi):
    mi = max(mi, 0)
    mi = mi if mi < len(opts) else 0 
    return list(opts)[mi], mi

def show_info(msg, win, color=cC):
    clear_screen(win)
    print_there(0,1, msg, win, color)

def show_err(msg, win, color=cR):
   show_info(msg, win, color)
   win.getch()
   clear_screen(win)

def main(std):

    global cR, cG ,cY ,cB ,cPink ,cC ,clC ,clY ,cGray ,clGray ,clG , cllC ,cO, cW_cB
    filters = {}
    now = datetime.datetime.now()
    filter_items = ["year", "conference", "dataset", "task"]
    opts = {"query":"reading comprehension", "year":"","page":1,"page-size":30,"task":"", "conference":"", "dataset":""}
    ranges = {
            "year":["All"] + [str(y) for y in range(now.year,2010,-1)], 
            "page":[str(y) for y in range(1,100)],
            "page-size":[str(y) for y in range(30,100,10)], 
            "task": ["All", "Reading Comprehension", "Machine Reading Comprehension","Sentiment Analysis", "Question Answering", "Transfer Learning","Natural Language Inference", "Computer Vision", "Machine Translation", "Text Classification", "Decision Making"],
            "conference": ["All", "Arxiv", "ACL", "Workshops", "EMNLP", "IJCNLP", "NAACL", "LERC", "CL", "COLING", "BEA"],
            "dataset": ["All","SQuAD", "RACE", "Social Media", "TriviaQA", "SNLI", "GLUE", "Image Net", "MS Marco", "TREC", "News QA" ]
            }
    ind = { "conference":0, "year":0, "page":0, "page-size":0, "task":0, "dataset":0 }

    mi = 0
    ci = 0
    confs = ["", "ACL","CLING","MSI","CLI"]
    ch = 'a'
    mode = 'm'
    cur.start_color()
    cur.use_default_colors()
    for i in range(0, cur.COLORS):
        cur.init_pair(i + 1, i, -1)
    cur.init_pair(250, cur.COLOR_WHITE, cur.COLOR_BLUE)

    menu_win = cur.newwin(10, 50, 3, 5)
    sub_menu_win = cur.newwin(12,30,5,50)
    rows, cols = std.getmaxyx()
    win_help = cur.newwin(1, cols, rows-1,0) 
    hide_cursor()
    _help = False
    for opt in opts:
       if opt in ranges:
           opts[opt] = ranges[opt][ind[opt]]
    clear_screen(std)
    print_there(2,0, "<< Nodreader V 1.0 >>".center(80))
    while ch != ord('q'):
        clear_screen(std)
        clear_screen(sub_menu_win)
        sel,mi = get_sel(opts, mi)
        if sel in ranges:
            opts[sel] = ranges[sel][ind[sel]]

        refresh_menu(opts, menu_win, sel)
        if mode == 's':
           if sel not in ranges:
              opts[sel]=""
              refresh_menu(opts, menu_win, sel)
              val = minput(menu_win, mi + 0, 0, "{:<15}".format(sel) + ":") 
              opts[sel] = val
              mi += 1
              sel,mi = get_sel(opts, mi)
              refresh_menu(opts, menu_win, sel)
              mode = 'm'
           else:
              count = 0
              for vi, v in enumerate(ranges[sel]):
                count += 1
                if count > 10:
                    break
                if vi == ind[sel]:
                   mprint(str(v),sub_menu_win, cO)
                else:
                   mprint(str(v), sub_menu_win, cC)

        if _help:
            if mode == 'm':
                show_info("Press <Enter> to set a value, r to search and q to quit.", win_help)
            else:
                show_info("Press <Enter> to set a value", win_help)
        ch = get_key(std)
        
        if ch == ord(':'):
            # show_cursor()
            cmd = input(":")
            hide_cursor()
            cmd = cmd.split('=')
            if len(cmd) == 1:
                ch = cmd[0]
            if len(cmd) > 1:
                key = cmd[0].strip()
                val = cmd[1].strip()
                if key not in opts:
                    err(key + "is an invalid option")
                else:
                   mi = list(opts.keys()).index(key)
                   if key not in ranges:
                       opts[key] = val
                   else:
                        if val in ranges[key]:
                            opts[key] = val
                            ind[key] = ranges[key].index(val)
                        else:
                            err(val + " is invalid for " + key)
        if ch == ord("h"):
            _help = not _help
        if ch == cur.KEY_DOWN:
            if mode == "m":
                mi += 1
            elif sel in ranges:
                ind[sel] += 1
        if ch == cur.KEY_UP:
            if mode == "m":
                mi -= 1
            elif sel in ranges:
                ind[sel] -= 1

        if sel in ranges:
            ind[sel] = min(ind[sel], len(ranges[sel]))
            ind[sel] = max(ind[sel], 0)
        if  ch == cur.KEY_ENTER or ch == 10 or ch == 13:
            mode = 's' if mode == 'm' else 'm'
        if ch == cur.KEY_RIGHT:
            mode = 's'
        elif ch == cur.KEY_LEFT:
            mode = 'm'
        elif ch == ord('q'):
            # show_cursor()
            break;
        elif ch == ord('r') or ch == ord('g'): 
            for k,v in opts.items():
                if k in filter_items and v and v != "All":
                    filters[k] = str(v)
            clear_screen(std)
            try:
                ret = request(std, opts["query"], opts["page"], opts["page-size"], filters)
                if ret:
                    err(ret)
            except KeyboardInterrupt:
                # show_cursor()
                ch = ord('q')


if __name__ == "__main__":
    wrapper(main)
