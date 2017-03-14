# import matplotlib.pyplot as plt
from graphics import *
import math
import random
import operator
import numpy as np


# Use the ETSU-Official Colors - GO BUCS!
etsu_blue = color_rgb(4, 30, 68)
etsu_gold = color_rgb(255, 199, 44)
etsu_bg = color_rgb(223, 209, 167)




class Field:
    """
        Class Field uses the graphics.py library

        It simulates an x by y field that contains Polygons, Lines, and Points.

        Search Space: Vertexes of each polygon, Start & End locations
    """

    def __init__(self, width, height, intitle):
        '''
            Create lists of points, polygons
        '''
        self.points = []
        self.path = []
        self.polygons = []
        self.locations = {}     # Dictionary of locations, key is city name
        self.extras = []
        self.width = width
        self.height = height
        self.start = Point(0, 0)
        self.end = Point(0, 0)
        self.win = GraphWin(title=intitle,width=width,height=height)


    def setCoords(self, x1, y1, x2, y2):
        '''
            Set the viewport of the Field
        '''
        self.win.setCoords(x1, y1, x2, y2)


    def setBackground(self, color):
        '''
            Set the background color
        '''
        self.win.setBackground(color)


    def add_start(self, startcity):
        '''
            Add and display the starting location
        '''
        self.start = self.locations[startcity]
        c = Circle(self.start, 25)
        c.setFill('green')
        #self.extras.append(c)
        text = Text(Point(self.start.x+8, self.start.y+50), 'Start')
        text.setSize(10)
        text.setTextColor('black')
        #self.extras.append(text)
        text.draw(self.win)
        c.draw(self.win)


    def add_end(self, end):
        '''
            Add and display the ending location
        '''
        self.points.append(end)
        self.end = end
        c = Circle(end, 2)
        c.setFill('red')
        self.extras.append(c)
        text = Text(Point(end.x - 2, end.y - 10), 'End')
        text.setSize(10)
        text.setTextColor('black')
        self.extras.append(text)
        text.draw(self.win)
        c.draw(self.win)


    def get_neighbors(self, node):
        '''
          Returns a list of neighbors of node -- Vertexes that the node can see.
          All vertexes are within node's line-of-sight.
        '''
        neighbors = []

        # Loop through vertexes
        for point in self.points:
            # Ignore the vertex if it is the same as the node passed
            if (point == node):
                continue

            intersects = False

            # Create a line that represents a potential path segment
            pathSegment = Line(node, point)

            # Loop through the Polygons in the Field
            for o in self.polygons:
                # If the path segment intersects the Polygon, ignore it.
                if (o.intersects(pathSegment)):
                    intersects = True
                    break

            # If the path segment does not intersect the Polygon, it is a
            #  valid neighbor.
            if (not intersects):
                neighbors.append(point)

        return neighbors


    def get_points(self):
        return self.points


    def show_route(self, start_index, generation, route, fitness):

        tour = [start_index] + route + [start_index]

        i = 0
        p1 = p2 = None

        while p2 != self.start:

            p1 = self.points[tour[i]]
            p2 = self.points[tour[i+1]]

            line = Line(p1,p2)
            line.setArrow("last")
            line.setOutline("green")
            line.draw(self.win)
            self.extras.append(line)

            # if generation % 100 == 0:
            text = Text(Point(-8000.00,3500.00),"Generation: " + str(generation) + ", Fitness: " + str(fitness))
            text.draw(self.win)
            self.extras.append(text)

            i += 1


    def wait(self):
        '''
            Pause the Window for action
        '''
        self.win.getMouse()


    def close(self):
        '''
            Closes the Window after a pause
        '''
        self.win.getMouse()
        self.win.close()


    def reset(self):
        for extra in self.extras:
            extra.undraw()
        self.extras = []


    def straight_line_distance(self, point1, point2):
        '''
            Returns the straight-line distance between point 1 and point 2
        '''
        # TODO: Complete this code. You must calculate the straight-line distance
        #  before the genetic algorithm will produce a result.
        xsq = math.pow(point1.x - point2.x, 2)
        ysq = math.pow(point1.y - point2.y, 2)
        ans = math.sqrt(xsq + ysq)

        return ans


    def read_files(self, citycoordinates, citynames):
        locations = list(np.loadtxt(citycoordinates))
        self.cities = [line.rstrip('\n') for line in open(citynames)]

        for x in range(0,len(locations)):
            location = locations[x]
            city = self.cities[x]
            point = Point(location[0],location[1])
            self.points.append(point)
            c = Circle(point, 15)
            c.setFill(etsu_blue)
            self.locations[city] = point
            c.draw(self.win)



