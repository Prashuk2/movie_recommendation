from flask import Flask, request, render_template
import pickle
import requests

app = Flask(__name__)

# Load your saved dataset and similarity matrix
with open("movie_data.pkl", "rb") as f:
    df = pickle.load(f)

with open("similarity_matrix.pkl", "rb") as f:
    similarity = pickle.load(f)

# TMDB API details
TMDB_API_KEY = "158da0f869c4549c3cf52a4efe1d2b52"
TMDB_IMAGE_BASE_URL = "https://image.tmdb.org/t/p/w500"  # poster size

def get_poster_url(movie_title):
    search_url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={movie_title}"
    response = requests.get(search_url)
    data = response.json()
    if data['results']:
        poster_path = data['results'][0].get('poster_path')
        if poster_path:
            return TMDB_IMAGE_BASE_URL + poster_path
    return None

def recommend(movie_title, n=5):
    movie_title_lower = movie_title.lower()
    # Check if movie exists
    if movie_title_lower not in df['title'].str.lower().values:
        return []
    idx = df[df['title'].str.lower() == movie_title_lower].index[0]
    sim_scores = list(enumerate(similarity[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)[1:n+1]

    recommended_movies = []
    for i, score in sim_scores:
        title = df.iloc[i]['title']
        poster = get_poster_url(title)
        recommended_movies.append({'title': title, 'poster': poster})
    return recommended_movies

@app.route('/', methods=['GET', 'POST'])
def home():
    recommended_movies = []
    movie = ""
    if request.method == 'POST':
        movie = request.form.get('movie')
        recommended_movies = recommend(movie, n=10)
    return render_template('index.html', recommended_movies=recommended_movies, movie=movie)

if __name__ == '__main__':
    app.run(debug=True)
