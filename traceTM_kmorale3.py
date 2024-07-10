#!/usr/bin/env python3

# Katie Morales
# Theory of Computing Project 3
# team kmorale3

# Tracing TM Behavior 

import sys

class TM: 
    def __init__(self, name, states, chars, tapechars, start, accept, reject, trans ):
        self.name       = name             # the NFA name
        self.states     = states           # set of states of the NFA
        self.chars      = chars            # set of chars
        self.tapechars  = tapechars        # set of tape characters
        self.start      = start            # start state of NFA
        self.accept     = accept           # set of accepting state(s)
        self.reject     = reject           # set of rejecting state(s)
        self.trans      = trans            # dictionary of transitions
        self.inputStr   = ''               # TM input string
        self.tape       = ''               # TM ending state
        self.totalTrans = 0                # total number of transitions taken
        self.depth      = 0                # depth of the transitions taken
        self.configs    = []               # configurations

def read_tm(input_file):
    ''' This function reads in a Turing Machine from an input file, assuming the TM is formatted as follows:

    Line 1: Name of machine
    Line 2: List of state names for Q
    Line 3: List of characters from Σ
    Line 4: List of characters from Γ
    Line 5: The start state
    Line 6: Accept state
    Line 7: Reject state

    Transitions Lines:
        The name of a state that the machine might be in.
        A character from Γ.
        The name of a state that the machine may go into if that character was found next
        The character from Γ that should replace the current tape cell.
        Either a L or a R denoting which direction to move the head next.
    '''

    # read the header
    name      = input_file.readline().rstrip().split(",")[0]
    states    = set(filter(None, input_file.readline().rstrip().split(",")))
    chars     = set(filter(None, input_file.readline().rstrip().split(",")))
    tapechars = set(filter(None, input_file.readline().rstrip().split(",")))
    start     = input_file.readline().rstrip().split(",")[0]
    accept    = set(filter(None, input_file.readline().rstrip().split(",")))
    reject    = set(filter(None, input_file.readline().rstrip().split(",")))

    # read the transitions into a dictionary
    trans = {}
    transition = list(filter(None, input_file.readline().rstrip().split(",")))
    source, tapeR, target, tapeW, direction = transition[0], transition[1], transition[2], transition[3], transition[4]

    while(source and tapeR and target and tapeW and direction):        
        trans[(source, tapeR)] = trans.get((source, tapeR), []) + [(target, tapeW, direction)]
        transition = list(filter(None, input_file.readline().rstrip().split(",")))
        if len(transition) > 2:
            source, tapeR, target, tapeW, direction = transition[0], transition[1], transition[2], transition[3], transition[4]
        else:
            source, tapeR, target, tapeW, direction = None, None, None, None, None

    # return an NFA project with the read in attributes   
    return TM(name, states, chars, tapechars, start, accept, reject, trans)

