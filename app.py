import pickle
import streamlit as st
import requests
import os
import gdown

# Google Drive File IDs
MOVIELIST_FILE_ID = '1a6zGa64w7L6mcT0eFL9lHp2vJz9Mo4j5'
SIMILARITY_FILE_ID = '1vIyvZOPqDQyELKJhtV1NiLLIFHHeyg6Y'

# Download files from Google Drive if not present
def download_from_gdrive(file_id, output):
    if not os.path.exists(output):
        gdown.download(f"https://drive.google.com/uc?id={file_id}", output, quiet=False)

download_from_gdrive(MOVIELIST_FILE_ID, "movie_list.pkl")
download_from_gdrive(SIMILARITY_FILE_ID, "similarity.pkl")

# Load data
movies = pickle.load(open('movie_list.pkl', 'rb'))
similarity = pickle.load(open('similarity.pkl', 'rb'))

def fetch_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US"
    data = requests.get(url).json()
    poster_path = data.get('poster_path', "")
    if not poster_path:
        return "https://via.placeholder.com/500x750?text=No+Image"
    return "https://image.tmdb.org/t/p/w500/" + poster_path

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

# Streamlit App UI
st.header('🎬 Movie Recommender System')
movie_list = movies['title'].values
selected_movie = st.selectbox("Type or select a movie from the dropdown", movie_list)

if st.button('Show Recommendation'):
    recommended_movie_names, recommended_movie_posters = recommend(selected_movie)
    cols = st.columns(5)
    for i in range(5):
        with cols[i]:
            st.text(recommended_movie_names[i])
            st.image(recommended_movie_posters[i])
