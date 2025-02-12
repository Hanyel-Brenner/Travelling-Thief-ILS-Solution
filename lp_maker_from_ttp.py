# -*- coding: utf-8 -*-
"""LP_maker_from_ttp.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1dvBdQciDo6e9TBs1d2nug-vFqDjVWIbZ

## Leitor de instâncias TTP
* Richard Rangel do N. Junior         156575
* Hanyel Brenner Camargos de Paula 156503
* Guilherme Vieira Justino 150007
"""
import gurobipy as grb
import numpy as np
import random
import math
import os

class TravelingThiefProblem:
    def __init__(self):
        self.problem_name = ""
        self.knapsack_capacity = 0
        self.num_items = 0
        self.min_speed = 0
        self.max_speed = 0
        self.renting_ratio = 0
        self.edge_weight_type = ""
        self.nodes = []
        self.items = []

    def read_from_file(self, filename):
        with open(filename, 'r') as file:
            lines = file.readlines()

        # Process the problem name and general parameters
        for line in lines:
            if line.startswith('PROBLEM NAME'):
                self.problem_name = line.split(':')[1].strip()
            elif line.startswith('DIMENSION'):
                self.num_nodes = int(line.split(':')[1].strip())
            elif line.startswith('NUMBER OF ITEMS'):
                self.num_items = int(line.split(':')[1].strip())
            elif line.startswith('CAPACITY OF KNAPSACK'):
                self.knapsack_capacity = int(line.split(':')[1].strip())
            elif line.startswith('MIN SPEED'):
                self.min_speed = float(line.split(':')[1].strip())
            elif line.startswith('MAX SPEED'):
                self.max_speed = float(line.split(':')[1].strip())
            elif line.startswith('RENTING RATIO'):
                self.renting_ratio = float(line.split(':')[1].strip())
            elif line.startswith('EDGE_WEIGHT_TYPE'):
                self.edge_weight_type = line.split(':')[1].strip()

        # Reading node coordinates
        reading_nodes = False
        for line in lines:
            if line.startswith('NODE_COORD_SECTION'):
                reading_nodes = True
            elif reading_nodes:
                if line.startswith('ITEMS SECTION'):
                    break
                node_data = line.split()
                node_index = int(node_data[0])
                x = float(node_data[1])
                y = float(node_data[2])
                self.nodes.append((node_index, x, y))

        # Reading items
        reading_items = False
        for line in lines:
            if line.startswith('ITEMS SECTION'):
                reading_items = True
            elif reading_items:
                item_data = line.split()
                item_index = int(item_data[0])
                profit = int(item_data[1])
                weight = int(item_data[2])
                assigned_node = int(item_data[3])
                self.items.append((item_index, profit, weight, assigned_node))

    def __repr__(self):
        return f"TravelingThiefProblem({self.problem_name}, {self.num_nodes} nodes, {self.num_items} items)"

"""
print("\nItems:")
for item in ttp.items:
  item_index, profit, weight, assigned_node = item
  print(f"Item {item_index}: Profit={profit}, Weight={weight}, Assigned Node={assigned_node}")

print("Cidades")
for node in ttp.nodes:
  node_index, x, y = node
  print(f"Node {node_index}: x={x}, y={y}")
"""

class tsp_lp_builder:
  def __init__(self, filename, cities):
    self.file = open(filename,'w')
    self.cities = cities
    self.file.close()
    self.x = [[0 for _ in range(len(self.cities))] for _ in range(len(self.cities))]
    self.d = [[0 for _ in range(len(self.cities))] for _ in range(len(self.cities))]

  def setDistanceBetweenCities(self):
    for i in range(len(self.cities)):
      for j in range(len(self.cities)):
        node_index, xi, yi = self.cities[i]
        node_index, xj, yj = self.cities[j]
        if i == j:
          self.d[i][j] = 99999999
        else :
          self.d[i][j] = round(np.sqrt(pow( (xi - xj) ,2) + pow( (yi - yj) , 2)))


  def setObjectiveFunction(self, filename):
      self.file = open(filename, 'a');
      self.file.write('MINIMIZE\n')
      for i in range(0, len(self.cities)):
        for j in range(0, len(self.cities)):
          if j == len(self.cities) - 1 and i != len(self.cities) - 1 : self.file.write(f'{self.d[i][j]} x{i}_{j} +')
          else : self.file.write(f'{self.d[i][j]} x{i}_{j}')
          if j != len(self.cities) - 1 : self.file.write(' + ')
      self.file.write('\n')
      self.file.close()

  def setConstraints(self, filename):
      N = len(self.cities)
      self.file = open(filename, 'a')
      self.file.write('SUBJECT TO\n')

      self.file.write('\nR1:')
      self.file.write('\n')

      for i in range(0, N):
        for j in range(0, N):
          self.file.write(f'x{i}_{j}')
          """if j != (N - 1) and not(i == N - 1 and j == N - 2):
            self.file.write(' + ')"""
          if j != (N - 1):
            self.file.write(' + ')
        self.file.write(' = 1\n')

      self.file.write('\nR2:')
      self.file.write('\n')

      for i in range(0, N):
        for j in range(0, N):
          self.file.write(f'x{j}_{i}')
          """if j != (N - 1) and not( i == N - 1 and j == N - 2) :
            self.file.write(' + ')"""
          if j != (N - 1):
            self.file.write(' + ')
        self.file.write(' = 1\n')

      self.file.write('\nR3:')
      self.file.write('\n')


      for i in range(1, N):
        for j in range(1, N):
          if i != j:
            self.file.write(f'u{i} - u{j} + {N} x{i}_{j} <= {N - 1}\n')
      self.file.write('u1 = 1\n');
      self.file.close()

  def setBounds(self, filename):
    N = len(self.cities)
    self.file = open(filename, 'a')
    self.file.write('BOUNDS\n')
    for i in range(1, N):
      self.file.write(f'u{i} >= 0\n');
    self.file.close();


  def setVariableTypes(self, filename):
    N = len(self.cities)
    self.file = open(filename, 'a')
    self.file.write('\nGENERALS\n')
    for i in range(0, len(self.cities)):
      self.file.write(f'u{i}\n')
    self.file.write('\nBINARIES\n')
    for i in range(0, N):
      for j in range(0, N ):
        self.file.write(f'x{i}_{j}\n')
    self.file.write('END')
    self.file.close()

