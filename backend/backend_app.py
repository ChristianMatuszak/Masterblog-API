from flask import Flask, jsonify, request, redirect
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # This will enable CORS for all routes

POSTS = [
    {"id": 1, "title": "First post", "content": "This is the first post."},
    {"id": 2, "title": "Second post", "content": "This is the second post."},
]


@app.route('/api/posts', methods=['GET'])
def get_posts():
    return jsonify(POSTS)


@app.route("/api/posts", methods=["POST"])
def add():
    posts = request.get_json()

    if not posts:
        return jsonify({"error": "Missing JSON body"}), 400

    title = posts.get("title", "").strip()
    content = posts.get("content", "").strip()

    missing = []
    if not title:
        missing.append("title")
    if not content:
        missing.append("content")

    if missing:
        return jsonify({"error": f"Missing or empty fields: {', '.join(missing)}"}), 400

    new_post = {
        "id": get_next_id(),
        "title": title,
        "content": content
    }

    POSTS.append(new_post)
    return jsonify(new_post), 201


@app.route("/api/posts/<int:post_id>", methods=["DELETE"])
def delete(post_id):
    post_delete = next((post for post in POSTS if post["id"] == post_id),None)

    if not post_delete:
        return jsonify({"error": f"Post with id {post_id} not found"}), 404

    POSTS.remove(post_delete)
    return jsonify({"message": f"Post {post_id} deleted"}), 200


@app.route("/api/posts/<int:post_id>", methods=["PUT"])
def update(post_id):

    posts = request.get_json()

    post = next((post for post in POSTS if post["id"] == post_id), None)
    if not post:
        return jsonify({"error": f"Post with id {post_id} not found"}), 404

    title = posts.get("title")
    content = posts.get("content",)

    if title is not None and not title.strip():
        return jsonify({"error": "Title cannot be empty"}), 400
    if content is not None and not content.strip():
        return jsonify({"error": "Content cannot be empty"}), 400

    if title is not None:
        if title.strip():
            post["title"] = title.strip()
    if content is not None:
        if content.strip():
            post["content"] = content.strip()

    return jsonify(post), 200


@app.route("/api/posts/search", methods=["GET"])
def search():
    title_query = request.args.get("title", "").lower()
    content_query = request.args.get("content", "").lower()

    results = []

    for post in POSTS:
        title_match = title_query in post["title"].lower() if title_query else True
        content_match = content_query in post["content"].lower() if content_query else True

        if title_match and content_match:
            results.append(post)

    return jsonify(results), 200

def get_next_id():
    if POSTS:
        return POSTS[-1]["id"] + 1
    return 1

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002, debug=True)
