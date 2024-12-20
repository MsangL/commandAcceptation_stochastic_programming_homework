
#from mip import *
from oa_data import *
from  gurobipy import *

# question 7
def Master(Integrality:int,data:OA_data):

    # This function initialize the master problem and its relaxation if Integrality equals 0
    K=range(data.nb_scenarios)
    N=range(data.nb_oders)

    modelMaster=Model("GUROBI")
    modelMaster.setParam('LazyConstraints', 1)
    modelMaster.Params.LogToConsole = 0

    # variables
    if Integrality == 1:
        x = [modelMaster.addVar(vtype=GRB.BINARY,name=f"x{i}") for i in N]
    else:
        x = [modelMaster.addVar(vtype=GRB.CONTINUOUS,lb=0,ub=1,name=f"x{i}") for i in N]

    theta = [modelMaster.addVar(vtype=GRB.CONTINUOUS,ub=1e10,name=f"theta{k}") for k in K]

    # Objective function
    modelMaster.setObjective(-sum(data.benefits[i]*x[i] for i in N)+(1/data.nb_scenarios)*sum(theta[k] for k in K),GRB.MINIMIZE)

    return modelMaster

# Questions 11 --12
def Direct_R1(data:OA_data,integrality:int):
    # This function solves the CONTINUOUS relaxation of the problem 
    N = range(data.nb_oders)
    K = range(data.nb_scenarios)

    model = Model("GUBOBI")
    model.Params.LogToConsole = 0
    model.setParam('TimeLimit', 3600)


    # variables
    if integrality==1:
        x = [model.addVar(vtype=GRB.BINARY,  name=f"x{i}") for i in N]
        y = [[model.addVar(vtype=GRB.BINARY, name=f"y{i},{k}") for i in N] for k in K]
        z = [[model.addVar(vtype=GRB.BINARY, name=f"z{i},{k}") for i in N] for k in K]
    else:
        x = [model.addVar(vtype=GRB.CONTINUOUS,lb=0,ub=1,name=f"x{i}") for i in N]
        y = [[model.addVar(vtype=GRB.CONTINUOUS,lb=0,ub=1, name=f"y{i},{k}") for i in N] for k in K]
        z = [[model.addVar(vtype=GRB.CONTINUOUS,lb=0,ub=1, name=f"z{i},{k}") for i in N] for k in K]

    # Objective function
    model.setObjective(-sum(data.benefits[i]*x[i] for i in N)+(1/len(K))*sum(data.outsourcing_costs[i]*z[k][i] for i in N for k in K),GRB.MINIMIZE)

    # Constraintes
    for k in K:
        model.addConstr(sum(data.scenarios[i][k]*y[k][i] for i in N) <= data.capacity)
        for i in N:
            model.addConstr(z[k][i]+y[k][i] == x[i])

    model.optimize()

    xVal=[model.getVarByName(f'x{i}').x for i in N]
    thetaVal = [sum(data.outsourcing_costs[i]*model.getVarByName(f'z{i},{k}').x for i in N ) for k in K]

    return model.objVal,xVal,thetaVal,model.Runtime,model.ObjBound



# This function solves the CONTINUOUS relaxation on the second stage problem R2
def getSecondStageCost_R2(x,k:int,data:OA_data):

    N = range(data.nb_oders)
    model = Model("GUROBI")
    model.Params.LogToConsole = 0

    # Variables
    y = [model.addVar(vtype=GRB.CONTINUOUS, lb=0,ub=float('inf'),name=f'y{i}') for i in N]
    z = [model.addVar(vtype=GRB.CONTINUOUS, lb=0,ub=float('inf'),name=f'z{i}') for i in N]
  
    # Objective 
    model.setObjective(sum(data.outsourcing_costs[i]*z[i] for i in N), GRB.MINIMIZE)

    # Constraints
    model.addConstr(sum(data.scenarios[i][k]*y[i] for i in N) <= data.capacity,'capacity')

    for i in N:
        model.addConstr(z[i]+y[i] == x[i],'equality')

    for i in N:
        model.addConstr(y[i] <= 1,'yBound')

    for i in N:
        model.addConstr(z[i] <= 1,'zBound')

    # Solve Model
    model.optimize()

    for i in model.getConstrs():

        if i.ConstrName == 'capacity':
            dual_capacity = i.pi 

    dual_equality = [i.pi for i in model.getConstrs() if i.ConstrName=='equality']
    dual_y = [i.pi for i in model.getConstrs() if i.ConstrName=='yBound']
    dual_z = [i.pi for i in model.getConstrs() if i.ConstrName=='zBound']

    return [model.objVal, dual_capacity,dual_equality,dual_y,dual_z,model.Runtime]
    

