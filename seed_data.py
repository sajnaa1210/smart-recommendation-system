import pandas as pd
import random

books_data = [
    {"book_id": 1, "title": "The Great Gatsby", "author": "F. Scott Fitzgerald", "genre": "Classic", "rating": 4.5, "description": "A story of the wealthy Jay Gatsby and his love for the beautiful Daisy Buchanan.", "image_url": "https://images.unsplash.com/photo-1544947950-fa07a98d237f?auto=format&fit=crop&q=80&w=400"},
    {"book_id": 2, "title": "1984", "author": "George Orwell", "genre": "Sci-Fi", "rating": 4.8, "description": "A novel about a dystopian future under the totalitarian regime of Big Brother.", "image_url": "https://images.unsplash.com/photo-1589829085413-56de8ae18c73?auto=format&fit=crop&q=80&w=400"},
    {"book_id": 3, "title": "To Kill a Mockingbird", "author": "Harper Lee", "genre": "Classic", "rating": 4.9, "description": "The story of a young girl and her father, a lawyer who defends a black man accused of a terrible crime.", "image_url": "https://images.unsplash.com/photo-1512820790803-83ca734da794?auto=format&fit=crop&q=80&w=400"},
    {"book_id": 4, "title": "Pride and Prejudice", "author": "Jane Austen", "genre": "Romance", "rating": 4.7, "description": "A romantic novel that charts the emotional development of the protagonist Elizabeth Bennet.", "image_url": "https://images.unsplash.com/photo-1543002588-bfa74002ed7e?auto=format&fit=crop&q=80&w=400"},
    {"book_id": 5, "title": "The Hobbit", "author": "J.R.R. Tolkien", "genre": "Fantasy", "rating": 4.8, "description": "A fantastic journey of Bilbo Baggins to win a share of the treasure guarded by Smaug.", "image_url": "https://images.unsplash.com/photo-1608666579024-db08b29fac41?auto=format&fit=crop&q=80&w=400"},
    {"book_id": 6, "title": "Dune", "author": "Frank Herbert", "genre": "Sci-Fi", "rating": 4.7, "description": "Set on the desert planet Arrakis, Dune is the story of the boy Paul Atreides.", "image_url": "https://images.unsplash.com/photo-1518770660439-4636190af475?auto=format&fit=crop&q=80&w=400"},
    {"book_id": 7, "title": "Harry Potter and the Sorcerer's Stone", "author": "J.K. Rowling", "genre": "Fantasy", "rating": 4.9, "description": "A young orphaned boy discovers his magical heritage and attends a magical school.", "image_url": "https://images.unsplash.com/photo-1618666012174-83b441c0bc76?auto=format&fit=crop&q=80&w=400"},
    {"book_id": 8, "title": "The Catcher in the Rye", "author": "J.D. Salinger", "genre": "Classic", "rating": 4.1, "description": "The experiences of a young boy, Holden Caulfield, after he is expelled from prep school.", "image_url": "https://images.unsplash.com/photo-1476275466078-4007374efac4?auto=format&fit=crop&q=80&w=400"},
    {"book_id": 9, "title": "The Lord of the Rings", "author": "J.R.R. Tolkien", "genre": "Fantasy", "rating": 4.9, "description": "An epic high-fantasy novel following the quest to destroy the One Ring.", "image_url": "https://images.unsplash.com/photo-1515549832467-8783363e19b6?auto=format&fit=crop&q=80&w=400"},
    {"book_id": 10, "title": "Fahrenheit 451", "author": "Ray Bradbury", "genre": "Sci-Fi", "rating": 4.6, "description": "A dystopian novel about a future American society where books are outlawed.", "image_url": "https://images.unsplash.com/photo-1506880018603-83d5b814b5a6?auto=format&fit=crop&q=80&w=400"},
    {"book_id": 11, "title": "The Alchemist", "author": "Paulo Coelho", "genre": "Fiction", "rating": 4.5, "description": "A story about an Andalusian shepherd boy who yearns to travel in search of a worldly treasure.", "image_url": "https://images.unsplash.com/photo-1511108690759-009324a90311?auto=format&fit=crop&q=80&w=400"},
    {"book_id": 12, "title": "The Da Vinci Code", "author": "Dan Brown", "genre": "Mystery", "rating": 4.3, "description": "A murder in the Louvre Museum reveals a sinister plot to uncover a secret.", "image_url": "https://images.unsplash.com/photo-1550592704-6c76defa9985?auto=format&fit=crop&q=80&w=400"},
    {"book_id": 13, "title": "A Game of Thrones", "author": "George R.R. Martin", "genre": "Fantasy", "rating": 4.8, "description": "Several noble houses fight for control of the mythical land of Westeros.", "image_url": "https://images.unsplash.com/photo-1628155930542-3c7a64e2c833?auto=format&fit=crop&q=80&w=400"},
    {"book_id": 14, "title": "The Hunger Games", "author": "Suzanne Collins", "genre": "Sci-Fi", "rating": 4.7, "description": "In a dystopian future, teens are forced to participate in a televised death match.", "image_url": "https://images.unsplash.com/photo-1584697964149-aebba81d9f48?auto=format&fit=crop&q=80&w=400"},
    {"book_id": 15, "title": "The Fault in Our Stars", "author": "John Green", "genre": "Romance", "rating": 4.6, "description": "Two teenage cancer patients begin a life-affirming journey to visit a reclusive author.", "image_url": "https://images.unsplash.com/photo-1518604642851-40efab156ecb?auto=format&fit=crop&q=80&w=400"},
    {"book_id": 16, "title": "Gone Girl", "author": "Gillian Flynn", "genre": "Mystery", "rating": 4.5, "description": "A thriller about a woman who disappears on her wedding anniversary.", "image_url": "https://images.unsplash.com/photo-1629851722830-466d71cb94db?auto=format&fit=crop&q=80&w=400"},
    {"book_id": 17, "title": "The Girl with the Dragon Tattoo", "author": "Stieg Larsson", "genre": "Mystery", "rating": 4.6, "description": "A journalist and a hacker investigate the disappearance of a wealthy patriarch's niece.", "image_url": "https://images.unsplash.com/photo-1600182607903-518f972b9a71?auto=format&fit=crop&q=80&w=400"},
    {"book_id": 18, "title": "The Martian", "author": "Andy Weir", "genre": "Sci-Fi", "rating": 4.8, "description": "An astronaut becomes stranded on Mars and must find a way to survive.", "image_url": "https://images.unsplash.com/photo-1451187580459-43490279c0fa?auto=format&fit=crop&q=80&w=400"},
    {"book_id": 19, "title": "It", "author": "Stephen King", "genre": "Horror", "rating": 4.4, "description": "Seven children are terrorized by an evil entity that exploits their fears.", "image_url": "https://images.unsplash.com/photo-1605806616949-1e87b487cb2a?auto=format&fit=crop&q=80&w=400"},
    {"book_id": 20, "title": "The Shining", "author": "Stephen King", "genre": "Horror", "rating": 4.5, "description": "A family heads to an isolated hotel for the winter where an evil presence drives the father to violence.", "image_url": "https://images.unsplash.com/photo-1505664194779-8beaceb93744?auto=format&fit=crop&q=80&w=400"},
    {"book_id": 21, "title": "Sapiens: A Brief History of Humankind", "author": "Yuval Noah Harari", "genre": "Non-Fiction", "rating": 4.8, "description": "A book that explores the history of the human species.", "image_url": "https://images.unsplash.com/photo-1456513080510-7bf3a84b82f8?auto=format&fit=crop&q=80&w=400"},
    {"book_id": 22, "title": "Educated", "author": "Tara Westover", "genre": "Non-Fiction", "rating": 4.7, "description": "A memoir about a young woman who, kept out of school, leaves her survivalist family and goes on to earn a PhD.", "image_url": "https://images.unsplash.com/photo-1532012197267-da84d127e765?auto=format&fit=crop&q=80&w=400"},
    {"book_id": 23, "title": "Becoming", "author": "Michelle Obama", "genre": "Non-Fiction", "rating": 4.9, "description": "The memoir of former United States First Lady Michelle Obama.", "image_url": "https://images.unsplash.com/photo-1491841550275-ad7854e35ca6?auto=format&fit=crop&q=80&w=400"},
    {"book_id": 24, "title": "The Silent Patient", "author": "Alex Michaelides", "genre": "Mystery", "rating": 4.5, "description": "A famous painter shoots her husband and never speaks another word.", "image_url": "https://images.unsplash.com/photo-1587876931567-564ce588bfbd?auto=format&fit=crop&q=80&w=400"},
    {"book_id": 25, "title": "Brave New World", "author": "Aldous Huxley", "genre": "Sci-Fi", "rating": 4.4, "description": "A dystopian society that is seemingly perfect but built on the loss of true human emotions.", "image_url": "https://images.unsplash.com/photo-1614728263952-84ea256f9679?auto=format&fit=crop&q=80&w=400"},
    {"book_id": 26, "title": "Ender's Game", "author": "Orson Scott Card", "genre": "Sci-Fi", "rating": 4.6, "description": "Gifted children are trained in military strategy to fight an alien race.", "image_url": "https://images.unsplash.com/photo-1451187580459-43490279c0fa?auto=format&fit=crop&q=80&w=400"},
    {"book_id": 27, "title": "A Court of Thorns and Roses", "author": "Sarah J. Maas", "genre": "Fantasy", "rating": 4.5, "description": "A huntress is taken to a magical kingdom where she falls for her captor.", "image_url": "https://images.unsplash.com/photo-1518770660439-4636190af475?auto=format&fit=crop&q=80&w=400"},
    {"book_id": 28, "title": "The Notebook", "author": "Nicholas Sparks", "genre": "Romance", "rating": 4.3, "description": "A story of young love, separation, and enduring passion.", "image_url": "https://images.unsplash.com/photo-1518604642851-40efab156ecb?auto=format&fit=crop&q=80&w=400"},
]

