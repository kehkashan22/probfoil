import pdb
m=1
def rule_Calc(rule):
    t_pos = 0.0
    f_pos = 0.0
    t_neg = 0.0
    f_neg = 0.0
    pi_list = rule[0]
    phi_list = rule[1]
    for pi, phi in zip(pi_list,phi_list):
      ni=1- pi
      nhi=1-phi
      t_pos_i= min(pi,phi)
      t_neg_i= min(ni, nhi)
      f_pos_i= max(0,ni - t_neg_i)
      f_neg_i=  max(0,pi- t_pos_i)
      t_pos+=t_pos_i 
      f_pos+= f_pos_i
      f_neg+= f_neg_i
      t_neg+= t_neg_i
    # print t_pos, f_pos, t_neg, f_neg
    return t_pos, f_pos, t_neg, f_neg

def global_score(rule):#accuracy
    t_pos, f_pos, t_neg, f_neg= rule_Calc(rule)
    if(t_pos + f_pos + t_neg + f_neg ==0):
        return 0
    return (t_pos + t_neg)/ (t_pos + f_pos + t_neg + f_neg)
def finding_recall(rule):
    t_pos, f_pos, t_neg, f_neg = rule_Calc(rule)
    if(t_pos + f_neg ==0):
        return 0
    return (t_pos) / (t_pos + f_neg)
def finding_precision(rule):
    t_pos, f_pos, t_neg, f_neg = rule_Calc(rule)
    if(t_pos + f_pos ==0):
        return 0
    return (t_pos) / (t_pos + f_pos)
def finding_m_est(rule):
    if len(rule[0]) == 0:
      return 0
    t_pos, f_pos, t_neg, f_neg = rule_Calc(rule)
    pos= t_pos + f_neg
    neg= t_neg+f_pos
    return (t_pos+(m* pos/(neg)))/ (t_pos+f_pos)
  
def local_score(list_h_u_c, H):
    l_score= finding_m_est(list_h_u_c)- finding_m_est(H)
    return l_score
def local_stop(list_h_u_c,c,H):
    if len(H[0]) == 0 and len(c[0]) == 0:
      return 0
    t_pos_h_c, f_pos_h_c, t_neg_h_c, f_neg_h_c= rule_Calc(list_h_u_c)
    t_pos_c, f_pos_c, t_neg_c, f_neg_c= rule_Calc(c)
    t_pos_h, f_pos_h, t_neg_h, f_neg_h= rule_Calc(H)
    a= t_pos_h_c- t_pos_h
    b= f_pos_c
    if(a==0 or b==0):
      return 1
    else:
      return 0

def phi_rule(predicate_list):
  if len(predicate_list) == 0:
    return [[],[]]
  final_list = []
  for i in range(3):#since 3 groundigns
    temp =1
    for p in predicate_list:
      temp = temp*(pi_dict[p][i])
    final_list.append(temp)
  # print final_list
  return [target_pi,final_list]

pi_dict = {"exam":[0.8,0.7,0.1],
"submission":[0.3,0.9,0.8],
"movie":[0.2,0.3,0.9]}
target_predicate = "stress"
target_pi = [0.7,0.8,0.4]
literals = ["exam","submission","movie"]

# print finding_precision([[0.7,0.8,0.4],[0.24,0.63,0.08]])
# print rule_Calc([[0.7,0.8,0.4],[0.24,0.63,0.08]])
# print global_score([[0.7,0.8,0.4],[0.24,0.63,0.08]])
# phi_rule(["exam","submission"])
# finding_m_est([[0.7,0.8,0.4],phi_rule(["exam","movie"])])
# print global_score([[0.7,0.8,0.4],phi_rule(["exam","movie"])])


#anchal code
#target_predicate 
h = [] #list of name and arity, can generalize more later[p1,p2]
H = []
b = []
c = []

while True:
  b = []
  b_phi = phi_rule(b)
  H_phi = phi_rule(H) 
  b_H_phi = phi_rule(b+H)
  ls = local_stop(b_H_phi,b_phi,H_phi)
  while not ls:
    arg_max = -10000 #a small random number
    l_2b_added = 0
    new_list = []
    for l in literals:
      if l not in b:
        new_list.append(l)
    for l in new_list:
      #for local_score
      b_phi = phi_rule(b)
      b_l_phi = phi_rule(b+[l])
      score = local_score(b_l_phi,b_phi) #b is a list of element same as l
      if score > arg_max:
        arg_max = score
        l_2b_added = l
    if l == -10000:
      print "*******Error: no literal is being added, local score not working"
    b = b + [l_2b_added]
    b_phi = phi_rule(b)
    H_phi = phi_rule(H) 
    b_H_phi = phi_rule(b+H)
    # pdb.set_trace()
    ls = local_stop(b_H_phi,b_phi,H_phi)
  #extra pruning neglecting
  H_phi = phi_rule(H) 
  b_H_phi = phi_rule(b+H)
  if len(b) != 0:
    print b,"body of new rule learnt"
  if global_score(H_phi) < global_score(b_H_phi):
    H = H + b
  else:# global_score(H_phi) >= global_score(b_H_phi):
    break