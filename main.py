import string
import hashlib
import hmac
import requests
import json
from threading import Thread
import time
import datetime

##################################################################################
ID = "ZOZ0WD80"
CTIME = "1611413629"
SONG_PATH = "/api/v2/song/getInfo"
STREAM_PATH = "/api/v2/song/getStreaming"
LYRIC_PATH = "/api/v2/lyric"
KEY = "882QcNXV4tUZbvAsjmFOHqNC1LpcBRKW"
API_KEY = "kI44ARvPwaqL7v0KuDSM0rGORtdY1nnw"
START = 0
END = 0
STEP = 250
COOKIE = "zmp3_rqid=MHwxNC4xNjEdUngMTMdUngMjE4fG51WeBGx8MTYxNjk0NjYzOTk0Mw;Path=/;Domain=.zingmp3.vn;Expires=Tue, 01-Jun-2021 15:50:39 GMT;Max-Age=5616000"

##################################################################################

def Hash256(value):
    h = hashlib.sha256(value.encode('utf-8'))
    return h.hexdigest()


def Hash512(value, key):
    return hmac.new(key.encode('utf-8'), value.encode('utf-8'), hashlib.sha512).hexdigest()


def getSongUrl(id, ctime):
    sig = Hash512(SONG_PATH + Hash256("ctime=" + ctime +
                  "id=" + id + "version=1.0.19"), KEY)
    return "https://zingmp3.vn/api/v2/song/getInfo?id=" + id + "&ctime=" + ctime + "&version=1.0.19&sig=" + sig + "&apiKey=" + API_KEY


def getLyricUrl(id, ctime):
    sig = Hash512(LYRIC_PATH + Hash256("ctime=" + ctime +
                  "id=" + id + "version=1.0.19"), KEY)
    return "https://zingmp3.vn/api/v2/song/getStreaming?id=" + id + "&ctime=" + ctime + "&version=1.0.19&sig=" + sig + "&apiKey=" + API_KEY


def getID(num):
    id = int2base(num, 21).upper()
    id = id.replace("I", "U")
    id = id.replace("G", "I")
    id = id.replace("H", "O")
    id = id.replace("J", "W")
    id = id.replace("K", "Z")
    while len(id)<6:
        id = '0'+id
        
    return id


digs = string.digits + string.ascii_letters
def int2base(x, base):
    if x < 0:
        sign = -1
    elif x == 0:
        return digs[0]
    else:
        sign = 1

    x *= sign
    digits = []

    while x:
        digits.append(digs[int(x % base)])
        x = int(x / base)

    if sign < 0:
        digits.append('-')

    digits.reverse()

    return ''.join(digits)


##################################################################################

def writeData(path,data):
    f = open(path,'a+',encoding='utf-8')
    obj=json.dumps(data,ensure_ascii=False).encode("utf8")
    f.write(obj.decode()+"\n")

def writeError(path,data):
    f = open(path,'a+',encoding='utf-8')
    obj=json.dumps(data,ensure_ascii=False).encode("utf8")
    f.write(obj.decode()+"\n")

def writeTotal(data):
    f = open("total.txt",'w',encoding='utf-8')
    f.write(str(data))

def getStart():
    f = open("total.txt")
    return int(f.read())
##################################################################################

# cook = ""
# res = requests.get(getSongUrl(getID(85000000),CTIME),headers={"cookie":"abc"})
# cook=res.headers["Set-Cookie"]
# print(cook)
# res = res = requests.get(getSongUrl("ZW"+getID(85000000),CTIME),headers={"Cookie":cook})
# wireData("./Data/vip.txt",res.json())
#print(res.json())


##################################################################################
url_t = "https://604f32afc20143001744c8aa.mockapi.io/api/v1/config/cf"