# Add full e-book content to all books
for book in books_data:
    chapters = []
    for i in range(1, 11):
        paragraphs = [
            f"The events unfolded naturally as the story of {book['title']} progressed. Under the watchful eye of {book['author']}, every character found their destiny in this {book['genre']} narrative.",
            "The wind howled through the trees, echoing the turmoil that broiled within the protagonist's heart. The journey embarked upon was arduous, and tested the limits of endurance.",
            "Days blurred into nights as the path wound deeper into uncharted territory. Companions were found and lost along the way; lessons were learned at great cost.",
            "In quiet moments, reflection brought clarity. The world seemed to shift, revealing hidden truths that had been obscured by the chaos of constant struggle and survival.",
            "The intricate plot thickened, drawing the reader deeper into a world of endless imagination and wonder. The mystery and emotion of the narrative culminated in profound revelations.",
            f"As chapter {i} concluded, the echoes of {book['title']} resonated, leaving an indelible mark on the landscape of {book['genre']} literature."
        ]
        # Multiply text to make it longer
        chapter_text = f"Chapter {i}\n\n" + "\n\n".join(paragraphs * 3)
        chapters.append(chapter_text)
        
    book['sample_text'] = "\n\n***\n\n".join(chapters)

df = pd.DataFrame(books_data)

if __name__ == '__main__':
    import os
    os.makedirs('data', exist_ok=True)
    df.to_csv('data/books.csv', index=False)
    print("Saved 28 books to data/books.csv")
