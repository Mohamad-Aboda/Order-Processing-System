from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import (
    AllowAny,
    IsAdminUser
)

# Local imports goes here!
from .models import Product, ProductImage
from .utils import multiple_image_upload
from orders.permissions import IsOwnerOrReadOnly
from .serializers import (
    ProductListCreateSerializer,
    ProductImageSerializer,
    ProductRetrieveUpdateDestroySerializer,
)


class ProductListCreateView(APIView):
    def get_permissions(self):
        if self.request.method == "POST":
            permission_classes = [IsAdminUser]
        else:
            permission_classes = [AllowAny]
        return [permission() for permission in permission_classes]

   
    def get(self, request, *args, **kwargs):
        products = Product.objects.all()
        serializer = ProductListCreateSerializer(products, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = ProductListCreateSerializer(
            data=request.data, context={"request": request}
        )
        if serializer.is_valid():
            product = serializer.save(user=request.user)
            response_data = serializer.data
            response_data["user"] = {
                "id": product.user.id,
                "username": product.user.first_name,
                "email": product.user.email,
            }
            return Response(response_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProductRetrieveUpdateDestroyView(APIView):
    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            permission_classes = [IsAdminUser]
        else:
            permission_classes = [AllowAny]
        return [permission() for permission in permission_classes]

    def get(self, request, pk):
        try:
            product = Product.objects.get(pk=pk)
            serializer = ProductRetrieveUpdateDestroySerializer(product)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Product.DoesNotExist:
            return Response(
                {"detail": "Product Does Not Exi."}, status=status.HTTP_404_NOT_FOUND
            )

    def put(self, request, pk):
        try:
            product = Product.objects.get(pk=pk)
            serializer = ProductRetrieveUpdateDestroySerializer(
                product,
                data=request.data,
            )
            if serializer.is_valid() and request.user == product.user:
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(
                    {"detail": "You do not have permission to update this product."},
                    status=status.HTTP_403_FORBIDDEN,
                )
        except Product.DoesNotExist:
            return Response(
                {"detail": "Product Does Not Exist."}, status=status.HTTP_404_NOT_FOUND
            )


    def patch(self, request, pk):
        try:
            product = Product.objects.get(pk=pk)
            serializer = ProductRetrieveUpdateDestroySerializer(
                product,
                data=request.data,
                partial=True
            )
            if serializer.is_valid() and request.user == product.user:
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(
                    {"detail": "You do not have permission to update this product."},
                    status=status.HTTP_403_FORBIDDEN,
                )
        except Product.DoesNotExist:
            return Response(
                {"detail": "Product Does Not Exist."}, status=status.HTTP_404_NOT_FOUND
            )

    def delete(self, request, pk):
        try:
            product = Product.objects.get(pk=pk)
            if request.user == product.user:
                product.delete()
                return Response(
                    {"detail": "Product deleted successfully."},
                    status=status.HTTP_204_NO_CONTENT,
                )
            else:
                return Response(
                    {"detail": "You do not have  permission to delete this product."},
                    status=status.HTTP_403_FORBIDDEN,
                )

        except Product.DoesNotExist:
            return Response(
                {"detail": "Product Does Not Exi."}, status=status.HTTP_404_NOT_FOUND
            )


class ProductImageListCreateView(APIView):
    parser_classes = (
        MultiPartParser,
        FormParser,
    )

    def get_permissions(self):
        if self.request.method == "POST":
            permission_classes = [IsAdminUser]
        else:
            permission_classes = [AllowAny]
        return [permission() for permission in permission_classes]

    """ List all images for single product based on the product id """

    def get(self, request, product_id):
        try:
            product = Product.objects.get(pk=product_id)
            images = ProductImage.objects.filter(product=product)
            serializer = ProductImageSerializer(images, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Product.DoesNotExist:
            return Response(
                {"detail": "Product Does Not Exist."}, status=status.HTTP_404_NOT_FOUND
            )

    """ Handel Single and Multipe image upload """

    def post(self, request, product_id):
        try:
            product = Product.objects.get(pk=product_id)
        except Product.DoesNotExist:
            return Response(
                {"detail": "Product Does Not Exist."}, status=status.HTTP_404_NOT_FOUND
            )

        uploaded_images = []

        """ Handel Multipe Images Upload """
        if multiple_image_upload(request):
            for image_file in request.FILES.getlist("image"):
                image_data = {"image": image_file, "product": product.id}
                serializer = ProductImageSerializer(data=image_data)
                if request.user == product.user:
                    if serializer.is_valid():
                        serializer.save(product=product)
                        uploaded_images.append(serializer.data)
                    else:
                        return Response(
                            serializer.errors, status=status.HTTP_400_BAD_REQUEST
                        )
                else:
                    return Response(
                    {"detail": "Yon don't have permissions to upload image for this product."}, status=status.HTTP_404_NOT_FOUND
                )
        else:
            """Handel Single Images Upload"""
            serializer = ProductImageSerializer(data=request.data)
            if request.user == product.user:
                if serializer.is_valid():
                    serializer.save(product=product)
                    uploaded_images.append(serializer.data)
                else:
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response(
                {"detail": "Yon don't have permissions to upload image for this product."}, status=status.HTTP_404_NOT_FOUND
            )

        return Response(uploaded_images, status=status.HTTP_201_CREATED)


class ProductImageRetrieveUpdateDestroyView(generics.RetrieveUpdateAPIView):
    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']: 
            permission_classes = [IsAdminUser]
        else:  # For other methods, use default permissions (AllowAny)
            permission_classes = [AllowAny]
        return [permission() for permission in permission_classes]
    
    queryset = ProductImage.objects.all()
    serializer_class = ProductImageSerializer


    def get(self, request, product_id, image_id):
        try:
            product = Product.objects.get(pk=product_id)
        except Product.DoesNotExist:
            return Response(
                {"detail": "Product Does Not Exist."}, status=status.HTTP_404_NOT_FOUND
            )

        try:
            image = ProductImage.objects.get(pk=image_id, product=product)
            serializer = ProductImageSerializer(image)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ProductImage.DoesNotExist:
            return Response(
                {"detail": "Product Image Does Not Exist."},
                status=status.HTTP_404_NOT_FOUND,
            )

    def update(self, request, product_id, image_id):
        try:
            product = Product.objects.get(pk=product_id)
        except Product.DoesNotExist:
            return Response(
                {"detail": "Product Does Not Exist."}, status=status.HTTP_404_NOT_FOUND
            )

        try:
            image = ProductImage.objects.get(pk=image_id, product=product)
            serializer = ProductImageSerializer(image, data=request.data)

            if serializer.is_valid() and product.user == request.user:
                serializer.save(product=product)
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except ProductImage.DoesNotExist:
            return Response(
                {"detail": "Product Image Does Not Exist."},
                status=status.HTTP_404_NOT_FOUND,
            )

    def delete(self, request, product_id, image_id):
        try:
            product = Product.objects.get(pk=product_id)
        except Product.DoesNotExist:
            return Response(
                {"detail": "Product Does Not Exist."}, status=status.HTTP_404_NOT_FOUND
            )

        try:
            image = ProductImage.objects.get(pk=image_id, product=product)
        except ProductImage.DoesNotExist:
            return Response(
                {"detail": "Product Image Does Not Exist."},
                status=status.HTTP_404_NOT_FOUND,
            )
        if product.user == request.user:
            image.delete()
            return Response(
                {"detail": "Product Image deleted successfully."},
                status=status.HTTP_204_NO_CONTENT,
            )
        else:    
            return Response(
                {"detail": "You do not have  permission to delete this image."},
                status=status.HTTP_403_FORBIDDEN,
            )


class ProductImagesDeleteAllImagesView(APIView):
    permission_classes = [IsAdminUser]
    def delete(self, request, product_id):
        try:
            product = Product.objects.get(pk=product_id)
        except Product.DoesNotExist:
            return Response(
                {"detail": "Product Does Not Exist."}, status=status.HTTP_404_NOT_FOUND
            )

        if request.user == product.user:
            ProductImage.objects.filter(product=product).delete()
            return Response(
                {"detail": "All Product Images deleted successfully."},
                status=status.HTTP_204_NO_CONTENT,
            )
        else:
            return Response(
                {"detail": "You do not have  permission to delete this image."},
                status=status.HTTP_403_FORBIDDEN,
            )
