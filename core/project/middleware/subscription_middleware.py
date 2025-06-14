from django.http import JsonResponse
from rest_framework.status import HTTP_403_FORBIDDEN
from django.urls import resolve, Resolver404


class SubscriptionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.api_prefix = "/api/"
        self.allowed_urls_without_subscription = [
            "register",
            "token_obtain_pair",
            "token_refresh",
            "v1:tariff:tariff-list-create",
            "v1:subscriptions:subscriptions-list-create",
            "swagger-ui",
            "redoc",
            "schema",
            "v1:users:",
        ]

    def __call__(self, request):
        if not request.path.startswith(self.api_prefix):
            return self.get_response(request)

        if hasattr(request, "user") and request.user.is_authenticated and request.user.is_staff:
            return self.get_response(request)

        url_name = None
        try:
            match = resolve(request.path_info)
            if match.app_names:
                full_url_name_parts = match.app_names + [match.url_name]
                url_name = ":".join(full_url_name_parts)
            else:
                url_name = match.url_name
        except Resolver404:
            pass

        if url_name is None:
            return self.get_response(request)

        if url_name in self.allowed_urls_without_subscription:
            return self.get_response(request)

        if not (hasattr(request, "user") and request.user.is_authenticated and request.user.has_active_subscription):
            return JsonResponse(
                {"message": "Для доступа к этому ресурсу требуется активная подписка."}, status=HTTP_403_FORBIDDEN
            )

        response = self.get_response(request)
        return response
