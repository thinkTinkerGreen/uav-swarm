def build_split_html():
    html = """<!DOCTYPE html>
<html>
<head>
    <title>Swarm Dual Demo</title>
    <style>
        body { margin: 0; padding: 0; display: flex; height: 100vh; overflow: hidden; background: #000; }
        iframe { flex: 1; border: none; }
        .divider { width: 4px; background: #333; cursor: col-resize; z-index: 10; }
    </style>
</head>
<body>
    <iframe src="flight_viewer_2d.html"></iframe>
    <div class="divider"></div>
    <iframe src="flight_viewer.html"></iframe>
</body>
</html>
"""
    with open("split_demo.html", "w") as f:
        f.write(html)
    print("Successfully built split_demo.html!")

if __name__ == "__main__":
    build_split_html()
