"""course_request_form URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path

from form.views import (
    CopyFromCourseView,
    EnrollmentUserView,
    ExcludeAnnouncementsView,
    HomePageView,
    LookUpUserView,
    MyCanvasSitesView,
    MyCoursesView,
    MyRequestsView,
    RequestDetailView,
    RequestFormView,
    SchoolListView,
    SectionEnrollmentView,
    SectionListView,
    SyncSectionView,
    ToggleSchoolView,
    create_canvas_site_view,
    delete_enrollment_user,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("django.contrib.auth.urls")),
    path("", HomePageView.as_view(), name="home"),
    path("my-requests", MyRequestsView.as_view(), name="my_requests"),
    path("my-courses", MyCoursesView.as_view(), name="my_courses"),
    path("my-canvas-sites", MyCanvasSitesView.as_view(), name="my_canvas_sites"),
    path("sections/", SectionListView.as_view(), name="sections"),
    path("sections/<pk>", RequestDetailView.as_view(), name="request_detail"),
    path("sections/<pk>/request/", RequestFormView.as_view(), name="section_request"),
    path("copy-from-course/", CopyFromCourseView.as_view(), name="copy_from_course"),
    path("sync-section", SyncSectionView.as_view(), name="sync_section"),
    path(
        "exclude-announcements/",
        ExcludeAnnouncementsView.as_view(),
        name="exclude_announcements",
    ),
    path(
        "section-enrollment", SectionEnrollmentView.as_view(), name="section_enrollment"
    ),
    path("enrollment-user", EnrollmentUserView.as_view(), name="enrollment_user"),
    path(
        "enrollment-user/delete", delete_enrollment_user, name="delete_enrollment_user"
    ),
    path("create-canvas-site", create_canvas_site_view, name="create_canvas_site"),
    path("look-up-user", LookUpUserView.as_view(), name="look_up_user"),
    path("schools", SchoolListView.as_view(), name="schools"),
    path("toggle-school", ToggleSchoolView.as_view(), name="toggle_school"),
]
