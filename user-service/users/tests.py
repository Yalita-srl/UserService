import json
from django.test import TestCase
from django.contrib.auth import get_user_model
from graphene_django.utils.testing import GraphQLTestCase

User = get_user_model()

class UserGraphQLTests(GraphQLTestCase):
    GRAPHQL_URL = "/graphql"

    def setUp(self):
        self.admin_user = User.objects.create_superuser(
            email="admin@test.com",
            password="adminpassword",
            name="Admin User",
            role="admin"
        )
        self.normal_user = User.objects.create_user(
            email="user@test.com",
            password="userpassword",
            name="Normal User",
            role="user"
        )

    def test_register_user_mutation(self):
        response = self.query(
            '''
            mutation registerUser($input: UserInput!) {
              registerUser(input: $input) {
                user {
                  id
                  email
                  name
                }
              }
            }
            ''',
            op_name='registerUser',
            input_data={
                "email": "newuser@test.com",
                "password": "newpassword",
                "name": "New User"
            }
        )
        self.assertResponseNoErrors(response)
        content = json.loads(response.content)
        self.assertEqual(content['data']['registerUser']['user']['email'], 'newuser@test.com')
        self.assertTrue(User.objects.filter(email='newuser@test.com').exists())

    def test_login_mutation(self):
        response = self.query(
            '''
            mutation tokenAuth($email: String!, $password: String!) {
              tokenAuth(email: $email, password: $password) {
                token
              }
            }
            ''',
            op_name='tokenAuth',
            variables={'email': 'user@test.com', 'password': 'userpassword'}
        )
        self.assertResponseNoErrors(response)
        content = json.loads(response.content)
        self.assertIn('token', content['data']['tokenAuth'])

    def test_users_query_unauthorized(self):
        # A normal user tries to get the list of all users
        response = self.query(
            '''
            query users {
              users {
                id
                email
              }
            }
            ''',
            op_name='users',
            headers=self.get_headers_for_user(self.normal_user)
        )
        # Expect an error because only admins can do this
        self.assertResponseHasErrors(response)

    def test_users_query_authorized(self):
        # An admin user gets the list of all users
        response = self.query(
            '''
            query users {
              users {
                id
                email
              }
            }
            ''',
            op_name='users',
            headers=self.get_headers_for_user(self.admin_user)
        )
        self.assertResponseNoErrors(response)
        content = json.loads(response.content)
        self.assertEqual(len(content['data']['users']), 2) # admin + normal user

    def get_headers_for_user(self, user):
        response = self.query(
            '''
            mutation tokenAuth($email: String!, $password: String!) {
              tokenAuth(email: $email, password: $password) {
                token
              }
            }
            ''',
            op_name='tokenAuth',
            variables={'email': user.email, 'password': 'userpassword' if user.role == 'user' else 'adminpassword'}
        )
        content = json.loads(response.content)
        token = content['data']['tokenAuth']['token']
        return {'HTTP_AUTHORIZATION': f'JWT {token}'}