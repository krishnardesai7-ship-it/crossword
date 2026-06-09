"""
Additional views for book summaries and personalized recommendations
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, FileResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.db.models import Q
from django.contrib import messages
import os
from .models import (
    product as product_model, 
    register as RegisterUser,
    checkout as checkout_model,
    BookPurchase,
    PersonalizedRecommendation,
    add_to_cart
)


def view_book_summary_pdf(request, product_id):
    """View or download the PDF summary of a book"""
    if "email" not in request.session:
        return redirect('accounts:login')
    
    product = get_object_or_404(product_model, id=product_id)
    
    if not product.summary_pdf:
        messages.error(request, 'PDF summary not available for this book.')
        return redirect('product', id=product_id)
    
    try:
        pdf_file = product.summary_pdf.open('rb')
        response = FileResponse(pdf_file, content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="{product.name}_summary.pdf"'
        return response
    except Exception as e:
        messages.error(request, f'Error loading PDF: {str(e)}')
        return redirect('product', id=product_id)


def download_book_summary_pdf(request, product_id):
    """Download the PDF summary of a book"""
    if "email" not in request.session:
        return redirect('accounts:login')
    
    product = get_object_or_404(product_model, id=product_id)
    
    if not product.summary_pdf:
        messages.error(request, 'PDF summary not available for this book.')
        return redirect('product', id=product_id)
    
    try:
        pdf_file = product.summary_pdf.open('rb')
        response = FileResponse(pdf_file, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{product.name}_summary.pdf"'
        return response
    except Exception as e:
        messages.error(request, f'Error downloading PDF: {str(e)}')
        return redirect('product', id=product_id)


def generate_recommendations(user, purchased_product=None):
    """
    Generate personalized book recommendations based on user's purchase history
    Uses category and tags matching for recommendation
    """
    try:
        # Get user's purchase history
        user_purchases = BookPurchase.objects.filter(user=user).values_list('product_id', flat=True)
        purchased_products = product_model.objects.filter(id__in=user_purchases)
        
        if not purchased_products.exists():
            # If no purchase history, recommend bestsellers and new releases
            recommendations_list = product_model.objects.filter(
                Q(bestseller=True) | Q(new_release=True) | Q(expert_pick=True)
            ).exclude(id__in=user_purchases)[:5]
        else:
            # Collect categories and tags from purchase history
            categories = set(purchased_products.values_list('category', flat=True))
            all_tags = set()
            for product in purchased_products:
                if product.recommendation_tags:
                    all_tags.update([tag.strip() for tag in product.recommendation_tags.split(',')])
            
            # Find books with matching categories or tags
            recommendations_list = product_model.objects.filter(
                Q(category__in=categories) | Q(recommendation_tags__icontains='')
            ).exclude(id__in=user_purchases).distinct()
            
            # If tags are available, prioritize books with matching tags
            if all_tags:
                tag_matching = []
                for prod in recommendations_list:
                    if prod.recommendation_tags:
                        prod_tags = set([tag.strip() for tag in prod.recommendation_tags.split(',')])
                        match_count = len(all_tags.intersection(prod_tags))
                        if match_count > 0:
                            tag_matching.append((prod, match_count * 20))
                
                # Sort by match count
                tag_matching.sort(key=lambda x: x[1], reverse=True)
                recommendations_list = [item[0] for item in tag_matching[:5]]
            else:
                recommendations_list = recommendations_list[:5]
        
        # Store recommendations in database
        PersonalizedRecommendation.objects.filter(user=user).delete()
        
        for idx, product in enumerate(recommendations_list):
            match_score = 100 - (idx * 15)  # Score decreases with rank
            recommendation_reason = f"Based on your interest in {product.category} books"
            
            PersonalizedRecommendation.objects.get_or_create(
                user=user,
                recommended_product=product,
                defaults={
                    'recommendation_reason': recommendation_reason,
                    'match_score': match_score
                }
            )
        
        return PersonalizedRecommendation.objects.filter(user=user)
    
    except Exception as e:
        print(f"Error generating recommendations: {str(e)}")
        return PersonalizedRecommendation.objects.filter(user=user)


def book_purchase_success(request, order_id):
    """
    Display purchase success page with personalized book recommendations
    Redirect here after successful payment/order placement
    """
    if "email" not in request.session:
        return redirect('accounts:login')
    
    uid = RegisterUser.objects.get(email=request.session['email'])
    order = get_object_or_404(checkout_model, id=order_id, register=uid)
    
    # Create BookPurchase records for this order
    try:
        purchased_products = product_model.objects.filter(name=order.product_name)
        for product in purchased_products:
            BookPurchase.objects.get_or_create(
                user=uid,
                product=product,
                order=order
            )
    except Exception as e:
        print(f"Error creating purchase record: {str(e)}")
    
    # Generate personalized recommendations
    recommendations = generate_recommendations(uid, order.product_name)
    
    context = {
        'order': order,
        'user': uid,
        'recommendations': recommendations,
        'recommendations_count': recommendations.count()
    }
    
    return render(request, 'customerapp/purchase_success.html', context)


@require_http_methods(["GET"])
def get_recommendations_api(request):
    """
    API endpoint to get personalized recommendations for the logged-in user
    Returns JSON format for AJAX calls
    """
    if "email" not in request.session:
        return JsonResponse({'error': 'User not authenticated'}, status=401)
    
    try:
        uid = RegisterUser.objects.get(email=request.session['email'])
        recommendations = generate_recommendations(uid)
        
        recommendations_data = []
        for rec in recommendations:
            recommendations_data.append({
                'id': rec.recommended_product.id,
                'name': rec.recommended_product.name,
                'author': rec.recommended_product.author_name,
                'price': rec.recommended_product.price,
                'image': rec.recommended_product.image.url if rec.recommended_product.image else None,
                'reason': rec.recommendation_reason,
                'match_score': rec.match_score,
                'category': rec.recommended_product.category,
            })
        
        return JsonResponse({
            'success': True,
            'recommendations': recommendations_data,
            'count': len(recommendations_data)
        })
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


def track_order_with_recommendations(request, order_id):
    """
    Track order and show related recommendations
    """
    if "email" not in request.session:
        return redirect('accounts:login')
    
    uid = RegisterUser.objects.get(email=request.session['email'])
    order = get_object_or_404(checkout_model, id=order_id, register=uid)
    
    # Generate recommendations based on this purchase
    recommendations = PersonalizedRecommendation.objects.filter(user=uid).order_by('-match_score')[:5]
    
    context = {
        'order': order,
        'recommendations': recommendations
    }
    
    return render(request, 'customerapp/track_order_with_recommendations.html', context)
