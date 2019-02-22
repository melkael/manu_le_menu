from django.conf.urls import url
from .views import YoMamaBotView

urlpatterns = [
              url(r'23423c1d8298a3cdb529ac0b766ec8c56a0f449103e8aa0ad2/?$', YoMamaBotView.as_view()) # noqa 505
               ]
