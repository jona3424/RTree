class Node:
    def __init__(self, mbr=None, entries=None, is_leaf=False, parent=None):
        self.mbr = mbr or (float('inf'), float('inf'), float('-inf'), float('-inf'))  # (xmin, ymin, xmax, ymax)
        self.entries = entries or []
        self.is_leaf = is_leaf
        self.parent = parent

    def update_mbr(self, mbr):
        xmin, ymin, xmax, ymax = self.mbr
        self.mbr = (min(xmin, mbr[0]), min(ymin, mbr[1]), max(xmax, mbr[2]), max(ymax, mbr[3]))

    def area(self):
        xmin, ymin, xmax, ymax = self.mbr
        return (xmax - xmin) * (ymax - ymin)

    def is_root(self):
        return self.parent is None


from collections import deque

class RTree:
    def __init__(self,m):
        self.limit=m
        self.root = Node()

    def insert(self, entry, node=None):
        if node is None:
            node = self.root

        # origin from split then use existing mbrt
        if isinstance(entry, Node):
            entry_mbr = entry.mbr
        else:
            entry_mbr = (entry[0], entry[1], entry[0], entry[1])

        # If leafnode
        if node.is_leaf:
            #if node full not full
            if len(node.entries) < self.limit:
                node.entries.append(entry)
                node.update_mbr(entry_mbr)
            # split
            else:
                node1, node2 = self.split(node, entry)
                if node.is_root():
                    self.root = Node(node.mbr, [node1, node2], False)
                    node1.parent = self.root
                    node2.parent = self.root
                else:
                    parent = node.parent
                    parent.entries.remove(node)
                    parent.entries.append(node1)
                    parent.entries.append(node2)
                    node1.parent = parent
                    node2.parent = parent
                    parent.update_mbr(node1.mbr)
                    parent.update_mbr(node2.mbr)

        else:
            # Select the child node that requires the least area enlargement
            min_enlargement = float('inf')
            min_area = float('inf')
            min_index = -1
            if node.entries:
                for i, child in enumerate(node.entries):
                    enlargement = self.area_enlargement(child.mbr, entry_mbr)
                    if enlargement < min_enlargement or (enlargement == min_enlargement and child.area() < min_area):
                        min_enlargement = enlargement
                        min_area = child.area()
                        min_index = i
                self.insert(entry, node.entries[min_index])
            else:
                node.entries.append(Node(entry_mbr, [entry], True, node))
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
        queue = deque([self.root])
        while queue:
            node = queue.popleft()
            print('Node: ' + str(node.mbr))
            for entry in node.entries:
                if isinstance(entry, Node):
                    print('  ' + f'Pravougaonik: {entry.mbr}')
                else:
                    print('  ' + f'List: {entry}')
            for child in node.entries:
                if isinstance(child,Node):
                    queue.append(child)

tree = RTree(4)
# # Add some entries...
# tree.insert((1, 2))
# tree.insert((3, 4))
# tree.insert((5, 6))
# tree.insert((12, 22))
# tree.insert((32, 42))
# tree.insert((52, 62))
# tree.insert((11, 1))
# tree.insert((3, 1))
# tree.insert((5, 1))
# tree.insert((17, 9))
# tree.insert((73, 9))
# tree.insert((75, 9))
# tree.insert((333, 1))
# tree.insert((555, 1))
# tree.insert((117, 9))
# tree.insert((73, 49))
# tree.insert((7, 19))
# tree.insert((15, 19))
#
# # Print the tree
# tree.print_tree_level_order()
# print(tree.range_search((12, 22, 73, 62)))


def insertData(filename,tree:RTree):
    f = open(filename, "r")
    for line in f:
        lista=line.split(",")
        tree.insert((int(lista[0]),int(lista[1])))

insertData("dokument.txt",tree)
tree.print_tree_level_order()
print(tree.range_search((7, 0, 9, 9)))