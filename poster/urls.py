from django.conf.urls import url
from django.contrib import admin
from django.urls import path, include

from apps.common.routers import CustomRouter
from apps.mc.api.urls import router as mc_router

# ===== BEGIN API PATTERNS =====
router = CustomRouter()
router.extend(mc_router)

api_patterns = ([url(r'^', include(router.urls)), ], 'api')

# ===== BEGIN URL PATTERNS =====
urlpatterns = []

# ===== INCLUDE API PATTERNS =====
urlpatterns += [
    url(r'^api/v1/', include(api_patterns)),
]

# ===== INCLUDE STANDARD PATTERNS =====
urlpatterns += [
    path('admin/', admin.site.urls),
    path('import/', include('apps.importing.urls')),
    path('mc/', include('apps.mc.urls')),
]
