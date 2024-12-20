from gurobipy import *
from oa_data import *
from bendersDecomposition import *
from accélaration import *
from IntegerLShaped import *
import time

class cutGeneration:
    def __init__(self,data:OA_data,model:Model):
        self.data=data
        self.model=model

    def __call__(self,model,where):

        if where ==GRB.Callback.MIPSOL:
            N = range(self.data.nb_oders)
            K = range(self.data.nb_scenarios)

            # get variables' value
            xSP = [model.cbGetSolution(model.getVarByName(f'x{i}')) for i in N] 
            thetaSP = [model.cbGetSolution(model.getVarByName(f'theta{k}')) for k in K]   

            for k in K:

                # solve the second stage problem for a fixed first stage decision and for a scenario k
                Q = self.getSecondStageCost_C(xSP,k,self.data)

                # test integer L-Shaped cut
                if thetaSP[k]+1e-5 < Q:
                     # compute delta                
                    delta = sum(model.getVarByName(f'x{i}') for i in N if xSP[i] > 0.9)-sum(model.getVarByName(f'x{i}') for i in N if xSP[i] < 0.1)

                    # Optimality cuts right hand value
                    expr = Q*delta-Q*(sum(xSP)-1)

                    # Add the ptimality cut
                    model.cbLazy(model.getVarByName(f'theta{k}') >= expr)
                    
    @classmethod
    def getSecondStageCost_C(cls,x,k:int,data:OA_data):

        N = range(data.nb_oders)
        model = Model("GUROBI")

        y = [model.addVar(vtype=GRB.BINARY, name=f"y{i}") for i in N] 
        z = [model.addVar(vtype=GRB.BINARY, name=f"z{i}") for i in N] 

        model.setObjective(sum(data.outsourcing_costs[i] * z[i] for i in N),GRB.MINIMIZE) 

        # Constraintes
        model.addConstr(sum(data.scenarios[i][k] * y[i] for i in N) <= data.capacity)
        
        for i in N:
            model.addConstr(z[i] + y[i] == x[i])

        model.optimize()

        return model.objVal

def Integer_LShaped(data:OA_data,modelMaster):   

    # change variable x into binary indeed, x is continuous in master problem
    for i in range(data.nb_oders):
        var = modelMaster.getVarByName(f'x{i}')
        var.VType = GRB.BINARY
    modelMaster.update() 

    start_time = time.time()

    callback = cutGeneration(data, modelMaster)  
    modelMaster.optimize(callback)

    end_time = time.time()

    if modelMaster.status == GRB.OPTIMAL:
        xVal = [modelMaster.getVarByName(f'x{i}').x for i in range(data.nb_oders)]
        thetaVal = [modelMaster.getVarByName(f'theta{k}').x for k in range(data.nb_scenarios)]
        run_time = end_time-start_time

    return modelMaster.objVal,xVal,thetaVal,run_time


# Question 18
def main_Interger_LShaped_with_callaback(data:OA_data,type_initial_cuts:int):
    """
        type_initial_cuts indicate the type of initial cuts we use. There are two types, the one of question 18 and the one of question 19
        if type_inital_cuts==1, use initial cuts of question 18
        else use the ones of question 19
    """

    run_time = 0
    # init master problem, with continuous x value. Integrality equal zero means that x is continous in interval [0,1]
    masterProblem = Master(Integrality=0,data=data) 
    masterProblem.optimize()
    run_time+=masterProblem.Runtime

    # generate initial cuts        
    if type_initial_cuts == 1:
        # intialicuts are the cuts from the LP relaxtion's master problem
        initialCuts,run_time_cut_determination = benders(1,data,masterProblem)
    else:
        # inout cuts from Fischetti et al.
        initialCuts,run_time_cut_determination = acceleration(data,masterProblem)

    run_time += run_time_cut_determination

    # add intial cuts to the master problem and solve it
    masterProblem,listConstr = benders_addRelaxationCuts(masterProblem,initialCuts,data)
    masterProblem.optimize()
    run_time += masterProblem.Runtime

    # remove non active initial cuts
    listNonActif = []
    for constr in masterProblem.getConstrs():
        if constr.slack > 0 and constr in listConstr:
            masterProblem = remove_non_active_cuts(masterProblem,constr)
            listNonActif.append(constr)

    # solve the problem, with initial x value
    obj,x,theta,run_time_LShaped = Integer_LShaped(data,masterProblem)

    run_time += run_time_LShaped
    return obj,x,theta,run_time



# Question 19 is in accélaration.py
