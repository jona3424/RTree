import random

import math


class Node:
    def __init__(self, m, M, parent=None):
        self.m = m  # minimum number of entries
        self.M = M  # maximum number of entries
        self.parent = parent  # reference to parent node
        self.children = []  # list to hold references to child nodes
        self.entries = []  # list to hold entries in the node
        self.mbr = [[None, None], [None, None]]  # minimum bounding rectangle (MBR)

    def update_mbr(self, new_entry):
        """Update the MBR of this node."""
        x, y = new_entry
        if self.mbr[0][0] is None or x < self.mbr[0][0]:
            self.mbr[0][0] = x
        if self.mbr[0][1] is None or x > self.mbr[0][1]:
            self.mbr[0][1] = x
        if self.mbr[1][0] is None or y < self.mbr[1][0]:
            self.mbr[1][0] = y
        if self.mbr[1][1] is None or y > self.mbr[1][1]:
            self.mbr[1][1] = y

    def is_leaf(self):
        """Check if the node is a leaf."""
        return not any(isinstance(i, Node) for i in self.children)

    def add_entry(self, entry, child=None):
        """Add a new entry to the node."""
        self.entries.append(entry)
        if child:
            self.children.append(child)
            child.parent = self
        self.update_mbr(entry)  # update MBR after adding a new entry

    def __str__(self):
        return str(self.entries)

class RTree:
    def __init__(self, m, M):
        self.m = m
        self.M = M
        self.root = Node(m, M)

    def _choose_leaf(self, N, E):
        if N.is_leaf():
            return N
        else:
            return self._choose_leaf(min(N.children, key=lambda child: self._area_increase(child.mbr, E)), E)

    def _area_increase(self, bounds, E):
        try:
            new_bounds = ([min(min_b, e) for min_b, e in zip(bounds[0], E)],
                          [max(max_b, e) for max_b, e in zip(bounds[1], E)])
            return self._area(new_bounds) - self._area(bounds)
        except IndexError:
            print(f"Error: Bounds and E are not of the same length. Bounds: {bounds}, E: {E}")

    def _area(self, bounds):
        return math.prod([max_b - min_b for min_b, max_b in zip(*bounds)])


    def _split_node(self, N):
        m = self.m
        # Sort entries by the length of their margin
        N.entries.sort(key=lambda entry: self._area(N.mbr))
        # Split around median
        split_index = len(N.entries) // 2
        N1_entries = N.entries[:split_index]
        N2_entries = N.entries[split_index:]

        N.entries = N1_entries
        N1 = N

        N2 = Node(self.m, self.M, parent=N.parent)  # set parent to N's parent
        N2.entries = N2_entries  # these are tuples not Nodes

        for entry in N2.entries:
            N2.update_mbr(entry)  # update MBR for each entry

        return N1, N2

    def Insert(self, E):
        L = self._choose_leaf(self.root, E)
        L.add_entry(E)

        if len(L.entries) > self.M:
            N1, N2 = self._split_node(L)
            if L == self.root:
                new_root = Node(self.m, self.M)
                new_root.entries = [N1.mbr, N2.mbr]
                new_root.children = [N1, N2]
                self.root = new_root
            else:
                if L.parent is not None:
                    if L in L.parent.children:
                        L.parent.children.remove(L)
                    L.parent.entries.remove(L.mbr)
                    L.parent.add_entry(N1.mbr, N1)
                    L.parent.add_entry(N2.mbr, N2)
                    if N2 not in L.parent.children:
                        L.parent.children.append(N2)
                else:
                    new_root = Node(self.m, self.M)
                    new_root.entries = [N1.mbr, N2.mbr]
                    new_root.children = [N1, N2]
                    self.root = new_root

    def intersects(self, r1, r2):
        return not (r1[0][1] < r2[0][0] or r1[0][0] > r2[0][1] or r1[1][1] < r2[1][0] or r1[1][0] > r2[1][1])

    def RangeSearch(self, N, Q):
        result = []

        if N.is_leaf():
            for E in N.entries:
                if self.intersects(E, Q):
                    result.append(E)
        else:
            for child in N.children:
                if self.intersects(child.mbr, Q):
                    result += self.RangeSearch(child, Q)
        return result

    def print_tree(self, N, depth=0):
        print('  ' * depth, N)
        for child in N.children:
            self.print_tree(child, depth+1)

    def print_whole_tree(self, N, depth=0):
        indent = ' ' * depth * 2
        if N.is_leaf():
            print(f"{indent}Leaf at depth {depth}: {N.entries}")
        else:
            print(f"{indent}Node at depth {depth} with MBR: {N.mbr}")
            for child in N.children:
                self.print_tree(child, depth + 1)

    def print_tree_level_order(self):
        from collections import deque
        queue = deque([(self.root,0)])

        while queue:
            node ,level= queue.popleft()
            indent = '  ' * level

            if(node.is_leaf()):
                print(indent +'Pravougaonik: ' + str(node.mbr))
                for  i in node.entries:
                    print(indent+indent+'Tacke: ' + str(i))
            else:
                print(indent + 'Pravougaonik: ' + str(node.mbr))
                for i in node.entries:
                    print(indent + indent + 'Tacke: ' + str(i))

                for i in node.children:
                    queue.append((i,level+1))







rtree=RTree(2,4)

rtree.Insert((1, 2))
rtree.Insert((3, 4))
rtree.Insert((5, 6))
rtree.Insert((12, 22))
rtree.Insert((32, 42))
rtree.Insert((52, 62))
rtree.Insert((11, 1))
rtree.Insert((3, 1))
rtree.Insert((5, 1))
rtree.Insert((17, 9))
rtree.Insert((73, 9))
rtree.Insert((75, 9))
rtree.Insert((2,1))
rtree.Insert((4,3))
rtree.Insert((6,5))
rtree.Insert(( 22,12))
rtree.Insert(( 42,32))
rtree.Insert(( 62,52))
rtree.Insert(( 1,11))
rtree.Insert((1,3))
rtree.Insert((1,5))

rtree.print_tree_level_order()
rtree.RangeSearch(rtree.root,(1, 2, 12, 22))