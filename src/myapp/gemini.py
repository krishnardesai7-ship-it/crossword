import os

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None

try:
    import google.generativeai as genai  # type: ignore[import]
except ImportError:
    genai = None

# Load .env file when python-dotenv is installed.
if load_dotenv is not None:
    load_dotenv()

# Get API key
api_key = os.getenv("GEMINI_API_KEY")

if genai is not None:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-1.5-flash")
else:
    model = None

def ask_gemini(user_input):
    try:
        prompt = f"""
You are a helpful bookstore chatbot.
User: {user_input}
Bot:
"""
        response = model.generate_content(prompt)
        return response.text

    except Exception as e:
        return "⚠️ AI is not working right now."

def suggest_from_other_sources(book_name):
    """
    Suggest where to find the book from external sources like Amazon and Flipkart
    """
    try:
        prompt = f"""
You are a helpful bookstore chatbot assistant. A customer is looking for a book but it's not available in our store.
Provide helpful suggestions for where they can find the book "{book_name}" online.

Include:
1. Amazon link format: https://www.amazon.in/s?k={book_name.replace(' ', '+')}
2. Flipkart link format: https://www.flipkart.com/search?q={book_name.replace(' ', '+')}
3. Other alternatives like BookMyShow, Google Play Books, etc.
4. A friendly message encouraging them to search there

Format the response nicely with emojis and links. Keep it concise.
"""
        response = model.generate_content(prompt)
        return response.text

    except Exception as e:
        # Fallback response with direct clickable links
        amazon_link = f"https://www.amazon.in/s?k={book_name.replace(' ', '+')}"
        flipkart_link = f"https://www.flipkart.com/search?q={book_name.replace(' ', '+')}"
        
        return f"""
📚 Book not available in our store, but here's where you can find it:

🛒 <a href="{amazon_link}" target="_blank">Amazon: Search '{book_name}'</a>

🛒 <a href="{flipkart_link}" target="_blank">Flipkart: Search '{book_name}'</a>

Or try other online platforms like <a href="https://play.google.com/store/books" target="_blank">Google Play Books</a>, <a href="https://www.bookmyshow.com" target="_blank">BookMyShow</a>, or your local library! 📖
"""
