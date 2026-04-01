import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import hashlib

GENRE_IMAGES = {
    'fiction': [
        'https://images.unsplash.com/photo-1474932430478-367dbb6832c1',
        'https://images.unsplash.com/photo-1519681393784-d120267933ba',
        'https://images.unsplash.com/photo-1456513080510-7bf3a84b82f8',
        'https://images.unsplash.com/photo-1476275466078-4007374efbbe',
        'https://images.unsplash.com/photo-1532012197267-da84d127e765'
    ],
    'science': [
        'https://images.unsplash.com/photo-1507413245164-6160d8298b31',
        'https://images.unsplash.com/photo-1532187863486-abf9d39d99c5',
        'https://images.unsplash.com/photo-1576086213369-97a306d36557'
    ],
    'history': [
        'https://images.unsplash.com/photo-1461360370896-922624d12aa1',
        'https://images.unsplash.com/photo-1505664194762-d63870747180',
        'https://images.unsplash.com/photo-1447069387593-a5de0862481e',
        'https://images.unsplash.com/photo-1531346878377-a5ec20888f23'
    ],
    'fantasy': [
        'https://images.unsplash.com/photo-1462331940025-496dfbfc7564',
        'https://images.unsplash.com/photo-1519681393784-d120267933ba',
        'https://images.unsplash.com/photo-1500462418834-7ea21102144e',
        'https://images.unsplash.com/photo-1534447677768-be436bb09401'
    ],
    'mystery': [
        'https://images.unsplash.com/photo-1509248961158-e54f6934749c',
        'https://images.unsplash.com/photo-1478720568477-152d9b164e26',
        'https://images.unsplash.com/photo-1505628346881-b72b27e84530'
    ],
    'romance': [
        'https://images.unsplash.com/photo-1518199266791-5375a83190b7',
        'https://images.unsplash.com/photo-1529156069972-7953256c6582',
        'https://images.unsplash.com/photo-1494774157365-9e04c6720e47'
    ],
    'biography': [
        'https://images.unsplash.com/photo-1508780709619-795624692641',
        'https://images.unsplash.com/photo-1544640808-32ca72ac7f67',
        'https://images.unsplash.com/photo-1455390582262-044cdead277a'
    ],
    'horror': [
        'https://images.unsplash.com/photo-1505628346881-b72b27e84530',
        'https://images.unsplash.com/photo-1509248961158-e54f6934749c'
    ],
    'childrens': [
        'https://images.unsplash.com/photo-1512820790803-83ca734da794',
        'https://images.unsplash.com/photo-1526723047558-a00d7682383c',
        'https://images.unsplash.com/photo-1481627834876-b7833e8f5570'
    ],
    'science-fiction': [
        'https://images.unsplash.com/photo-1451187580459-43490279c0fa',
        'https://images.unsplash.com/photo-1446776811953-b23d57bd21aa',
        'https://images.unsplash.com/photo-1506318137071-a8e063b4bcc0'
    ],
    'poetry': [
        'https://images.unsplash.com/photo-1473186505569-9c61870c11f9',
        'https://images.unsplash.com/photo-1471107340929-a87cd0f5b5f3',
        'https://images.unsplash.com/photo-1510626398611-c742710ca991'
    ],
    'art': [
        'https://images.unsplash.com/photo-1460661419201-fd4cecdf8a8b',
        'https://images.unsplash.com/photo-1513364776144-60967b0f800f',
        'https://images.unsplash.com/photo-1549490349-8643362247b5'
    ],
    'cookbooks': [
        'https://images.unsplash.com/photo-1556910103-1c02745aae4d',
        'https://images.unsplash.com/photo-1504674900247-0877df9cc836',
        'https://images.unsplash.com/photo-1495521821757-a1efb6729352'
    ],
    'religion': [
        'https://images.unsplash.com/photo-1507692049790-de58290a4334',
        'https://images.unsplash.com/photo-1544427928-c44caeb57594'
    ],
    'classic': [
        'https://images.unsplash.com/photo-1544640808-32ca72ac7f67',
        'https://images.unsplash.com/photo-1524995997946-a1c2e315a42f',
        'https://images.unsplash.com/photo-1512820790803-83ca734da794'
    ],
    'default': [
        'https://images.unsplash.com/photo-1544947950-fa07a98d237f',
        'https://images.unsplash.com/photo-1512820790803-83ca734da794',
        'https://images.unsplash.com/photo-1532012197267-da84d127e765',
        'https://images.unsplash.com/photo-1543005128-d39e50435763',
        'https://images.unsplash.com/photo-1497633762265-9d179a990aa6',
        'https://images.unsplash.com/photo-1456513080510-7bf3a84b82f8',
        'https://images.unsplash.com/photo-1516979187457-637abb4f9353'
    ]
}

