#!/usr/bin/env python3
"""
library_catalog.py

Library Book Catalog using Red-Black Tree indices:
 - rbt_by_id: RBTree keyed by book_id (unique)
 - rbt_by_title: RBTree keyed by (title_lower, book_id) to support fast title search and prefix search.

Features:
 - Insert, delete, search by ID
 - Search by title exact or prefix (case-insensitive)
 - In-order listing by ID or by title
 - Save / load JSON
 - Simple CLI

Author: ChatGPT (GPT-5 Thinking mini) for student project template
Date: 2025
"""

import json
import sys
from dataclasses import dataclass, asdict
from typing import Any, Optional, Generator, Tuple, List

# ---------------------
# Red-Black Tree classes
# ---------------------

RED = "RED"
BLACK = "BLACK"

class RBNode:
    __slots__ = ("key", "value", "left", "right", "parent", "color")
    def __init__(self, key=None, value=None, color=BLACK, left=None, right=None, parent=None):
        self.key = key
        self.value = value
        self.left: 'RBNode' = left
        self.right: 'RBNode' = right
        self.parent: 'RBNode' = parent
        self.color = color

    def __repr__(self):
        return f"RBNode({self.key}, color={self.color})"

class RBTree:
    def __init__(self):
        # single sentinel NIL node
        self.NIL = RBNode()
        self.NIL.left = self.NIL.right = self.NIL.parent = self.NIL
        self.NIL.color = BLACK
        self.root: RBNode = self.NIL

    # Helper: left-rotate x
    def _left_rotate(self, x: RBNode):
        y = x.right
        x.right = y.left
        if y.left != self.NIL:
            y.left.parent = x
        y.parent = x.parent
        if x.parent == self.NIL:
            self.root = y
        elif x == x.parent.left:
            x.parent.left = y
        else:
            x.parent.right = y
        y.left = x
        x.parent = y

    # Helper: right-rotate x
    def _right_rotate(self, x: RBNode):
        y = x.left
        x.left = y.right
        if y.right != self.NIL:
            y.right.parent = x
        y.parent = x.parent
        if x.parent == self.NIL:
            self.root = y
        elif x == x.parent.right:
            x.parent.right = y
        else:
            x.parent.left = y
        y.right = x
        x.parent = y

    # Insert (key, value)
    def insert(self, key, value):
        node = RBNode(key=key, value=value, color=RED, left=self.NIL, right=self.NIL, parent=self.NIL)
        y = self.NIL
        x = self.root
        while x != self.NIL:
            y = x
            if node.key < x.key:
                x = x.left
            elif node.key > x.key:
                x = x.right
            else:
                # If key exists, replace value and return existing node
                x.value = value
                return x
        node.parent = y
        if y == self.NIL:
            self.root = node
        elif node.key < y.key:
            y.left = node
        else:
            y.right = node
        # fixup
        self._insert_fixup(node)
        return node

    def _insert_fixup(self, z: RBNode):
        while z.parent.color == RED:
            if z.parent == z.parent.parent.left:
                y = z.parent.parent.right
                if y.color == RED:
                    # case 1
                    z.parent.color = BLACK
                    y.color = BLACK
                    z.parent.parent.color = RED
                    z = z.parent.parent
                else:
                    if z == z.parent.right:
                        # case 2
                        z = z.parent
                        self._left_rotate(z)
                    # case 3
                    z.parent.color = BLACK
                    z.parent.parent.color = RED
                    self._right_rotate(z.parent.parent)
            else:
                # symmetric
                y = z.parent.parent.left
                if y.color == RED:
                    z.parent.color = BLACK
                    y.color = BLACK
                    z.parent.parent.color = RED
                    z = z.parent.parent
                else:
                    if z == z.parent.left:
                        z = z.parent
                        self._right_rotate(z)
                    z.parent.color = BLACK
                    z.parent.parent.color = RED
                    self._left_rotate(z.parent.parent)
        self.root.color = BLACK

    # Search node by key
    def search_node(self, key) -> Optional[RBNode]:
        x = self.root
        while x != self.NIL and key != x.key:
            if key < x.key:
                x = x.left
            else:
                x = x.right
        return x if x != self.NIL else None

    def search(self, key):
        n = self.search_node(key)
        return n.value if n is not None else None

    # Minimum node from x
    def _minimum(self, x: RBNode) -> RBNode:
        while x.left != self.NIL:
            x = x.left
        return x

    # Successor
    def _successor(self, x: RBNode) -> Optional[RBNode]:
        if x.right != self.NIL:
            return self._minimum(x.right)
        y = x.parent
        while y != self.NIL and x == y.right:
            x = y
            y = y.parent
        return y if y != self.NIL else None

    # Transplant u with v
    def _transplant(self, u: RBNode, v: RBNode):
        if u.parent == self.NIL:
            self.root = v
        elif u == u.parent.left:
            u.parent.left = v
        else:
            u.parent.right = v
        v.parent = u.parent

    # Delete key
    def delete(self, key) -> bool:
        z_node = self.search_node(key)
        if z_node is None:
            return False
        z = z_node
        y = z
        y_original_color = y.color
        if z.left == self.NIL:
            x = z.right
            self._transplant(z, z.right)
        elif z.right == self.NIL:
            x = z.left
            self._transplant(z, z.left)
        else:
            y = self._minimum(z.right)
            y_original_color = y.color
            x = y.right
            if y.parent == z:
                x.parent = y
            else:
                self._transplant(y, y.right)
                y.right = z.right
                y.right.parent = y
            self._transplant(z, y)
            y.left = z.left
            y.left.parent = y
            y.color = z.color
        if y_original_color == BLACK:
            self._delete_fixup(x)
        return True

    def _delete_fixup(self, x: RBNode):
        while x != self.root and x.color == BLACK:
            if x == x.parent.left:
                w = x.parent.right
                if w.color == RED:
                    w.color = BLACK
                    x.parent.color = RED
                    self._left_rotate(x.parent)
                    w = x.parent.right
                if w.left.color == BLACK and w.right.color == BLACK:
                    w.color = RED
                    x = x.parent
                else:
                    if w.right.color == BLACK:
                        w.left.color = BLACK
                        w.color = RED
                        self._right_rotate(w)
                        w = x.parent.right
                    w.color = x.parent.color
                    x.parent.color = BLACK
                    w.right.color = BLACK
                    self._left_rotate(x.parent)
                    x = self.root
            else:
                w = x.parent.left
                if w.color == RED:
                    w.color = BLACK
                    x.parent.color = RED
                    self._right_rotate(x.parent)
                    w = x.parent.left
                if w.right.color == BLACK and w.left.color == BLACK:
                    w.color = RED
                    x = x.parent
                else:
                    if w.left.color == BLACK:
                        w.right.color = BLACK
                        w.color = RED
                        self._left_rotate(w)
                        w = x.parent.left
                    w.color = x.parent.color
                    x.parent.color = BLACK
                    w.left.color = BLACK
                    self._right_rotate(x.parent)
                    x = self.root
        x.color = BLACK

    # In-order traversal generator (yields (key, value))
    def inorder(self) -> Generator[Tuple[Any, Any], None, None]:
        def _inorder(node: RBNode):
            if node != self.NIL:
                yield from _inorder(node.left)
                yield (node.key, node.value)
                yield from _inorder(node.right)
        yield from _inorder(self.root)

    # Lower bound: first node with key >= given key
    def lower_bound_node(self, key) -> Optional[RBNode]:
        x = self.root
        lb = None
        while x != self.NIL:
            if x.key >= key:
                lb = x
                x = x.left
            else:
                x = x.right
        return lb

    # Utility: size
    def size(self) -> int:
        cnt = 0
        for _ in self.inorder():
            cnt += 1
        return cnt

    # For debugging: pretty print (inorder)
    def debug_inorder_list(self) -> List[Tuple[Any, Any]]:
        return list(self.inorder())

