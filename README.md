## Description
In this lab you will simulate demand paging and see howthe number of page faults depends on page size, program size, replacement algorithm, and job mix (job mix is deﬁned belowand includes locality and multiprogramming level).

The idea is to have a driver generate memory references and then have a demand paging simulator (called pager below) decide if each reference causes a page fault. Assume all memory references are for entities of one ﬁxed size, i.e., model a word oriented machine, containing M words. Although in a real OS memory is needed for page tables, OS code, etc., you should assume all M words are available for page frames.

The program is invokedwith 6 command line arguments, 5 positive integers and one string:
* M, the machine size in words. 
* P, the page size in words. 
* S, the size of each process, i.e., the references are to virtual addresses 0..S-1. 
* J, the ‘‘job mix’’, which determines A, B, and C, as described below. 
* N, the number of references for each process. 
* R, the replacement algorithm, LIFO (NOT FIFO), RANDOM, or LRU.

The driverreads all input, simulates N memory references per program, and produces all output. The driveruses round robin scheduling with quantum q=3 (i.e., 3 references for process 1, then 3 for process 2, etc.).

The drivermodels locality by ensuring that a fraction A of the references are to the address one higher than the current (representing a sequential memory reference), a fraction B are to a nearby lower address (representing a backward branch), a fraction C are to a nearby higher address (representing a jump around a ‘‘then’’ or ‘‘else’’block), and the remaining fraction (1-A-B-C) are to random addresses. Speciﬁcally, if the current word referenced by a process is w,then the next reference by this process is to the word with address:
* w+1 mod S with probability A 
* w-5 mod S with probability B 
* w+4 mod S with probability C 
* a random value in 0..S-1 each with probability (1-A-B-C)/S

Since there are S possible references in case 4 each with probability (1-A-B-C)/S, the total probability of case 4 is 1-A-B-C, and the total probability for all four cases is A+B+C+(1-A-B-C)=1 as required.

There are four possible sets of processes (i.e., values for J):
```
J=1: One process with A=1 and B=C=0, the simplest (fully sequential) case.
J=2: Four processes, each with A=1 and B=C=0.
J=3: Four processes, each with A=B=C=0 (fully random references).
J=4: One process with A=.75, B=.25 and C=0; one process with A=.75, B=0, and C=.25; one process with A=.75, B=.125 and C=.125; and one process with A=.5, B=.125 and C=.125.
```

The pager routine processes each reference and determines if a fault occurs, in which case it makes this page resident. If there are no free frames for this faulting page, a resident page is evicted using replacement algorithm R. The algorithms are global (i.e., the victim can be anyframe not just ones used by the faulting process). Because the lab only simulates demand paging and does not simulate the running of actual processs, I believe you will ﬁnd it easiest to just implement a frame table (see next paragraph) and not page tables.

As we know, each process has an associated page table, which contains in its ith entry the number of the frame containing this process’s ith page (or an indication that the page is not resident). The frame table (there is only one for the entire system) contains the reverse mapping: The ith entry in the frame table speciﬁes the page contained in the ith frame (or an indication that the frame is empty). Speciﬁcally the ith entry contains the pair (P, p) if page p of process P is contained in frame i.

The system begins with all frames empty,i.e. no pages loaded. So the ﬁrst reference for each process will deﬁnitely be a page fault. If arun has D processes (J=1 has D=1, the others have D=4), then process k (1<=k<=D) begins by referencing word 111*k mod S.

Your program echos the input values read and produces the following output. Foreach process, print the number of page faults and the average residencytime. The latter is deﬁned as the time (measured in memory references) that the page was evicted minus the time it was loaded. So at eviction calculate the current page’sresidencytime and add it to a running sum. (Pages neverevicted do not contribute to this sum.) The average is this sum divided by the number of evictions.Finally,print the total number of faults and the overall average residencytime (the total of the running sums divided by the total number of evictions).
