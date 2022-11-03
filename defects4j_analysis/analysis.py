#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep  1 14:29:58 2022

@author: michael
"""
import json

with open("defects4j-bugs.json") as f:
    db = json.loads("".join(f.readlines()))

db.sort(key=lambda bug: (bug['program'], bug['bugId']))

categories = {
        'mdAdd': {'description': "Method definition addition", 'causal': 'sometimes'},
        'mdRem': {'description': "Method definition removal", 'causal': 'sometimes'},
        'mdRen': {'description': "Method definition renaming", 'causal': 'never'},
        'mdParAdd': {'description': "Parameter addition in method definition", 'causal': 'structural'},
        'mdParRem': {'description': "Parameter removal from method definition", 'causal': 'structural'},
        'mdRetTyChange': {'description': "Method return type modification", 'causal': 'never'},
        'mdParTyChange': {'description': "Parameter type modification in method definition", 'causal': 'never'},
        'mdModChange': {'description': "Method modifier change", 'causal': 'never'},
        'mdOverride': {'description': "Method overriding addition or removal", 'causal': 'sometimes'},
        'mcAdd': {'description': "Method call addition", 'causal': 'sometimes'},
        'mcRem': {'description': "Method call removal", 'causal': 'sometimes'},
        'mcRepl': {'description': "Method call replacement", 'causal': 'sometimes'},
        'mcParSwap': {'description': "Method call parameter value swapping", 'causal': 'never'},
        'mcParAdd': {'description': "Method call parameter addition", 'causal': 'structural'},
        'mcParRem': {'description': "Method call parameter removal", 'causal': 'structural'},
        'mcParValChange': {'description': "Method call parameter value modification", 'causal': 'never'},
        'mcMove': {'description': "Method call moving", 'causal': 'never'},
        'objInstAdd': {'description': "Object instantiation addition", 'causal': 'structural'},
        'objInstRem': {'description': "Object instantiation removal", 'causal': 'structural'},
        'objInstMod': {'description': "Object instantiation modification", 'causal': 'sometimes'},
        'varAdd': {'description': "Variable addition", 'causal': 'structural'},
        'varRem': {'description': "Variable removal", 'causal': 'structural'},
        'varReplVar': {'description': "Variable replacement by another variable", 'causal': 'structural'},
        'exTryCatchAdd': {'description': "try-catch addition", 'causal': 'sometimes'},
        'exTryCatchRem': {'description': "try-catch removal", 'causal': 'sometimes'},
        'exThrowsAdd': {'description': "throw addition", 'causal': 'never'},
        'exThrowsRem': {'description': "throw removal", 'causal': 'never'},
        'condExpRed': {'description': "Conditional expression reduction", 'causal': 'sometimes'},
        'condExpExpand': {'description': "Conditional expression expansion", 'causal': 'sometimes'},
        'condExpMod': {'description': "Conditional expression modification", 'causal': 'functional'},
        'condBranIfAdd': {'description': "Conditional (if) branch addition", 'causal': 'sometimes'},
        'condBranIfElseAdd': {'description': "Conditional (if-else) branches addition", 'causal': 'sometimes'},
        'condBranElseAdd': {'description': "Conditional (else) branch addition", 'causal': 'sometimes'},
        'condBranCaseAdd': {'description': "Conditional (case in switch) branch addition", 'causal': 'sometimes'},
        'condBranRem': {'description': "Conditional (if or else) branch removal", 'causal': 'sometimes'},
        'assignAdd': {'description': "Assignment addition", 'causal': 'structural'},
        'assignRem': {'description': "Assignment removal", 'causal': 'structural'},
        'assignExpChange': {'description': "Assignment expression modification", 'causal': 'sometimes'},
        'loopAdd': {'description': "Loop addition", 'causal': 'sometimes'},
        'loopRem': {'description': "Loop removal", 'causal': 'sometimes'},
        'loopCondChange': {'description': "Loop conditional expression modification", 'causal': 'sometimes'},
        'loopInitChange': {'description': "Loop initialization field modification", 'causal': 'sometimes'},
        'varTyChange': {'description': "Variable type change", 'causal': 'never'},
        'varModChange': {'description': "Variable modifier change", 'causal': 'never'},
        'varReplMc': {'description': "Variable replacement by method call", 'causal': 'sometimes'},
        'tyAdd': {'description': "Type addition", 'causal': 'never'},
        'tyImpInterf': {'description': "Type implemented interface modification", 'causal': 'sometimes'},
        'retExpChange': {'description': "Return expression modification", 'causal': 'sometimes'},
        'retBranchAdd': {'description': "Return statement addition", 'causal': 'sometimes'},
        'retRem': {'description': "Return statement removal", 'causal': 'sometimes'},
        'wrapsIf': {'description': "Wraps-with if statement", 'causal': 'useless'},
        'wrapsIfElse': {'description': "Wraps-with if-else statement", 'causal': 'useless'},
        'wrapsElse': {'description': "Wraps-with else statement", 'causal': 'useless'},
        'wrapsTryCatch': {'description': "Wraps-with try-catch block", 'causal': 'useless'},
        'wrapsMethod': {'description': "Wraps-with method call", 'causal': 'useless'},
        'wrapsLoop': {'description': "Wraps-with loop", 'causal': 'sometimes'},
        'unwrapIfElse': {'description': "Unwraps-from if-else statement", 'causal': 'useless'},
        'unwrapMethod': {'description': "Unwraps-from method call", 'causal': 'useless'},
        'unwrapTryCatch': {'description': "Unwraps-from try-catch block", 'causal': 'useless'},
        'condBlockExcAdd': {'description': "Conditional block addition with exception throwing", 'causal': 'sometimes'},
        'condBlockRetAdd': {'description': "Conditional block addition with return statement", 'causal': 'sometimes'},
        'condBlockOthersAdd': {'description': "Conditional block addition", 'causal': 'sometimes'},
        'condBlockRem': {'description': "Conditional block removal", 'causal': 'sometimes'},
        'missNullCheckP': {'description': "Missing null check addition", 'causal': 'never'},
        'missNullCheckN': {'description': "Missing non-null check addition", 'causal': 'never'},
        'expLogicExpand': {'description': "Logic expression expansion", 'causal': 'sometimes'},
        'expLogicReduce': {'description': "Logic expression reduction", 'causal': 'sometimes'},
        'expLogicMod': {'description': "Logic expression modification", 'causal': 'never'},
        'expArithMod': {'description': "Arithmetic expression modification", 'causal': 'functional'},
        'codeMove': {'description': "Code Moving", 'causal': 'never'},
        'wrongVarRef': {'description': "Wrong Variable Reference", 'causal': 'structural'},
        'wrongMethodRef': {'description': "Wrong Method Reference", 'causal': 'sometimes'},
        'singleLine': {'description': "Single Line", 'causal': 'useless'},
        'notClassified': {'description': "Not classified", 'causal': 'sometimes'},
        'copyPaste': {'description': "Copy/Paste", 'causal': 'useless'},
        'constChange': {'description': "Constant Change", 'causal': 'functional'},
        # Undefined categories
        'wrongComp': {'description': "Wrong computation?", 'causal': 'sometimes'},
        'missComp': {'description': "Missing computation?", 'causal': 'sometimes'},
        'initFix': {'description': "Init fix?", 'causal': 'sometimes'},
        'blockRemove': {'description': "Block removal?", 'causal': 'sometimes'},
        'fixAPI': {'description': "Fix API?", 'causal': 'sometimes'},
    }

structural_causal_categories = [category for category in categories if categories[category]['causal'] == 'structural']
functional_causal_categories = [category for category in categories if categories[category]['causal'] == 'functional']
non_causal_categories = [category for category in categories if categories[category]['causal'] == 'never']
useless_categories = [category for category in categories if categories[category]['causal'] == 'useless']

repair_actions = set()
repair_patterns = set()

structural_causal_bugs = []
functional_causal_bugs = []
non_causal_bugs = []
unknown = []

for bug in db:
    known = False
    repair_actions = repair_actions.union(bug['repairActions'])
    repair_patterns = repair_patterns.union(bug['repairPatterns'])
    bug_categories = set(bug['repairActions']).union(bug['repairPatterns']).difference(useless_categories)
    if len(bug_categories.intersection(structural_causal_categories)) > 0:
        structural_causal_bugs.append(bug)
        known = True
    if len(bug_categories.intersection(functional_causal_categories)) > 0:
        functional_causal_bugs.append(bug)
        known = True
    if all([categories[category]['causal'] == 'never' for category in bug_categories]):
        non_causal_bugs.append(bug)
        known = True
    if not known:
        unknown.append(bug)
        print(bug['program'], bug['bugId'], bug_categories)

# assert (
#     structural_causal_bugs + functional_causal_bugs + non_causal_bugs + unknown
# ) == len(db)

print(f"\n{len(db)} bugs in total")
print(f"structural causal bugs: {len(structural_causal_bugs)} functional causal bugs: {len(functional_causal_bugs)}")
print(f"structural and causal bugs: {len([x for x in structural_causal_bugs if x in functional_causal_bugs])}")
print(f"non-causal bugs: {len(non_causal_bugs)} unknown: {len(unknown)}")
print(f"{len(repair_actions)} repair actions")
print(f"{len(repair_patterns)} repair patterns")
