from datetime import datetime

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import load_only

from app import password_policy
from app.database import db_session
from app.models import Register, UserAdmin, ExternalSiteUser
from flask import jsonify, make_response
from flask_apispec import doc, use_kwargs
from flask_apispec.views import MethodResource
from flask_restful import Resource
from marshmallow import fields, Schema
from werkzeug.security import generate_password_hash


class AdminUserRegistrationSchema(Schema):
    token = fields.String(required=True)
    first_name = fields.String(required=False)
    last_name = fields.String(required=False)
    password = fields.String(required=True)


class UserRegister(MethodResource, Resource):
    """Provides api for register a new Admin Users"""

    @doc(description='This endpoint provide registering option for admin users.', tags=['User Registration'],
         params={
             'token': {
                 'description': 'Invitation token',
                 'in': 'query',
                 'type': 'string',
                 'required': True
             },
             'first_name': {
                 'description': 'User\' First Name.',
                 'in': 'query',
                 'type': 'string',
                 'required': False
             },
             'last_name': {
                 'description': 'User\' Last Name.',
                 'in': 'query',
                 'type': 'string',
                 'required': False
             },
             'password': {
                 'description': 'Account password.',
                 'in': 'query',
                 'type': 'string',
                 'required': True
             },
         },
         responses={200: {'description': 'Пользователь успешно зарегистрирован.'},
                    400: {'description': "Введенный пароль не соответствует политике паролей."},
                    401: {'description': "Для регистрации необходимо указать пароль."},
                    403: {'description': "Приглашение не было найдено или просрочено. "
                                         "Пожалуйста свяжитесь с своим системным администратором."},

                    }
         )
    @use_kwargs(AdminUserRegistrationSchema)
    def post(self, **kwargs):
        token = kwargs.get("token")
        password = kwargs.get("password")
        registration_record = Register.query.filter_by(token=token).first()

        if (not registration_record
                or registration_record.token_expiration_date < datetime.now()):
            return make_response(jsonify(message="Приглашение не было найдено или просрочено. "
                                                 "Пожалуйста свяжитесь с своим системным администратором."), 403)
        # This key is no longer required.
        del kwargs['token']

        if not password:
            return make_response(jsonify("Для регистрации необходимо указать пароль."), 401)

        kwargs['email'] = registration_record.email
        kwargs['password'] = generate_password_hash(password)

        if not password_policy.validate(password):
            return make_response(jsonify(message="Введенный пароль не соответствует политике паролей."), 400)

        # Create a new Admin user
        db_session.add(UserAdmin(**kwargs))
        # delete invitation
        db_session.delete(registration_record)
        db_session.commit()

        return make_response(jsonify(message="Пользователь успешно зарегистрирован."), 200)


class ExternalUserRegistration(MethodResource, Resource):

    @doc(description='Receives user data from the portal for further registration.', tags=['User Registration'])
    @use_kwargs(
        {'id': fields.Int(required=True),
         'id_hash': fields.Str(description='md5 hash of external_id', required=True),
         'first_name': fields.Str(required=True),
         'last_name': fields.Str(required=True),
         'email': fields.Str(required=True),
         'specializations': fields.Str(required=True)}
    )
    def post(self, **kwargs):
        external_id = kwargs.get('id')

        user = ExternalSiteUser.query.options(load_only('external_id')).filter_by(external_id=external_id).first()
        if user:
            user.first_name = kwargs.get('first_name')
            user.last_name = kwargs.get('last_name')
            user.specializations = kwargs.get('specializations')
            user.updated_date = datetime.now()

        else:
            user = ExternalSiteUser(
                external_id=external_id,
                external_id_hash=kwargs.get('id_hash'),
                first_name=kwargs.get('first_name'),
                last_name=kwargs.get('last_name'),
                email=kwargs.get('email'),
                specializations=kwargs.get('specializations'),
            )
            db_session.add(user)

        try:
            db_session.commit()
        except IntegrityError:
            return make_response(jsonify(message='some mistake'), 400)

        return make_response(jsonify(message='successful'), 200)