# Question 13 
# This function contains the core of the Benders decomposition
def benders_question13(xVal,theta_k,k:int,masterProblem:Model,data:OA_data):
    N = range(data.nb_oders)

    # Solve the subproblem (in its primal form) and get the dual values
    obj, dual_capacity,dual_equality,dual_y,dual_z,run_time = getSecondStageCost_R2(xVal,k,data)

    DSP_k = dual_capacity*data.capacity+sum(xVal[i]*dual_equality[i] for i in N)+sum(i for i in dual_y)+sum(i for i in dual_z)

    # Process solution
    if theta_k+1e-5<DSP_k:

        expr = dual_capacity*data.capacity+sum(masterProblem.getVarByName(f'x{i}')*dual_equality[i] for i in N)+sum(i for i in dual_y)+sum(i for i in dual_z)
        masterProblem.addConstr(masterProblem.getVarByName(f'theta{k}') >= expr)

        return [True,run_time,masterProblem,dual_capacity,dual_equality,dual_y,dual_z]
    else:
        return [False,run_time,masterProblem,0,0,0,0]

# Question 14
# This method solves the problem using benders decomposition (by calling method benders_question13) and returns the optimility cuts if cut=1
def benders(cut:int,data:OA_data,masterProblem:Model):

    run_time = 0
    # if cut equals 1, this function allows determining the initial cuts, otherwise it contains the Benders loop
    masterProblem.optimize()
    xVal = [masterProblem.getVarByName(f'x{i}').x for i in range(data.nb_oders)]
    thetaVal = [masterProblem.getVarByName(f"theta{k}").x for k in range(data.nb_scenarios)]

    run_time+=masterProblem.Runtime

    if cut == 1:
        # coupe is a dict of added cuts for each scenario
        coupe = dict((i,[]) for i in range(data.nb_scenarios))
    criterion = 1
    
    while criterion!=0:
        criterion = 0

        for k in range(data.nb_scenarios):

            # do the test and eventuality add a cut for scenario k
            bool,run_time_secondStage,masterProblem,dual_capacity,dual_equality,dual_y,dual_z = benders_question13(xVal,thetaVal[k],k,masterProblem,data)
            run_time +=run_time_secondStage

            # updated master problem
            if bool == True: # i.e. we added a cut to the master problem in the previous line
                criterion = criterion+1

                if cut == 1:
                    #question 15, store feasible cut
                    coupe[k].append((dual_capacity,dual_equality,dual_y,dual_z))
                    
        # solve master problem to get the new values of x and theta
        masterProblem.optimize()
        run_time += masterProblem.Runtime

        # get values of x and theta
        xVal = [masterProblem.getVarByName(f'x{i}').x for i in range(data.nb_oders)]
        thetaVal = [masterProblem.getVarByName(f"theta{k}").x for k in range(data.nb_scenarios)]

    if cut == 1:
        print(f'La solution via Benders est {masterProblem.objVal} le cpu est {run_time}')

        return coupe,run_time
    else:
        print(f'La solution via Benders est {masterProblem.objVal} le cpu est {run_time}')
        return 0,run_time



# Question 16
def benders_addRelaxationCuts(masterProblem:Model, coupe:dict,data:OA_data):
    """ This function adds the initial cuts to the master problem """
    listConstrs=[]
    for k in range(data.nb_scenarios):

        for cut in coupe[k]: # cut is a vector of dual values in the form (a,[...],[...],[...])

            expr = cut[0]*data.capacity + sum(masterProblem.getVarByName(f'x{i}')*cut[1][i] for i in range(data.nb_oders)) + sum(i for i in cut[2]) + sum(i for i in cut[3])
            constr = masterProblem.addConstr(masterProblem.getVarByName(f'theta{k}') >= expr)
            listConstrs.append(constr)
    
    return masterProblem,listConstrs

# question 17
def remove_non_active_cuts(masterProblem,NonActifConstraint):

    # remove non active cuts from the master problem
    masterProblem.remove(NonActifConstraint)
    return masterProblem


def main(case):
    data = OA_data.read_from_file('data_O5/OA_O5_S3_L0.5_B10_R5_1.txt')    
    if case == 1:
        # Solve the model with a solveur
        print(f' la valeur objectif est {Direct_R1(data,1)}')
        return 0
    if case == 2:
        masterProblem = Master(Integrality=1,data=data) # Integrality equal zero means that x is continous in interval [0,1]
        initialCuts,run_time = benders(1,data,masterProblem)
    

#main(2)
# remaining is in CallbackVersion.py