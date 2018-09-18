# coding: utf8
#!/usr/bin/env python

from scipy import spatial
import math
from math import pi
import os
import difflib
from geopy.distance import geodesic
import threading

##########################

angle_max = 8 # In degrees
points_aligned = 10

# Set limitation
lookup_nearest = 100

# Set max distance between portal to origin
max_dist = True # either True or False
max_dist_val = 5 # In km

##########################




def export_ref():
    actions = ["deployed", "captured", "hacked", "created", "destroyed"]
    geo = {}

    with open("game_log.tsv", encoding="utf8") as logs:
        for line in logs:
            for action in actions:
                if action in line:
                    line_a = line.split("\t")
                    geo[line_a[1]] = line_a[1]+","+line_a[2]
    with open("coos.geo", "w") as f:
        for coo in geo.values():
            f.write(coo+"\n")
        
def merge_geo():
    geo = []
    i = 1
    while os.path.exists("coos"+str(i)+".geo"):
        i += 1
    for k in range(i):
        str_i = str(i) if i != 0 else ""
        with open(f"coos{str_i}.geo", encoding="utf8") as f:
            for line in f:
                line_a = line.split(",")
                if line_a[0] == "None":
                    continue
                line_a = (float(line_a[0]), float(line_a[1]))
                if line_a in geo:
                    continue
                geo.append(line_a)
    with open("coos.geo", "w") as f:
        for coo in geo.values():
            f.write(coo+"\n")


def dotproduct(v1, v2):
    return sum((a*b) for a, b in zip(v1, v2))

def length(v):
    return math.sqrt(dotproduct(v, v))

def angle_sub(v1, v2):
    try:
        return math.acos(dotproduct(v1, v2) / (length(v1) * length(v2)))
    except ValueError:
        return 2

def angle(v1, v2):
    return angle_sub(v1, v2)*180/pi
    
def angle_in(origin, ref, point):
    v1 = (ref[0] - origin[0], ref[1] - origin[1])
    v2 = (point[0] - origin[0], point[1] - origin[1])
    return angle(v1, v2)
    
def get_geo():
    geo = []    
    with open("coos.geo", encoding="utf8") as f:
        for line in f:
            line_a = line.split(",")
            if line_a[0] == "None":
                continue
            line_a = (float(line_a[0]), float(line_a[1]))
            geo.append(line_a)
    return geo
    
def progress_calc(i):
    #Progress calculation
    progress = float(i) / progress_calc.progress_max * 100
    if progress > progress_calc.progress_last + 5:
        progress_calc.progress_last = progress
        print(str(int(progress)) +"% done")
        
best_alignments = []
lock = threading.Lock() 

def manage_aligned(best_alignments, aligned):
    global lock
    aligned_nb = len(aligned)
    if aligned_nb <= points_aligned:
        return best_alignments
    for x in best_alignments:
        for y in x:
            if difflib.SequenceMatcher(None, y, aligned).ratio() > 0.9:
                return best_alignments
    lock.acquire()
    while len(best_alignments) < aligned_nb + 1:
        best_alignments.append([])
    best_alignments[aligned_nb].append(aligned)
    lock.release()
    print("Found "+str(aligned_nb)+"!")
    return best_alignments

class compute(threading.Thread):
    def __init__(self, tree, geo):
        threading.Thread.__init__(self)
        self.state = 0
        self.tree = tree
        self.geo = geo

    def run(self):
        self.state = 1
        lock.acquire()
        self.points = [self.geo[index] for index in self.tree.query([self.origin], lookup_nearest)[1][0][1:]]
        lock.release()
        self.is_cluster_aligned()
        self.state = 2
        
    def set_params(self, origin):
        self.origin = origin
        self.state = 0
        
    def is_cluster_aligned(self):
        global best_alignments
        points = self.points
        origin = self.origin
        #For each nearest points, set one as the reference point
        for ref in points:
            aligned = [origin, ref]
            v1 = (ref[0] - origin[0], ref[1] - origin[1])
            
            #For each remaining nearest points
            for point in points:
                if point == ref:
                    continue
                v2 = (point[0] - origin[0], point[1] - origin[1])
                #If the angle (ref, origin, point) and
                #(previous, previous-1, point) are low enough -> aligned
                if angle(v1, v2) < angle_max and angle_in(aligned[-2], aligned[-1], point) < angle_max:
                    if not max_dist or geodesic(point, origin).km < max_dist_val:
                        aligned.append(point)
            #If there are enough aligned points
            best_alignments = manage_aligned(best_alignments, aligned)


        

def get_best_alignments(geo):
    tree = spatial.KDTree(geo)
    global best_alignments
    try:
        progress_calc.progress_last = 0
        nb_points = len(geo)
        progress_calc.progress_max = float(nb_points)
        nb_threads = (os.cpu_count() + 1)
        threads = [compute(tree, geo)] * nb_threads
        
        j = 0
        for i in range(nb_points): # For each point
            progress_calc(i)

            origin = geo[i]
            #nearest = tree.query([origin], lookup_nearest)
            #points = [geo[index] for index in tree.query([origin], lookup_nearest)[1][0][1:]]
            done = False
            while not done:
                done = True
                if j == 0 and threads[j].is_alive():
                    threads[j].join()
                    threads[j].set_params(origin)
                    threads[j].run()
                elif not threads[j].is_alive():
                    threads[j].set_params(origin)
                    threads[j].run()
                else:
                    done = False
                j += 1
                j = j % nb_threads
            #best_alignments = is_cluster_aligned(best_alignments, points, origin)
    except KeyboardInterrupt:
        pass
    try:
        for thread in threads:
            thread.join()
    except:
        pass
    return best_alignments

def print_best_alignments(best_alignments):
    if not best_alignments:
        return
    for x in range(len(best_alignments)):
        if len(best_alignments[x]) > 0:
            print(str(x)+" aligned -> " + str(len(best_alignments[x])) + " found !")
    for x in range(len(best_alignments)):
        aligned_n = best_alignments[x]
        for aligned in aligned_n:
            #print("")
            # print in a format readable by http://www.hamstermap.com/quickmap.php
            for point in aligned:
                print(str(point[0])+","+str(point[1]))

def main():
    if not os.path.exists("coos.geo"):
        print("Parsing game_log.tsv")
        export_ref()
    if os.path.exists("coos1.geo"):
        merge_geo()
    print("looking for alignments")
    print_best_alignments(get_best_alignments(get_geo()))

if __name__ == "__main__":
    main()