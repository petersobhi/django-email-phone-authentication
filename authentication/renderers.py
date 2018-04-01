from collections import OrderedDict

from rest_framework_json_api.renderers import JSONRenderer
from rest_framework import relations
from rest_framework.settings import api_settings
from rest_framework_json_api import utils

class JSONRenderer(JSONRenderer):
    @classmethod
    def build_json_resource_obj(cls, fields, resource, resource_instance, resource_name,
                                force_type_resolution=False):
        # Determine type from the instance if the underlying model is polymorphic
        if force_type_resolution:
            resource_name = utils.get_resource_type_from_instance(resource_instance)
        resource_data = [
            ('type', resource_name),
            # ('id', encoding.force_text(resource_instance.pk) if resource_instance else None),
            ('attributes', cls.extract_attributes(fields, resource)),
        ]
        relationships = cls.extract_relationships(fields, resource, resource_instance)
        if relationships:
            resource_data.append(('relationships', relationships))
        # Add 'self' link if field is present and valid
        if api_settings.URL_FIELD_NAME in resource and \
                isinstance(fields[api_settings.URL_FIELD_NAME], relations.RelatedField):
            resource_data.append(('links', {'self': resource[api_settings.URL_FIELD_NAME]}))
        return OrderedDict(resource_data)