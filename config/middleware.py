from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest
from django.utils.deprecation import MiddlewareMixin
from django_ratelimit.core import get_usage


class LoginRateLimitMiddleware(MiddlewareMixin):
    """Rate limit authentication attempts to reduce automated abuse."""

    protected_paths = (
        "/accounts/login/",
        "/accounts/signup/",
        "/accounts/password/reset/",
    )

    def process_view(self, request: HttpRequest, view_func, view_args, view_kwargs):
        if request.method != "POST":
            return None

        if not any(request.path.endswith(path) for path in self.protected_paths):
            return None

        usage = get_usage(
            request,
            group="auth-post",
            fn=view_func,
            key="ip",
            rate=settings.AUTH_RATE_LIMIT,
            method=["POST"],
            increment=True,
        )

        if usage and usage.get("should_limit"):
            raise PermissionDenied("Too many authentication requests. Please try again later.")

        return None
