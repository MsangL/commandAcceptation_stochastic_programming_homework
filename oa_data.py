# Description: This file contains the class OA_data which is used to store the data of the order acceptance problem.

from typing import Sequence


# a scenario is just the list of processing times for each order
class OA_scenario:
    def __init__(self, processing_times):
        self.processing_times:list[int] = processing_times
    def __str__(self):
        return f'processing_times: {self.processing_times}'
    def __repr__(self):
        return self.__str__()

class OA_data:
    def __init__(self, nb_oders, nb_scenarios, capacity):
        self.nb_oders:int = nb_oders
        self.nb_scenarios:int = nb_scenarios
        self.capacity:int = capacity
        self.scenarios={}
        self.ids = []
        self.benefits = []
        self.outsourcing_costs = []

    @classmethod
    def read_from_file(cls, file_path:str):
        with open(file_path, 'r') as file:
            nb_orders, nb_scenarios, capacity = map(int, file.readline().split())
            data = cls(nb_orders, nb_scenarios, capacity)
            for i in range(nb_orders):
                order_id, benefit, outsourcing_cost = map(int, file.readline().split())
                data.ids.append(order_id)
                data.benefits.append(benefit)
                data.outsourcing_costs.append(outsourcing_cost)
                processing_times = list(map(int, file.readline().split()))
                data.scenarios[i]=processing_times
        return data
    
    def __str__(self):
        return f'nb_orders: {self.nb_oders}, nb_scenarios: {self.nb_scenarios}, capacity: {self.capacity}, scenarios: {self.scenarios}\n benefice {self.benefits} outsource {self.outsourcing_costs}'
    def __repr__(self):
        return self.__str__()
"""  
def test():
    data = OA_data.read_from_file('data_O5/OA_O5_S3_L0.5_B10_R5_2.txt')
    print(data)
    return data
test()
"""