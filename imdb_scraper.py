
import pandas as pd
import webbrowser
import os
import html

print("Loading IMDb datasets...")

# Load movie information
movie_chunks = []

for chunk in pd.read_csv(
    "title.basics.tsv.gz",
    sep="\t",
    usecols=[
        "tconst",
        "titleType",
        "primaryTitle",
        "startYear",
        "genres"
    ],
    na_values="\\N",
    dtype=str,
    chunksize=100000
):
    movie_chunks.append(
        chunk[chunk["titleType"] == "movie"]
    )

movies = pd.concat(movie_chunks, ignore_index=True)

print("Movies loaded successfully!")

# Load ratings
ratings = pd.read_csv(
    "title.ratings.tsv.gz",
    sep="\t",
    usecols=["tconst", "averageRating", "numVotes"]
)

# Merge datasets
result = pd.merge(movies, ratings, on="tconst")

result["averageRating"] = pd.to_numeric(
    result["averageRating"], errors="coerce"
)

result["numVotes"] = pd.to_numeric(
    result["numVotes"], errors="coerce"
)

result = result.dropna(
    subset=["averageRating", "numVotes"]
)

# Select movies with minimum votes
result = result[result["numVotes"] >= 1000]

# Display 100 movies
result = result.sort_values(
    by="averageRating",
    ascending=False
).head(100).copy()

print("Creating IMDb movie website...")

# Create clickable IMDb links
result["IMDb Page"] = result["tconst"].apply(
    lambda x: f'<a href="https://www.imdb.com/title/{x}/" target="_blank">View on IMDb</a>'
)

# Save CSV without HTML links
result.drop(columns=["IMDb Page"]).to_csv(
    "imdb_movie_ratings.csv",
    index=False
)

# Create HTML table
table = result[
    [
        "primaryTitle",
        "startYear",
        "genres",
        "averageRating",
        "numVotes",
        "IMDb Page"
    ]
].to_html(index=False, escape=False)

# Website design
page = f"""
<!DOCTYPE html>
<html>
<head>
<title>IMDb Movie Rating Analyzer</title>

<style>
body {{
    background: #141414;
    color: white;
    font-family: Arial;
    padding: 25px;
}}

h1 {{
    background: #f5c518;
    color: black;
    padding: 20px;
    text-align: center;
}}

input {{
    width: 90%;
    padding: 14px;
    margin: 20px 0;
    border-radius: 8px;
    font-size: 16px;
}}

table {{
    width: 100%;
    border-collapse: collapse;
    background: white;
    color: black;
}}

th {{
    background: #f5c518;
    padding: 13px;
}}

td {{
    padding: 12px;
    text-align: center;
    border: 1px solid #ddd;
}}

tr:nth-child(even) {{
    background: #eeeeee;
}}

a {{
    color: #0066cc;
    font-weight: bold;
}}

</style>
</head>

<body>

<h1>IMDb Movie Rating Analyzer</h1>

<h2>Top 100 Movies</h2>

<input type="text" id="search"
placeholder="Search your favourite movie..."
onkeyup="searchMovie()">

{table}

<script>
function searchMovie() {{
    let input = document.getElementById("search");
    let filter = input.value.toLowerCase();
    let rows = document.querySelectorAll("table tr");

    for (let i = 1; i < rows.length; i++) {{
        let text = rows[i].innerText.toLowerCase();
        rows[i].style.display =
            text.includes(filter) ? "" : "none";
    }}
}}
</script>

</body>
</html>
"""

# Save website
with open("imdb_results.html", "w", encoding="utf-8") as file:
    file.write(page)

print("Opening official IMDb website...")

# Open official IMDb homepage
webbrowser.open_new_tab("https://www.imdb.com/")

# Open our project website
webbrowser.open_new_tab(
    "file:///" + os.path.abspath("imdb_results.html").replace("\\", "/")
)

print("100 movies displayed successfully!")
print("Project completed!")
