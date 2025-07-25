
from rest_framework import status, viewsets
from rest_framework.views import APIView
from rest_framework.authentication import TokenAuthentication
from .permissions import IsAssociationActive
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.conf import settings

from .serializers import HouseSerializer
from  houses.models import House  # update this if your House model is in another app
import traceback

# Create your views here.


#Andriod App API

# --------------------------------
# 👤 User Profile API
# --------------------------------
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profile_view(request):
    user = request.user
    return Response({
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
    })



# --------------------------------
# 🚪 Add House API
# --------------------------------
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_house(request):
    serializer = HouseSerializer(data=request.data)

    if serializer.is_valid():
        try:
            # Save the house with the associated user’s association
            house = serializer.save(association=request.user.association)

            # Send welcome email
            if house.email:
                print("📧 Preparing to send email to:", house.email)

                association_name = house.association.name
                subject = f"🌸 Welcome to {association_name} Residents' Association!"
                from_email = settings.DEFAULT_FROM_EMAIL
                to_email = house.email

                context = {
                    "association_name": association_name,
                    "resident": house.owner_name or "Esteemed Resident",
                    "president": "Mr. Ravi Kambampati",
                    "contact": "+91-9492039333",
                    "email": "contact@colony.org",
                    "portal_link": "https://colony-app.example.com",
                }

                # Render HTML and plain fallback text
                text_content = "Welcome to our community!"
                html_content = render_to_string("andriodapi/welcome_email.html", context)

                # Compose and send email
                msg = EmailMultiAlternatives(subject, text_content, from_email, [to_email])
                msg.attach_alternative(html_content, "text/html")
                msg.send(fail_silently=False)

                print("✅ Email sent successfully.")

        except Exception as e:
            print("❌ Email sending failed:", e)
            traceback.print_exc()

        return Response(HouseSerializer(house).data, status=status.HTTP_201_CREATED)

    # Return serializer errors if validation fails
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# # --------------------------------
# # 🏠 House Type Choices
# # --------------------------------
# class HouseTypeChoices(APIView):
#     permission_classes = [IsAuthenticated, IsAssociationActive]
#
#     def get(self, request):
#         choices = [
#             {"value": "individual", "label": "Individual"},
#             {"value": "apartment", "label": "Apartment"},
#             {"value": "mall", "label": "Mall"}
#         ]
#         return Response(choices)


# --------------------------------
# 🏘️ House ViewSet
# --------------------------------
class HouseViewSet(viewsets.ModelViewSet):
    serializer_class = HouseSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsAssociationActive]

    def get_queryset(self):
        return House.objects.filter(association=self.request.user.association)

    def perform_create(self, serializer):
        serializer.save(association=self.request.user.association)


# --------------------------------
# 📱 GET House by Mobile Number
# --------------------------------
# @api_view(['GET'])
# @permission_classes([IsAuthenticated])
# def get_house_by_mobile(request):
#     mobile = request.GET.get('mobile')
#     if not mobile:
#         return Response({"error": "Missing mobile parameter"}, status=status.HTTP_400_BAD_REQUEST)
#
#     try:
#         house = House.objects.get(phone_number=mobile, association=request.user.association)
#         serializer = HouseSerializer(house)
#         return Response(serializer.data)
#     except House.DoesNotExist:
#         return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_house_by_mobile(request):
    mobile = request.GET.get('mobile')

    if not mobile:
        return Response({"error": "Mobile number is required."}, status=400)

    houses = House.objects.filter(phone_number=mobile, association=request.user.association)

    if not houses.exists():
        return Response({"message": "No house found for this mobile number."}, status=404)

    serializer = HouseSerializer(houses, many=True)
    return Response(serializer.data)







