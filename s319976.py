from Problem import Problem
from src.solver_class import MySimulatedAnnealingSolver


def solution(p: Problem):
    solver = MySimulatedAnnealingSolver(p)
    solution, cost = solver.run()
    print("solution:\n", solution, "\ncost:\n", cost)
    return solution
