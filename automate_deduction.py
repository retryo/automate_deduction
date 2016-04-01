#!/usr/bin/env python
import sys
import copy
#import time
#start_time=time.time()
#buggy program
def remove_html_markup(s):
    tag   = False
    quote = False
    out   = ""

    for c in s:

        if c == '<' and not quote:
            tag = True
        elif c == '>' and not quote:
            tag = False
        elif c == '"' or c == "'" and tag:
            quote = not quote
        elif not tag:
            out = out + c

    return out

# ddmin is a delta debug function which searches for minimal
# sets of inputs that causes failures on the provided 
# functions every permutatuins of the inputs 

def ddmin(s):
    """Search 
    """
    if test(s)=="PASS":
        return None

    n = 2     # Initial granularity
    while len(s) >= 2:
        start = 0
        subset_length = len(s) / n
        some_complement_is_failing = False

        while start < len(s):
            complement = s[:start] + s[start + subset_length:]

            if test(complement) == "FAIL":
                s = complement
                n = max(n - 1, 2)
                some_complement_is_failing = True
                break
                
            start += subset_length

        if not some_complement_is_failing:
            if n == len(s):
                break
            n = min(n * 2, len(s))
    return s


# Use this function to record the covered lines in the 
# program, in order of their execution and save in the 
# list coverage
coverage =[]
def traceit(frame, event, arg):
    global coverage
    if event =='line':
        coverage.append(frame.f_lineno)
        
    return traceit

# We use these variables to communicate between callbacks
# and drivers
the_line      = None
the_iteration = None
the_state     = None
the_diff      = None
the_input     = None

# Stop at THE_LINE/THE_ITERATION and store the state in THE_STATE
def trace_fetch_state(frame, event, arg):
    global the_line
    global the_iteration
    global the_state

    if frame.f_lineno == the_line:
        the_iteration = the_iteration - 1
        if the_iteration == 0:
            the_state = copy.deepcopy(frame.f_locals)
            if the_state==None:# Avoids returning empty list
                the_state ={}
            the_line = None  # Don't get called again
            return None

    return trace_fetch_state

# Get the state at LINE/ITERATION
def get_state(input, line, iteration):
    global the_line
    global the_iteration
    global the_state
    
    the_line      = line
    the_iteration = iteration
    sys.settrace(trace_fetch_state)
    y = remove_html_markup(input)
    sys.settrace(None)
    
    return the_state

# Stop at THE_LINE/THE_ITERATION and apply the differences in THE_DIFF 
def trace_apply_diff(frame, event, arg):
    global the_line
    global the_diff
    global the_iteration

    if frame.f_lineno == the_line:
        the_iteration = the_iteration - 1
        if the_iteration == 0:
            frame.f_locals.update(the_diff)
            the_line = None
            return None  # Don't get called again
    
    return trace_apply_diff
    
# Testing function: Call remove_html_output, stop at THE_LINE/THE_ITERATION, 
# and apply the diffs in DIFFS at THE_LINE
def test(diffs):
    global the_diff
    global the_input
    global the_line
    global the_iteration

    line      = the_line
    iteration = the_iteration
    
    the_diff = diffs
    sys.settrace(trace_apply_diff)
    y = remove_html_markup(the_input)
    sys.settrace(None)

    the_line      = line
    the_iteration = iteration

    if y.find('<') == -1:
        return "PASS"
    else:
        return "FAIL"

def make_locations(coverage):
    # This function returns a list of tuples in the format
    # [(line, iteration), (line, iteration) ...], for 
    # auto_cause_chain function's input
    locations=[]
    iter_num={}
    for ln in coverage:
        if ln not in iter_num:
            iter_num[ln]=1
        else:
            iter_num[ln]+=1
        locations.append((ln,iter_num[ln]))

    return locations

def auto_cause_chain(locations):
    global html_fail, html_pass, the_input, the_line,\
            the_iteration, the_diff
    print "The program was started with", repr(html_fail)
    # Test over multiple locations
    causes =[]
    diff_check={}
    line_check={}
    for (line, iteration) in locations:
        if line in line_check:
            continue

        # Get the passing and the failing state
        state_pass = get_state(html_pass, line, iteration)
        state_fail = get_state(html_fail, line, iteration)
    
        # Compute the differences
        diffs = []

        for var in state_fail:
            if (var not in state_pass) or\
             state_pass[var] != state_fail[var]:
                diffs.append((var, state_fail[var]))

        the_input = html_pass
        the_line  = line
        the_iteration  = iteration

        if tuple(diffs) in diff_check:
            continue
        cause = ddmin(diffs)
        if cause!=None:
            line_check[line]=True 
            diff_check[tuple(diffs)]=True
            for c in cause:
                if c not in causes:
                    causes.append(c)

    for var,val in causes:
        print "Then", var, "became", repr(val)
    print "Then the program failed."

###### Testing runs
# We will test your function with different strings and on a different function      
html_fail = '"<b>foo</b>"'
html_pass = "'<b>foo</b>'"
coverage = []
def main():
    global coverage
    # This will fill the coverage variable with all lines executed in a
    # failing run
    sys.settrace(traceit)
    remove_html_markup(html_fail)
    sys.settrace(None)
    locations = make_locations(coverage)
    auto_cause_chain(locations)

if __name__=='__main__':
    main()
"""
The program was started with '"<b>foo</b>"'
Then s became '"<b>foo</b>"'
Then c became '"'
Then quote became True
...
"""