class kp_lp_builder:
  def __init__(self, filename, items, knapsack_capacity):
    self.file = open(filename,'w')
    self.items = items
    self.knapsack_capacity = knapsack_capacity
    self.file.close()
    self.z = [0]*len(items)

  def setObjectiveFunction(self, filename):
    N = len(self.items)
    self.file = open(filename, 'a');
    self.file.write('MAXIMIZE\n')
    for i in range(0, N):
      item_index, profit, weight, assigned_node = self.items[i]
      if i != N - 1 : self.file.write(f'{profit} z{i} + ')
      else : self.file.write(f'{profit} z{i}')
    self.file.write('\n')
    self.file.close()

  def setConstraints(self, filename):
    N = len(self.items)
    self.file = open(filename, 'a')
    self.file.write('SUBJECT TO\n')
    for i in range(0, N):
      item_index, profit, weight, assigned_node = self.items[i]
      if i != N - 1 : self.file.write(f'{weight} z{i} + ')
      else : self.file.write(f'{weight} z{i} <= {self.knapsack_capacity}')
    self.file.write('\n')
    self.file.close()

  def setBounds(self, filename):
    N = len(self.items)
    self.file = open(filename, 'a')
    self.file.write('BOUNDS\n')
    for i in range(0, N):
      item_index, profit, weight, assigned_node = self.items[i]
      if i != N - 1 : self.file.write(f'{weight} z{i} + ')
      else : self.file.write(f'{weight} z{i}')
    self.file.write('\n')
    self.file.close()

  def setVariableTypes(self, filename):
    N = len(self.items)
    self.file = open(filename, 'a')
    self.file.write('BINARIES\n')
    for i in range(0, N):
      self.file.write(f'z{i}\n')
    self.file.write('END')
    self.file.close()

class result_loader:

  def __init__(self, filename, ttp):
    self.file = open(filename,'r');
    self.lines = self.file.readlines();
    self.ttp = ttp;
    self.file.close();

  def getObjectiveValueIndex(self, problem):
    values = [];
    for line in self.lines:
      if "Objective value" in line:
        values.append(float(line.split('=')[1].strip()));
    if problem == 'kp':
      bestResultIndex = values.index(max(values));
      return bestResultIndex;
    if problem == 'tsp':
      bestResultIndex = values.index(min(values));
      return bestResultIndex;

  def getKpResult(self, bestResultIndex):
    res = [];
    for i in range(bestResultIndex + 1, len(self.lines)):
      if "Objective value" in self.lines[i]:
        break;
      else:
        res.append(float(self.lines[i].split(' ')[1].strip()));
    return res;

  def getTspResult(self, bestResultIndex):
    n = len(self.ttp.nodes);
    x = [[0 for _ in range(0,n)] for _ in range(0,n)];
    u = [0 for _ in range(0,n)];
    nOfLines = len(self.lines);
    for i in range(bestResultIndex + 1, nOfLines):
      if "Objective value" in self.lines[i]:
        break;
      else:
        if "x" in self.lines[i]:
          variable = self.lines[i].split(' ')[0].strip();
          number = float(self.lines[i].split(' ')[1].strip());
          #print(variable);
          #print(number);
          lineIndex = int(variable.split('_')[0].strip()[1:]);
          columnIndex = int(variable.split('_')[1].strip());
          if columnIndex > n - 1 :
            raise Exception()
          x[lineIndex][columnIndex] = number;
        if "u" in self.lines[i]:
          variable = self.lines[i].split(' ')[0].strip();
          number = float(self.lines[i].split(' ')[1].strip());
          #print(variable);
          #print(number);
          lineIndex = int(variable[1:])
          u[lineIndex] = number
           
    return x,u

