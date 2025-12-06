from flask import Flask, render_template, request, redirect, url_for, flash, send_file
import io
import json
import os
from library_catalog import LibraryCatalog, Book, demo_seed

app = Flask(__name__)
app.secret_key = "replace_this_with_a_random_secret"  # change for production

# Global catalog instance (keeps state while server runs)
catalog = LibraryCatalog()
demo_seed(catalog)  # optional: load initial demo data

# Home
@app.route("/")
def index():
    stats = {
        "by_id_count": catalog.by_id.size(),
        "by_title_count": catalog.by_title.size()
    }
    return render_template("index.html", stats=stats)

# Add / Update book
@app.route("/add", methods=["GET", "POST"])
def add_book():
    if request.method == "POST":
        try:
            book_id = int(request.form["book_id"])
            title = request.form["title"].strip()
            author = request.form.get("author", "").strip()
            year = int(request.form.get("year", 0))
            copies = int(request.form.get("copies", 1))
            book = Book(book_id=book_id, title=title, author=author, year=year, copies=copies)
            status = catalog.add_book(book)
            flash(f"Book {status}: ID {book_id} — {title}", "success")
            return redirect(url_for("index"))
        except Exception as e:
            flash(f"Invalid input: {e}", "danger")
            return redirect(url_for("add_book"))
    return render_template("add_book.html")

# Search
@app.route("/search", methods=["GET", "POST"])
def search():
    results = []
    query_type = None
    if request.method == "POST":
        qtype = request.form.get("type")
        query_type = qtype
        if qtype == "id":
            try:
                bid = int(request.form.get("book_id"))
                b = catalog.search_by_id(bid)
                if b:
                    results = [b]
                    flash(f"Found book with ID {bid}", "success")
                else:
                    flash("No book found with that ID.", "warning")
            except Exception as e:
                flash("Invalid ID.", "danger")
        elif qtype == "title_exact":
            title = request.form.get("title", "").strip()
            results = catalog.search_by_title_exact(title)
            if results:
                flash(f"Found {len(results)} match(es) for exact title '{title}'", "success")
            else:
                flash("No exact title matches.", "warning")
        elif qtype == "title_prefix":
            prefix = request.form.get("prefix", "").strip()
            results = catalog.search_by_title_prefix(prefix)
            if results:
                flash(f"Found {len(results)} match(es) for prefix '{prefix}'", "success")
            else:
                flash("No prefix matches.", "warning")
    return render_template("search.html", results=results, query_type=query_type)

# Delete
@app.route("/delete", methods=["GET", "POST"])
def delete():
    if request.method == "POST":
        try:
            bid = int(request.form.get("book_id"))
            ok = catalog.delete_by_id(bid)
            if ok:
                flash(f"Deleted book with ID {bid}.", "success")
            else:
                flash("Book ID not found.", "warning")
        except Exception as e:
            flash("Invalid ID.", "danger")
        return redirect(url_for("index"))
    return render_template("delete.html")

# List all (choose order by query param)
@app.route("/list")
def list_books():
    order = request.args.get("order", "id")
    if order == "title":
        books = catalog.list_all_by_title()
    else:
        books = catalog.list_all_by_id()
    return render_template("list_books.html", books=books, order=order)

# Save catalog -> prompt download JSON
@app.route("/export")
def export_catalog():
    data = [b.to_dict() for b in catalog.list_all_by_id()]
    buffer = io.BytesIO()
    buffer.write(json.dumps(data, indent=2).encode("utf-8"))
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name="catalog.json", mimetype="application/json")

# Upload JSON to load catalog
@app.route("/import", methods=["POST"])
def import_catalog():
    if "file" not in request.files:
        flash("No file part", "danger")
        return redirect(url_for("index"))
    f = request.files["file"]
    if f.filename == "":
        flash("No selected file", "danger")
        return redirect(url_for("index"))
    try:
        data = json.load(f)
        # rebuild catalog
        catalog.by_id = catalog.by_id.__class__()     # new RBTree
        catalog.by_title = catalog.by_title.__class__()
        for d in data:
            book = Book.from_dict(d)
            catalog.add_book(book)
        flash("Catalog loaded from uploaded file.", "success")
    except Exception as e:
        flash(f"Failed to load file: {e}", "danger")
    return redirect(url_for("index"))

# Clear catalog (dangerous, for testing)
@app.route("/clear", methods=["POST"])
def clear_catalog():
    catalog.by_id = catalog.by_id.__class__()
    catalog.by_title = catalog.by_title.__class__()
    flash("Catalog cleared.", "info")
    return redirect(url_for("index"))

if __name__ == "__main__":
    # When developing locally, use debug=True. For production, set debug=False.
    app.run(debug=True, host="127.0.0.1", port=5000)
