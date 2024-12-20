
from gurobipy import *
from oa_data import *
from bendersDecomposition import *
from accélaration import *
from IntegerLShaped import *
from callbackVersion import *


def main_experiments():

    for r in [50, 100]:
        for b in [10, 100]:
            for s in [10, 50, 500]:
                for l in [0.7, 0.9]:
                    I="$\\mathcal{K}$ & i & \\Obj & \\runTime_Direct & \\runTime_relax & \\runTime_inout \\\\ \n"
                    for i in range(5):
                        # Import instance
                        data = OA_data.read_from_file(f'data_O5/OA_O5_S{s}_L{l}_B{b}_R{r}_{i}.txt')  

                        # Solve using different methods

                        # direct in q solveur
                        obj_direct, x_direct, theta_direct,run_time_direct, best_bound = Direct_R1(data, 1)

                        # iterative integer LShaped
                        #obj_integer_LShaped_Iter,x_integer_LShaped_Iter,theta_intger_LShaped_Iter,run_time_integer_LShaped_Iter = mainIntegerLShaped(data)

                        # Integer LShaped with initial cuts comming form the LP relaxation of de problem
                        obj_relax, x_relax, theta_relax,run_time_relax = main_Interger_LShaped_with_callaback(data, 1)

                        # Integer LShaped with initial cuts determined with the algorithm inspired by Fischetti et al. 2017
                        obj_inout, x_inout, theta_inout,run_time_inout = main_Interger_LShaped_with_callaback(data, 2)

                        # Write results to file
                        with open(f'solutions_O5/OA_O5_S{s}_L{l}_B{b}_R{r}_{i}.txt', 'w') as file:
                            file.write(f'Direct Solution: obj {obj_direct}, x {x_direct}, theta {theta_direct} runtime {run_time_direct} best bound {best_bound}\n\n')
                            #file.write(f'Iterative integer L-Shaped: obj {obj_integer_LShaped_Iter}, x {x_integer_LShaped_Iter}, theta {theta_intger_LShaped_Iter} runtime {run_time_integer_LShaped_Iter} \n\n')
                            file.write(f'Relaxation Solution: obj {obj_relax}, x {x_relax}, theta {theta_relax} runtime {run_time_relax}\n\n')
                            file.write(f'In-Out Solution: obj {obj_inout}, x {x_inout}, theta {theta_inout} runtime {run_time_inout}\n\n')

                        I = I + f'{s}&{i}& {obj_direct:2f} & {run_time_direct:2f} & {run_time_relax:2f} & {run_time_inout:2f} \\\\ \n'

                    # Write results to file
                    with open(f'solutions_O5/OA_O5_S{s}_L{l}_B{b}_R{r}_table.txt', 'a') as file:
                        file.write(I)


main_experiments()