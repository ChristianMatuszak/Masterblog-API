from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # This will enable CORS for all routes

POSTS = [
    {"id": 1, "title": "First post", "content": "This is the first post."},
    {"id": 2, "title": "Second post", "content": "This is the second post."},
]


@app.route("/api/posts", methods=["GET"])
def get_posts():
    """
    Retrieves the list of blog posts, optionally sorted by title or content.

    Query Parameters:
        sort (str, optional): Field to sort by. Accepts 'title' or 'content'.
        direction (str, optional): Sort order. Accepts 'asc' (ascending) or 'desc' (descending).

    Returns:
        Response: JSON list of posts, sorted if parameters are valid.
        HTTP 200: On success.
        HTTP 400: If invalid sort or direction parameters are provided.
    """
    sort_by = request.args.get("sort")
    direction = request.args.get("direction")

    if sort_by and sort_by not in ["title", "content"]:
        return jsonify({"error": "Invalid sort. Use 'title' or 'content'."}), 400

    if direction and direction not in ["asc", "desc"]:
        return jsonify({"error": "Invalid direction. Use 'asc' or 'desc'."}), 400

    sorted_posts = POSTS.copy()
    if sort_by:
        reverse = direction == "desc"
        sorted_posts.sort(key=lambda x: x[sort_by].lower(), reverse=reverse)

    return jsonify(sorted_posts), 200


@app.route("/api/posts", methods=["POST"])
def add():
    """
    Creates a new blog post with a title and content.

    JSON Body:
        {
            "title": "Post Title",
            "content": "Post Content"
        }

    Returns:
        Response: The newly created post as a JSON object.
        HTTP 201: On successful creation.
        HTTP 400: If title or content is missing or empty, or if the body is not valid JSON.
    """
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
    """
    Deletes a blog post by its ID.

    Path Parameters:
        post_id (int): The ID of the post to delete.

    Returns:
        Response: A message confirming deletion.
        HTTP 200: On successful deletion.
        HTTP 404: If the post with the given ID does not exist.
    """
    post_delete = next((post for post in POSTS if post["id"] == post_id),None)

    if not post_delete:
        return jsonify({"error": f"Post with id {post_id} not found"}), 404

    POSTS.remove(post_delete)
    return jsonify({"message": f"Post {post_id} deleted"}), 200


@app.route("/api/posts/<int:post_id>", methods=["PUT"])
def update(post_id):
    """
    Updates the title and/or content of an existing blog post.

    Path Parameters:
        post_id (int): The ID of the post to update.

    JSON Body:
        {
            "title": "Updated Title (optional)",
            "content": "Updated Content (optional)"
        }

    Returns:
        Response: The updated post as a JSON object.
        HTTP 200: On successful update.
        HTTP 400: If provided title or content is empty.
        HTTP 404: If the post with the given ID does not exist.
    """
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
    """
    Searches for blog posts by title and/or content keywords.

    Query Parameters:
        title (str, optional): Substring to search for in the title.
        content (str, optional): Substring to search for in the content.

    Returns:
        Response: A list of posts matching the search criteria.
        HTTP 200: Always returns 200, even if the result list is empty.
    """
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
    """
    Calculates the next unique ID for a new blog post.

    Returns:
        int: The next available post ID. Starts from 1 if no posts exist.
    """
    if POSTS:
        return POSTS[-1]["id"] + 1
    return 1

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002, debug=True)
