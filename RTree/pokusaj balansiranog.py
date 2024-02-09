import math

class Node:
    def __init__(self, m, M, parent=None, is_leaf=True):
        self.m = m
        self.M = M
        self.parent = parent
        self.children = []
        self.entries = []
        self.mbr = None  # Updated to None initially
        self.is_leaf = is_leaf

    def update_mbr(self, mbr):
        if self.mbr is None:
            self.mbr = (mbr[0], mbr[1], mbr[0], mbr[1])
        else:
            xmin, ymin, _, _ = self.mbr
            x, y, _, _ = mbr
            self.mbr = (min(xmin, x), min(ymin, y), max(xmin, x), max(ymin, y))

    def add_entry(self, entry, child=None):
        """Add a new entry to the node."""
        self.update_mbr(entry)  # update MBR before adding a new entry
        self.entries.append(entry)
        if child:
            self.children.append(child)
            child.parent = self

    def _area(self, bounds):
        xmin, ymin, xmax, ymax = bounds
        return (xmax - xmin) * (ymax - ymin)

    def __str__(self):
        return str(self.entries)

class RTree:
    def __init__(self, m, M):
        self.m = m
        self.M = M
        self.root = Node(m, M, is_leaf=True)  # Root starts as a leaf node

    def _choose_leaf(self, N, E):
        if N.is_leaf:
            return N
        else:
            if N.children:
                return self._choose_leaf(min(N.children, key=lambda child: self._area_increase(child.mbr, E)), E)
            else:
                # No children, treat N as a leaf node
                return N

    def _area_increase(self, bounds, E):
        try:
            new_bounds = (
                [min(min_b, e) for min_b, e in zip(bounds[0], E)],
                [max(max_b, e) for max_b, e in zip(bounds[1], E)],
            )
            return self._area(new_bounds) - self._area(bounds)
        except IndexError:
            print(f"Error: Bounds and E are not of the same length. Bounds: {bounds}, E: {E}")

    def _split_node(self, N):
        m = self.m
        # Sort entries by the length of their margin
        N.entries.sort(key=lambda entry: self._area(entry))
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

    def _area(self, bounds):
        if len(bounds) == 4:
            xmin, ymin, xmax, ymax = bounds
            return (xmax - xmin) * (ymax - ymin)
        else:
            return 0

    def insert(self, E):
        L = self._choose_leaf(self.root, E)
        L.add_entry(E)

        if len(L.entries) > self.M:
            N1, N2 = self._split_node(L)
            if L == self.root:
                new_root = Node(self.m, self.M)
                new_root.add_entry(N1.mbr, N1)
                new_root.add_entry(N2.mbr, N2)
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
                    new_root.add_entry(N1.mbr, N1)
                    new_root.add_entry(N2.mbr, N2)
                    self.root = new_root

    def intersects(self, r1, r2):
        return not (r1[0][1] < r2[0][0] or r1[0][0] > r2[0][1] or r1[1][1] < r2[1][0] or r1[1][0] > r2[1][1])

    def range_search(self, N, Q):
        result = []

        if N.is_leaf:
            for E in N.entries:
                if self.intersects(E, Q):
                    result.append(E)
        else:
            for child in N.children:
                if self.intersects(child.mbr, Q):
                    result += self.range_search(child, Q)
        return result

    def print_tree_level_order(self):
        from collections import deque
        queue = deque([(self.root, 0)])

        while queue:
            node, level = queue.popleft()
            indent = '  ' * level

            if node.is_leaf:
                print(indent + 'Pravougaonik: ' + str(node.mbr))
                for i in node.entries:
                    print(indent + indent + 'Tacke: ' + str(i))
            else:
                print(indent + 'Pravougaonik: ' + str(node.mbr))
                for i in node.entries:
                    print(indent + indent + 'Tacke: ' + str(i))

                for i in node.children:
                    queue.append((i, level + 1))


rtree = RTree(2, 4)

rtree.insert((1, 2))
rtree.insert((3, 4))
rtree.insert((5, 6))
rtree.insert((12, 22))
rtree.insert((32, 42))
rtree.insert((52, 62))
rtree.insert((11, 1))
rtree.insert((3, 1))
rtree.insert((5, 1))
rtree.insert((17, 9))
rtree.insert((73, 9))
rtree.insert((75, 9))
rtree.insert((2, 1))
rtree.insert((4, 3))
rtree.insert((6, 5))
rtree.insert((22, 12))
rtree.insert((42, 32))
rtree.insert((62, 52))
rtree.insert((1, 11))
rtree.insert((1, 3))
rtree.insert((1, 5))

rtree.print_tree_level_order()