def trace_tm(myTM, input_str,maxTrans):
    ''' This function takes in a turing machine object, input string, and maximum number of transitions.
        It performs a breadth first search trace of the input string on the turing machine and returns 
        as soon as the string is accepted, the maximum number of transitions have been reached, or all 
        transitions have been taken and the string never reaches an accept state.
    '''
    # used to index the tape / input string
    tapeHead   = 0
    # start state
    start      = myTM.start
    # depth of tree, aka transitions per trace
    depth      = 0
    # total transitions taken over all traces, should not count the start as a transition so initialized to -1
    totalTrans = -1
    # data structure to hold the traces
    frontier   = []
    # array of configurations, unique to each trace
    configurations = []
    # have the current state, the tape (starts as input string), the current tapehead location, and the depth
    frontier.append((start,input_str, tapeHead, depth,configurations))
    while(frontier):
        # bfs FIFO, get the next trace's info
        state, tape, tapeHead, depth, configs = frontier.pop(0)

        # increment transitions
        totalTrans += 1

        # check for maximum transittions
        if totalTrans == maxTrans:
            print(f'The program has halted after reaching the maximum number of transitions: {maxTrans}')
            return

        # means that the machine has an invalid transition
        if tapeHead < 0 or tapeHead > len(tape):
            print("ERROR: INCORRECT TRANSITION IN MACHINE")
            break

        # not a valid transiton -> halt this particular trace
        if (state, tape[tapeHead]) not in myTM.trans.keys():
            continue

        # construct configuration string
        if tapeHead == 0:
            currConfig = state + " " + tape
        else:
            currConfig = tape[:tapeHead] + " " + state + " " + tape[tapeHead:]

        # gt transitions based on current state and input 
        for nextState, newChar, direction in myTM.trans[(state, tape[tapeHead])]:
            # update tape
            newTape = tape[: tapeHead] + str(newChar) + tape[(tapeHead + 1):]
            # move tape head
            if direction == "L":
                newTapeHead = tapeHead - 1
            else:
                newTapeHead = tapeHead + 1
            # check if nextState is an accepted state
            if nextState in myTM.accept:
                # add the crrent and final configurations to the trace's list of configurations
                configs.append(currConfig)
                if tapeHead == 0:
                    finalConfig = state + tape
                else:
                    finalConfig = tape[:newTapeHead] + " " +nextState + " " + tape[newTapeHead:]
                configs.append(finalConfig) 
                # update turing machine object
                myTM.configs    = configs
                myTM.totalTrans = totalTrans + 1
                myTM.depth      = depth + 1
                myTM.tape = tape[: tapeHead] + str(newChar) + tape[(tapeHead + 1):]
                #print results
                print(f'Depth of Configuration Tree: {myTM.depth}')
                print(f'Total Transitions Taken:     {myTM.totalTrans}')
                print(f'String accepted in {myTM.depth} steps:')
                for c in myTM.configs:
                    print(c)
                return
            # add transition to frontierto be traced, each transition gets its own configs copy 
            frontier.append((nextState, newTape, newTapeHead, depth +1, configs + [currConfig]))
    
    # if the while loop exits and the main body of the function is reached, then the string is not accepted
    # print results for no accepted path
    print(f'Depth of Configuration Tree: {depth}')
    print(f'Total Transitions Taken:     {totalTrans}')
    print(f'String rejected in {totalTrans} steps')

    return

def main():
    command = ' '.join(sys.argv)
    print(command)
    file_name  = sys.argv[1]
    # assume empty string if input not provided
    if len(sys.argv) < 3:
        input_str = ""
        maxTrans = sys.maxsize
    # check for max configs flag
    elif len(sys.argv) >= 5:
        # get the input string from command line 
        input_str  = str(sys.argv[2]) + ""
        # max transitions flag
        if sys.argv[3] == "-T":
            # get the max transitions if an integer was entered, otherwise ignore
            try:
                maxTrans = int(sys.argv[4])
            except:
                maxTrans = sys.maxsize    
        else:
            maxTrans = sys.maxsize    
    else:
        input_str  = str(sys.argv[2]) + ""
        maxTrans = sys.maxsize

    input_file = open(file_name, "r") 

    # build the NFA
    myTM = read_tm(input_file)
    myTM.inputStr = input_str + "_"

    print(f'Name:                        {myTM.name}')
    print(f'Input String:               \'{myTM.inputStr}\'')
    if maxTrans != sys.maxsize:
        print(f'Max Transitions:             {maxTrans}')

    trace_tm(myTM, input_str + "_", maxTrans)
    print("\n##############################################\n")

    '''
    print(f'Name: {myTM.name}')
    print(f'States: {myTM.states}')
    print(f'Sigma: {myTM.chars}')
    print(f'TapeChars: {myTM.tapechars}')
    print(f'Start: {myTM.start}')
    print(f'Accept: {myTM.accept}')
    print(f'Reject: {myTM.reject}')
    print('Transitions: ')
    for source, result in myTM.trans.items():
        print(f'{source} {result}')
    '''



if __name__ == '__main__':
    main()