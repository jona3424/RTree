class Node:
    def __init__(self, entries=None, mbr=None, parent=None, is_leaf=True, children=None):
        self.entries = entries if entries else []
        self.mbr = mbr if mbr else self.calculate_mbr()
        self.parent = parent
        self.is_leaf = is_leaf
        self.children = children if children else []

    def calculate_mbr(self):
        if not self.entries:
            return (0, 0, 0, 0)  # Default MBR if there are no entries
        # Initialize MBR to first entry
        min_x, min_y, max_x, max_y = self.entries[0]

        # Update MBR to include all entries
        for entry in self.entries:
            min_x = min(min_x, entry[0])
            min_y = min(min_y, entry[1])
            max_x = max(max_x, entry[2])
            max_y = max(max_y, entry[3])

        self.mbr = (min_x, min_y, max_x, max_y)

    def update_mbr(self, mbr):
        xmin, ymin, xmax, ymax = self.mbr
        self.mbr = (min(xmin, mbr[0]), min(ymin, mbr[1]), max(xmax, mbr[2]), max(ymax, mbr[3]))

    def area(self):
        xmin, ymin, xmax, ymax = self.mbr
        return (xmax - xmin) * (ymax - ymin)

    def is_root(self):
        return self.parent is None

    def add_child(self, child):
        self.children.append(child)
        child.parent = self


from collections import deque

class RTree:
    def __init__(self):
        self.root = Node()

    def insert(self, entry, node=None):
        if node is None:
            node = self.root

        # If entry is a Node instance (from a split), use its MBR for the calculations
        if isinstance(entry, Node):
            entry_mbr = entry.mbr
        else:
            entry_mbr = (entry[0], entry[1], entry[0], entry[1])

        # If node is a leaf
        if node.is_leaf:
            # If the leaf can accommodate the new entry, add the entry
            if len(node.entries) < 5:
                node.entries.append(entry)
                node.update_mbr(entry_mbr)
            # Otherwise, split the leaf
            else:
                node1, node2 = self.split(node, entry)
                if node.is_root():
                    self.root = Node(mbr=node.mbr, children=[node1, node2],
                                     is_leaf=False)  # Make the root a non-leaf node
                    node1.parent = self.root
                    node2.parent = self.root
                else:
                    parent = node.parent
                    parent.children.remove(node)  # Change entries to children
                    parent.children.append(node1)  # Change entries to children
                    parent.is_leaf = False  # Make the parent a non-leaf node
                    node1.parent = parent
                    self.insert(node2, self.root)
            # If node is not a leaf
        # If node is not a leaf
        else:
            # Select the child node that requires the least area enlargement
            min_enlargement = float('inf')
            min_area = float('inf')
            min_index = -1
            if node.children:
                for i, child in enumerate(node.children):
                    enlargement = self.area_enlargement(child.mbr, entry_mbr)
                    if enlargement < min_enlargement or (enlargement == min_enlargement and child.area() < min_area):
                        min_enlargement = enlargement
                        min_area = child.area()
                        min_index = i
                self.insert(entry, node.children[min_index])
            else:
                node.children.append(Node(entries=[entry], mbr=entry_mbr, parent=node, is_leaf=True))
                node.update_mbr(entry_mbr)


    def area_enlargement(self, mbr, entry):
        xmin, ymin, xmax, ymax = mbr
        new_area = (max(xmax, entry[0]) - min(xmin, entry[0])) * (max(ymax, entry[1]) - min(ymin, entry[1]))
        old_area = (xmax - xmin) * (ymax - ymin)  # Use direct calculation instead of calling self.area(mbr)
        return new_area - old_area

    def split(self, node, entry):
        # Linear split
        entries = node.entries + [entry]
        entries.sort(key=lambda x: x.mbr[0] if isinstance(x, Node) else x[0])
        l1 = entries[:len(entries) // 2]
        l2 = entries[len(entries) // 2:]
        n1 = Node(mbr=self.compute_mbr(l1), entries=l1, is_leaf=True)
        n2 = Node(mbr=self.compute_mbr(l2), entries=l2, is_leaf=True)
        return n1, n2

    def compute_mbr(self, entries):
        entries = [entry.mbr if isinstance(entry, Node) else entry for entry in entries]
        xmin = min(entries, key=lambda x: x[0])[0]
        ymin = min(entries, key=lambda x: x[1])[1]
        xmax = max(entries, key=lambda x: x[0])[0]
        ymax = max(entries, key=lambda x: x[1])[1]
        return (xmin, ymin, xmax, ymax)

    def range_search(self, region, node=None):
        if node is None:
            node = self.root

        results = []

        # If node is a leaf node
        if node.is_leaf:
            for entry in node.entries:
                if self.intersect((entry[0], entry[1], entry[0], entry[1]), region):
                    results.append(entry)
        else:
            for child in node.entries:
                if self.intersect(child.mbr, region):
                    results.extend(self.range_search(region, child))
        return results

    def intersect(self, mbr1, mbr2):
        xmin1, ymin1, xmax1, ymax1 = mbr1
        xmin2, ymin2, xmax2, ymax2 = mbr2
        return not (xmin1 > xmax2 or xmax1 < xmin2 or ymin1 > ymax2 or ymax1 < ymin2)

    def print_tree(self, node=None, level=0):
        if node is None:
            node = self.root

        if node.is_leaf:
            for entry in node.entries:
                print('  ' * level + f'Leaf: {entry}, MBR: {node.mbr}')
        else:
            print('  ' * level + f'Node: {node.mbr}')
            for child in node.entries:
                self.print_tree(child, level + 1)

    def print_tree_level_order(self):
        # Use a queue to keep track of nodes and their levels
        queue = deque([(self.root, 0)])

        while queue:
            node, level = queue.popleft()  # Dequeue a node and its level

            indent = '  ' * level
            print(indent + 'Node MBR (rectangle): {}'.format(node.mbr))

            for entry in node.entries:
                    print(indent + '  Dot: {}'.format(entry))
            for child in node.children:
                    queue.append((child, level + 1))  # Enqueue child and next level

tree = RTree()
# Add some entries...
tree.insert((1, 2))
tree.insert((3, 4))
tree.insert((5, 6))
tree.insert((12, 22))
tree.insert((32, 42))
tree.insert((52, 62))
tree.insert((11, 1))
tree.insert((3, 1))
tree.insert((5, 1))
tree.insert((17, 9))
tree.insert((73, 9))
tree.insert((75, 9))

# Print the tree
tree.print_tree_level_order()