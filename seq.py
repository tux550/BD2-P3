import os
import json
import heapq
import numpy as np
from itertools import count
from config import *
from images import ImageLoader, get_image_distance, get_image_vector

### SEQUENTIAL
class SequentialFile():
    def __init__(self, force=True):
        if (force or not os.path.exists(SEQUENTIAL_FILE)):
            self.init_seqfile()

    # ------------------------------------------------
    #                WRITE AND READ
    # ------------------------------------------------
    def init_seqfile(self):
        count = 0
        ### Create Sequential File
        for filename, imgvec in ImageLoader(IMG_LIST):
            with open(SEQUENTIAL_FILE, 'a') as f:
                print(f"DEBUG: SeqFile - #{count} : {filename}")
                count += 1
                data = {filename:list(imgvec)}
                jsondata = json.dumps(data) + "\n"
                f.write(jsondata)

    def read_seqfile(self):
        ### Read Sequential File
        with open(SEQUENTIAL_FILE, 'r') as f:
            for jsondata in f:
                data = json.loads(jsondata)
                for filename, tmp in data.items():
                    imgvec = np.ndarray(shape=(128,))
                    for i in range(128) : imgvec[i] = tmp[i]
                    yield (filename, imgvec)
            
    # ------------------------------------------------
    #                  OPERATIONS
    # ------------------------------------------------
    def KNNSearch(self,q,k):
        tiebreaker = count() # Avoid numpy error from equal vectors
        result = []
        for (filename, imgvec) in self.read_seqfile():
            dist = - get_image_distance(q,imgvec) # Dist negativa para convertir min heap a max heap
            if (len(result) < k):
                heapq.heappush(result, (dist, next(tiebreaker), (filename, imgvec)))
            else:
                current_max = result[0]
                if (current_max[0] < dist):
                    heapq.heappop(result)
                    heapq.heappush(result, (dist, next(tiebreaker), (filename, imgvec)))
        result = [(tup[2], - tup[0]) for tup in result]
        result.sort(key=lambda tup : tup[1])
        return result

    def RangeSearch(self,q,radius):
        result = []
        for (filename, imgvec) in self.read_seqfile():
            dist = get_image_distance(q,imgvec) # Dist negativa para convertir min heap a max heap
            if (dist <= radius):
                result.append( ((filename, imgvec), dist) )
        result.sort(key=lambda tup : tup[1])
        return result

if __name__=="__main__":
    db = SequentialFile(force=False)
    q = get_image_vector('data/lfw/Azra_Akin/Azra_Akin_0001.jpg')

    print("----------")
    print("TEST KNN")
    result = db.KNNSearch(q,3)
    for (filename, _), dist in result:
        print(f"FILE:{filename} <> DIST:{dist}")

    print("----------")
    print("TEST RANGE")
    result = db.RangeSearch(q,0.7)
    for (filename, _), dist in result:
        print(f"FILE:{filename} <> DIST:{dist}")