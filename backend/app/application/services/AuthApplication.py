from app.infrastructure.repositories.PointSaleEmailLoginCodeRepository import PointSaleEmailLoginCodeRepository
from app.infrastructure.repositories.WordpressUserRepository import WordpressUserRepository
from app.application.services.WordpressPasswordVerifier import WordpressPasswordVerifier
from app.domain.interfaces.IApplicationUserRepository import IApplicationUserRepository
from app.domain.interfaces.IPointSaleEmailRepository import IPointSaleEmailRepository
from app.domain.dtos.AuthDto import LoginDto, AuthResponseDto, AuthUserDto
from app.infrastructure.repositories.RoleRepository import RoleRepository
from app.application.interfaces.IAuthApplication import IAuthApplication
from app.application.services.EmailService import EmailService
from app.application.services.JwtService import JwtService
from datetime import datetime, timedelta, timezone
from app.infrastructure.db.config import settings
import hashlib
import secrets
import hmac
import time

POINT_SALE_ROLE_NAME = "PDV"

class AuthApplication(IAuthApplication):

    def __init__(
        self,
        applicationUserRepository: IApplicationUserRepository,
        wordpressUserRepository: WordpressUserRepository,
        wordpressPasswordVerifier: WordpressPasswordVerifier,
        roleRepository: RoleRepository,
        pointSaleEmailRepository: IPointSaleEmailRepository,
        pointSaleEmailLoginCodeRepository: PointSaleEmailLoginCodeRepository,
        emailService: EmailService
    ):
        self.applicationUserRepository = applicationUserRepository
        self.wordpressUserRepository = wordpressUserRepository
        self.wordpressPasswordVerifier = wordpressPasswordVerifier
        self.roleRepository = roleRepository
        self.pointSaleEmailRepository = pointSaleEmailRepository
        self.pointSaleEmailLoginCodeRepository = pointSaleEmailLoginCodeRepository
        self.emailService = emailService

    def _nowBogota(self) -> datetime:
        colombiaTimezone = timezone(timedelta(hours=-5))
        return datetime.now(colombiaTimezone).replace(tzinfo=None)

    def _normalizeEmail(self, email: str) -> str:
        return email.strip().lower()

    def _hashPointSaleCode(self, email: str, code: str) -> str:
        value = f"{self._normalizeEmail(email)}.{code}.{settings.JWT_SECRET_KEY}"
        return hashlib.sha256(value.encode("utf-8")).hexdigest()

    def login(self, loginData: LoginDto) -> AuthResponseDto:
        username = loginData.username.strip()

        wordpressUser = self.wordpressUserRepository.getByLoginOrEmail(username)

        if not wordpressUser:
            raise ValueError("Usuario o contraseña incorrectos.")

        passwordIsValid = self.wordpressPasswordVerifier.verify(loginData.password, wordpressUser["wordpressUserPass"])

        if not passwordIsValid:
            raise ValueError("Usuario o contraseña incorrectos.")

        return self._authorizeAndBuildAuthResponse(wordpressUser)
    
    def requestPointSaleEmailCode(self, emailPointSale: str) -> None:
        email = self._normalizeEmail(emailPointSale)

        pointSaleEmail = self.pointSaleEmailRepository.getByEmail(email)

        if not pointSaleEmail:
            raise ValueError("El correo de punto de venta no está registrado.")

        if not pointSaleEmail.statusPointSaleEmail:
            raise ValueError("El correo de punto de venta está inactivo.")

        now = self._nowBogota()
        code = str(secrets.randbelow(1000000)).zfill(6)
        codeHash = self._hashPointSaleCode(email, code)
        expiresAt = now + timedelta(minutes=settings.POINT_SALE_LOGIN_CODE_EXPIRE_MINUTES)

        self.pointSaleEmailLoginCodeRepository.invalidatePendingCodes(pointSaleEmail.IdPointSaleEmail, now)
        self.pointSaleEmailLoginCodeRepository.create(pointSaleEmail.IdPointSaleEmail, codeHash, expiresAt, now)
        self.emailService.sendPointSaleLoginCode(email, code)

    def verifyPointSaleEmailCode(self, emailPointSale: str, code: str) -> AuthResponseDto:
        email = self._normalizeEmail(emailPointSale)
        cleanCode = code.strip()

        if not cleanCode.isdigit() or len(cleanCode) != 6:
            raise ValueError("El código debe tener 6 dígitos.")

        pointSaleEmail = self.pointSaleEmailRepository.getByEmail(email)

        if not pointSaleEmail:
            raise ValueError("El correo de punto de venta no está registrado.")

        if not pointSaleEmail.statusPointSaleEmail:
            raise ValueError("El correo de punto de venta está inactivo.")

        now = self._nowBogota()

        loginCode = self.pointSaleEmailLoginCodeRepository.getLatestAvailableCode(pointSaleEmail.IdPointSaleEmail, now)

        if not loginCode:
            raise ValueError("El código no existe o ya expiró.")

        if loginCode.attempts >= settings.POINT_SALE_LOGIN_MAX_ATTEMPTS:
            raise ValueError("El código superó el número máximo de intentos.")

        expectedHash = self._hashPointSaleCode(email, cleanCode)

        if not hmac.compare_digest(expectedHash, loginCode.codeHash):
            self.pointSaleEmailLoginCodeRepository.increaseAttempts(loginCode)
            raise ValueError("El código ingresado no es válido.")

        self.pointSaleEmailLoginCodeRepository.markAsUsed(loginCode, now)

        return self._buildPointSaleEmailAuthResponse(pointSaleEmail)

    def intranetAccess(self, userLogin: str, ts: int, sig: str) -> AuthResponseDto:
        self._validateIntranetSignature(userLogin, ts, sig)

        wordpressUser = self.wordpressUserRepository.getByLogin(userLogin)

        if not wordpressUser:
            raise PermissionError("Usuario de WordPress no encontrado.")

        return self._authorizeAndBuildAuthResponse(wordpressUser)

    def getCurrentUser(self, wordpressUserId: int) -> AuthResponseDto:
        wordpressUser = self.wordpressUserRepository.getById(wordpressUserId)

        if not wordpressUser:
            raise PermissionError("Usuario de WordPress no encontrado.")

        return self._authorizeAndBuildAuthResponse(wordpressUser)
    
    def getCurrentPointSaleEmailUser(self, pointSaleEmailId: int) -> AuthResponseDto:
        pointSaleEmail = self.pointSaleEmailRepository.getById(pointSaleEmailId)

        if not pointSaleEmail:
            raise PermissionError("Correo de punto de venta no encontrado.")

        if not pointSaleEmail.statusPointSaleEmail:
            raise PermissionError("El correo de punto de venta está inactivo.")

        return self._buildPointSaleEmailAuthResponse(pointSaleEmail)
    
    def _buildPointSaleEmailAuthResponse(self, pointSaleEmail) -> AuthResponseDto:
        role = self.roleRepository.getByName(POINT_SALE_ROLE_NAME)

        if not role:
            raise PermissionError("No existe el rol PDV.")

        if not role.statusRole:
            raise PermissionError("El rol PDV está inactivo.")

        menuOptions = self.roleRepository.getMenuOptionsByRole(role.IdRole)

        tokenPayload = {
            "sub": f"pdv:{pointSaleEmail.IdPointSaleEmail}",
            "authType": "POINT_SALE_EMAIL",
            "pointSaleEmailId": pointSaleEmail.IdPointSaleEmail,
            "pointSaleEmail": pointSaleEmail.emailPointSale,
            "roleIds": [role.IdRole]
        }

        accessToken = JwtService.createToken(tokenPayload)

        return AuthResponseDto(
            accessToken=accessToken,
            user=AuthUserDto(
                IdApplicationUser=None,
                wordpressUserId=None,
                wordpressUserLogin=pointSaleEmail.emailPointSale,
                wordpressUserEmail=pointSaleEmail.emailPointSale,
                wordpressDisplayName=pointSaleEmail.emailPointSale,
                pointSaleEmailId=pointSaleEmail.IdPointSaleEmail,
                pointSaleEmail=pointSaleEmail.emailPointSale,
                roles=[role],
                menuOptions=menuOptions
            )
        )

    def _authorizeAndBuildAuthResponse(self, wordpressUser: dict) -> AuthResponseDto:
        applicationUser = self.applicationUserRepository.getByWordpressUserId(wordpressUser["wordpressUserId"])

        if not applicationUser:
            raise PermissionError("El usuario no está autorizado para ingresar al aplicativo.")

        if not applicationUser.statusApplicationUser:
            raise PermissionError("El usuario está inactivo en el aplicativo.")

        roles = self.applicationUserRepository.getRolesByApplicationUser(applicationUser.IdApplicationUser)

        if not roles:
            raise PermissionError("El usuario no tiene roles asignados.")

        menuOptions = self.applicationUserRepository.getMenuOptionsByApplicationUser(applicationUser.IdApplicationUser)

        tokenPayload = {
            "sub": str(wordpressUser["wordpressUserId"]),
            "wordpressUserId": wordpressUser["wordpressUserId"],
            "wordpressUserLogin": wordpressUser["wordpressUserLogin"],
            "IdApplicationUser": applicationUser.IdApplicationUser,
            "roleIds": [role.IdRole for role in roles]
        }

        accessToken = JwtService.createToken(tokenPayload)

        return AuthResponseDto(
            accessToken=accessToken,
            user=AuthUserDto(
                IdApplicationUser=applicationUser.IdApplicationUser,
                wordpressUserId=wordpressUser["wordpressUserId"],
                wordpressUserLogin=wordpressUser["wordpressUserLogin"],
                wordpressUserEmail=wordpressUser["wordpressUserEmail"],
                wordpressDisplayName=wordpressUser["wordpressDisplayName"],
                roles=roles,
                menuOptions=menuOptions
            )
        )

    def _validateIntranetSignature(self, userLogin: str, ts: int, sig: str) -> None:
        now = int(time.time())

        if ts > now + 60:
            raise PermissionError("La firma de intranet tiene una fecha inválida.")

        if now - ts > settings.INTRANET_SSO_EXPIRE_SECONDS:
            raise PermissionError("El enlace de intranet expiró.")

        message = f"{userLogin}.{ts}".encode("utf-8")

        expectedSignature = hmac.new(
            settings.INTRANET_SSO_SECRET.encode("utf-8"),
            message,
            hashlib.sha256
        ).hexdigest()

        if not hmac.compare_digest(expectedSignature, sig):
            raise PermissionError("La firma de intranet no es válida.")