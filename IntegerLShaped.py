
from gurobipy import *
from oa_data import *
from bendersDecomposition import *

import random

def getSecondStageCost(x,k:int,data:OA_data):

    N = range(data.nb_oders)
    model = Model("GUROBI")
    model.Params.LogToConsole = 0

    # Variables
    y = [model.addVar(vtype=GRB.BINARY,name=f'y{i}') for i in N]
    z = [model.addVar(vtype=GRB.BINARY,name=f'z{i}') for i in N]
  
    # Objective 
    model.setObjective(sum(data.outsourcing_costs[i]*z[i] for i in N), GRB.MINIMIZE)

    # Constraints
    model.addConstr(sum(data.scenarios[i][k]*y[i] for i in N) <= data.capacity,'capacity')

    for i in N:
        model.addConstr(z[i]+y[i] == x[i],'equality')

    status=model.optimize()

    if status == GRB.Status.OPTIMAL:
        return model.ObjVal,model.Runtime


# Question 8
def LShape(data:OA_data,k:int,theta_k:float,masterProblem:Model,x):

    N = range(data.nb_oders)

    # get second stage cost
    Q,run_time_second_stage = getSecondStageCost(x,k,data)


    # compute delta
    delta = sum(masterProblem.getVarByName(f'x{i}') for i in N if x[i] > 0.9) - sum(masterProblem.getVarByName(f'x{i}') for i in N if x[i] < 0.1)

    # test integer L-Shaped cut
    if theta_k + 1e-5 <= Q:

        expr = Q*delta-Q*(sum(x)-1)
        
        masterProblem.addConstr(masterProblem.getVarByName(f'theta{k}') >= expr)

        return [True,masterProblem,run_time_second_stage]
    else:
        return [False,masterProblem,run_time_second_stage]



def mainIntegerLShaped(data:OA_data):

    Integrality = 1
    run_time = 0
     
    # init master problem
    masterProblem = Master(Integrality,data)
    masterProblem.optimize()

    # get value of (x theta)
    xVal = [masterProblem.getVarByName(f'x{i}').x for i in range(data.nb_oders)]
    thetaVal = [masterProblem.getVarByName(f'theta{k}').x for k in range(data.nb_scenarios)] 

    print(f' x est {xVal} et theta est {thetaVal}*******************************************************')

    criterion = 1
    while criterion != 0:

        criterion = 0

        # for each scenarion getSecondStageCost
        for k in range(data.nb_scenarios):

            bool,masterProblem,run_time_lsh = LShape(data,k,thetaVal[k],masterProblem,xVal)
            run_time += run_time_lsh

            if bool == True:
                criterion += 1

        masterProblem.optimize()
        run_time += masterProblem.Runtime

        xVal = [masterProblem.getVarByName(f'x{i}').x for i in range(data.nb_oders)]
        thetaVal = [masterProblem.getVarByName(f'theta{k}').x for k in range(data.nb_scenarios)] 
        print(f' x est {xVal} et theta est {thetaVal}*******************************************************')

    return masterProblem.ObjVal,xVal,thetaVal,run_time

def main_experiments():
    for r in [50, 100]:
        for b in [10, 100]:
            for s in [10, 50, 500]:
                for l in [0.7, 0.9]:
                    I=""
                    for i in range(5):


                        # Import instance
                        data = OA_data.read_from_file(f'iterative_ILShaped/OA_O5_S{s}_L{l}_B{b}_R{r}_{i}.txt')  

                        # Solve using different methods
                        obj,run_time = mainIntegerLShaped(data)
                        
                        I = I + f'& {obj:2f} & {run_time}\\\\ \n'
                    
                    # Write results to file
                    with open(f'solutions_O5/OA_O5_S{s}_L{l}_B{b}_R{r}_table.txt', 'a') as file:
                        file.write(I)



#main_experiments()

