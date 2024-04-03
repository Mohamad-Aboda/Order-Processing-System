# 🚀 Order Processing System

## Table of Contents


- [Overview](#overview)
- [Local Setup 👨‍💻](#local-setup)
    - [Virtual Environment Setup](#virtual-environment-setup)
        - [On Linux](#on-linux)
        - [On Windows](#on-windows)
    - [Installing Dependencies And Run Server](#installing-dependencies-and-run-server)
- [Docker Setup 🐳](#docker-setup-🐳)
- [API Documentation](#api-documentation)
  - [User Endpoints](#user-endpoints)
  - [Order Endpoints](#order-endpoints)
  - [Cart Endpoints](#cart-endpoints)
  - [Product Endpoints](#product-endpoints)

## Overview

Order Processing System for an online store.. It provides a RESTful API for user management, product listing, cart management, order processing, and payment integration with Stripe.

**Features:**
1. Users can register and login to the platform.
2. Users can browse products, add them to the cart, and proceed to checkout.
3. Users can view their orders and their cart contents.
4. Users can make payments using Stripe integration, with email confirmation sent upon successful payment.
5. Only admin users can create, update and delete products.
6. Implemented logging to enhance tracking and debugging functionalities.
7. Integrated GitHub Actions to automate the process of pushing Docker images to Docker Hub.

Note: For testing the product endpoints, you can use the following admin credentials or create admin user:

```bash
    Email: admin@gmail.com
    Password: admin
```


**Testing Endpoints:**
- To test the API endpoints, you can import the [Postman collection](Order_Processing_System.postman_collection.json) provided in the repository and try the endpoints in Postman.

**API Flow:**
1. **Register User:**
   - Use the `/api/v1/users/signup/` endpoint to register a new user by providing username, email, and password.

2. **Login User:**
   - Use the `/api/v1/users/login/` endpoint to login a user by providing username and password.
   - The response will include a JWT token.

3. **Browse Products:**
   - Use the `/api/v1/products/` endpoint to list all products available in the store.

4. **Add Product to Cart:**
   - Use the `/api/v1/carts/add/<int:product_id>/` endpoint to add a product to the user's cart.

5. **View Cart:**
   - Use the `/api/v1/carts/` endpoint to view the contents of the user's cart.

6. **Create Order:**
   - Use the `/api/v1/orders/` endpoint to create an order by providing the user id.

7. **Process Payment:**
   - Use the `/api/v1/orders/<int:pk>/payment/` endpoint to initiate the payment process using Stripe integration.

```bash
Note: Brevo removes the BREVO_API_KEY from the account, which prevents email confirmation from being sent. Therefore, email confirmation will not be sent unless a valid API key is provided.generate your own API key and update the API key in the configuration to enable email confirmation upon successful payment or you can contact me to provide a valid API key.
```







8. **View Orders:**
   - Use the `/api/v1/orders/all/` endpoint to view all orders placed by the user.

## Getting Started

## Local Setup

1. Clone the repository and move to the project directory:

    ```bash
    git clone https://github.com/your-username/your-repo-name
    cd your-repo-name
    ```
## Virtual Environment Setup

2. Create a virtual environment:

    ```bash
    python3 -m venv venv
    ```

3. Activate the virtual environment:

    - ### On Windows:

        ```bash
        .\venv\Scripts\activate
        ```

    - ### On Linux:

        ```bash
        source venv/bin/activate
        ```

## Installing Dependencies And Run Server

4. Install dependencies 

    ```bash
    pip install -r requirements.txt
    ```

5. Apply migrations:

    ```bash
    python3 manage.py makemigrations
    python3 manage.py migrate
    ```
6. Run server:

    ```bash
    python manage.py runserver
    ```
    The application will be accessible at [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

## Docker Setup 🐳

To build and run the Django E-Commerce App using Docker, follow these steps:

1. Build the Docker image:

    ```bash
    make build
    ```

2. Start the Docker containers:

    ```bash
    make up
    ```

    Alternatively, you can combine both steps with a single command:

    ```bash
    make build-up
    ```

    The application will be accessible at [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

### Additional Docker Commands:

- To stop and remove Docker containers:

    ```bash
    make down
    ```

Make sure to have Docker and Docker Compose installed before running these commands. If you encounter any issues, refer to the [Local Setup](#local-setup) section for alternative methods.

Feel free to adjust the instructions based on your specific needs or provide more details if necessary.


# API Documentation

Django E-Commerce App is an e-commerce application built with Django and Django REST Framework.

Explore the API.

## User Endpoints


| Method | Endpoint                  | Description           | Body                                    | Header    | Response            |
|--------|---------------------------|-----------------------|-----------------------------------------|-----------|---------------------|
| POST   | `/api/v1/users/signup/`    | Register a new user  | (email,first_name, last_name, password) | -         | New user data       |
| POST   | `/api/v1/users/login/`     | Login a user         |   (email, password)                     | -         | JWT tokens          |
| POST   | `/api/v1/users/logout/`    | Logout a user        |    (refresh token)                      | -         | success logout msg  |


![-------------------------------------------------------------](https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/rainbow.png)

## Order Endpoints

| Method| Endpoint                         |  Description           | Body                        | Header               | Response            |
|-------|----------------------------------|----------------------- |-----------------------------|----------------------|---------------------|
| POST  | `/api/v1/orders/`                |    Create a new order  | (cart data)                 | Authorization token  | New order data      |
| GET   | `/api/v1/orders/all/`            | Get all orders         | -                           | Authorization token  | List of orders      |
| GET   | `/api/v1/orders/<int:pk>/`       | Get order details      | -                           | Authorization token  | Order details       |
| DELETE| `/api/v1/orders/<int:pk>/cancel/`| Cancel an order        | -                           | Authorization token  | Success message     |

![-------------------------------------------------------------](https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/rainbow.png)

## Cart Endpoints

| Method | Endpoint                  | Description           | Body                        | Header               | Response            |
|--------|---------------------------|-----------------------|-----------------------------|----------------------|---------------------|
| GET    | `/api/v1/carts/`    | Get user's cart   | - | Authorization token | User's cart data       |
| POST   | `/api/v1/carts/add/<int:product_id>/`        | Add product to cart         | quantity | Authorization token      | Success message    |
| POST   | `/api/v1/carts/remove/<int:product_id>/`      | Remove product from cart   | quantity | Authorization token | Success message |
  
![-------------------------------------------------------------](https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/rainbow.png)

## Product Endpoints

| Method | Endpoint                                      | Description                      | Body       | Header               | Response            |
|--------|-----------------------------------------------|----------------------------------|------------|----------------------|---------------------|
| GET    | `/api/v1/products/`                           | List all products                | -          | -                    | List of products    |
| POST   | `/api/v1/products/`                           | Create a new product             | (data)     | Authorization token  | New product data    |
| GET    | `/api/v1/products/<int:pk>/`                 | Retrieve product details         | -          | -                    | Product details     |
| PUT    | `/api/v1/products/<int:pk>/`                 | Update product details           | (data)     | Authorization token  | Updated product data|
| DELETE | `/api/v1/products/<int:pk>/`                 | Delete a product                 | -          | Authorization token  | Success message     |
| GET    | `/api/v1/products/<int:pk>/images/`          | List all images for a product    | -          | -                    | List of images      |
| POST   | `/api/v1/products/<int:pk>/images/`          | Add an image to a product        | (image)    | Authorization token  | Success message     |
| GET    | `/api/v1/products/<int:pk>/images/<int:image_id>/` | Retrieve an image for a product | -          | -                    | Image details       |
| PUT    | `/api/v1/products/<int:pk>/images/<int:image_id>/` | Update an image for a product | (image)    | Authorization token  | Success message     |
| DELETE | `/api/v1/products/<int:pk>/images/<int:image_id>/` | Delete an image from a product | -          | Authorization token  | Success message     |
| DELETE | `/api/v1/img-products/<int:product_id>/images/delete-all/` | Delete all images from a product | -          | Authorization token  | Success message |



