# Domain-level exceptions.


class UserAlreadyExistsError(Exception):
    pass


def api_exception_handler(exc, context):
    import logging
    from rest_framework import status
    from rest_framework.response import Response
    from rest_framework.views import exception_handler

    response = exception_handler(exc, context)
    if response is not None:
        return response

    if isinstance(exc, UserAlreadyExistsError):
        return Response({"detail": str(exc)}, status=status.HTTP_409_CONFLICT)

    logging.getLogger("django.request").exception("Unhandled exception", exc_info=exc)
    return Response({"detail": "internal error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