class GeneticSearch:
    """
        Inner Class: GeneticSearch
    """


    def __init__(self, field, generations, population_size, mutation_rate):
        self.field = field
        self.population = None
        self.chromosome_size = len(self.field.points)-1
        self.generations = generations
        self.population_size = population_size
        self.mutation_rate = mutation_rate
        self.start_index = self.field.points.index(self.field.start)
        self.values = []


    def print_population(self, generation, chromosomes):
        '''
            Show the first x chromosomes in the given generation
        '''
        index = 0
        print("===== GENERATION %d" % generation)
        for chromosome in self.population:
            print ("Index %5d , Fitness %0.4f : %s" % (index,chromosome[1], ''.join(str(chromosome[0]))))
            index = index + 1
            if index > chromosomes:
                break


    def initialize_population(self):
        '''
            Create the initial population at random
        '''
        self.population = []

        for x in list(range(0, self.population_size)):

            individual = random.sample(range(self.chromosome_size+1), self.chromosome_size+1)
            individual.remove(self.start_index)
            fitness = self.fitnessfcn(individual)
            self.population.append([individual,fitness])

        self.population.sort(key=operator.itemgetter(1), reverse=True)


    def fitnessfcn(self, individual):
        '''
            The shortest distance describes the most fit path. Therefore,
             the fitness function returns the total route distance negated.
        '''

        fitness = 0
        value = 0
        tour = [self.start_index] + individual + [self.start_index]

        index = 0
        p1 = p2 = None
        while p2 != self.field.start:
            p1 = self.field.points[tour[index]]
            p2 = self.field.points[tour[index+1]]
            fitness += self.field.straight_line_distance(p1,p2)
            index += 1

        if value == None:
            value = -1

        if fitness == 0:
            value = 0
        else:
            value = -fitness

        return value


    def reproduce(self, parent1, parent2):
        '''
            Reproduce using parent1 and parent2.
        '''

        # TODO: Complete the code to create two children using a crossover strategy.
        #  Explain your strategy in project2writeup.docx

        child1 = []
        child2 = []
        nums = list(range(0, 27))
        nums.remove(23)

        selection1 = random.choice([1, 2, 3, 4])
        selection2 = random.choice([1, 2, 3, 4])

        # Child1
        if selection1 == 1:
            child1.extend(parent1[0:14])
            filler = set(nums).difference(set(child1))
            f = list(filler)
            random.shuffle(f)
            child1.extend(f)
        elif selection1 == 2:
            child1.extend(parent1[14:27])
            filler = set(nums).difference(set(child1))
            f = list(filler)
            random.shuffle(f)
            child1.extend(f)
        elif selection1 == 3:
            child1.extend(parent2[0:14])
            filler = set(nums).difference(set(child1))
            f = list(filler)
            random.shuffle(f)
            child1.extend(f)
        elif selection1 == 4:
            child1.extend(parent2[14:27])
            filler = set(nums).difference(set(child1))
            f = list(filler)
            random.shuffle(f)
            child1.extend(f)

        # Child2
        if selection2 == 1:
            child2.extend(parent1[0:14])
            filler = set(nums).difference(set(child2))
            f = list(filler)
            random.shuffle(f)
            child2.extend(f)
        elif selection2 == 2:
            child2.extend(parent1[14:27])
            filler = set(nums).difference(set(child2))
            f = list(filler)
            random.shuffle(f)
            child2.extend(f)
        elif selection2 == 3:
            child2.extend(parent2[0:14])
            filler = set(nums).difference(set(child2))
            f = list(filler)
            random.shuffle(f)
            child2.extend(f)
        elif selection2 == 4:
            child2.extend(parent2[14:27])
            filler = set(nums).difference(set(child2))
            f = list(filler)
            random.shuffle(f)
            child2.extend(f)

        return [child1,child2]

    def make_filler(self, l):
        nums = list(range(0, 27))
        for int in nums:
            if (int in l):
                nums.remove(int)
        return nums

    def mutate(self,child):
        '''
            Mutation Strategy
        '''

        # TODO: Perform a mutation on the child chromosome
        #  Explain your strategy in project2writeup.docx
        a = random.choice(range(0, 25))
        b = random.choice(range(0, 25))
        child[a], child[b] = child[b], child[a]

        return child


    def print_result(self):
        '''
            Displays the resulting route in the console.
        '''
        individual = self.population[0][0]
        fitness = self.population[0][1]

        print(" Final Route in %d Generations" % self.generations)
        print(" Final Distance : %5.3f\n" % -fitness)

        counter = 1

        print ("%2d. %s" % (counter, self.field.cities[self.start_index]))
        counter += 1

        for index in individual:
            print ("%2d. %s" % (counter, self.field.cities[index]))
            counter += 1

        print ("%2d. %s" % (counter, self.field.cities[self.start_index]))


    def run(self):
        '''
            Run the genetic algorithm. Note that this method initializes the
             first population.
        '''
        generations = 0

        self.initialize_population()

        last_fitness = 0
        fitness_counter = 0

        while generations <= self.generations:
            new_population = []
            parent1 = []
            parent2 = []

            retain = math.ceil(self.population_size*0.10)
            new_population = self.population[:retain]
            for i in list(range(0,math.ceil((self.population_size-retain+1)/2))):

                # TODO: Complete the Selection Strategy to create two children
                #  Currently, the algorithm just takes the first two items as parents.
                #  Alter this strategy.
                sel1 = random.choice(new_population)
                sel2 = random.choice(new_population)
                parent1 = sel1[0]
                parent2 = sel2[0]

                children = self.reproduce(parent1,parent2)

                child1 = children[0]
                child2 = children[1]

                if (random.random() < self.mutation_rate):
                    child1 = self.mutate(child1)
                if (random.random() < self.mutation_rate):
                    child2 = self.mutate(child2)

                fitness1 = self.fitnessfcn(child1)
                fitness2 = self.fitnessfcn(child2)

                new_population.append([child1, fitness1])
                new_population.append([child2, fitness2])

            generations = generations + 1
            new_population.sort(key=operator.itemgetter(1),reverse=True)

            self.population = new_population

            # Show the route every 100 generations to save processing
            if generations % 100 == 0:
                self.field.reset()
                self.field.show_route(self.start_index, generations, self.population[0][0], self.population[0][1])

            current_fitness = self.population[0][1]
            if current_fitness == last_fitness:
                fitness_counter += 1
            else:
                fitness_counter = 0
            last_fitness = current_fitness

            self.values.append(self.population[0][1])   # You could use this for plotting





def main():
    '''
        Create the search space and conduct the genetic search
    '''
    f = Field(1000, 400, "Search Space")
    f.setCoords(-9000, 1800, -4500, 3600)
    f.setBackground(etsu_bg)
    f.read_files("coordinates.txt", "cities.txt")
    f.add_start("Washington, DC")

    # TODO: Alter parameters to find a better result. Generations should be in
    #  multiples of 100 because the algorithm only displays the best result
    #  in intervals of 100 generations.
    genetics = GeneticSearch(f, 50000, 2000, 0.5)
    genetics.run()

    genetics.print_result()

    f.wait()
    f.close()




main()
