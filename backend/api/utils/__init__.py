import random
import string
from django.utils.text import slugify

'''
random_generator is located here:
http://joincfe.com/blog/random-string-generator-in-python/
'''

DONT_USE = ['create']


def random_generator(size=10, chars=string.ascii_lowercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def unique_slug_generator(instance, new_slug=None):
    """
    This is for a Django project and it assumes your instance
    has a model with a slug field and a title character (char) field.
    """
    if new_slug is not None:
        slug = new_slug
    else:
        slug = slugify(instance.title)
    if slug in DONT_USE:
        new_slug = "{slug}-{randstr}".format(slug=slug,
                                             randstr=random_generator(size=4))
        return unique_slug_generator(instance, new_slug=new_slug)
    qs_exists = instance.__class__.objects.filter(slug=slug).exists()
    if qs_exists:
        new_slug = "{slug}-{randstr}".format(slug=slug,
                                             randstr=random_generator(size=4))
        return unique_slug_generator(instance, new_slug=new_slug)
    return slug