import pickle
import streamlit as st
import requests
import os

# -------------------- Google Drive Download Helpers --------------------
def download_file_from_google_drive(file_id, destination):
    URL = "https://drive.google.com/uc?export=download"
    session = requests.Session()

    response = session.get(URL, params={'id': file_id}, stream=True)
    token = get_confirm_token(response)

    if token:
        params = {'id': file_id, 'confirm': token}
        response = session.get(URL, params=params, stream=True)

    save_response_content(response, destination)

def get_confirm_token(response):
    for key, value in response.cookies.items():
        if key.startswith('download_warning'):
            return value
    return None

def save_response_content(response, destination):
    CHUNK_SIZE = 32768
    with open(destination, "wb") as f:
        for chunk in response.iter_content(CHUNK_SIZE):
            if chunk:
                f.write(chunk)

# -------------------- Google Drive File IDs --------------------
MOVIELIST_FILE_ID = '1a6zGa64w7L6mcT0eFL9lHp2vJz9Mo4j5'
SIMILARITY_FILE_ID = '1vIyvZOPqDQyELKJhtV1NiLLIFHHeyg6Y'

# -------------------- Download .pkl Files If Not Present --------------------
if not os.path.exists("movie_list.pkl"):
    download_file_from_google_drive(MOVIELIST_FILE_ID, "movie_list.pkl")

if not os.path.exists("similarity.pkl"):
    download_file_from_google_drive(SIMILARITY_FILE_ID, "similarity.pkl")

# -------------------- Load Data --------------------
movies = pickle.load(open('movie_list.pkl', 'rb'))
similarity = pickle.load(open('similarity.pkl', 'rb'))

# -------------------- Fetch Movie Poster --------------------
def fetch_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US"
    try:
        data = requests.get(url).json()
        poster_path = data.get('poster_path', None)
        if not poster_path:
            return "https://via.placeholder.com/500x750?text=No+Image"
        return "https://image.tmdb.org/t/p/w500/" + poster_path
    except:
        return "https://via.placeholder.com/500x750?text=No+Image"

# -------------------- Recommendation Logic --------------------
def recommend(movie):
    index = movies[movies['title'] == movie].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    recommended_movie_names = []
    recommended_movie_posters = []

    for i in distances[1:6]:
        movie_id = movies.iloc[i[0]].movie_id
        recommended_movie_names.append(movies.iloc[i[0]].title)
        recommended_movie_posters.append(fetch_poster(movie_id))

    return recommended_movie_names, recommended_movie_posters

# -------------------- Streamlit UI --------------------
st.set_page_config(page_title="🎥 Movie Recommender", layout="wide")
st.title('🎬 Movie Recommender System')

movie_list = movies['title'].values
selected_movie = st.selectbox("🎞️ Choose a movie", movie_list)

if st.button('🎯 Show Recommendation'):
    recommended_movie_names, recommended_movie_posters = recommend(selected_movie)
    cols = st.columns(5)
    for i in range(5):
        with cols[i]:
            st.image(recommended_movie_posters[i])
            st.caption(recommended_movie_names[i])
