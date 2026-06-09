# Book Store Features - Implementation Guide

## New Features Added

This document outlines the new personalized book recommendation and PDF summary features added to your Django book store application.

---

## 1. **PDF Book Summary Features**

### Overview
Users can now view and download PDF summaries of books directly from the product details page.

### Features
- **View Summary**: Users can view PDF summaries inline in the browser
- **Download Summary**: Users can download PDF files for offline reading
- **Easy Access**: PDF summary buttons appear on product detail pages if a summary is available

### How to Use

#### For Admin/Store Manager:
1. Go to Django Admin (`/admin/`)
2. Navigate to **Products**
3. Edit any product
4. Upload a PDF file in the **"summary_pdf"** field
5. Save the product

#### For Users:
1. Navigate to any book's product page
2. If a summary is available, you'll see two buttons:
   - **👁️ View Summary** - Opens PDF in browser (can read online)
   - **⬇️ Download PDF** - Downloads the PDF to your device
3. Click the desired button

### Database Fields
- `summary_pdf`: FileField for uploading PDF summaries (uploaded to `book_summaries/` folder)

---

## 2. **Personalized Book Recommendations**

### Overview
The system automatically generates personalized book recommendations based on:
- User's purchase history
- Book categories and tags
- Related interests

### Features
- **Automatic Generation**: Recommendations are generated automatically after purchase
- **Matching Score**: Each recommendation has a match score (0-100%) indicating how relevant it is
- **Smart Filtering**: System learns from user preferences over time
- **Multi-Format Display**: Recommendations appear in:
  - Purchase Success page (popup/prominent display)
  - Order Tracking page
  - API endpoint (for custom implementations)

### How It Works

#### Recommendation Algorithm:
1. **Purchase Tracking**: When a user buys a book, it's recorded in `BookPurchase` model
2. **Category Analysis**: System identifies book categories from purchase history
3. **Tag Matching**: System extracts recommendation tags from books and finds matches
4. **Ranking**: Books are ranked by relevance score and sorted
5. **Storage**: Top 5 recommendations are stored for quick retrieval

#### Recommendation Tags:
Each book can have multiple tags (comma-separated) for better recommendations:
- Examples: `education, motivation, adventure, technology, romance, self-help`
- Set via Django Admin in the **"recommendation_tags"** field

### Database Models

#### BookPurchase Model
Tracks when users purchase books:
```python
- user: Foreign Key to RegisterUser
- product: Foreign Key to product
- order: Foreign Key to checkout (optional)
- purchased_date: Timestamp of purchase
```

#### PersonalizedRecommendation Model
Stores generated recommendations:
```python
- user: Foreign Key to RegisterUser
- recommended_product: Foreign Key to product
- recommendation_reason: Text explaining why recommended
- match_score: Float (0-100)
- created_at: Timestamp
- is_viewed: Boolean to track if user viewed recommendation
```

---

## 3. **Purchase Flow with Recommendations**

### User Journey

#### Cash on Delivery (COD):
1. User adds books to cart
2. Proceeds to checkout
3. Selects COD as payment method
4. Order is created immediately
5. **Redirected to Purchase Success page** (NEW)
   - Shows order confirmation
   - Displays 5 personalized recommendations
   - User can click to view recommended books

#### Online Payment (Razorpay):
1. User proceeds through Razorpay payment
2. Payment is processed
3. **Redirected to Purchase Success page** (NEW)
   - Shows order confirmation
   - Displays 5 personalized recommendations
   - User can click to view recommended books

### Purchase Success Page Features
- Order summary with all details
- Order status tracker
- **Personalized recommendations section**:
  - Book cover images
  - Title, author, price
  - Match score percentage
  - Reason for recommendation (AI-generated)
  - "View Book" button to navigate to product page

---

## 4. **API Endpoint for Recommendations**

### Endpoint: `GET /api/recommendations/`

Returns personalized recommendations in JSON format.

#### Request:
```
GET /api/recommendations/
Headers: 
  - User must be logged in (session-based)
```

#### Response (Success - 200):
```json
{
  "success": true,
  "count": 5,
  "recommendations": [
    {
      "id": 1,
      "name": "The Great Book Title",
      "author": "John Doe",
      "price": 299,
      "image": "/media/products/book1.jpg",
      "reason": "Based on your interest in Adventure books",
      "match_score": 95,
      "category": "adventure"
    },
    ...
  ]
}
```

#### Response (Not Authenticated - 401):
```json
{
  "error": "User not authenticated"
}
```

#### Usage:
```javascript
fetch('/api/recommendations/', {
  method: 'GET',
  credentials: 'include'
})
.then(response => response.json())
.then(data => console.log(data.recommendations));
```

---

## 5. **Order Tracking with Recommendations**

### New Route: `/track-order-with-recommendations/<order_id>/`

Enhanced order tracking page that includes:
- Order status timeline (visual progress indicator)
- Full order details
- Product information
- **Related recommendations** based on the purchased book

### Features
- Visual status timeline showing order progress
- Estimated delivery information
- Product details with image
- Smart recommendations related to the purchase
- Mobile-responsive design

---

## 6. **Setting Up the Features**

### Step 1: Create Migrations
```bash
cd src
python manage.py makemigrations
python manage.py migrate
```

### Step 2: Update Product Records
Add PDF summaries and recommendation tags:
1. Go to Django Admin
2. For each product:
   - Upload a PDF summary (if available)
   - Add recommendation tags (comma-separated)
   - Save

