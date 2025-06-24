from flask import Flask, request, jsonify
import math
import json # Import json to handle data parsing from URL

# Re-embedding the is_point_in_polygon function to make the API self-contained
def is_point_in_polygon(point, polygon):
    """
    Determines if a point is inside a polygon using the ray casting algorithm.

    Args:
        point (tuple): A tuple (x, y) representing the coordinates of the test point.
        polygon (list): A list of tuples, where each tuple (x, y) represents a vertex
                        of the polygon in order (either clockwise or counter-clockwise).
                        The polygon must be closed (the last vertex connects to the first).

    Returns:
        bool: True if the point is inside or on the boundary of the polygon, False otherwise.
    """
    x, y = point
    n = len(polygon)
    inside = False

    if n < 3:
        return False

    p1x, p1y = polygon[0]
    for i in range(n):
        p2x, p2y = polygon[(i + 1) % n]

        # Check if the point is on a vertex
        if (x, y) == (p1x, p1y) or (x, y) == (p2x, p2y):
            return True

        # Check for intersection with the ray extending right from the point
        if ((p1y <= y < p2y) or (p2y <= y < p1y)):
            if (p2y - p1y) == 0: # Horizontal edge
                if y == p1y and min(p1x, p2x) <= x <= max(p1x, p2x):
                    return True
                pass
            else:
                intersect_x = p1x + (y - p1y) * (p2x - p1x) / (p2y - p1y)
                if intersect_x > x:
                    inside = not inside
                elif intersect_x == x: # Point is on a vertical edge or exactly on intersection
                    return True

        p1x, p1y = p2x, p2y

    return inside

# Initialize the Flask app
app = Flask(__name__)

# Define the API endpoint
@app.route('/is_inside_polygon', methods=['GET']) # Changed to GET method
def check_point_in_polygon():
    """
    API endpoint to check if a given point is inside a polygon.
    Expects 'point' and 'polygon' as URL query parameters.

    Example URL:
    /is_inside_polygon?point=[2,2]&polygon=[[0,0],[5,0],[5,5],[0,5]]
    """
    try:
        # For GET requests, parameters are in request.args (query string)
        point_str = request.args.get('point')
        polygon_str = request.args.get('polygon')

        # Input validation for presence of parameters
        if not all([point_str, polygon_str]):
            return jsonify({"error": "Missing 'point' or 'polygon' query parameters"}), 400

        try:
            # Parse the string representations of point and polygon into Python objects
            point = json.loads(point_str)
            polygon = json.loads(polygon_str)
        except json.JSONDecodeError:
            return jsonify({"error": "Invalid JSON format for 'point' or 'polygon'"}), 400

        # Input validation for types and structure (same as your POST method)
        if not isinstance(point, list) or len(point) != 2:
            return jsonify({"error": "'point' must be a list of two numbers [x, y]"}), 400

        if not isinstance(polygon, list) or len(polygon) < 3:
            return jsonify({"error": "'polygon' must be a list of at least 3 [x, y] vertices"}), 400

        for vertex in polygon:
            if not isinstance(vertex, list) or len(vertex) != 2:
                return jsonify({"error": "Each vertex in 'polygon' must be a list of two numbers [x, y]"}), 400

        # Convert point and polygon elements to tuples for the function
        point_tuple = tuple(point)
        polygon_list_of_tuples = [tuple(v) for v in polygon]

        # Call the ray casting function
        result = is_point_in_polygon(point_tuple, polygon_list_of_tuples)

        return jsonify({"is_inside": result}), 200

    except Exception as e:
        # Catch any unexpected errors
        return jsonify({"error": str(e)}), 500

# To run this Flask app locally for testing:
if __name__ == '__main__':
    app.run(debug=True, port=5000)