class BookRecommender:
    def __init__(self, data_path='data/books.csv'):
        self.data_path = data_path
        self.df = None
        self.cosine_sim = None
        self.count_matrix = None
        self.tfidf_matrix = None
        self.load_data()

    def load_data(self):
        try:
            self.df = pd.read_csv(self.data_path)
            # Create a 'content' column to use for similarity: genre + description + author
            self.df['genre'] = self.df['genre'].fillna('')
            self.df['description'] = self.df['description'].fillna('')
            self.df['author'] = self.df['author'].fillna('')
            
            # CountVectorizer on metadata (genre + author)
            self.df['metadata'] = self.df['genre'] + " " + self.df['author']
            count_vec = CountVectorizer(stop_words='english')
            self.count_matrix = count_vec.fit_transform(self.df['metadata'])
            
            # TfidfVectorizer on text description
            tfidf_vec = TfidfVectorizer(stop_words='english')
            self.tfidf_matrix = tfidf_vec.fit_transform(self.df['description'])
            
            # Compute cosine similarity matrices
            sim_count = cosine_similarity(self.count_matrix, self.count_matrix)
            sim_tfidf = cosine_similarity(self.tfidf_matrix, self.tfidf_matrix)
            
            # Combine them (50/50 blend)
            self.cosine_sim = (sim_count + sim_tfidf) / 2.0
            
            # Update image URLs if they are placeholders
            self._apply_unique_images()
            
        except FileNotFoundError:
            print(f"Error: Could not find {self.data_path}. Ensure it exists.")
            self.df = pd.DataFrame()



    def get_all_books(self):
        if self.df.empty:
            return []
        
        # shuffle initially to show different books on home
        return self.df.sample(frac=1).to_dict(orient='records')

    def get_genres(self):
        if self.df.empty:
            return []
        return sorted(self.df['genre'].unique())

    def get_recommendations_by_genre(self, genre, top_n=6):
        if self.df.empty:
            return []
            
        genre_books = self.df[self.df['genre'].str.lower() == genre.lower()]
        
        if genre_books.empty:
            return self.get_top_rated(top_n)
            
        return genre_books.sort_values(by='rating', ascending=False).head(top_n).to_dict(orient='records')
        
    def get_top_rated(self, top_n=6):
        if self.df.empty:
            return []
        return self.df.sort_values(by='rating', ascending=False).head(top_n).to_dict(orient='records')

    def get_similar_books(self, book_title, top_n=6):
        """Recommends books similar to the given title, with fuzzy matching"""
        if self.df.empty:
            return []
            
        # 1. Try exact/contains match first for efficiency
        # We look for the most relevant match if multiple exist
        matches = self.df[self.df['title'].str.contains(book_title, case=False, na=False)]
        
        if not matches.empty:
            # If exact match exists, pick it. Otherwise pick the shortest match (usually the intended title)
            exact_match = matches[matches['title'].str.lower() == book_title.lower()]
            if not exact_match.empty:
                idx = exact_match.index[0]
            else:
                idx = matches['title'].str.len().idxmin()
        else:
            # Use fuzzy library-less approach (simple ratio or difflib)
            import difflib
            titles = self.df['title'].tolist()
            closest_matches = difflib.get_close_matches(book_title, titles, n=1, cutoff=0.3)
            
            if closest_matches:
                idx = self.df.index[self.df['title'] == closest_matches[0]][0]
            else:
                # If truly not found, return empty list
                return []
            
        # Get pairwise similarity scores
        sim_scores = list(enumerate(self.cosine_sim[idx]))
        
        # Sort books based on similarity scores
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
        
        # Get indices of most similar books (ignoring the book itself)
        sim_scores = sim_scores[1:top_n+1]
        book_indices = [i[0] for i in sim_scores]
        
        # Add a flag to indicate which book we are showing results for
        results = self.df.iloc[book_indices].to_dict(orient='records')
        for r in results:
            r['target_book_title'] = self.df.iloc[idx]['title']
            
        return results

    def get_book_by_id(self, book_id):
        if self.df.empty:
            return None
        book = self.df[self.df['book_id'] == int(book_id)]
        if book.empty:
            return None
        return book.iloc[0].to_dict()

    def get_books_by_ids(self, book_ids):
        if self.df.empty or not book_ids:
            return []
        
        book_ids = [int(i) for i in book_ids]
        books = self.df[self.df['book_id'].isin(book_ids)]
        return books.to_dict(orient='records')

    def get_user_based_recommendations(self, liked_ids, viewed_ids, top_n=8):
        if self.df.empty or (not liked_ids and not viewed_ids):
            return self.get_top_rated(top_n)

        liked_ids = [int(i) for i in liked_ids]
        viewed_ids = [int(i) for i in viewed_ids]

        liked_indices = self.df.index[self.df['book_id'].isin(liked_ids)].tolist()
        viewed_indices = self.df.index[self.df['book_id'].isin(viewed_ids)].tolist()

        if not liked_indices and not viewed_indices:
            return self.get_top_rated(top_n)

        # Build user profile vectors
        user_profile_count = np.zeros(self.count_matrix.shape[1])
        user_profile_tfidf = np.zeros(self.tfidf_matrix.shape[1])

        # Weight liked books higher
        for idx in liked_indices:
            user_profile_count += self.count_matrix[idx].toarray()[0] * 2.0
            user_profile_tfidf += self.tfidf_matrix[idx].toarray()[0] * 2.0

        # Weight viewed books lower
        for idx in viewed_indices:
            if idx not in liked_indices: 
                user_profile_count += self.count_matrix[idx].toarray()[0] * 1.0
                user_profile_tfidf += self.tfidf_matrix[idx].toarray()[0] * 1.0

        # Normalize the user profiles
        norm_count = np.linalg.norm(user_profile_count)
        if norm_count > 0: 
            user_profile_count = user_profile_count / norm_count
            
        norm_tfidf = np.linalg.norm(user_profile_tfidf)
        if norm_tfidf > 0: 
            user_profile_tfidf = user_profile_tfidf / norm_tfidf

        user_profile_count = user_profile_count.reshape(1, -1)
        user_profile_tfidf = user_profile_tfidf.reshape(1, -1)

        sim_count = cosine_similarity(user_profile_count, self.count_matrix)[0]
        sim_tfidf = cosine_similarity(user_profile_tfidf, self.tfidf_matrix)[0]
        
        sim_scores = (sim_count + sim_tfidf) / 2.0
        book_indices = sim_scores.argsort()[::-1]

        # Filter out books they already liked to show fresh recommendations
        recommended_indices = [i for i in book_indices if self.df.iloc[i]['book_id'] not in liked_ids]
        
        if not recommended_indices:
            return self.get_top_rated(top_n)

        return self.df.iloc[recommended_indices[:top_n]].to_dict(orient='records')

    def _apply_unique_images(self):
        """Replaces common placeholder images with genre-specific high-quality ones"""
        placeholder_substring = "photo-1544947950-fa07a98d237f"
        
        def get_image(row):
            current_url = str(row['image_url'])
            if placeholder_substring in current_url:
                genre = str(row['genre']).lower()
                
                # Check for genre matches in our mapping
                selected_pool = GENRE_IMAGES['default']
                for g, pool in GENRE_IMAGES.items():
                    if g in genre:
                        selected_pool = pool
                        break
                
                # Use a hash of the title to pick an image from the pool AND add a unique signature
                title_hash_raw = hashlib.md5(row['title'].encode()).hexdigest()
                pool_idx = int(title_hash_raw, 16) % len(selected_pool)
                selected_base = selected_pool[pool_idx]
                
                sig = title_hash_raw[:6]
                return f"{selected_base}?auto=format&fit=crop&q=80&w=400&sig={sig}"
            
            return current_url

        self.df['image_url'] = self.df.apply(get_image, axis=1)

