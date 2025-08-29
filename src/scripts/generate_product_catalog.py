#!/usr/bin/env python3
"""
Generate Product Catalog from Real Customer Data

This script analyzes the real customer data from customers.json to create:
1. A comprehensive product catalog with accurate pricing
2. Product preference scores based on actual purchase frequency
3. Average quantities per product
4. Category distribution and preferences
5. Price range analysis

The output can be used to improve the order generation simulation.
"""

import json
import os
from collections import Counter, defaultdict
from datetime import datetime
import statistics


def load_customer_data():
    """Load the real customer data."""
    input_file = "./data/customers.json"
    
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            customers = json.load(f)
        print(f"✅ Loaded {len(customers)} customers from {input_file}")
        return customers
    except FileNotFoundError:
        print(f"❌ Could not find {input_file}")
        return []
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in {input_file}: {e}")
        return []


def analyze_product_data(customers):
    """
    Analyze all customer data to extract product information.
    
    Returns:
    dict: Comprehensive product analysis including catalog, preferences, and statistics
    """
    
    # Data collection structures
    product_stats = defaultdict(lambda: {
        'total_quantity': 0,
        'total_orders': 0,
        'prices': [],
        'customers': set(),
        'order_dates': []
    })
    
    category_stats = defaultdict(lambda: {
        'total_quantity': 0,
        'total_orders': 0,
        'products': set(),
        'avg_price': 0
    })
    
    all_orders = 0
    total_revenue = 0
    
    print("🔍 Analyzing customer purchase patterns...")
    
    for customer in customers:
        customer_id = customer.get('id', 'unknown')
        historical_orders = customer.get('historical_purchase_frequency', [])
        
        for order in historical_orders:
            all_orders += 1
            order_lines = order.get('order_lines', [])
            order_date = order.get('order_date', '')
            
            for line in order_lines:
                product_name = line.get('product_name', '').strip()
                price = line.get('product_price')
                quantity = line.get('quantity', 1)
                
                if not product_name or product_name == 'Unknown Product' or price is None:
                    continue
                
                # Update product statistics
                product_stats[product_name]['total_quantity'] += quantity
                product_stats[product_name]['total_orders'] += 1
                product_stats[product_name]['prices'].append(price)
                product_stats[product_name]['customers'].add(customer_id)
                if order_date:
                    product_stats[product_name]['order_dates'].append(order_date)
                
                # Update category statistics
                category = categorize_product(product_name)
                category_stats[category]['total_quantity'] += quantity
                category_stats[category]['total_orders'] += 1
                category_stats[category]['products'].add(product_name)
                
                total_revenue += price * quantity
    
    print(f"📊 Analyzed {all_orders} orders with {len(product_stats)} unique products")
    print(f"💰 Total revenue analyzed: {total_revenue:,.2f} GEL")
    
    return {
        'product_stats': dict(product_stats),
        'category_stats': dict(category_stats),
        'total_orders': all_orders,
        'total_revenue': total_revenue
    }


def categorize_product(product_name):
    """Categorize a product based on its name."""
    name_lower = product_name.lower()
    
    # Coffee varieties/origins
    if any(keyword in name_lower for keyword in ['ბრაზილია', 'გვატემალა', 'ეთიოპია', 'კოლუმბია', 'ელ-სალვადორი']):
        return 'coffee_origin'
    
    # Flavored coffee
    if any(keyword in name_lower for keyword in ['კარამელი', 'ვანილი', 'ტყის თხილი', 'მაკაპუნო', 'შოკოლად']):
        return 'flavored_coffee'
    
    # Colored/numbered varieties
    if any(keyword in name_lower for keyword in ['მწვანე', 'ლურჯი', 'წითელი', 'იასამნისფერი', 'ბურგუნდი', 'ყვითელი']):
        return 'coffee_blend'
    
    # Cups and accessories
    if any(keyword in name_lower for keyword in ['ჭიქა', 'ჰოლდერი', 'მეტალის', 'ფაიფურის']):
        return 'accessories'
    
    # Vending machine items
    if 'vending' in name_lower or 'ვენდინგ' in name_lower:
        return 'vending'
    
    # Special products
    if any(keyword in name_lower for keyword in ['meama', 'მეამა', 'პაკეტი']):
        return 'subscription'
    
    # Instant/ground coffee
    if 'ნალექიანი' in name_lower:
        return 'instant_coffee'
    
    # Free/Tier point items
    if any(keyword in name_lower for keyword in ['free', 'tier point']):
        return 'free_items'
    
    # Default category
    return 'other'


