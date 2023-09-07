from django.contrib.auth.models import User
from drf_yasg.utils import swagger_auto_schema
from rest_framework import serializers
from rest_framework.decorators import action
from django.contrib.auth import authenticate
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ["password"]


class UserListCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ["id"]


class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=200)
    password = serializers.CharField(max_length=60)

    def validate(self, attrs):
        user = authenticate(username=attrs.get("username"), password=attrs.get("password"))
        if not user:
            raise ValidationError("User not found")
        return True


class UserLoginResponseSerializer(serializers.Serializer):
    message = serializers.CharField(max_length=256)
    code = serializers.CharField(max_length=10)


class UserViewSet(ModelViewSet):
    lookup_field = "username"
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def list(self, requset, *args, **kwargs):
        return Response({"data": self.queryset.values_list(flat=True)})

    def retrieve(self, request, username, *args, **kwargs):
        user = User.objects.filter(username=username).last()
        if not user:
            return Response(status=404, data={"message": "Not found"})
        return Response(status=200, data=UserSerializer(user).data)

    def update(self, request, username, *args, **kwargs):
        user = User.objects.filter(username=username).last()
        if not user:
            return Response(status=404, data={"message": "Not found"})
        serializer = UserSerializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=200, data=serializer.data)

    @action(methods=["POST"], detail=False)
    def login(self, request, *args, **kwargs):
        print("*" * 20, flush=True)
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        resonse_dict = {"message": "Successful", "code": "SUCCESSFUL"}
        return Response(status=200, data=UserLoginResponseSerializer(resonse_dict).data)

    @action(methods=["POST"], detail=False)
    def logout(self, request, *args, **kwargs):
        resonse_dict = {"message": "Successful", "code": "SUCCESSFUL"}
        return Response(status=200, data=UserLoginResponseSerializer(resonse_dict).data)

    @swagger_auto_schema(request_body=UserListCreateSerializer, responses={201: UserLoginResponseSerializer})
    @action(methods=["POST"], detail=False)
    def createWithList(self, request, *args, **kwargs):
        serializer = UserListCreateSerializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)
        for u in serializer.data:
            User.objects.create_user(**u)

        resonse_dict = {"message": "Successful", "code": "SUCCESSFUL"}
        return Response(status=201, data=UserLoginResponseSerializer(resonse_dict).data)