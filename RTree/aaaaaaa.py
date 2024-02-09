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
        return (min_x, min_y, max_x, max_y)

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

    def __str__(self) -> str:
        return f"Entries: {self.entries}, MBR: {self.mbr}, Is Leaf: {self.is_leaf}, Parent: {self.parent}, Children: {len(self.children)}"

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
            # Here, we make sure the entry is treated as a bounding rectangle
            entry_mbr = (entry[0], entry[1], entry[0], entry[1])
            entry = (entry[0], entry[1], entry[0], entry[1])  # This line is new

        # If node is a leaf
        if node.is_leaf:
            # If the leaf can accommodate the new entry, add the entry
            if len(node.entries) < 2:
                node.entries.append(entry)
                node.update_mbr(entry_mbr)
            # Otherwise, split the leaf
            else:
                node1, node2 = self.split(node, entry)
                if node.is_root():
                    self.root = Node(mbr=node.mbr, children=[node1, node2], is_leaf=False)
                    node1.parent = self.root
                    node2.parent = self.root
                else:
                    parent = node.parent
                    # Check if the node's mbr is in parent's entries before trying to remove
                    if node.mbr in parent.entries:
                        parent.entries.remove(node.mbr)  # Remove the old MBR from the parent's entries
                    parent.entries.append(node1.mbr)  # Add the new MBRs to the parent's entries
                    parent.entries.append(node2.mbr)
                    # Check if the node is in parent's children before trying to remove
                    if node in parent.children:
                        parent.children.remove(node)  # Remove the old node from the parent's children
                    parent.children.append(node1)  # Add the new nodes to the parent's children
                    parent.children.append(node2)
                    node1.parent = parent
                    node2.parent = parent
                    if len(parent.entries) > 2:  # If the parent is now overfull, split it
                        self.insert(parent, parent.parent)
        # If node is not a leaf, recurse down the tree
        else:
            # Choose the child that will require the least area enlargement to accommodate the new entry
            best_child = min(node.children, key=lambda child: self.area_enlargement(child.mbr, entry_mbr))
            self.insert(entry, best_child)

    def area_enlargement(self, mbr, entry_mbr):
        xmin, ymin, xmax, ymax = mbr
        exmin, eymin, exmax, eymax = entry_mbr
        new_mbr = (min(xmin, exmin), min(ymin, eymin), max(xmax, exmax), max(ymax, eymax))
        return Node(entries=[mbr, new_mbr]).area() - Node(entries=[mbr]).area()

    def split(self, node, entry):
        # Linear split
        entries = node.entries + [entry]
        entries.sort(key=lambda x: x.mbr[0] if isinstance(x, Node) else x[0])
        l1 = entries[:len(entries) // 2]
        l2 = entries[len(entries) // 2:]
        n1 = Node(entries=[e.mbr if isinstance(e, Node) else e for e in l1], is_leaf=node.is_leaf)
        n2 = Node(entries=[e.mbr if isinstance(e, Node) else e for e in l2], is_leaf=node.is_leaf)
        return n1, n2

    def search(self, entry):
        def _search(node):
            if node.is_leaf:
                return any(e == entry for e in node.entries)
            else:
                return any(_search(child) for child in node.children if self.is_in_mbr(child.mbr, entry))
        return _search(self.root)

    def is_in_mbr(self, mbr, entry):
        xmin, ymin, xmax, ymax = mbr
        return xmin <= entry[0] <= xmax and ymin <= entry[1] <= ymax

    def print_level_order(self):
        queue = deque([(self.root, 0)])  # Start with the root at level 0
        current_level = 0

        while queue:
            node, level = queue.popleft()

            # Add indentation for each level
            indent = '  ' * level

            # Print a newline when we reach a new level
            if level != current_level:
                print()
                current_level = level

            # Print the MBR of inner nodes as rectangle coordinates
            if not node.is_leaf:
                print(f"{indent}Rectangle {node.mbr}")
            else:
                # Print the entries of leaf nodes as dots
                print(f"{indent}Rectangle {node.mbr}")
                for entry in node.entries:
                    print(f"{indent}Dot {entry}")

            # Add all children of the node to the queue
            for child in node.children:
                queue.append((child, level + 1))

        print()  # Print a final newline

# Testing the code
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
tree.insert((2,1))
tree.insert((4,3))
tree.insert((6,5))
tree.insert(( 22,12))
tree.insert(( 42,32))
tree.insert(( 62,52))
tree.insert(( 1,11))
tree.insert((1,3))
tree.insert((1,5))



tree.print_level_order()

print(tree.search((1, 2, 1, 2)))  # True
print(tree.search((75, 9, 75, 9)))  # True
print(tree.search((100, 200, 100, 200)))  # False


