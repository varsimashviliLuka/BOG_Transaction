from flask_restx import reqparse, inputs
from src.extensions import api


auth_ns = api.namespace('Authentification', description='API მომხმარებლის აუტენტიფიკაციის შესახებ', path='/api')

registration_parser = reqparse.RequestParser()

registration_parser.add_argument('email', type=inputs.email(check=True), required=True, help="გთხოვთ შეიყვანეთ მეილი luka.varsimashvili@iliauni.edu.ge")
registration_parser.add_argument('password', type=str, required=True, help="გთხოვთ შეიყვანეთ პაროლი")
registration_parser.add_argument('passwordRepeat', type=str, required=True, help='გთხოვთ გაიმეორეთ პაროლი')

# Auth parser
auth_parser = reqparse.RequestParser()
auth_parser.add_argument("email", required=True, type=str, help="გთხოვთ შეიყვანეთ მეილი luka.varsimashvili@iliauni.edu.ge")
auth_parser.add_argument("password", required=True, type=str, help="გთხოვთ შეიყვანეთ პაროლი")