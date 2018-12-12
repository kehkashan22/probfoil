from problog.program import PrologString
from problog.program import PrologFile
from problog.core import ProbLog
from problog.engine import DefaultEngine
from problog.logic import Term
from problog import get_evaluatable
from collections import defaultdict
import time
import argparse
import sys
import random

class Predicate:
    def __init__(self, name, arity, groundings, types, pi_list):
        self.name = name
        self.arity = arity
        self.groundings = groundings
        self.types = types
        self.pi = pi_list

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
        print(key)
        print("Types:", types)

    for modeinfo in data.query('mode', 1):
        modeinfo = modeinfo[0]
        modes.append((modeinfo.functor, list(map(str, modeinfo.args))))
        print(modes)
    print(types.items())
    for predicate, types in types.items():
        arg_values = zip(*data.query(*predicate))
        for a, t in zip(arg_values, types):
            for value in a:
                values[predicate].add(value)
                groundings[t].add(value)
    print(values)
    print(groundings)

    
    

def argparser():
    parser = argparse.ArgumentParser()
    parser.add_argument('files', nargs='+')
    return parser

if __name__ == '__main__':
    main()