def generate_product_catalog(product_stats, category_stats, total_orders):
    """
    Generate a comprehensive product catalog with preference scores.
    
    Returns:
    dict: Product catalog with preference scores, frequencies, and statistics
    """
    
    print("🏷️  Generating product catalog...")
    
    # Calculate total product frequency across all orders
    total_product_frequency = sum(stats['total_orders'] for stats in product_stats.values())
    
    # Generate product catalog
    product_catalog = []
    
    for product_name, stats in product_stats.items():
        frequency = stats['total_orders']
        preference_score = frequency / total_product_frequency if total_product_frequency > 0 else 0
        avg_quantity = stats['total_quantity'] / frequency if frequency > 0 else 1
        
        # Calculate price statistics
        prices = stats['prices']
        avg_price = statistics.mean(prices) if prices else 0
        min_price = min(prices) if prices else 0
        max_price = max(prices) if prices else 0
        
        # Calculate customer reach
        unique_customers = len(stats['customers'])
        
        product_catalog.append({
            'name': product_name,
            'frequency': frequency,
            'preference_score': round(preference_score, 4),
            'avg_quantity': round(avg_quantity, 2),
            'avg_price': round(avg_price, 2),
            'min_price': round(min_price, 2),
            'max_price': round(max_price, 2),
            'unique_customers': unique_customers,
            'category': categorize_product(product_name),
            'total_quantity_sold': stats['total_quantity']
        })
    
    # Sort by frequency (most popular first)
    product_catalog.sort(key=lambda x: x['frequency'], reverse=True)
    
    return product_catalog


def generate_category_analysis(category_stats, product_catalog):
    """
    Generate category-level analysis and preferences.
    
    Returns:
    dict: Category analysis with preferences and statistics
    """
    
    print("📂 Generating category analysis...")
    
    category_analysis = {}
    
    for category, stats in category_stats.items():
        products_in_category = [p for p in product_catalog if p['category'] == category]
        
        if not products_in_category:
            continue
        
        total_category_quantity = stats['total_quantity']
        total_category_orders = stats['total_orders']
        avg_price = statistics.mean([p['avg_price'] for p in products_in_category]) if products_in_category else 0
        
        category_analysis[category] = {
            'total_quantity': total_category_quantity,
            'total_orders': total_category_orders,
            'avg_price': round(avg_price, 2),
            'product_count': len(products_in_category),
            'top_products': [p['name'] for p in products_in_category[:5]]
        }
    
    return category_analysis


