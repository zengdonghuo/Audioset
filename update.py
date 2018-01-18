#!/usr/bin/env python
import csv
import commands
from compiler.ast import flatten
import os
import re
import cPickle as cp
import json

'''
    read [class_labels_indics] file
    result:(lid,lname) and (lname,lid)
'''

def psrcsv(file_path, tag):
    with open(file_path) as csvfile:
        reader = csv.reader(csvfile)
        headings = next(reader)
        print "The headings is like this:",headings,'\n'
        point = 0
        
        if tag=="cli":
            lid_lname_dict = {}
            lname_lid_dict = {}
            for re in reader:
                point+=1
                if point>=1:
                    lid = re[1]
                    lname = re[2].strip()
                    lid_lname_dict[lid] = lname
                    lname_lid_dict[lname] = lid
            csvfile.close()
            
            return lid_lname_dict, lname_lid_dict

        elif tag=="bt":
            vid_lid_dict = {}
            vid_startend_dict = {}
            for _line in reader:
                point+=1
                lst = []
                if point<3:
                    print _line,point
                else:
                    mid = _line[0].strip()
                    start, end = _line[1].strip(), _line[2].strip()
                    vid_startend_dict[mid] = start,end
                    labels = _line[3:] # lid list
                    [lst.append(_item.replace('"','').strip()) for _item in labels]
                    vid_lid_dict[mid] = lst
            csvfile.close()
            
            return vid_lid_dict, vid_startend_dict

def AudiosetStart():
    path = '/home/zeng/Audio_tensorflow/audioset/'
    lid_lname_dict,lname_lid_dict = psrcsv(path+'class_labels_indices.csv', 'cli')
    print "The output result of [class_labels_indices.csv], for example:\n1.",\
          dict(lid_lname_dict.items()[:10]),"\n2.",dict(lname_lid_dict.items()[:10]),'\n'

    dict1, dict2 = psrcsv(path+'label/balanced_train_segments.csv','bt')
    dict3, dict4 = psrcsv(path+'label/eval_segments.csv','bt')
    vid_lid_dict = dict(dict1, **dict3)
    vid_startend_dict = dict(dict2, **dict4)
    
    print '\nThe vid_lid_dict is like this:\n',\
          dict(vid_lid_dict.items()[:5])

    return lid_lname_dict,lname_lid_dict, vid_lid_dict, vid_startend_dict
    
def get_label_lst(path):
    dicts = {}
    with open(path) as fs:
        lines = fs.readlines()
        fs.close()
    
    for lin in lines:
        ln = lin.rstrip('\n').split('\t')
        dicts[ln[0]]=ln[2]
        
    return dicts

def updating(vid_lid_dict,lid_lname_dict,inputs):
    vid_lname_dict={}
    if type(inputs) is dict:
        lsts = inputs.keys()
    elif type(inputs) is list:
        lsts = inputs
    for item,label in vid_lid_dict.items():
        lab = []
        for ii in label:
            name=lid_lname_dict[ii]
            lab.append(name)
        if set(lab).issubset(set(lsts)):
            vid_lname_dict[item]=lab

    return  vid_lname_dict

def get_multi_only(vid_lid_dict,lid_lname_dict,dicts):
    multi_dict = {}
    onlyone_dict = {}

    vid_lname_dict = updating(vid_lid_dict, lid_lname_dict,dicts)
    for item,label in vid_lname_dict.items():
        if len(label)>1 and '' not in label:
            multi_dict[item]=label
        else:
            onlyone_dict[item]=label
            
    with open("doc/multi_dict.csv","w") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['index', 'vid', 'label'])
        for index,(vid,label) in enumerate(multi_dict.items()):
            writer.writerow([str(index),str(vid),str(';'.join(label))])
        csvfile.close()
                            
    with open("doc/onlyone_dict.csv","w") as csvfiles:
        writers = csv.writer(csvfiles)
        writers.writerow(['index', 'vid', 'label'])
        for indexs,(vids,labels) in enumerate(onlyone_dict.items()):
            writers.writerow([str(indexs),str(vids),str(''.join(labels))])
        csvfiles.close()
        
    lname_vid_mdict = {}
    lname_vid_odict = {}
    for item in dicts.keys():
        lname_vid_mdict[item]=[]
    for items in dicts.keys():
        lname_vid_odict[items]=[]
        
    
    for vid,lablst in multi_dict.items():
        for lab in lablst:
            if lname_vid_mdict.has_key(lab):
                lname_vid_mdict[lab].append(vid)
            else:
                lname_vid_mdict[lab]=[]

    for ks,vs in onlyone_dict.items():
        labels = ''.join(vs)
        if lname_vid_odict.has_key(labels):
            lname_vid_odict[labels].append(ks)
        else:
            lname_vid_odict[labels]=[]
            
    with open("doc/lname_vid_mdict.txt",'w') as f:
        for _lname, _vidlst in lname_vid_mdict.items():
            line = _lname+":"+'<SEP>'.join(_vidlst)+'\n'
            f.write(line)
        f.close()
        
    with open("doc/lname_vid_odict.txt",'w') as fs:
        for _lname, _vidlst in lname_vid_odict.items():
            lines = _lname+":"+'<SEP>'.join(_vidlst)+'\n'
            fs.write(lines)
        fs.close()
        
    return multi_dict, onlyone_dict,lname_vid_mdict,\
           lname_vid_odict,onlyone_dict,multi_dict