# ---------------------
# Book model
# ---------------------
@dataclass
class Book:
    book_id: int
    title: str
    author: str
    year: int
    copies: int = 1

    def to_dict(self):
        return asdict(self)

    @staticmethod
    def from_dict(d):
        return Book(
            book_id=d["book_id"],
            title=d["title"],
            author=d.get("author", ""),
            year=int(d.get("year", 0)),
            copies=int(d.get("copies", 1))
        )

# ---------------------
# Library Catalog manager
# ---------------------
class LibraryCatalog:
    def __init__(self):
        self.by_id = RBTree()    # key = book_id
        # for titles we use (title_lower, book_id) to keep unique keys & lexicographic order by title then id
        self.by_title = RBTree()

    # Add or update a book
    def add_book(self, book: Book):
        # Check if ID exists
        existing = self.by_id.search_node(book.book_id)
        if existing:
            # update existing record
            existing.value = book
            # also update by_title: need to remove old title entry and insert new
            # find old title node(s) corresponding to this id
            # old key would be (old_title_lower, id)
            # We'll try to delete any by_title node with matching id
            # To do that, search by lower_bound on (title_lower, id) across all titles can't know old title easily.
            # Simpler: walk title tree and remove node with second element == id (not expensive for updates)
            self._remove_title_nodes_for_id(book.book_id)
            key = (book.title.lower(), book.book_id)
            self.by_title.insert(key, book)
            return "updated"
        else:
            # new insert
            self.by_id.insert(book.book_id, book)
            key = (book.title.lower(), book.book_id)
            self.by_title.insert(key, book)
            return "inserted"

    def _remove_title_nodes_for_id(self, book_id):
        # iterate keys in title tree to find any nodes with matching id (should be at most one)
        to_delete = []
        for key, _ in self.by_title.inorder():
            if key[1] == book_id:
                to_delete.append(key)
        for k in to_delete:
            self.by_title.delete(k)

    # Delete by ID
    def delete_by_id(self, book_id) -> bool:
        book_node = self.by_id.search_node(book_id)
        if book_node is None:
            return False
        book = book_node.value
        # delete from both trees
        self.by_id.delete(book_id)
        title_key = (book.title.lower(), book.book_id)
        self.by_title.delete(title_key)
        return True

    # Search by ID
    def search_by_id(self, book_id) -> Optional[Book]:
        return self.by_id.search(book_id)

    # Search by exact title (case-insensitive). Returns list of Book
    def search_by_title_exact(self, title: str) -> List[Book]:
        tkey = title.lower()
        # lower_bound key is (tkey, -infty) to get first title >= tkey
        # Python doesn't have -inf for ids; since id type is int we can use -sys.maxsize
        lb_key = (tkey, -sys.maxsize)
        node = self.by_title.lower_bound_node(lb_key)
        res = []
        while node:
            key = node.key
            if key[0] == tkey:
                res.append(node.value)
                node = self.by_title._successor(node)
            else:
                break
        return res

    # Prefix search for titles (case-insensitive). Returns list of Book
    def search_by_title_prefix(self, prefix: str) -> List[Book]:
        p = prefix.lower()
        lb_key = (p, -sys.maxsize)
        node = self.by_title.lower_bound_node(lb_key)
        res = []
        while node:
            key = node.key
            if key[0].startswith(p):
                res.append(node.value)
                node = self.by_title._successor(node)
            else:
                break
        return res

    # List all books ordered by id or by title
    def list_all_by_id(self) -> List[Book]:
        return [v for _, v in self.by_id.inorder()]

    def list_all_by_title(self) -> List[Book]:
        return [v for _, v in self.by_title.inorder()]

    # Save to JSON file
    def save_to_file(self, filename: str):
        data = [book.to_dict() for book in self.list_all_by_id()]
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        return True

    # Load from JSON file (rebuild indices)
    def load_from_file(self, filename: str):
        with open(filename, "r", encoding="utf-8") as f:
            arr = json.load(f)
        # reset
        self.by_id = RBTree()
        self.by_title = RBTree()
        for d in arr:
            book = Book.from_dict(d)
            self.add_book(book)
        return True

