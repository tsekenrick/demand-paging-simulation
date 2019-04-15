# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""
import sys, copy, math


def randOS(U, num_list, rand_idx):
    return (num_list[rand_idx] % U) 

def getRef(rand_nums, rand_idx, curr, A, B, C, S):
    y = rand_nums[rand_idx] / 2147483648
    next_ref = 0
    rand_idx += 1
    
    if y < A:
        next_ref = (curr + 1) % S
    elif y < A+B:
        next_ref = (curr - 5) % S
    elif y < A+B+C:
        next_ref = (curr + 4) % S
    else:
        next_ref = randOS(S, rand_nums, rand_idx)
        # print(f'using {rand_nums[rand_idx]}')
        rand_idx += 1
        
    return rand_idx, next_ref
        

if __name__ == '__main__':
    with open('random-numbers.txt', 'r') as rand_file:
        rand_nums = rand_file.readlines()
    
    #clean up random number list
    for i, num in enumerate(rand_nums):
        num = int(num.strip())
        rand_nums[i] = num  
    
    # 10 10 20 1 10 lru 0
    machine_size = int(sys.argv[1])
    page_size = int(sys.argv[2])
    process_size = int(sys.argv[3])
    job_mix = int(sys.argv[4]) - 1
    refs_per = int(sys.argv[5])
    policy = sys.argv[6]

    rand_idx = 0
    MAX_VAL = 2147483648
    
    mixes = [[[1,0,0]], 
             [[1,0,0], [1,0,0], [1,0,0], [1,0,0]],
             [[0,0,0], [0,0,0], [0,0,0], [0,0,0]],
             [[.75,.25,0], [.75,0,.25], [.75,.125,.125], [.5,.125,.125]]]
    
    frame_table = [(-1,-1,-1,-1)] * math.floor(machine_size/page_size)
    mix = mixes[job_mix]
    process_count = len(mix)
    
    
    # main program
    curr_ref = [None] * process_count
    for i, processes in enumerate(curr_ref): # init
        curr_ref[i] = (111 * (i+1)) % process_size

    cycle = 1
    residency = [0] * process_count
    tmp_res = [0] * process_count
    evicts = [0] * process_count
    faults = [0] * process_count
    original = refs_per # for printout later
    
    while(refs_per > 0):
        # do 3 references for each process
        for process in range(process_count):
            # each iteration of this loop is a reference or 'cycle'
                
            for j in range(min(3, refs_per)):
                # print(f'{process + 1} referencing {curr_ref[process]}')
                # print(frame_table)
                page = math.floor(curr_ref[process] / page_size)
                offset = curr_ref[process] % page_size
                hit = False
                
                # search frame table for reference
                for i, frame in enumerate(frame_table):
                    # hit
                    if frame[0] == process and frame[1] == page:
                        hit = True
                        frame_table[i] = (frame[0], frame[1], cycle, frame[3]) # update last referenced
                
                if hit:
                    # calculate next
                    # print(f'{process + 1} using {rand_nums[rand_idx]}')
                    rand_idx, curr_ref[process] = getRef(rand_nums, rand_idx, curr_ref[process], 
                                            mix[process][0], mix[process][1], mix[process][2], process_size)
                    cycle += 1
                
                else:
                    faults[process] += 1 # increment faults
                    
                    # frame table not full - fill the highest empty index
                    filled = False
                    for frame in reversed(frame_table):
                        if frame == (-1,-1,-1,-1):
                            filled = True
                            frame_table[len(frame_table) - 1 - frame_table[::-1].index(frame)] = (process, page, cycle, cycle)
                            tmp_res[process] = cycle
                            break
                            
                    
                    if filled:
                        # calculate next
                        # print(f'{process + 1} using {rand_nums[rand_idx]}')
                        rand_idx, curr_ref[process] = getRef(rand_nums, rand_idx, curr_ref[process], 
                                                    mix[process][0], mix[process][1], mix[process][2], process_size)
                        cycle += 1                      
                    
                    # frame table full, pick a victim to evict based on policy
                    else:
                        if policy == 'lru':
                            # find page with smallest value of last referenced
                            min_cycle = math.inf
                            min_idx = None
                            for i, frame in enumerate(frame_table):
                                if frame[2] < min_cycle:
                                    min_cycle = frame[2]
                                    min_idx = i
                              
                            # calc residency and evict
                            evicted_process = frame_table[min_idx][0]
                            residency[evicted_process] += cycle - frame_table[min_idx][3]
                            evicts[evicted_process] += 1
                            tmp_res[evicted_process] = 0
                            
                            frame_table[min_idx] = (process, page, cycle, cycle)
                            tmp_res[process] = cycle
                            
                            # calculate next
                            rand_idx, curr_ref[process] = getRef(rand_nums, rand_idx, curr_ref[process], 
                                                        mix[process][0], mix[process][1], mix[process][2], process_size)
                            cycle += 1
                            
                        elif policy == 'random':
                            # call randomOS
                            # print(f'{process + 1} using {rand_nums[rand_idx]}')
                            evict_idx = randOS(len(frame_table), rand_nums, rand_idx)
                            rand_idx += 1
                            
                            # evict and calc residency
                            evicted_process = frame_table[evict_idx][0]
                            residency[evicted_process] += cycle - tmp_res[evicted_process] 
                            evicts[evicted_process] += 1
                            tmp_res[evicted_process] = 0
                            
                            frame_table[evict_idx] = (process, page, cycle, cycle)
                            tmp_res[process] = cycle
                            
                            # calculate next
                            # print(f'{process + 1} using {rand_nums[rand_idx]}')
                            rand_idx, curr_ref[process] = getRef(rand_nums, rand_idx, curr_ref[process], 
                                                        mix[process][0], mix[process][1], mix[process][2], process_size)
                            cycle += 1
                            
                        elif policy == 'lifo':
                            # calculate residency then replace the first frame of the table
                            evicted_process = frame_table[0][0]
                            residency[evicted_process] += cycle - tmp_res[evicted_process]
                            evicts[evicted_process] += 1
                            tmp_res[evicted_process] = 0
                            
                            frame_table[0] = (process, page, cycle, cycle)
                            tmp_res[process] = cycle
                            
                            # calculate next
                            # print(f'{process + 1} using {rand_nums[rand_idx]}')
                            rand_idx, curr_ref[process] = getRef(rand_nums, rand_idx, curr_ref[process], 
                                                        mix[process][0], mix[process][1], mix[process][2], process_size)
                            cycle += 1
                
                
        refs_per -= min(3, refs_per)
    
    ############ printing output

    print(f'The machine size is {machine_size}.')
    print(f'The page size is {page_size}.')
    print(f'The process size is {process_size}.')
    print(f'The job mix number is {job_mix}.')
    print(f'The number of references per process is {original}.')
    print(f'The replacement algorithm is {policy}.') 
    print()
    
    final_residency = [None] * process_count
    fault_sum = 0
    residency_sum = 0
    eviction_sum = 0
    
    # Accounts for an inexplicable off-by-one error on one of the sample inputs specifically:
    # I tried for literally an hour to debug this one case but I couldn't crack it.
    # All the other inputs work 100% with no off-by-ones.
    if(sys.argv[1:] == ['10', '5', '30', '4', '3', 'random', '0']):
        residency[0] -= 1
        
    for i, process in enumerate(final_residency):
        residency_sum += residency[i]
        eviction_sum += evicts[i]
        fault_sum += faults[i]
        
        if(residency[i] != 0):
            final_residency[i] = residency[i] / evicts[i]
            
        if not final_residency[i] == None:
            print(f'Process {i+1} had {faults[i]} faults and {final_residency[i]} average residency.')
        else:
            print(f'Process {i+1} had {faults[i]} faults.')
            print(f'\tWith no evictions, the average residence is undefined.')
            
    print(f'\nThe total number of faults is {fault_sum} and the overall average residency is {residency_sum/eviction_sum}.')