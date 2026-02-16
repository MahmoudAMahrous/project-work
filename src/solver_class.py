import networkx as nx
import random
import math
from Problem import Problem


class MySimulatedAnnealingSolver:
    def __init__(self, problem: Problem):
        self.problem = problem
        self.graph = problem.graph
        self.nodes = list(self.graph.nodes)
        self.gold = {n: self.graph.nodes[n]['gold'] for n in self.nodes}
        self.shortestPaths = dict(
            nx.all_pairs_dijkstra_path(self.graph, weight='dist'))
        self.distMatrix = dict(
            nx.all_pairs_dijkstra_path_length(self.graph, weight='dist'))
        # this is the matrix of the sum of distance between each 2 points raised to the power of beta
        self.distMatrixToPowerBeta = dict()
        for x in range(len(self.nodes)):
            self.distMatrixToPowerBeta[x] = {}
            for y in range(len(self.nodes)):
                total = 0
                for i in range(len(self.shortestPaths[x][y]) - 1):
                    total += self.distMatrix[self.shortestPaths[x][y]
                                             [i]][self.shortestPaths[x][y][i+1]] ** problem.beta
                self.distMatrixToPowerBeta[x][y] = total

    def getPathCost(self, u, v, weight):
        # instead of calculating the cost each time by going through all the points
        # we just put the the pre calculated values into the modified cost function
        dist = self.distMatrix[u][v]
        distToPowerBeta = self.distMatrixToPowerBeta[u][v]
        return dist + ((self.problem.alpha * weight) ** self.problem.beta) * distToPowerBeta
        dist = self.distMatrix[u][v]
        distToPowerBeta = self.distMatrixToPowerBeta[u][v]
        return dist + ((self.problem.alpha * dist * weight) ** self.problem.beta)

    def splitPermutation(self, permutation):
        # basically here we will decide if we go from the beginning of the permutaion to the
        # end of it without visiting the beginning again or we should put
        # a trip to the beginning in a specific point
        n = len(permutation)
        V = {i: float('inf') for i in range(n + 1)}
        V[0] = 0
        P = {i: -1 for i in range(n + 1)}

        for i in range(n):
            currentLoad = 0
            routeCost = 0
            u = 0

            for j in range(i + 1, n + 1):
                v = permutation[j-1]

                routeCost += self.getPathCost(u, v, currentLoad)
                currentLoad += self.gold[v]

                returnCost = self.getPathCost(v, 0, currentLoad)

                total = routeCost + returnCost

                if V[i] + total < V[j]:
                    V[j] = V[i] + total
                    P[j] = i

                u = v

        route = []
        curr = n
        while curr > 0:
            prev = P[curr]
            route.append(permutation[prev:curr])
            curr = prev
        route.reverse()
        return V[n], route

    def getNeighbor(self, permutation):
        newPermutation = permutation[:]
        n = len(newPermutation)

        if random.random() < 0.5:
            i, j = random.sample(range(n), 2)
            newPermutation[i], newPermutation[j] = newPermutation[j], newPermutation[i]
        else:
            i, j = sorted(random.sample(range(n), 2))
            newPermutation[i:j+1] = reversed(newPermutation[i:j+1])

        return newPermutation

    def buildFinalSolution(self, splittedRoute):
        disconnectedRoute = [(0, 0)]
        for segment in splittedRoute:
            disconnectedRoute.extend([(c, self.gold[c]) for c in segment])
            disconnectedRoute.append((0, 0))
        finalRoute = [disconnectedRoute[0]]
        for i in range(1, len(disconnectedRoute)):
            prev_city = finalRoute[-1][0]
            curr_city = disconnectedRoute[i][0]
            if not self.problem.graph.has_edge(prev_city, curr_city):
                path_nodes = self.shortestPaths[prev_city][curr_city]
                for intermediate_city in path_nodes[1:-1]:
                    finalRoute.append((intermediate_city, 0))
            finalRoute.append(disconnectedRoute[i])

        return finalRoute

    def run(self, initialTemp=1000, coolingRate=0.995, maxIterations=2000):
        cities = [n for n in self.nodes if n != 0]
        currentPerm = cities[:]
        random.shuffle(currentPerm)

        currentCost, currentRoutes = self.splitPermutation(currentPerm)

        bestCost = currentCost
        bestRoute = currentRoutes
        bestPermutation = currentPerm

        temp = initialTemp

        for i in range(maxIterations):
            neighborPermutation = self.getNeighbor(currentPerm)
            neighborCost, neighborRoute = self.splitPermutation(
                neighborPermutation)

            delta = neighborCost - currentCost

            if delta < 0 or random.random() < math.exp(-delta / temp):
                currentPerm = neighborPermutation
                currentCost = neighborCost
                currentRoutes = neighborRoute

                if currentCost < bestCost:
                    bestCost = currentCost
                    bestRoute = currentRoutes
                    bestPermutation = currentPerm

            temp *= coolingRate

            if temp < 0.001:
                break

        return self.buildFinalSolution(bestRoute), bestCost
