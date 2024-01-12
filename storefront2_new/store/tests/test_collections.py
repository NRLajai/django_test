from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APIClient
import pytest
from store.models import Collection, Product
from model_bakery import baker


@pytest.fixture
# def create_collection(api_client, collection):        # if we pass a collection as parameter directly, ficture will through error
def create_collection(api_client):
    def do_create_collection(collection):
        return api_client.post("/store/collections/", collection)
    return do_create_collection

@pytest.fixture
def authenticate(api_client):
    def do_authenticate(is_staff=False):
        return api_client.force_authenticate(user=User(is_staff=is_staff))
    return do_authenticate



@pytest.mark.django_db                      # tests to access DB
class TestCreateCollection:

    # @pytest.mark.skip
    def test_if_user_is_anonymous_returns_401(self, api_client, create_collection):
        response = create_collection({"title": "a"})

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_if_user_is_not_admin_returns_403(api_client, create_collection, authenticate):
        authenticate()

        response = create_collection({"title": "a"})

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_if_data_is_invalid_returns_400(api_client, create_collection, authenticate):
        authenticate(is_staff=True)

        response = create_collection({"title": ""})

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["title"] is not None
        
    def test_if_data_is_valid_returns_201(api_client, create_collection, authenticate):
        authenticate(is_staff=True)

        response = create_collection({"title": "a"})

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["id"] > 0


@pytest.mark.django_db
class TestRetriveCollection:
    def test_if_collection_exists_returns_200(self, api_client):
        collection = baker.make(Collection)
        # baker.make(Product, collection=collection, _quantity=10)        # all 10 products will be same collection
        # print(collection.__dict__)

        response = api_client.get(f"/store/collections/{collection.id}/")

        # assert False
        assert response.status_code == status.HTTP_200_OK
        assert response.data == {
            "id" : collection.id,
            "title" : collection.title,
            "products_count" : 0
        }

# AAA (Arrange, Act, Assert) 

# @pytest.mark.django_db
# class TestCreateCollection:
# 
    # @pytest.mark.skip
    # def test_if_user_is_anonymous_returns_401(self):
        # client = APIClient()
        # response = client.post("/store/collections/", {"title": "a"})
# 
        # assert response.status_code == status.HTTP_401_UNAUTHORIZED
# 
    # def test_if_user_is_not_admin_returns_403(self):
        # client = APIClient()
        # client.force_authenticate(user={})        
        # response = client.post("/store/collections/", {"title": "a"})
# 
        # assert response.status_code == status.HTTP_403_FORBIDDEN
# 
    # def test_if_data_is_invalid_returns_400(self):
        # client = APIClient()
        # client.force_authenticate(user=User(is_staff=True))        
        # response = client.post("/store/collections/", {"title": ""})
# 
        # assert response.status_code == status.HTTP_400_BAD_REQUEST
        # assert response.data["title"] is not None
        # 
    # def test_if_data_is_valid_returns_201(self):
        # client = APIClient()
        # client.force_authenticate(user=User(is_staff=True))        
        # response = client.post("/store/collections/", {"title": "a"})
# 
        # assert response.status_code == status.HTTP_201_CREATED
        # assert response.data["id"] > 0


