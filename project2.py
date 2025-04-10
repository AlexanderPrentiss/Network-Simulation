from graph import Graph, Vertex
from priority_queue import PriorityQueue
from sys import maxsize

class ISPNetwork:
    def __init__(self):
        self.network = Graph()
        self.MST = Graph()

    def buildGraph(self, filename):
        cur = None
        with open(filename, 'r') as file:
            data = file.readlines()
            for i in data:
                line = i.split(',')
                for j in range(2):
                   self.network.addEdge(line[0], line[1], float(line[2]))
        pass

    def pathExist(self, router1, router2, hops):
        if not self.network.getVertex(router1) or not self.network.getVertex(router2): #Check whether router1 and router2 exist
            return False
        if router1 == router2: #Check wheter router1 and router2 are the same
            return True
        to_search = [(router1, 0)] #List of touples containing the key and level
        searched = [router1] #Keys we've searched
        while to_search: #While there are still keys to search
            cur, cur_hops = to_search.pop(0) #Remove top value in queue and search through its neighbors
            while cur_hops >= hops and to_search: #If the current key is too far away, find another one
                cur, cur_hops = to_search.pop(0)
            neighbors = self.network.getVertex(cur).getConnections() #Gets a list of connections
            for router in neighbors: #Check all neighbors to see:
                router = router.id #Converts from vertex object to key
                if router == router2: #Is this key router2?
                    return True
                if router not in searched and cur_hops+1 < hops: #If this is a key we should search later
                    searched.append(router) #Add to searched
                    to_search.append((router, cur_hops+1)) #Add key and level to the queue
        return False #Router 2 is not within hops but is in the list
                

    def buildMST(self, source):
        pq = PriorityQueue()
        for vertex in self.network: #Get all vertices in the network
            vertex.setDistance(maxsize) #Set each vertex to have infinite distance
            vertex.setPred(None) #Remove all predecesors 
        source_vertex = self.network.getVertex(source)
        source_vertex.setDistance(0) #set the source distance to 0
        pq.buildHeap([(vertex.getDistance(), vertex) for vertex in self.network]) #Make priority queue of all vertices
        while not pq.isEmpty(): #While there are vertices left
            current_vertex = pq.delMin() #remove the top item from the priority queue
            if current_vertex.getPred(): #if the vertex has predecesors
                self.MST.addEdge(current_vertex.getPred().getId(), current_vertex.getId(), current_vertex.getDistance()) #add vertex to MST
            for next_vertex in current_vertex.getConnections(): #Get all neighbors
                new_cost = current_vertex.getWeight(next_vertex) #Set the weight
                if next_vertex in pq and new_cost < next_vertex.getDistance():
                    next_vertex.setPred(current_vertex) #Set the next next vertex's predicesor to the current vertex
                    next_vertex.setDistance(new_cost) #Set the distance for the new vertex
                    pq.decreaseKey(next_vertex, new_cost) #decrease the heap
        pass

    def findPath(self, router1, router2):
        if not self.MST.getVertex(router1) or not self.MST.getVertex(router2): #Check to see if router 1 and 2 are in the MST
            return 'path not exist'
        #djikstra's
        path = [] #holds the path
        pq = PriorityQueue() #Create priority queue
        source = self.MST.getVertex(router1)
        source.setDistance(0) #Sets the source distance to 0
        pq.buildHeap([(vertex.getDistance(), vertex) for vertex in self.MST]) #creates PriorityQueue of all vertices and their distances
        while not pq.isEmpty(): #While there are still nodes to search
            current_vertex = pq.delMin() #get the current node from the top of the queue
            if current_vertex.getId() == router2: #if we found route 2
                while current_vertex: #while there is a node left to iterate to
                    path.insert(0, current_vertex.getId()) #add the node to the begining of the path
                    if current_vertex.getPred(): #if there is a predecesor
                        if current_vertex.getPred().getPred() == current_vertex: #if there is a loop
                            return 'path not exist'
                    current_vertex = current_vertex.getPred() #set current to the next predecesor
                break #break original loop because we found the router2
            for next_vertex in current_vertex.getConnections(): #for all neighbors 
                newDist = current_vertex.getDistance() + current_vertex.getWeight(next_vertex) #the new distance would be current's distance plus the weight
                if newDist < next_vertex.getDistance(): #if the new distance is more efficient
                    next_vertex.setDistance(newDist) #update distance with new distance
                    next_vertex.setPred(current_vertex) #update predecesor 
                    pq.decreaseKey(next_vertex,newDist) #decrement heap
        output = str(path.pop(0)) #add the first vertex to the output
        for i in path: #add all other elements to the output with the correct arrow notation
            output += f' -> {i}'
        return output
        pass

    def findForwardingPath(self, router1, router2):
        if not self.network.getVertex(router1) or not self.network.getVertex(router2): #Check to see if router 1 and 2 are in the MST
            return 'path not exist'
        #djikstra's
        for vertex in self.network:
            vertex.setDistance(maxsize)
            vertex.setPred(None)
        #path = []
        pq = PriorityQueue()
        source = self.network.getVertex(router1)
        source.setDistance(0)
        pq.buildHeap([(vertex.getDistance(), vertex) for vertex in self.network])
        while not pq.isEmpty():
            current_vertex = pq.delMin()
            for next_vertex in current_vertex.getConnections():
                newDist = current_vertex.getDistance() + current_vertex.getWeight(next_vertex)
                if newDist < next_vertex.getDistance():
                    next_vertex.setDistance(newDist)
                    next_vertex.setPred(current_vertex)
                    pq.decreaseKey(next_vertex,newDist)
        path=[]
        curr = self.network.getVertex(router2)
        while curr is not None:
            path.append(curr.getId())
            cur = curr.getPred()
        reverse_path = path[::-1]
        if not reverse_path or reverse_path[0] != router1.getId():
            return 'path not exist'
        else:
            return '->'.join(reverse_path) + ' ('+str(router2.getDistance())+')'
        pass

    def findPathMaxWeight(self, router1, router2):
        if not self.network.getVertex(router1) or not self.network.getVertex(router2): #Check to see if router 1 and 2 are in the MST
            return 'path not exist'
        #djikstra's
        path = []
        pq = PriorityQueue()
        source = self.network.getVertex(router1)
        source.setDistance(maxsize)
        pq.buildHeap([(vertex.getDistance(), vertex) for vertex in self.MST])
        while not pq.isEmpty():
            current_vertex = pq.delMin()
            if current_vertex.getId() == router2:
                while current_vertex:
                    path.insert(0, current_vertex.getId())
                    if current_vertex.getPred():
                        if current_vertex.getPred().getPred() == current_vertex:
                            return 'path not exist'
                    current_vertex = current_vertex.getPred()
                break
            max_weight = maxsize #Set the max weight to be impossibly high
            for next_vertex in current_vertex.getConnections(): #For the neighbors of the current vertex
                new_max_weight = current_vertex.getWeight(next_vertex) #Use the weight between current and next
                if new_max_weight < max_weight: # if this weight is less than the current max_Weight
                    max_weight = new_max_weight
                    next_vertex.setDistance(max_weight)
                    next_vertex.setPred(current_vertex)
                    pq.decreaseKey(next_vertex,max_weight)
        if len(path) == 0:
            return 'path not exist'
        output = str(path.pop(0))
        for i in path:
            output += f' -> {i}'
        return output
        pass

    def checkLoop(self, route):
        for router in route: #for every router in the route
            visited = [] #have a list of visited nodes
            cur_router = router #set current router
            while route.get(cur_router, None):
                if cur_router in visited: #if the route loops
                    return True 
                visited.append(cur_router) #add the vertex to visited
                cur_router = route[cur_router] #update cur to the next router
        return False
        pass


