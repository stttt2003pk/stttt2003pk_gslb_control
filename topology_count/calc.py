import os
import sys
from topology import Topology

def bubble_sort_according_to_score(topology_list):

    try:
        iter_len = len(topology_list)
        if iter_len < 2:
            return topology_list
        for i in range(iter_len-1):
            for j in range(iter_len-i-1):
                if topology_list[j].score < topology_list[j+1].score:  
                    topology_list[j], topology_list[j+1] = topology_list[j+1], topology_list[j]
    except:
        print sys.exc_info()
        return 2

files = open('topology20160505OA.txt', 'r')

topology_record = []

for line in files:
    temp = Topology()
    temp.getFromStr(line.strip())
    topology_record.append(temp)
files.close()

topology_dict = {}

for index in topology_record:
    identify = index.service + ':' + index.location
    if identify in topology_dict:
        topology_dict[identify].append(index.datacenter)
    else:
        topology_dict[identify]=[]
        topology_dict[identify].append(index.datacenter)

for index in topology_record:
    identify = index.service + ':' + index.location
    for i in range(len(topology_dict[identify])):
        if index.datacenter == topology_dict[identify][i]:
            index.priority = i + 1
    index.countScore()


bubble_sort_according_to_score(topology_record)
wb = open('OA_GTM_CMD_20160505','wb')
for index in topology_record:
    print index
    wb.write(str(index))
wb.close( )


    

    
        
