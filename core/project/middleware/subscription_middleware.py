import logging

from django.contrib.auth.models import AnonymousUser
from django.http import JsonResponse
from django.urls import (
    resolve,
    Resolver404,
)
from rest_framework.status import HTTP_403_FORBIDDEN
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import (
    InvalidToken,
    TokenError,
)


logger = logging.getLogger("subscription_middleware")


class SubscriptionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.api_prefix = "/api/"
        self.public_api_urls = [
            "v1:register",
            "v1:token_obtain_pair",
            "v1:token_refresh",
            "v1:token_verify",
            "swagger-ui",
            "redoc",
            "schema",
        ]
        self.subscription_exempt_urls_prefixes = [
            "v1:tariff:",
            "v1:subscriptions:",
            "v1:users:",
        ]
        self.jwt_authenticator = JWTAuthentication()
        logger.info("SubscriptionMiddleware инициализирован.")

    def __call__(self, request):
        logger.debug(f"Получен запрос для пути: {request.path}")

        if not request.path.startswith(self.api_prefix):
            logger.debug(f"Путь '{request.path}' не начинается с префикса API, пропускаем.")
            return self.get_response(request)

        try:
            user_auth_tuple = self.jwt_authenticator.authenticate(request)
            if user_auth_tuple:
                authenticated_user, token = user_auth_tuple
                request.user = authenticated_user
                logger.debug(
                    f"Пользователь '{authenticated_user.email}' (ID: {authenticated_user.id}) аутентифицирован через JWT в мидлваре."
                )
            else:
                request.user = AnonymousUser()
        except (InvalidToken, TokenError) as e:
            logger.warning(f"Ошибка JWT аутентификации в мидлваре для '{request.path}': {e}")
            request.user = AnonymousUser()
        except Exception as e:
            logger.error(f"Неожиданная ошибка во время JWT аутентификации в мидлваре: {e}")
            request.user = AnonymousUser()

        if hasattr(request, "user") and request.user.is_authenticated and request.user.is_staff:
            logger.info(
                f"Пользователь '{request.user.email}' (ID: {request.user.id}) является сотрудником, проверка подписки пропущена."
            )
            return self.get_response(request)

        url_name = None
        try:
            match = resolve(request.path_info)
            if match.app_names:
                full_url_name_parts = match.app_names + [match.url_name]
                url_name = ":".join(full_url_name_parts)
            else:
                url_name = match.url_name
            logger.debug(f"Имя URL разрешено для пути '{request.path_info}': '{url_name}'")
        except Resolver404:
            logger.warning(f"URL '{request.path_info}' не может быть разрешен (Resolver404), пропускаем.")
            return self.get_response(request)

        if url_name is None:
            logger.warning(f"Имя URL не было определено для пути: {request.path_info}, пропускаем.")
            return self.get_response(request)

        is_exempt_from_subscription = False
        for pattern in self.public_api_urls:
            if url_name == pattern:
                is_exempt_from_subscription = True
                logger.debug(f"Имя URL '{url_name}' соответствует шаблону публичного API '{pattern}'.")
                break

        if not is_exempt_from_subscription:
            for pattern_prefix in self.subscription_exempt_urls_prefixes:
                if url_name.startswith(pattern_prefix):
                    is_exempt_from_subscription = True
                    logger.debug(
                        f"Имя URL '{url_name}' соответствует шаблону префикса, исключенного из проверки подписки '{pattern_prefix}'."
                    )
                    break

        if is_exempt_from_subscription:
            logger.info(f"Запрос к '{url_name}' разрешен без проверки подписки (в белом списке).")
            return self.get_response(request)

        if not (hasattr(request, "user") and request.user.is_authenticated):
            logger.warning(f"Доступ к '{url_name}' заблокирован: требуется аутентификация.")
            return JsonResponse(
                {"message": "Для доступа к этому ресурсу требуется аутентификация."}, status=HTTP_403_FORBIDDEN
            )

        if not request.user.has_active_subscription:
            user_info = f"Пользователь '{request.user.email}' (ID: {request.user.id})"
            logger.warning(f"Доступ к '{url_name}' заблокирован для {user_info}: требуется активная подписка.")
            return JsonResponse(
                {"message": "Для доступа к этому ресурсу требуется активная подписка."}, status=HTTP_403_FORBIDDEN
            )

        logger.debug(f"Запрос к '{url_name}' разрешен, пользователь имеет активную подписку.")
        response = self.get_response(request)
        return response
