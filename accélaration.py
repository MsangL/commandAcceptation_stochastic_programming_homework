from gurobipy import *

from bendersDecomposition import *

# question 19
def acceleration(data:OA_data,masterProblem:Model):
    N=range(data.nb_oders)
    K=range(data.nb_scenarios)

    run_time=0

    # initialization of the master problem without any cut
    masterProblem=Master(0,data)

    # j'ai choix d'initialiser x et theta tilde avec la solution initiale de problème maître sans coupes
    masterProblem.optimize()
    run_time+=masterProblem.Runtime

    # choose a initial value x that is feasible for the first stage problem
    x_tilde=[masterProblem.getVarByName(f'x{i}').x for i in N]
    theta_tilde=[masterProblem.getVarByName(f'theta{k}').x for k in K] # theta_k=L where L is the lower bound of the second stage problem

    # set algorithm's parameters
    lb=-float('inf')
    stalled=0
    stop=False
    lambda_param=0.5

   
    # coupe is a dict of added cuts for each scenario
    coupe=dict((i,[]) for i in K)

    while stop != True:
        # solve the master problem to get l
        masterProblem.optimize()
        l = masterProblem.ObjVal
        run_time+=masterProblem.Runtime

        # get value of (x,theta)
        xVal=[masterProblem.getVarByName(f'x{i}').x for i in N]
        thetaVal=[masterProblem.getVarByName(f'theta{k}').x for k in K]


        # if the current solution is better than the lower bound (minimization problem), update the lower bound
        if l > lb:
            lb = l
            stalled = 0
        else:
            stalled += 1
            if stalled == 5:
                lambda_param = 0

        # compute the stabilized separation point 
        xSep= [lambda_param*x_tilde[i]+(1-lambda_param)*xVal[i] for i in N]
        thetaSep= [lambda_param*theta_tilde[k]+(1-lambda_param)*thetaVal[k] for k in K]

        current_obj = -sum(data.benefits[i]*xVal[i] for i in N)+(1/len(K))*sum(thetaVal[k] for k in K)

        newcuts=0
        for k in range(data.nb_scenarios):

            # solve the second stage problem
            obj,dual_capacity,dual_equality,dual_y,dual_z,run_time_second_stage=getSecondStageCost_R2(xSep,k,data)
            run_time+=run_time_second_stage


            # compute second stage problem's objective value
            DSP_k=dual_capacity*data.capacity+sum(xSep[i]*dual_equality[i] for i in N)+sum(i for i in dual_y)+sum(i for i in dual_z)

            if thetaSep[k]+1e-5<DSP_k:
                # right hand value of the cut
                expr = dual_capacity*data.capacity+sum(masterProblem.getVarByName(f'x{i}')*dual_equality[i] for i in N)+sum(i for i in dual_y)+sum(i for i in dual_z)
                
                #add the cuts
                masterProblem.addConstr(masterProblem.getVarByName(f'theta{k}') >= expr)

                # store the cut's information
                coupe[k].append((dual_capacity,dual_equality,dual_y,dual_z))
                newcuts += 1

        # upadte x and theta tidle
        x_tilde=[0.5 * (x_tilde[i] + xVal[i]) for i in N]
        theta_tilde=[0.5 * (theta_tilde[k] + thetaVal[k]) for k in K]


        if lambda_param==0 and newcuts==0:
            stop=True

    return coupe,run_time
"""
    def main():
        data = OA_data.read_from_file('data_O5/OA_O5_S3_L0.5_B10_R5_1.txt')   
        masterProblem=Master(0,data)
        print(acceleration(data,masterProblem)) 

    main()
"""