def resolveObj(obj):
    if "isOffical" in obj:
        del obj["isOffical"]
    if "username" in obj:
        del obj["username"]
    if "isWorldWide" in obj:
        del obj["isWorldWide"]
    if "link" in obj:
        del obj["link"]
    if "isZMA" in obj:
        del obj["isZMA"]
    if "zingChoise" in obj:
        del obj["zingChoise"]
    if "isPrivate" in obj:
        del obj["isPrivate"]
    if "preRelease" in obj:
        del obj["preRelease"]
    if "streamingStatus" in obj:
        del obj["streamingStatus"]
    if "allowAudioAds" in obj:
        del obj["allowAudioAds"]
    if "userid" in obj:
        del obj["userid"]
    if "isRBT" in obj:
        del obj["isRBT"]
    if "album" in obj:
        del obj["album"]
    if "radio" in obj:
        del obj["radio"]
    if "liked" in obj:
        del obj["liked"]
    if "mvlink" in obj:
        del obj["mvlink"]
    if "alias" in obj:
        del obj["alias"]
    if "thumbnail" in obj:
        del obj["thumbnail"]

    listSec = []
    if 'sections' in obj:
        for sec in obj['sections'][0]['items']:
            listSec.append(sec['encodeId'])
    obj['sections'] = listSec

    listArt = []
    if 'artists' in obj:
        for art in obj['artists']:
            listArt.append({"id":art['id'],"name":art['name']})
            writeData("art.txt",{"id":art['id'],"name":art['name']})
    obj['artists']=listArt
    
    listComposers = []
    if 'composers' in obj:
        for com in obj['composers']:
            listComposers.append({"id":com['id'],"name":com['name']})
            writeData("com.txt",{"id":com['id'],"name":com['name']})
    obj['composers'] = listComposers


    listGenres = []
    types=""
    if 'genres' in obj:
        for gen in obj['genres']:
            types+=gen['alias']+"-"
            listGenres.append({"id":gen['id'],"name":gen['name']})
    obj['genres'] = listGenres
    obj['types']=types

    return obj

        




def process_id(prefix,id,cook):
    """process a single ID"""
    try:
        res = requests.get(getSongUrl(prefix+getID(id),CTIME),headers={"cookie":cook},timeout=10)
        obj = res.json()
        #print(obj)
        try:
            if obj['err'] ==-201:
                print("Cookie expire")
                global COOKIE
                COOKIE = res.headers["Set-Cookie"]
                cook=COOKIE
                return process_id(prefix,id,cook)
            elif obj['err'] == -1023:
                return id
                #print("Not found")
            elif obj['err'] == 0:
                r = resolveObj(obj['data'])
                writeData("Data/"+r['types'],r)
            else:
                print("SOMETHING ERROR")
                writeError("error.txt",obj['url'])
        except:
            print("DCM eroorrror")
            writeError("id-err.txt",obj)
        finally:
            #writeError("id-err.txt",obj)
            return id
    except resquest.Timeout:
        print("Timeout------------------------------")
    except resquest.ConnectionError:
        print("Connect ERR------------------------------")
        
    # finally:
    #     print("ERROR CC j do")
    #     writeError("id-err.txt",id)
    #     return id
    return id

def process_range(prefix,id_range, store=None):
    """process a number of ids, storing the results in a dict"""
    if store is None:
        store = {}
    for id in id_range:
        store[id] = process_id(prefix,id,COOKIE)
        #store[id] = id

    return store

def threaded_process_range(nthreads, id_range):
    """process the id range in a specified number of threads"""
    storeZW = {}
    threadsZW = []
    storeZO = {}
    threadsZO = []

    # create the threads
    for i in range(nthreads):
        ids = id_range[i::nthreads]
        t1 = Thread(target=process_range, args=("ZW",ids,storeZW))
        t2 = Thread(target=process_range, args=("ZO",ids,storeZO))
        threadsZW.append(t1)
        threadsZO.append(t2)

    # start the threads
    [ t1.start() for t1 in threadsZW ]
    [ t2.start() for t2 in threadsZO ]
    # wait for the threads to finish
    [ t1.join() for t1 in threadsZW ]
    [ t2.join() for t2 in threadsZO ]

    return storeZO.update(storeZW)


def Clone():
    START = getStart()
    while START > END:
        print("-------------------------------------------")
        print(str(START)+"----"+(datetime.datetime.now().strftime("%X")))
        threaded_process_range(STEP,list(range(START-STEP,START)))
        START-=STEP
        writeTotal(START)
        #time.sleep(1)

if __name__ == "__main__":
    Clone()
