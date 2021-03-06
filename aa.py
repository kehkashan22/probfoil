from problog.program import PrologString
from problog.program import PrologFile
from problog.core import ProbLog
from problog.engine import DefaultEngine
from problog.logic import Term
from problog import get_evaluatable
from collections import defaultdict
import argparse
import sys

class Predicate:
    def __init__(self, name, arity, groundings, pi_dict, types):
        self.name = name
        self.arity = arity
        self.pi_dict = pi_dict #keys are groundings and values are pi for them
        self.groundings = groundings
        self.types = types
        

class DataFile(object):
    #file where all querying and db extension happens
    def __init__(self, *sources):
        self._database = DefaultEngine().prepare(sources[0])
        # pdb.set_trace()
        for source in sources[1:]:
            for clause in source:
                # pdb.set_trace()
                self._database += clause

    def query(self, predicate_name, arity=None, arguments=None):
        if arguments is None:
            assert arity is not None
            arguments = [None] * arity

        query = Term(predicate_name, *arguments)
        return self._database.engine.query(self._database, query)

    def ground(self, rule, functor=None, arguments=None):
        if rule is None:
            db = self._database
            target = Term(functor)
        else:
            db = self._database.extend()
            target = None
            for clause in rule.to_clauses(functor):
                target = clause.head
                db += clause

        if arguments is not None:
            # pdb.set_trace()
            queries = [target.with_args(*args) for args in arguments]
        else:
            queries = [target]

        return self._database.engine.ground_all(db, queries=queries)

    def evaluate(self, rule, functor=None, arguments=None, ground_program=None):
        if ground_program is None:
            # pdb.set_trace()
            ground_program = self.ground(rule, functor, arguments)

        knowledge = get_evaluatable().create_from(ground_program) #ddnnf object of all groundings
        return knowledge.evaluate() #for each grounding given, finds probability from database and applies it
        #output looks something like this:
        #{flies(1): 1.0, flies(2): 1.0, flies(3): 1.0, flies(4): 1.0, flies(5): 1.0, flies(6): 1.0, flies(7): 1.0, flies(8): 1.0, flies(9): 1.0, flies(10): 0.0}




def main(argv=sys.argv[1:]):
    types = {}    # dict[tuple[str,int],tuple[str]]: signature / argument types
    values = defaultdict(set)   # dict[str, set[Term]]: values in data for given type
    groundings = defaultdict(set)
    modes = []   
    # pdb.set_trace()
    args = argparser().parse_args(argv)
    # yahan load input files and create database
    data = DataFile(*(PrologFile(source) for source in args.files))
    print(data._database)
    for typeinfo in data.query('base', 1):
        typeinfo = typeinfo[0]
        argtypes = list(map(str, typeinfo.args))
        key = (typeinfo.functor, len(argtypes))
        if key in types:
            raise ValueError("A type definition already exists for '%s/%s'."
                             % (typeinfo.functor, len(argtypes)))
        else:
            types[key] = argtypes
    print(types)

    for modeinfo in data.query('mode', 1):
        modeinfo = modeinfo[0]
        modes.append((modeinfo.functor, list(map(str, modeinfo.args))))
    #     print(modes)
    # print(types.items())
    for predicate, type_el in types.items():
        arg_values = zip(*data.query(*predicate))
        for a, t in zip(arg_values, type_el):
            for value in a:
                values[predicate].add(value)
                groundings[t].add(value) 
    # print(values)
    # print(groundings) #predicate name, arity is the key and value: actual groundings
    # grounding is also a dicyionary
    # print(values)
    # print("Types:", types)

    target = data.query('learn', 1)[0]
    target_name, target_arity = target[0].args
    Literals_List = []
    for i in values.keys():
        name = i[0]
        arity = i[1]
        g = tuple(values[i])
        print(g)
        # print(name, arity, g)
        g1 = [r for r in data.query(name, arity)]
        # print(g1)
        temp = Predicate(name, arity, g1, data.evaluate(None, name, g1, None), types[i])
        Literals_List.append(temp)
    prev_list = []
    for i in Literals_List:
        if i.name == target_name:
            prev_list = i.pi_dict.values()

def argparser():
    parser = argparse.ArgumentParser()
    parser.add_argument('files', nargs='+')
    return parser

#anchal code
#target_predicate 
h = [] #list of name and arity, can generalize more later[p1,p2]
H = []
b = []
c = [] #dont think we need this

while True:
  b = []
  ls = localstop(H,b)
  while not ls:
    arg_max = -10000 # change to 0?
    l_2b_added = 0
    for l in literals:
      score = localscore(b,l) #b is a list of element same as l
      if score > arg_max:
        arg_max = score
        l_2b_added = l
    if l == -10000:
      print "*******Error: no literal is being added, local score not working"
    b = b + l
    ls = localstop(H,b)
  #extra pruning neglecting
  if globalscore(H) < globalscore(H + b):
    H = H + b
  if (globalscore(H) > globalscore(H + b)):
    break
return H



def rule_Calc(rule):
    trial_pi_phi= data.evaluate(rule, arguments=groundings)
    t_pos = 0.0 
    f_pos = 0.0  
    t_neg = 0.0
    f_neg = 0.0
    pi_list= prev_list
    phi_list= list(trial_pi_phi.values())
    # need to re-confirm how to do this.is evaluate, ground and values used here
    for pi, phi in zip(pi_list,phi_list): # need to confirm what to put here.wonky answers!
      ni=1- pi
      nhi=1-phi
      t_pos_i= min(pi,phi)
      t_neg_i= min(ni, nhi)
      f_pos_i= max(0, t_neg_i - ni)
      f_neg_i=  max(0,pi- t_pos_i)
      t_pos+=t_pos_i 
      f_pos+= f_pos_i
      f_neg+= f_neg_i
      t_neg+= t_neg_i
    return t_pos, f_pos, t_neg, f_neg

def finding_accuracy(rule):
    t_pos, f_pos, t_neg, f_neg= rule_Calc(rule)
    return (t_pos + t_neg)/ (t_pos + f_pos + t_neg + f_neg)
def finding_recall(rule):
    t_pos, f_pos, t_neg, f_neg = rule_Calc(rule)
    return (t_pos) / (t_pos + f_neg)
def finding_precision(rule):
    t_pos, f_pos, t_neg, f_neg = rule_Calc(rule)
    return (t_pos) / (t_pos + f_pos)
def finding_m_est(rule):
    t_pos, f_pos, t_neg, f_neg = rule_Calc(rule)
    pos= t_pos + f_neg
    neg= t_neg+f_pos
    return (t_pos+(m* pos/(pos+neg)))/ (t_pos+f_pos+m)
  
def local_score(H, c):
    list_h_u_c= H + c
    l_score= finding_m_est(list_h_u_c)- finding_m_est(H)
    return l_score
def local_stop(H,c):
    list_h_u_c= H + c
    t_pos_h_c, f_pos_h_c, t_neg_h_c, f_neg_h_c= rule_Calc(list_h_u_c)
    t_pos_c, f_pos_c, t_neg_c, f_neg_c= rule_Calc(c)
    t_pos_h, f_pos_h, t_neg_h, f_neg_h= rule_Calc(H)
    a= t_pos_h_c- t_pos_h
    b= f_pos_c
    print ("a=", a, "b=",b)
    if(a==0 or b=0):
      return 1
    else
      return 0