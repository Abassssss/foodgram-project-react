from django.contrib.auth import get_user_model
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from .models import (
    Follow,
    Ingredient,
    IngredientInRecipe,
    Recipe,
    RecipeInCart,
    RecipeInFavorite,
    Tag,
)

User = get_user_model()


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ("id", "name", "color", "slug")


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ("id", "name", "measurement_unit")
        read_only_fields = ("name", "measurement_unit")


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    name = serializers.CharField(source="ingredient.name", read_only=True)
    measurement_unit = serializers.CharField(
        source="ingredient.measurement_unit", read_only=True
    )

    class Meta:
        model = IngredientInRecipe
        fields = (
            "id",
            "name",
            "measurement_unit",
            "amount",
        )
        read_only_fields = ("name", "measurement_unit")


class RecipeCreateSerializer(serializers.ModelSerializer):
    image = Base64ImageField()
    ingredients = IngredientInRecipeSerializer(many=True)

    class Meta:
        model = Recipe
        fields = (
            "tags",
            "ingredients",
            "name",
            "image",
            "text",
            "cooking_time",
        )

    def create(self, validated_data):
        tags_data = validated_data.pop("tags")
        ingredients_data = validated_data.pop("ingredients")

        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags_data)

        ingredients = []
        for ingredient in ingredients_data:
            ingredients.append(
                IngredientInRecipe(
                    recipe=recipe,
                    ingredient=ingredient["id"],
                    amount=ingredient["amount"],
                )  # 😢
            )

        IngredientInRecipe.objects.bulk_create(ingredients)

        return recipe


class RecipeSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()
    tags = TagSerializer(
        many=True,
    )
    ingredients = IngredientInRecipeSerializer(
        source="ingredientinrecipe_set", many=True
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            "id",
            "tags",
            "author",
            "ingredients",
            "is_favorited",
            "is_in_shopping_cart",
            "name",
            "image",
            "text",
            "cooking_time",
        )

    def get_author(self, recipe):
        return UserSerializer(recipe.author, omit=["recipes"]).data

    def get_is_favorited(self, recipe):
        request = self.context.get("request")

        if request is None or request.user.is_anonymous:
            return None

        return RecipeInFavorite.objects.filter(
            user=request.user, recipe=recipe
        ).exists()

    def get_is_in_shopping_cart(self, recipe):
        request = self.context.get("request")

        if request is None or request.user.is_anonymous:
            return None

        return RecipeInCart.objects.filter(
            user=request.user, recipe=recipe
        ).exists()


class FollowSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(
        slug_field="username",
        read_only=True,
        default=serializers.CurrentUserDefault(),
    )
    following = serializers.SlugRelatedField(
        slug_field="username", queryset=User.objects.all()
    )

    def validate(self, data):
        user = self.context["request"].user
        following = data["following"]

        if user == following:
            raise serializers.ValidationError("Нельзя подписаться на себя")

        return data

    class Meta:
        model = Follow
        fields = ("__all__",)
        validators = [
            UniqueTogetherValidator(
                queryset=Follow.objects.all(), fields=["user", "following"]
            )
        ]


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()
    recipes = RecipeSerializer(many=True, read_only=True)
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
            "recipes",
            "recipes_count",
        )
        ref_name = "ReadOnlyUsers"

    def __init__(self, *args, **kwargs):
        omit = kwargs.pop("omit", [])
        super().__init__(*args, **kwargs)
        for field in omit:
            del self.fields[field]

    def get_recipes_count(self, user):
        return user.recipes.count()

    def get_is_subscribed(self, user):
        request = self.context.get("request")

        if request is None or request.user.is_anonymous:
            return None

        return Follow.objects.filter(user=request.user, author=user).exists()


# class RecipeInFavorite(serializers.ModelSerializer):
#     model = RecipeInFavorite
#     # fields =