# ---------------------
# CLI / Demo functions
# ---------------------

def print_book(book: Book):
    if not book: 
        print("No book.")
        return
    print(f"ID: {book.book_id} | Title: {book.title} | Author: {book.author} | Year: {book.year} | Copies: {book.copies}")

def demo_seed(catalog: LibraryCatalog):
    seed = [
        Book(101, "Introduction to Algorithms", "Cormen et al.", 2009, copies=3),
        Book(205, "Design Patterns", "Gamma et al.", 1995, copies=2),
        Book(150, "Clean Code", "Robert C. Martin", 2008, copies=4),
        Book(300, "The Pragmatic Programmer", "Andrew Hunt", 1999, copies=1),
        Book(120, "Introduction to Algorithms", "Cormen et al.", 2009, copies=1),
        Book(220, "Algorithms Unlocked", "Cormen", 2013, copies=2),
        Book(180, "Data Structures and Algorithms in Python", "Goodrich", 2013, copies=2),
    ]
    for b in seed:
        catalog.add_book(b)

def cli_loop():
    catalog = LibraryCatalog()
    demo_seed(catalog)
    print("Library Catalog (RBTree-based) — demo seed loaded.")
    MENU = """
Choose an option:
1. Add / Update book
2. Delete book by ID
3. Search book by ID
4. Search book by title (exact)
5. Search book by title prefix
6. List all books (by ID)
7. List all books (by Title)
8. Save catalog to JSON
9. Load catalog from JSON
0. Exit
"""
    while True:
        print(MENU)
        choice = input("Enter choice: ").strip()
        if choice == "1":
            try:
                bid = int(input("Book ID (integer): ").strip())
                title = input("Title: ").strip()
                author = input("Author: ").strip()
                year = int(input("Year: ").strip())
                copies = int(input("Copies: ").strip())
            except Exception as e:
                print("Invalid input:", e)
                continue
            b = Book(book_id=bid, title=title, author=author, year=year, copies=copies)
            status = catalog.add_book(b)
            print(f"Book {status}.")
        elif choice == "2":
            try:
                bid = int(input("Book ID to delete: ").strip())
            except:
                print("Invalid ID.")
                continue
            ok = catalog.delete_by_id(bid)
            print("Deleted." if ok else "Book not found.")
        elif choice == "3":
            try:
                bid = int(input("Book ID to search: ").strip())
            except:
                print("Invalid ID.")
                continue
            b = catalog.search_by_id(bid)
            if b:
                print_book(b)
            else:
                print("Not found.")
        elif choice == "4":
            title = input("Title (exact, case-insensitive): ").strip()
            res = catalog.search_by_title_exact(title)
            if res:
                print(f"Found {len(res)} match(es):")
                for book in res:
                    print_book(book)
            else:
                print("No matches.")
        elif choice == "5":
            pref = input("Title prefix (case-insensitive): ").strip()
            res = catalog.search_by_title_prefix(pref)
            if res:
                print(f"Found {len(res)} match(es):")
                for book in res:
                    print_book(book)
            else:
                print("No matches.")
        elif choice == "6":
            arr = catalog.list_all_by_id()
            print(f"Total: {len(arr)} books (by ID):")
            for b in arr:
                print_book(b)
        elif choice == "7":
            arr = catalog.list_all_by_title()
            print(f"Total: {len(arr)} books (by Title):")
            for b in arr:
                print_book(b)
        elif choice == "8":
            fn = input("Filename to save (e.g. sample_books.json): ").strip()
            if not fn:
                fn = "sample_books.json"
            catalog.save_to_file(fn)
            print("Saved.")
        elif choice == "9":
            fn = input("Filename to load (e.g. sample_books.json): ").strip()
            if not fn:
                print("sample_books.json")
            try:
                catalog.load_from_file(fn)
                print("Loaded.")
            except Exception as e:
                print("Error loading:", e)
        elif choice == "0":
            print("Bye.")
            break
        else:
            print("Unknown option.")

# ---------------------
# If run as script
# ---------------------
if __name__ == "__main__":
    try:
        cli_loop()
    except KeyboardInterrupt:
        print("\nInterrupted. Exiting.")