class iterated_local_search:
  def __init__(self, kp_sol, tsp_sol, n, m):
    self.kp_sol = kp_sol[:];
    self.tsp_sol = tsp_sol[:];
    self.kp_size = n;
    self.tsp_size = m;

  #tem uma margem de minimo e maximo
  def iterate(self,minIter, maxIter , perturbationFactor):
    kp_sol = self.kp_sol;
    tsp_sol = self.tsp_sol;
    for counter in range(minIter, maxIter):
      #Escolhe o ttp ou o kp aleatoriamente para pertubar
      switch = random.randint(0,1);
      if(switch == 0):
        kp_sol_perturbed = self.perturbation(kp_sol, perturbationFactor, counter,'kp');
      else:
        tsp_sol_perturbed = self.perturbation(tsp_sol, perturbationFactor, counter,'tsp');

    return kp_sol_perturbed, tsp_sol_perturbed

  def perturbation(self, sol, perturbationFactor, iterNumber ,problemType):
    if(problemType == 'kp'):
      i = random.randint(0, self.kp_size-1);
      min_j = max(0, i - int(perturbationFactor * self.kp_size))
      max_j = min(self.kp_size - 1, i + int(perturbationFactor * self.kp_size))
      j = random.randint(min_j, max_j);
      sol[i], sol[j] = sol[j], sol[i];
      return sol;

    if(problemType == 'tsp'):
        i, j = random.sample(range(self.tsp_size), 2)  # Escolhe dois índices distintos
        sol[i], sol[j] = sol[j], sol[i]  # Realiza a troca
    return sol

"""para o tsp usar round,para o tsp usar ceil
Para assim poder encontrar os resultados das instancias lá
"""

#Travelling thief problem is read

def generate_kp_LPs(ttpDirectoryPath, lpOutDir):
  os.makedirs(lpOutDir)
  for element in os.listdir(ttpDirectoryPath):
    print(element)
    temp = element.split('.')[0]
    kp_lp_path = os.path.join(lpOutDir, temp + '-kp.lp')

    ttp = TravelingThiefProblem()
    ttp.read_from_file(os.path.join(ttpDirectoryPath,element))

    kp = kp_lp_builder(kp_lp_path, ttp.items, ttp.knapsack_capacity)
    kp.setObjectiveFunction(kp_lp_path)
    kp.setConstraints(kp_lp_path)  
    kp.setVariableTypes(kp_lp_path)

def generate_tsp_LPs(ttpDirectoryPath, lpOutDir):
   os.makedirs(lpOutDir)
   for element in os.listdir(ttpDirectoryPath):
    print(element)
    temp = element.split('.')[0]
    tsp_lp_path = os.path.join(lpOutDir, temp + '-tsp.lp')

    ttp = TravelingThiefProblem()
    ttp.read_from_file(os.path.join(ttpDirectoryPath,element))

    tsp = tsp_lp_builder(tsp_lp_path,ttp.nodes)
    tsp.setDistanceBetweenCities()
    tsp.setObjectiveFunction(tsp_lp_path)
    tsp.setConstraints( tsp_lp_path)
    tsp.setBounds(tsp_lp_path)
    tsp.setVariableTypes(tsp_lp_path)

def solve_LPs(lpFilesDir, solOutDir):
   os.makedirs(solOutDir)
   for element in os.listdir(lpFilesDir):
    temp = element.split('.')[0]
    outDirPath = os.path.join(solOutDir, temp + '.sol')
    model = grb.read(os.path.join(lpFilesDir, element))
    model.optimize()
    model.write(outDirPath)
   
generate_kp_LPs('berlin52-ttp', 'kp_lp_files')
generate_tsp_LPs('berlin52-ttp', 'tsp_lp_files')
solve_LPs('kp_lp_files', 'kp_sol_files')
solve_LPs('tsp_lp_files', 'tsp_sol_files')

"""
ttp = TravelingThiefProblem()
ttp.read_from_file("./berlin52-ttp/berlin52_n51_bounded-strongly-corr_01.ttp")

#Travelling salesman problem is constructed in LP format based on ttp read instace
tsp = tsp_lp_builder("lp-tsp.lp",ttp.nodes)
tsp.setDistanceBetweenCities()
tsp.setObjectiveFunction("lp-tsp.lp")
tsp.setConstraints("lp-tsp.lp")
tsp.setBounds("lp-tsp.lp")
tsp.setVariableTypes("lp-tsp.lp")

#Knapsack problem is constructed in LP format based on ttp read instance
kp = kp_lp_builder("lpkp.lp", ttp.items, ttp.knapsack_capacity)
kp.setObjectiveFunction("lpkp.lp")
kp.setConstraints("lpkp.lp")
kp.setVariableTypes("lpkp.lp")

#LP models are read using gurobi python API and solution is writen to solution file
model = grb.read('lpkp.lp')
model.optimize()
model.write('sol.sol')

#After solving the model, we take the solution file and read it using solution loader
results = result_loader('sol.sol', ttp)
index = results.getObjectiveValueIndex('kp')
print(results.getKpResult(index))

model2 = grb.read('lp-tsp.lp')
model2.optimize()
model2.write('sol2.sol')

results2 = result_loader('sol2.sol',ttp)
index2 = results2.getObjectiveValueIndex('tsp')
x, u = results2.getTspResult(index2)

"""