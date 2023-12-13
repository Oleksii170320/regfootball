from django import template
import footballs.views as views


register = template.Library()

@register.simple_tag()
def get_rout():
    return views.district_bd
