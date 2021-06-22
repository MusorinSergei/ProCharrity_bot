from app import docs
from app.apis.users import UsersList, User_item
from app.apis.auth.refresh import Refresh
from app.apis.auth.login import Login
from app.apis.auth.password_reset import PasswordReset
from app.apis.auth.registration import UserRegister
from app.apis.auth.invitation_checker import InvitationChecker
from app.apis.auth.send_reg_invitation import SendRegistrationInvitе
from app.apis.create_categories import CreateCategories
from app.apis.create_tasks import CreateTasks
from app.tg_statistics import Analysis

docs.register(Login)
docs.register(Refresh)
docs.register(UserRegister)
docs.register(PasswordReset)
docs.register(UsersList)
docs.register(User_item)
docs.register(SendRegistrationInvitе)
docs.register(InvitationChecker)
docs.register(CreateCategories)
docs.register(CreateTasks)
docs.register(Analysis)
