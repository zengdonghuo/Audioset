from update import psrcsv, updating, getvidlst,getOffspring,moving,getaudios,getAllchild,AudiosetStart,get_video,getSegment
import cPickle as cp
import commands
import os

lid_lname_dict,lname_lid_dict, vid_lid_dict, vid_startend_dict = AudiosetStart()
##################################################################434333##################################################
clas = ['Synthetic singing', 'Child singing', 'Female singing', 'Rapping', 'Male singing', 'Chant', 'Choir', 'Mantra', 'Yodeling']
classes = []
classes.extend(clas)
classes.extend('Singing')
class1 = ["Music", "Acoustic environment"]
classes.extend(getOffspring(class1))
classes.extend(class1)
vid_lname_dict2 = updating(vid_lid_dict,lid_lname_dict,classes)

dicts = {}
dict1s = {}
dict2s = {}
dict3s = {}
you_dict = {}

for item in clas:
    item = item.replace(" ", "_")
    globals()[item+"_dict"]={}
    print item+"_dict"
    
for vid, lname in vid_lname_dict2.items():
    lst = list(set(lname).intersection(set(clas)))
    if len(lst)>0:
        dicts[vid] = lst
        if len(lst)==1:
            dict1s[vid] = lst
        elif len(lst)==2:
            dict2s[vid]=lst
        elif len(lst)==3:
            dict3s[vid]=lst
        else:
            print vid,lst
            
for ids, lnames in dict1s.items():
    lists = list(set(lnames).intersection(set(clas)))
    label=lists[0]
    for item in clas:
        if label == item:
            item = item.replace(" ", "_")
            globals()[item+"_dict"][ids]=label

print len(dict1s),'\ndict2s',len(dict2s),'\ndict3s',len(dict3s)
######################################35353535#############################################
with open("/media/zeng/F65C985C5C981A07/zengdonghuo/doc/singsing.pkl","w") as f:
    cp.dump(dicts, f)
    f.close()
######################################34242432#############################################
tempfull = "/home/zeng/Audioset/videoset/fullvideo/"
tempaudio = "/home/zeng/Audioset/videoset/fullaudio/"
orignal = '/home/zeng/Audioset/videoset/video/'
lists = getvidlst(orignal) ## get all existed video
video_lst = dict1s.keys()
candlst = list(set(video_lst).difference(set(lists)))
get_video(candlst, tempfull) ## get full time video from youtube
vid_se_dict = {}
for _item in candlst:
    vid_se_dict[_item]=vid_startend_dict[_item]## get the start and end time
    
getSegment(vid_se_dict, fullvideo, orignal) ## extract 10 sec segment
##out=['-W5c6CeUMPE', '-COelgvUEW4', '-ECK_BisOLM', '-24dqQM_rDk', '-r2-9oyIzkQ', '-IvJaK7HLtQ', '-nQ9a0P1TlY', '-CniGkDLq-Y', '-EVRXQpt1-8', '-F8ZP9sXcKM', '-lK6DOYxQ6s', '-K1BRF6qng8', '-9phJ0sJrXg', '-tpq_bzSKes', '-JfpacjZWyw', '-TvUb8THUq4']
audio_path ="/media/zeng/F65C985C5C981A07/zengdonghuo/Audio/Singing/"
video_path = '/media/zeng/F65C985C5C981A07/zengdonghuo/Video/Singing/'

for item in clas:
    items = item.replace(" ", "_")
    print len(globals()[items+"_dict"])
    dicts = globals()[items+"_dict"]
    target = video_path+items
    print target
    moving(orignal, target, dicts)

getaudios(video_path, audio_path)
