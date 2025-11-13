import graphene
import graphql_jwt
import users.schema

class Query(users.schema.Query, graphene.ObjectType):
    # This class will inherit from multiple Queries
    # as we begin to add more apps.
    pass

class ObtainJSONWebTokenWithUser(graphql_jwt.ObtainJSONWebToken):
    user = graphene.Field(users.schema.UserType)

    @classmethod
    def resolve(cls, root, info, **kwargs):
        # The default resolve method in ObtainJSONWebToken handles authentication
        # and returns an instance of the mutation itself.
        # We call the superclass resolve method to get the authenticated user
        # and then return an instance of our custom mutation class with the user object.
        # The user is available on info.context.user after successful authentication.
        return cls(user=info.context.user)

class Mutation(users.schema.Mutation, graphene.ObjectType):
    token_auth = ObtainJSONWebTokenWithUser.Field()
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()

schema = graphene.Schema(query=Query, mutation=Mutation)
