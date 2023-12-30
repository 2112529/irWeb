import networkx as nx

class PageRank:
    def __init__(self, graph, d=0.85, max_iter=100, tol=1.0e-6):
        self.graph = graph
        self.V = len(graph)
        self.d = d
        self.max_iter = max_iter
        self.tol = tol
        self.ranks = dict()

    def rank(self):
        for key in self.graph:
            self.ranks[key] = 1 / float(self.V)
        
        for _ in range(self.max_iter):
            prev_ranks = self.ranks.copy()
            for node in self.graph:
                rank_sum = 0.0
                
                # Consider incoming edges for directed graph
                try:
                    neighbors = self.graph.predecessors(node) if self.graph.is_directed() else self.graph[node]
                except:
                    neighbors = self.graph[node]
                
                for n in neighbors:
                    if self.graph.is_directed():
                        outlinks = len(list(self.graph.successors(n)))
                    else:
                        outlinks = len(self.graph[n])
                    if outlinks > 0:
                        rank_sum += (1 / float(outlinks)) * prev_ranks[n]

                # Update the rank
                self.ranks[node] = (1 - self.d) / float(self.V) + self.d * rank_sum
            
            # Check for convergence
            err = sum([abs(self.ranks[node] - prev_ranks[node]) for node in self.graph])
            if err < self.V * self.tol:
                break
        return self.ranks

# Example usage
# Creating a graph as a dictionary where each key has a set of outgoing links
graph = {
    'A': {'B', 'C'},
    'B': {'C'},
    'C': {'A'},
    'D': {'C'}
}

# Convert the graph to a NetworkX graph for PageRank computation
nx_graph = nx.DiGraph(graph)

# Initialize PageRank
pr = PageRank(nx_graph, d=0.85, max_iter=100, tol=1e-6)

# Compute the PageRank
rankings = pr.rank()

# Print the PageRank of each node
print(rankings)
