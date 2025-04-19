import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime
import time
import requests
import plotly.express as px
import plotly.graph_objects as go
from streamlit_lottie import st_lottie

# Set up the page configuration
st.set_page_config(
    page_title="Personal Library Manager",
    page_icon="🔮📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Function to load Lottie JSON animations
def load_lottieurl(url):
    try:
        r = requests.get(url)
        if r.status_code != 200:
            return None
        return r.json()
    except:
        return None

# Initialize session state variables
if 'library' not in st.session_state:
    st.session_state.library = []
if 'search_results' not in st.session_state:
    st.session_state.search_results = []
if 'book_added' not in st.session_state:
    st.session_state.book_added = False
if 'book_removed' not in st.session_state:
    st.session_state.book_removed = False
if 'current_view' not in st.session_state:
    st.session_state.current_view = "library"

# Load the library from a JSON file
def load_library():
    try:
        if os.path.exists('library.json'):
            with open('library.json', 'r') as file:
                st.session_state.library = json.load(file)
            return True
        return False
    except Exception as e:
        st.error(f'Error loading: {e}')
        return False

# Save the library to a JSON file
def save_library():
    try:
        with open('library.json', 'w') as file:
            json.dump(st.session_state.library, file)
        return True
    except Exception as e:
        st.error(f"Error saving library: {e}")
        return False

# Function to add a new book
def add_book(title, author, publication_year, genre, read_bool):
    book = {
        "title": title,
        "author": author,
        "publication_year": publication_year,
        "genre": genre,
        "read_status": read_bool
    }
    st.session_state.library.append(book)
    save_library()
    st.session_state.book_added = True
    st.success(f"Book '{title}' added successfully!")

# Function to get library statistics
def get_library_stats():
    total_books = len(st.session_state.library)
    read_books = sum(1 for book in st.session_state.library if book['read_status'])
    percent_read = (read_books / total_books * 100) if total_books > 0 else 0

    genres = {}
    authors = {}
    decades = {}

    for book in st.session_state.library:
        genres[book['genre']] = genres.get(book['genre'], 0) + 1
        authors[book['author']] = authors.get(book['author'], 0) + 1
        decade = (book['publication_year'] // 10) * 10
        decades[decade] = decades.get(decade, 0) + 1

    genres = dict(sorted(genres.items(), key=lambda x: x[1], reverse=True))
    authors = dict(sorted(authors.items(), key=lambda x: x[1], reverse=True))
    decades = dict(sorted(decades.items(), key=lambda x: x[0]))

    return {
        'total_books': total_books,
        'read_books': read_books,
        'percent_read': percent_read,
        'genres': genres,
        'authors': authors,
        'decades': decades,
    }

# Function to create visualizations for library statistics
def create_visualization(stats):
    if stats['total_books'] > 0:
        fig_read_status = go.Figure(data=[go.Pie(
            labels=['Read', 'Unread'],
            values=[stats['read_books'], stats['total_books'] - stats['read_books']],
            hole=.4,
            marker=dict(colors=['#4CAF50', '#FB7171'])
        )])
        fig_read_status.update_layout(
            title_text='Read vs Unread Books',
            showlegend=True,
            height=400,
            template="plotly_dark"
        )
        st.plotly_chart(fig_read_status, use_container_width=True)

    if stats['genres']:
        genres_df = pd.DataFrame({
            'Genre': list(stats['genres'].keys()),
            'Count': list(stats['genres'].values())
        })
        fig_genres = px.bar(
            genres_df,
            x='Genre',
            y='Count',
            color='Count',
            color_continuous_scale=px.colors.sequential.Blues
        )
        fig_genres.update_layout(
            title_text='Books by Genre',
            xaxis_title='Genres',
            yaxis_title='Number of Books',
            height=400,
            template="plotly_dark"
        )
        st.plotly_chart(fig_genres, use_container_width=True)

    if stats['decades']:
        decades_df = pd.DataFrame({
            'Decade': [f"{decade}s" for decade in stats['decades'].keys()],
            'Count': list(stats['decades'].values())
        })
        fig_decades = px.line(
            decades_df,
            x='Decade',
            y='Count',
            markers=True,
            line_shape="spline"
        )
        fig_decades.update_layout(
            title_text='Books by Publication Decade',
            xaxis_title='Decade',
            yaxis_title='Number of Books',
            height=400,
            template="plotly_dark"
        )
        st.plotly_chart(fig_decades, use_container_width=True)

load_library()

# Sidebar Design with Animation
st.sidebar.markdown("<h1 style='text-align: center; color: #6C4D92;'>Library Navigation</h1>", unsafe_allow_html=True)  # Lighter color

lottie_book = load_lottieurl("https://assets10.lottiefiles.com/packages/lf20_bet3v4ks.json")
if lottie_book:
    with st.sidebar:
        st_lottie(lottie_book, height=200, key='book_animation')
else:
    st.sidebar.info("📚 Welcome to the Library!")

# Sidebar Navigation Options with improved layout
nav_option = st.sidebar.radio(
    "Choose an option:",
    ["View Library", "Add Book", "Search Books", "Library Statistics"]
)

if nav_option == "View Library":
    st.session_state.current_view = 'library'
elif nav_option == "Add Book":
    st.session_state.current_view = "add"
elif nav_option == "Search Books":
    st.session_state.current_view = "search"
elif nav_option == "Library Statistics":
    st.session_state.current_view = "stats"

# Main header with new styling
st.markdown("<h1 style='text-align: center; color: #6C4D92;'>The Book Corner</h1>", unsafe_allow_html=True)  # Lighter color

# View for Adding Book
if st.session_state.current_view == "add":
    st.markdown("<h2 style='text-align: center; color: #4A90E2;'>Add a New Book</h2>", unsafe_allow_html=True)

    with st.form(key='add_book_form'):
        col1, col2 = st.columns(2)

        with col1:
            title = st.text_input("Book Title", max_chars=100)
            author = st.text_input("Author",  max_chars=100)
            publication_year = st.number_input("Publication Year", min_value=1000, max_value=datetime.now().year, step=1, value=2024)

        with col2:
            genre = st.select_slider("Genre", [
                "Fiction", "Non-Fiction", "Science", "Technology", "Romance", "Poetry", "Self-Help", "Art", "Religion", "History", "Others"
            ])
            read_status = st.selectbox("Read Status", ["Read", "Unread"])
            read_bool = read_status == "Read"

        submit_button = st.form_submit_button(label="Add Book")

        if submit_button and title and author:
            add_book(title, author, publication_year, genre, read_bool)

# Display library statistics
if st.session_state.current_view == "stats":
    stats = get_library_stats()
    create_visualization(stats)

# View for Displaying Library
if st.session_state.current_view == "library":
    st.markdown("<h2 style='text-align: center; color: #4A90E2;'>Your Library Collection</h2>", unsafe_allow_html=True)

    if st.session_state.library:
        df = pd.DataFrame(st.session_state.library)
        df['read_status'] = df['read_status'].apply(lambda x: 'Read' if x else 'Unread')
        st.dataframe(df.style.set_properties(**{
            'background-color': '#F1F1F1',  # Lighter background
            'color': '#6C4D92',  # Lighter text color
            'border-color': '#4A90E2'
        }), use_container_width=True)
    else:
        st.info("No books added yet. Start by adding a new book from the sidebar! 📚")
