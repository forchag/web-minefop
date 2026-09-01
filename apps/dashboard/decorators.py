from django.contrib.auth.decorators import user_passes_test

#: A single gate for every dashboard view: anonymous or non-staff users are
#: sent to the dashboard's own login page (not /admin/'s), preserving
#: `next` so they land back where they were headed.
staff_required = user_passes_test(
    lambda user: user.is_authenticated and user.is_staff,
    login_url="dashboard:login",
)