def generate_default_preferences(product_catalog, category_analysis):
    """
    Generate default product preferences for new customers.
    
    Returns:
    dict: Default preferences based on overall market data
    """
    
    print("⭐ Generating default preferences...")
    
    # Get top products by frequency (top 20%)
    top_products_count = max(5, len(product_catalog) // 5)
    top_products = product_catalog[:top_products_count]
    
    # Calculate total frequency for normalization
    total_frequency = sum(p['frequency'] for p in top_products)
    
    default_products = []
    for product in top_products:
        default_products.append({
            'name': product['name'],
            'frequency': product['frequency'],
            'preference_score': round(product['frequency'] / total_frequency, 4),
            'avg_quantity': product['avg_quantity']
        })
    
    # Calculate category preferences
    total_category_quantity = sum(cat['total_quantity'] for cat in category_analysis.values())
    category_preferences = {}
    
    for category, stats in category_analysis.items():
        if total_category_quantity > 0:
            category_preferences[category] = round((stats['total_quantity'] / total_category_quantity) * 100, 1)
        else:
            category_preferences[category] = 0
    
    # Calculate price range from all products
    all_prices = [p['avg_price'] for p in product_catalog if p['avg_price'] > 0]
    avg_price_range = (min(all_prices), max(all_prices)) if all_prices else (20, 30)
    
    # Calculate typical items per order
    total_items = sum(p['total_quantity_sold'] for p in product_catalog)
    typical_items_per_order = total_items / len(product_catalog) if product_catalog else 2
    
    return {
        'preferred_products': default_products,
        'category_preferences': category_preferences,
        'avg_price_range': (round(avg_price_range[0], 2), round(avg_price_range[1], 2)),
        'typical_items_per_order': round(typical_items_per_order, 1)
    }


def save_analysis_results(product_catalog, category_analysis, default_preferences):
    """Save the analysis results to a single comprehensive JSON file."""
    
    # Create output directory if it doesn't exist
    os.makedirs('./data/analysis', exist_ok=True)
    
    # Create comprehensive analysis with everything you need
    analysis_data = {
        'generated_at': datetime.now().isoformat(),
        'summary': {
            'total_products': len(product_catalog),
            'total_categories': len(category_analysis),
            'top_product': product_catalog[0]['name'] if product_catalog else 'None',
            'most_popular_category': max(category_analysis.items(), key=lambda x: x[1]['total_orders'])[0] if category_analysis else 'None'
        },
        'product_catalog': product_catalog,
        'category_analysis': category_analysis,
        'default_preferences': default_preferences
    }
    
    # Save single comprehensive file
    analysis_file = './data/analysis/customer_analysis.json'
    with open(analysis_file, 'w', encoding='utf-8') as f:
        json.dump(analysis_data, f, indent=2, ensure_ascii=False)
    
    print(f"💾 Saved analysis results to: {analysis_file}")
    print(f"   📊 Contains: {len(product_catalog)} products, {len(category_analysis)} categories, and default preferences")


def print_summary(product_catalog, category_analysis, default_preferences):
    """Print a summary of the analysis results."""
    
    print("\n" + "="*60)
    print("📊 ANALYSIS SUMMARY")
    print("="*60)
    
    print(f"🏷️  Total products analyzed: {len(product_catalog)}")
    print(f"📂 Total categories: {len(category_analysis)}")
    print(f"⭐ Default products for new customers: {len(default_preferences['preferred_products'])}")
    
    print(f"\n🏆 TOP 5 MOST POPULAR PRODUCTS:")
    for i, product in enumerate(product_catalog[:5], 1):
        print(f"   {i}. {product['name'][:50]}...")
        print(f"      Frequency: {product['frequency']}, Avg price: {product['avg_price']} GEL")
        print(f"      Avg quantity: {product['avg_quantity']}, Customers: {product['unique_customers']}")
    
    print(f"\n📂 CATEGORY BREAKDOWN:")
    for category, stats in sorted(category_analysis.items(), key=lambda x: x[1]['total_orders'], reverse=True):
        print(f"   {category}: {stats['total_orders']} orders, {stats['total_quantity']} items")
        print(f"      Avg price: {stats['avg_price']} GEL, Products: {stats['product_count']}")
    
    print(f"\n⭐ DEFAULT PREFERENCES FOR NEW CUSTOMERS:")
    print(f"   Typical items per order: {default_preferences['typical_items_per_order']}")
    print(f"   Price range: {default_preferences['avg_price_range'][0]} - {default_preferences['avg_price_range'][1]} GEL")
    print(f"   Category preferences:")
    for category, percentage in default_preferences['category_preferences'].items():
        print(f"      {category}: {percentage}%")


def main():
    """Main function to run the product catalog generation."""
    
    print("🚀 MEAMA Product Catalog Generator")
    print("="*50)
    
    # Load customer data
    customers = load_customer_data()
    if not customers:
        return
    
    # Analyze product data
    analysis_data = analyze_product_data(customers)
    if not analysis_data['product_stats']:
        print("❌ No product data found in customer orders")
        return
    
    # Generate product catalog
    product_catalog = generate_product_catalog(
        analysis_data['product_stats'],
        analysis_data['category_stats'],
        analysis_data['total_orders']
    )
    
    # Generate category analysis
    category_analysis = generate_category_analysis(
        analysis_data['category_stats'],
        product_catalog
    )
    
    # Generate default preferences
    default_preferences = generate_default_preferences(product_catalog, category_analysis)
    
    # Save results
    save_analysis_results(product_catalog, category_analysis, default_preferences)
    
    # Print summary
    print_summary(product_catalog, category_analysis, default_preferences)
    
    print("\n✅ Product catalog generation completed successfully!")


if __name__ == "__main__":
    main()
