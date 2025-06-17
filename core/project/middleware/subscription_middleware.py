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
        logger.info("SubscriptionMiddleware initialized.")

    def __call__(self, request):
        logger.debug(f"Request received for path: {request.path}")

        if not request.path.startswith(self.api_prefix):
            logger.debug(f"Path '{request.path}' does not start with API prefix, skipping.")
            return self.get_response(request)

        try:
            # Попытка аутентификации пользователя через JWT в мидлваре
            user_auth_tuple = self.jwt_authenticator.authenticate(request)
            if user_auth_tuple:
                authenticated_user, token = user_auth_tuple
                request.user = authenticated_user
                logger.debug(
                    f"User '{authenticated_user.email}' (ID: {authenticated_user.id}) authenticated via JWT in middleware."
                )
            else:
                # Если authenticate вернул None, значит токен отсутствовал или был не в том формате,
                # но не вызвал исключения. Пользователь пока остается AnonymousUser.
                request.user = AnonymousUser()
        except (InvalidToken, TokenError) as e:
            logger.warning(f"JWT authentication error in middleware for '{request.path}': {e}")
            request.user = AnonymousUser()
        except Exception as e:
            logger.error(f"Unexpected error during JWT authentication in middleware: {e}")
            request.user = AnonymousUser()

        if hasattr(request, "user") and request.user.is_authenticated and request.user.is_staff:
            logger.info(f"User '{request.user.email}' (ID: {request.user.id}) is staff, skipping subscription check.")
            return self.get_response(request)

        url_name = None
        try:
            match = resolve(request.path_info)
            if match.app_names:
                full_url_name_parts = match.app_names + [match.url_name]
                url_name = ":".join(full_url_name_parts)
            else:
                url_name = match.url_name
            logger.debug(f"URL name resolved for path '{request.path_info}': '{url_name}'")
        except Resolver404:
            logger.warning(f"URL '{request.path_info}' could not be resolved (Resolver404), skipping.")
            return self.get_response(request)

        if url_name is None:
            logger.warning(f"url_name was not determined for path: {request.path_info}, skipping.")
            return self.get_response(request)

        is_exempt_from_subscription = False
        for pattern in self.public_api_urls:
            if url_name == pattern:
                is_exempt_from_subscription = True
                logger.debug(f"URL name '{url_name}' matched public API pattern '{pattern}'.")
                break

        if not is_exempt_from_subscription:
            for pattern_prefix in self.subscription_exempt_urls_prefixes:
                if url_name.startswith(pattern_prefix):
                    is_exempt_from_subscription = True
                    logger.debug(
                        f"URL name '{url_name}' matched subscription exempt prefix pattern '{pattern_prefix}'."
                    )
                    break

        if is_exempt_from_subscription:
            logger.info(f"Request to '{url_name}' allowed without subscription check (whitelisted).")
            return self.get_response(request)

        if not (hasattr(request, "user") and request.user.is_authenticated):
            logger.warning(f"Access to '{url_name}' blocked: authentication required.")
            return JsonResponse(
                {"message": "Authentication required to access this resource."}, status=HTTP_403_FORBIDDEN
            )

        if not request.user.has_active_subscription:
            user_info = f"User '{request.user.email}' (ID: {request.user.id})"
            logger.warning(f"Access to '{url_name}' blocked for {user_info}: active subscription required.")
            return JsonResponse(
                {"message": "An active subscription is required to access this resource."}, status=HTTP_403_FORBIDDEN
            )

        logger.debug(f"Request to '{url_name}' allowed, user has an active subscription.")
        response = self.get_response(request)
        return response
