# 📚 Library Catalog System (using Red-Black Tree)

A modern, web-based Library Management System built using **Red-Black Tree (RBT)** for fast searching, insertion, and deletion of books.  
This project features a clean Flask web interface with Bootstrap UI, dynamic catalog operations, JSON import/export, and efficient backend indexing.

Designed as part of an **Advanced Data Structures Mini Project (M.Tech)** — but built like a real-world application.

---

## 📁 Project Structure

```
LibraryRBTree/
│
├── library_catalog.py                   # Core project: RBT implementation + Flask routes
├── requirements.txt                     # Python dependencies
│
├── templates/                           # Frontend HTML (Flask Jinja templates)
│ ├── layout.html
│ ├── index.html
│ ├── add_book.html
│ ├── search.html
│ ├── delete.html
│ └── list_books.html
│
├── static/
│ └── styles.css                         # Modern UI styling (Bootstrap + custom)
│
└── README.md 
```

---

## 🧠 **Features**

- 🌲 **Red-Black Tree (RBT) data structure** for super-fast insert, search, and delete  
- 🔎 Search by:
  - Book ID  
  - Exact Title  
  - Title Prefix  
- ➕ Add / Update books  
- 🗑 Delete books  
- 📋 View full book catalog (sorted)  
- 📁 JSON import/export to save & restore catalog  
- 🖥 **Modern Flask Web UI** with Bootstrap  
- 📱 Fully responsive UI  
- ⚡ Real-time dynamic interactions  

---

## 🚀 Getting Started

### 1️⃣ Clone the Repository

git clone https://github.com/yourusername/Library-Catalog-System-using-RedBlackTree.git
cd LibraryRBTree

### 2️⃣ Install Dependencies
```
pip install -r requirements.txt
```
### 3️⃣ Run the Application
```
python library_catalog.py
```
Open your browser and visit:

http://127.0.0.1:5000/

---

## 🌐 Web Interface Pages

- Home Dashboard – statistics + quick actions
- Add Book – insert or update book entries
- Search Book – by ID, exact title, or prefix
- Delete Book – remove by ID
- List Books – full, sorted catalog display
- Import/Export – load/save your entire RBT catalog in JSON format

---

## 🧪 Requirements

- Python 3.8+
- Flask
- Bootstrap (via CDN)
- Basic knowledge of RBT (optional but helpful)

---

## 📌 Notes

- The system maintains two separate RBTs:
- One indexed by Book ID
- One indexed by Title
- All data is in-memory; use Export Catalog to save your work
- Import supports .json files only

---

## 📄 License

This project is licensed under the MIT License — free to use, modify, and distribute with attribution.

---

## 🙌 Acknowledgements

- Flask — for backend web framework
- Bootstrap — UI styling
- Red-Black Tree — core data structure
- Python — powering the entire application

---

> Built with ❤️ using **Python, Flask, Bootstrap and Advanced Data Structures**
