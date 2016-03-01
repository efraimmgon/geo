from django.core import serializers
import json


def dump_object(obj):
	"""
	Takes a model object instance as input. Returns a string
	in json format.
	- model; fields; pk
	"""
	data = serializers.serialize('json', [obj])
	struct = json.loads(data)
	data = json.dumps(struct[0])
	return data