def getlid(path):
    '''get all 100% labels'''
    ranks_lst = []
    id_label_lst = []
    rank_dict={}
    pattern_rule=re.compile(r'\t|:')
    with open(path) as g:
        rank_lst = g.readlines()
        for item1 in rank_lst:                
            item1_str = re.sub(pattern_rule, '=', item1)
            item1_lst = item1_str.split('=')
            assert item1_str.count('=')==2
            ranks_lst.append(item1_lst[1])## ranks_lst contain all 79 classes names
            rank_dict[item1_lst[1]]=item1_lst[2].strip()
        g.close()
        
    return rank_dict
                    
def getAudios():
    orignal = "/home/zeng/Audioset/videoset/20video/"
    target = "/home/zeng/Audioset/videoset/20audio/"
    lsts = []
    for dirpaths, dirnames, filenames in os.walk(orignal):
        lsts.extend(dirnames)
        if len(dirpaths.split("/")[-1])>0:
            lname=dirpaths.split("/")[-1]
            os.chdir(target)
            comm="mkdir "+lname
            commands.getstatusoutput(comm)
            os.chdir(orignal+lname)
            for filename in filenames:
                inputs = filename
                outputs = target+lname+"/"+filename.replace(".mkv", ".mp3")
                print outputs
                line = "ffmpeg -i "+inputs+" -f mp3 -vn "+outputs
                try:
                    commands.getstatusoutput(line)
                except:
                    print item

def getvidlst(path):
    lists=[]
    for dirpaths, dirnames, filenames in os.walk(path):
        for files in filenames:
            files = files.replace(".mkv", "")
            lists.append(files)
        
    return lists

def json_reading():
    with open("ontology.json", 'r') as f:
        data = json.load(f)
        f.close()
        return data

###################################################################################
'''Use id and name to search related informations'''
def id_search_name(mid):
    data = json_reading()
    for item in range(len(data)):
        index = data[item]
        if index['id']==mid:
            return [index['name'],index['description'], index['citation_uri'], \
                    index['positive_examples'], index['child_ids'],\
                    index['restrictions']]
        
def name_search_id(name):
    data = json_reading()
    for item in range(len(data)):
        index = data[item]
        if index['name']==name:
            return [index['id'],index['description'], index['citation_uri'], \
                    index['positive_examples'], index['child_ids'],\
                    index['restrictions']]
        
############################getting children process#########################
def getchild(father): ## father is video id
    children = []
    if '/' in father:
        try:
            child = id_search_name(father)[4]
        except:
            print 'Please! input a right string format! instead of',type(father)
            return 0
    else:
        child = name_search_id(father)[4]
    for chi in child:
        children.append(id_search_name(chi)[0])
        
    return list(set(children))

def getChildren(father): ## father is video id
    lsts = []
    childlst = []
    lee = []
    data = json_reading()
    lst = getchild(father)
    if len(lst)>0:
       childlst.extend(lst)
       for ls in lst:
           child = getAllchild(ls)
           for _ch in child:
               if _ch:
                   lsts.append(_ch)
    
    return childlst, lsts

def getAllchild(father):
    lists = []
    childlst, lsts = getChildren(father)
    lists.extend(childlst)
    lists.extend(lsts)
    
    return list(set(lists))

def getOffspring(classlst):
    labelSet = []
    for item in classlst:
        child = getAllchild(name_search_id(item)[0])
        if child:
            labelSet.extend(child)
            
    return labelSet


def moving(orignal, target, dicts):
    pattern_rule=re.compile(r',')
    name = target.split('/')[-1]
    for vid in dicts:
        os.chdir(target.replace(name,''))    
        comm="mkdir "+name
        commands.getstatusoutput(comm)
        os.chdir(orignal)
        line = 'cp '+vid+'.mkv '+target
        try:
            commands.getstatusoutput(line)
        except:
            print vid

def get_video(vid_lst, loadfile):
    '''
        Use youtube id list to crawl fulltime videos
        You need input youtube id list and your expected video path
    '''
    filename = ''
    for item in vid_lst:
        if loadfile[-1]=="/":
            filename = loadfile+str(item)
        else:
            filename = loadfile+"/"+str(item)
        path = "http://www.youtube.com/watch?v="+item
        line = "youtube-dl -o "+filename+' '+path
        try:
            commands.getstatusoutput(line)
        except:
            print item

def formats(seconds):
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    forms = "%02d:%02d:%02d" % (h, m, s)
    return forms

def getSegment(vid_startend_dict, fvideofile, videofile):
    for vid, (start, end) in vid_startend_dict.items():
        start = int(start.split(".")[0])
        end = int(end.split(".")[0])
        duration = end-start
        start = formats(start)
        name = ""+vid+".mkv"
        segment = videofile+name
        os.chdir(fvideofile)
        line = "ffmpeg -y -i "+name+" -ss "+str(start)+" -t "+str(duration)+" -c copy -avoid_negative_ts 1 "+segment
    try:
        commands.getstatusoutput(line)
    except:
        print item

def getaudios(orignal, target):
    lsts = []
    for dirpaths, dirnames, filenames in os.walk(orignal):
        lsts.extend(dirnames)
        if len(dirpaths.split("/")[-1])>0:
            lname=dirpaths.split("/")[-1]
            os.chdir(target)
            comm="mkdir "+lname
            commands.getstatusoutput(comm)
            os.chdir(orignal+lname)
            for filename in filenames:
                inputs = filename
                outputs = target+lname+"/"+filename.replace(".mkv", ".mp3")
##                print outputs
                line = "ffmpeg -i "+inputs+" -f mp3 -vn "+outputs
                try:
                    commands.getstatusoutput(line)
                except:
                    print item
                    
###########################end getting children process#######################

    
