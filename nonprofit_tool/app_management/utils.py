import traceback
from .models import ErrorLog

def log_error(app_name, function_name, error_message):
    stack_trace = traceback.format_exc()
    ErrorLog.objects.create(
        app_name=app_name,
        function_name=function_name,
        error_message=error_message,
        stack_trace=stack_trace
    )
