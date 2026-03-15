from flask_restx import Resource

from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from src.models import User
from src.api.nsmodels import auth_ns, registration_parser, auth_parser



@auth_ns.route('/registration')
@auth_ns.doc(responses={200: 'OK', 400: 'Invalid Argument', 401: 'JWT Token Expires', 403: 'Forbidden', 404: 'Not Found'})
class RegistrationApi(Resource):
    @auth_ns.doc(parser=registration_parser)
    @jwt_required()
    @auth_ns.doc(security='JsonWebToken')
    def post(self):
        '''მომხმარებლის რეგისტრაცია'''

        args = registration_parser.parse_args()
        identity = get_jwt_identity()

        admin = User.query.filter_by(uuid=identity).first()
        if not admin.check_permission():
            return {"message": 'თქვენ არ გაქვთ მომხმარებლის რეგისტრაციის უფლება'}, 403
    
        # Validate password length and pattern
        if args["password"] != args["passwordRepeat"]:
            return {"error": "პაროლები არ ემთხვევა."}, 400
        
        if len(args["password"]) < 8:
            return {"error": "პაროლი უნდა იყოს მინიმუმ 8 სიმბოლო."}, 400

        if User.query.filter_by(email=args["email"]).first():
            return {"error": "ელ.ფოსტის მისამართი უკვე რეგისტრირებულია."}, 400

        role = Role.query.filter_by(name=args["role_name"]).first()
        if not role:
            return {"error": "როლი ვერ მოიძებნა."}, 400

        new_user = User(
            email=args["email"],
            password=args["password"],
            role_id=role.id
        )

        new_user.create()
        return {"message": 'მომხმარებელი წარმატებით დარეგისტრირდა'}, 200
    
@auth_ns.route('/login')
@auth_ns.doc(responses={200: 'OK', 400: 'Invalid Argument', 401: 'JWT Token Expires', 403: 'Forbidden', 404: 'Not Found'})
class AuthorizationApi(Resource):
    @auth_ns.doc(parser=auth_parser)
    def post(self):
        '''მომხმარებლის სისტემაში შესვლა'''
        args = auth_parser.parse_args()

        # Look up the user by email
        user = User.query.filter_by(email=args["email"]).first()
        if not user:
            return {"error": "შეყვანილი პაროლი ან ელ.ფოსტა არასწორია."}, 400

        # Check if the password matches
        if user.check_password(args["password"]):
            # Create tokens with the user's UUID as the identity
            access_token = create_access_token(identity=user.uuid)
            refresh_token = create_refresh_token(identity=user.uuid)
            return {
                "message": "წარმატებით გაიარეთ ავტორიზაცია.",
                "access_token": access_token,
                "refresh_token": refresh_token
            }, 200
        
        # If the password is incorrect
        else:
            return {"error": "შეყვანილი პაროლი ან ელ.ფოსტა არასწორია."}, 400

@auth_ns.route('/refresh')
@auth_ns.doc(responses={200: 'OK', 400: 'Invalid Argument', 401: 'JWT Token Expires', 403: 'Forbidden', 404: 'Not Found'})
class AccessTokenRefreshApi(Resource):
    @jwt_required(refresh=True)
    @auth_ns.doc(security='JsonWebToken')
    def post(self):
        '''JWT ტოკენის დარეფრეშება'''
        identity = get_jwt_identity()
        access_token = create_access_token(identity=identity)
        response = {
            "access_token": access_token
        }

        return response