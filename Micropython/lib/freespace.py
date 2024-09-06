import os
def get_freespace():
    x = os.statvfs("/pyboard")
    blocksize = x[0]
    freeblocks = x[3]
    kilobytes = freeblocks * blocksize / 1024      
    return kilobytes

kilobytes = get_freespace()
print(kilobytes, "kB free")

