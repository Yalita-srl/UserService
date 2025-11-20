import graphene
from graphene_django import DjangoObjectType
from graphql_jwt.decorators import login_required, staff_member_required
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator

User = get_user_model()

# 1. GraphQL Type for User Model
class UserType(DjangoObjectType):
    class Meta:
        model = User
        fields = ("id", "email", "name", "phone", "address", "role", "created_at")

# 2. Input Type for Mutations
class UserInput(graphene.InputObjectType):
    email = graphene.String(required=True)
    password = graphene.String(required=True)
    name = graphene.String(required=True)
    phone = graphene.String()
    address = graphene.String()
    role = graphene.String(default_value="user")

# 3. Queries
class Query(graphene.ObjectType):
    # Get a single user by ID
    user = graphene.Field(UserType, id=graphene.ID(required=True))
    
    # Get a paginated list of all users (admin only)
    users = graphene.List(
        UserType,
        page=graphene.Int(),
        limit=graphene.Int()
    )

    @login_required
    def resolve_user(self, info, id):
        """
        Retrieves a user by their ID.
        Authorization:
        - Any logged-in user can request their own profile.
        - Admins can request any user's profile.
        - Restaurant owners can only request their own profile.
        """
        current_user = info.context.user
        target_user = User.objects.filter(id=id).first()

        if not target_user:
            return None

        # Admin can see anyone
        if current_user.is_admin:
            return target_user
        
        # Restaurant owner can only see themselves
        if current_user.is_restaurant_owner and current_user.id != target_user.id:
            raise Exception("You are not authorized to view this profile.")

        # Regular user can only see themselves
        if current_user.id == target_user.id:
            return target_user
        
        raise Exception("You are not authorized to view this profile.")

    @staff_member_required
    def resolve_users(self, info, page=1, limit=10):
        """
        Retrieves a paginated list of all users.
        Authorization: Admin only.
        """
        paginator = Paginator(User.objects.all().order_by('id'), limit)
        page_obj = paginator.get_page(page)
        return page_obj.object_list

# 4. Mutations

# Register a new user
class RegisterUser(graphene.Mutation):
    user = graphene.Field(UserType)

    class Arguments:
        input = UserInput(required=True)

    def mutate(self, info, input):
        if User.objects.filter(email=input.email).exists():
            raise Exception("Email already exists.")
        
        # Ensure only admins can create other admins or restaurant owners
        current_user = info.context.user
        if input.role in ['admin', 'restaurant_owner'] and (not current_user.is_authenticated or not current_user.is_admin):
            raise Exception("You are not authorized to create this type of user.")

        user = User.objects.create_user(
            email=input.email,
            password=input.password,
            name=input.name,
            phone=input.phone,
            address=input.address,
            role=input.role
        )
        return RegisterUser(user=user)

# Update an existing user
class UpdateUser(graphene.Mutation):
    user = graphene.Field(UserType)

    class Arguments:
        id = graphene.ID(required=True)
        input = UserInput(required=True)

    @login_required
    def mutate(self, info, id, input):
        current_user = info.context.user
        user_to_update = User.objects.get(pk=id)

        # Check authorization
        if not current_user.is_admin and current_user.id != user_to_update.id:
            raise Exception("You are not authorized to perform this action.")

        # Update fields
        user_to_update.email = input.email
        user_to_update.name = input.name
        user_to_update.phone = input.phone
        user_to_update.address = input.address
        
        # Only admin can change role
        if current_user.is_admin:
            user_to_update.role = input.role

        if input.password:
            user_to_update.set_password(input.password)
        
        user_to_update.save()
        return UpdateUser(user=user_to_update)

# Delete a user
class DeleteUser(graphene.Mutation):
    success = graphene.Boolean()
    id = graphene.ID()

    class Arguments:
        id = graphene.ID(required=True)

    @staff_member_required
    def mutate(self, info, id):
        try:
            user_to_delete = User.objects.get(pk=id)
            user_to_delete.delete()
            return DeleteUser(success=True, id=id)
        except User.DoesNotExist:
            raise Exception("User not found.")


class Mutation(graphene.ObjectType):
    register_user = RegisterUser.Field()
    update_user = UpdateUser.Field()
    delete_user = DeleteUser.Field()