Example tags:
```
fiction, adventure, bestseller, young-adult
romance, emotional, modern, relationships
mystery, detective, suspense, crime
```

### Step 3: Test the Features

#### Test PDF Summary:
1. Navigate to a product with PDF
2. Click "View Summary" or "Download PDF"
3. Verify PDF opens/downloads correctly

#### Test Recommendations:
1. Go to Shop page
2. Add a book to cart
3. Complete checkout (COD or Razorpay)
4. Verify purchase success page shows recommendations
5. Test recommendation API: `curl http://yourdomain/api/recommendations/`

### Step 4: Customize (Optional)

#### Modify Recommendation Algorithm:
Edit `book_views.py` in the `generate_recommendations()` function:
```python
def generate_recommendations(user, purchased_product=None):
    # Modify the logic here for different recommendation strategies
    # Change match_score calculation
    # Adjust number of recommendations (default: 5)
```

#### Customize Recommendation UI:
Edit template files:
- `purchase_success.html` - Success page styling
- `track_order_with_recommendations.html` - Tracking page styling

---

## 7. **File Structure**

### New Files Created:
```
src/myapp/
├── book_views.py                          # New book-specific views
├── models.py                              # Updated with new models
├── urls.py                                # Updated with new routes
├── templates/customerapp/
│   ├── purchase_success.html              # New success page with recommendations
│   ├── track_order_with_recommendations.html  # New tracking page
│   └── product.html                       # Updated with PDF summary section
```

### Modified Files:
```
src/myapp/
├── models.py                              # Added BookPurchase, PersonalizedRecommendation
├── views.py                               # Updated payment_success, checkout views
├── urls.py                                # Added new URL patterns
├── templates/customerapp/product.html     # Added PDF summary section
```

---

## 8. **Admin Configuration**

### Configure Book Models in Django Admin

Update `admin.py`:
```python
from django.contrib import admin
from .models import product, BookPurchase, PersonalizedRecommendation

@admin.register(product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'category', 'summary_pdf', 'recommendation_tags']
    search_fields = ['name', 'author_name']
    list_filter = ['category', 'bestseller', 'new_release']
    fieldsets = (
        ('Basic Info', {
            'fields': ('name', 'author_name', 'price', 'published_year')
        }),
        ('Media', {
            'fields': ('image', 'summary_pdf')
        }),
        ('Details', {
            'fields': ('description', 'category', 'recommendation_tags')
        }),
        ('Flags', {
            'fields': ('bestseller', 'new_release', 'expert_pick')
        }),
    )

@admin.register(BookPurchase)
class BookPurchaseAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'purchased_date']
    list_filter = ['purchased_date', 'product__category']
    search_fields = ['user__username', 'product__name']
    readonly_fields = ['purchased_date']

@admin.register(PersonalizedRecommendation)
class RecommendationAdmin(admin.ModelAdmin):
    list_display = ['user', 'recommended_product', 'match_score', 'created_at']
    list_filter = ['match_score', 'created_at', 'is_viewed']
    search_fields = ['user__username', 'recommended_product__name']
    readonly_fields = ['created_at', 'match_score']
```

---

## 9. **Troubleshooting**

### PDF not showing on product page:
- **Solution**: Ensure `summary_pdf` field is populated in Django Admin
- **Check**: File path in media folder: `media/book_summaries/`

### Recommendations not appearing:
- **Solution 1**: Ensure user has made a purchase
- **Solution 2**: Check that products have `recommendation_tags` set
- **Solution 3**: Regenerate recommendations: `python manage.py shell`
  ```python
  from myapp.models import RegisterUser
  from myapp.book_views import generate_recommendations
  user = RegisterUser.objects.first()
  generate_recommendations(user)
  ```

### Permission denied when accessing PDF:
- **Solution**: Check media folder permissions
- **Command**: `chmod -R 755 media/book_summaries/`

---

## 10. **Advanced Customization**

### Change Recommendation Count:
In `book_views.py`, modify:
```python
recommendations_list = purchased_products.filter(...)[:5]  # Change 5 to desired count
```

### Adjust Match Score Calculation:
```python
match_score = 100 - (idx * 15)  # Modify the 15 value for different scoring
```

### Add More Recommendation Factors:
Extend the `generate_recommendations()` function to include:
- User view history
- User review ratings
- Price range preferences
- Reading level

---

## 11. **Performance Tips**

- **Cache Recommendations**: Use Django cache for frequently accessed recommendations
- **Async Generation**: For high-traffic sites, generate recommendations asynchronously using Celery
- **Database Indexing**: Add indexes on `BookPurchase.user` and `PersonalizedRecommendation.user`

---

## 12. **Support & Debugging**

Enable debugging logs:
```python
# In views.py, book_views.py
import logging
logger = logging.getLogger(__name__)
logger.info(f"Generating recommendations for user: {user.username}")
```

View Django logs:
```bash
python manage.py runserver --debug
```

---

## Summary

Your book store now has:
✅ PDF book summaries with view/download functionality
✅ Smart personalized recommendations based on purchase history
✅ Enhanced purchase success experience with recommendations popup
✅ Order tracking with related book recommendations
✅ RESTful API endpoint for recommendation data
✅ Admin interface for managing all features

**Next Steps**:
1. Run migrations
2. Upload PDF files for books in admin
3. Add recommendation tags to products
4. Test the complete user journey
5. Customize styles/messaging as needed

---

**Questions?** Check the code comments in `book_views.py` and template files for detailed explanations.
