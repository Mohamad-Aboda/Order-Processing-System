from django.http import JsonResponse

def show_endpoints(request):
    base_url = "http://127.0.0.1:8000"
    
    endpoints = [
    ]

    # User endpoints
    user_endpoints = [
        {"Method": "POST", "Endpoint": f"{base_url}/api/v1/users/signup/", "Description": "Register a new user"},
        {"Method": "POST", "Endpoint": f"{base_url}/api/v1/users/login/", "Description": "View to login a user"},
        {"Method": "POST", "Endpoint": f"{base_url}/api/v1/users/logout/", "Description": "View to logout a user"},
    ]
    endpoints.extend(user_endpoints)

    # Product endpoints
    product_endpoints = [
        {"Method": "GET/POST", "Endpoint": f"{base_url}/api/v1/products/", "Description": "List and create products"},
        {"Method": "GET/PUT/DELETE", "Endpoint": f"{base_url}/api/v1/products/<pk>/", "Description": "Retrieve, update, or delete a product"},
        {"Method": "GET/POST", "Endpoint": f"{base_url}/api/v1/img-products/<int:product_id>/images/", "Description": "List and create product images"},
        {"Method": "GET/PUT/DELETE", "Endpoint": f"{base_url}/api/v1/img-products/<int:product_id>/images/<int:image_id>/", "Description": "Retrieve, update, or delete a product image"},
        {"Method": "DELETE", "Endpoint": f"{base_url}/api/v1/img-products/<int:product_id>/images/delete-all/", "Description": "Delete all images of a product"},
    ]
    endpoints.extend(product_endpoints)

    # Order endpoints
    order_endpoints = [
        {"Method": "POST", "Endpoint": f"{base_url}/api/v1/orders/", "Description": "Create an order"},
        {"Method": "POST", "Endpoint": f"{base_url}/api/v1/orders/<int:pk>/cancel/", "Description": "Cancel an order"},
        {"Method": "GET", "Endpoint": f"{base_url}/api/v1/orders/<int:pk>/", "Description": "Retrieve an order"},
        {"Method": "GET", "Endpoint": f"{base_url}/api/v1/orders/all/", "Description": "List all orders"},
        {"Method": "POST", "Endpoint": f"{base_url}/api/v1/orders/<int:pk>/payment/", "Description": "Process payment for an order"},
    ]
    endpoints.extend(order_endpoints)

    # Cart endpoints
    cart_endpoints = [
        {"Method": "GET", "Endpoint": f"{base_url}/api/v1/cart/", "Description": "Retrieve the user's cart"},
        {"Method": "POST", "Endpoint": f"{base_url}/api/v1/cart/add/<int:product_id>/", "Description": "Add a product to the cart"},
        {"Method": "POST", "Endpoint": f"{base_url}/api/v1/cart/remove/<int:product_id>/", "Description": "Remove a product from the cart"},
    ]
    endpoints.extend(cart_endpoints)

    return JsonResponse({"endpoints": endpoints}, json_dumps_params={'indent': 2})
