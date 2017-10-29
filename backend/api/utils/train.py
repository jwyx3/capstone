from nltk.corpus import stopwords
from nltk.tokenize import regexp_tokenize
from nltk import ngrams
import collections
import itertools
import logging
import re
import os


class UsedCar(object):
    __slots__ = [
        'year', 'make', 'model', 'odometer',
        'dealer', 'posted_at', 'latitude', 'longitude',
        'title_status', 'cylinders', 'drive', 'fuel',
        'transmission', 'type', 'color', 'condition',
        'size', 'post_url', 'price'
    ]

    excluded_attr = []

    @classmethod
    def get_attrs(cls):
        return [attr for attr in cls.__slots__ if attr not in cls.excluded_attr]

    def __init__(self, **kwargs):
        for attr in self.__slots__:
            setattr(self, attr, kwargs.get(attr))

    def __str__(self):
        return ','.join(str(getattr(self, attr)) for attr in self.get_attrs())

    def to_dict(self):
        return {k: getattr(self, k) for k in self.get_attrs()}

    def to_ad(self, make=None, model=None):
        ad, ok = {}, True
        for k, v in self.to_dict().items():
            if k in ('year', 'make', 'model', 'price') and not v:
                ok = False
                break
            if k == 'make':
                ad['make'] = make or v
            elif k == 'model':
                ad['model'] = model or v
            elif k == 'type':
                ad['category'] = v
            elif k == 'url':
                ad['post_url'] = v
            elif k in ('latitude', 'longitude', 'price') and v:
                ad[k] = float(v)
            elif k in ('odometer', 'cylinders', 'year') and v:
                ad[k] = int(v)
            elif k in ('dealer',):
                ad[k] = bool(v)
            elif v:
                ad[k] = v
        return ad if ok else None

    def to_train_post(self, make_id=None, make=None, model_id=None, model=None):
        ad = self.to_ad(make, model)

        if make_id is not None:
            ad['make_id'] = int(make_id)
        if model_id is not None:
            ad['model_id'] = int(model_id)

        required = (
            'year', 'make', 'model', 'odometer', 'dealer', 'title_status',
            'post_url', 'posted_at', 'price')
        missing = [k for k in required if ad.get(k) in ['', None]]

        if missing:
            logging.info("some fields (%s) are missing and don't add into train set", missing)
            return None

        fields = (
            'year', 'make', 'model', 'odometer', 'dealer', 'title_status',
            'cylinders', 'drive', 'fuel', 'transmission', 'color',
            'condition', 'size', 'post_url', 'posted_at', 'price',
            'make_id', 'model_id')
        for field in fields:
            if field not in ad:
                ad[field] = None
        return ad


def validate_required(data, required=None):
    if required:
        for field in required:
            assert field in data


def get_data_dir(filename):
    return os.path.join(os.path.dirname(__file__), '../../data', filename)


def load_make_model():
    make_model = collections.defaultdict(set)
    with open(get_data_dir('make_model.txt'), 'r') as fh:
        for line in fh:
            make, model = line.strip().split(',')
            make_model[make].add(model)
    return make_model


def load_models_mapping(make_model):
    models_mapping = {
        make: {
            model: set([model]) for model in models
        } for make, models in make_model.items()
    }
    with open(get_data_dir('model_synonym.txt'), 'r') as fh:
        for line in fh:
            line = line.strip()
            if line:
                make, models = line.split(',', 1)
                models = models.split(',')
                for model in models:
                    if make not in models_mapping:
                        models_mapping[make] = {}
                    if models[0] not in models_mapping[make]:
                        models_mapping[make][models[0]] = set()
                    models_mapping[make][models[0]].add(model)
    return models_mapping


def load_makes_mapping(make_model, models_mapping):
    makes_mapping = {make: make for make in make_model.keys()}
    with open(get_data_dir('make_synonym.txt'), 'r') as fh:
        for line in fh:
            line = line.strip()
            if line:
                makes = line.split(',')
                for make in makes:
                    makes_mapping[make] = makes[0]
    # combine model and make
    for make in models_mapping:
        if make not in makes_mapping:
            makes_mapping[make] = make
    return makes_mapping


stop_words = set(stopwords.words('english'))
stop_words.update([
    '.', ',', '"', "'", '?', '!', ':', ';', '(', ')', '[', ']',
    '{', '}', '&', '/', '...', '--', '+', '*', '|', "),", "**"
])
BODY_LEN = 50


def is_valid(m, excluded=None):
    if not excluded:
        excluded = []
    return m and m.group(1) and ':' not in m.group(1) and m.group(1) not in excluded


def get_used_car(item, makes_mapping, models_mapping):
    text = str(' '.join(item['attr_text'] + [item['title'], item['body'][:BODY_LEN]]).lower().encode('utf-8'))
    attr_text = str(' '.join(item['attr_text']))

    logging.debug("text: %s, attr_text: %s", text, attr_text)

    # tokens
    digit_tokens = [x for x in regexp_tokenize(text, pattern='\d+')]
    tokens = [x for x in regexp_tokenize(text, pattern='[a-z0-9-]+')]

    used_car = UsedCar()

    # get year, only cars after 1990
    year = [x for x in digit_tokens]
    if len(year) == 0 or int(year[0]) < 1990:
        return None
    year = year[0]
    used_car.year = int(year.strip())

    # get price
    if not item['price']:
        return None
    used_car.price = float(item['price'].strip())

    # get title status
    m = re.match('.*title status: ([\w:]+) .*', text)
    if not m or ':' in m.group(1):
        return None
    used_car.title_status = m.group(1).strip()

    # get make
    used_car.make = None
    for make in itertools.chain(ngrams(tokens, 3), ngrams(tokens, 2), tokens):
        if isinstance(make, tuple):
            make = ' '.join(make)
        if make in makes_mapping:
            used_car.make = makes_mapping[make].strip()
            break
    if not used_car.make:
        return None

    logging.debug("make of used car: %s", used_car.make)

    # get model
    used_car.model = None
    if used_car.make not in models_mapping:
        return None
    for model in itertools.chain(ngrams(tokens, 3), ngrams(tokens, 2), tokens):
        models_to_check = [model]
        if isinstance(model, tuple):
            models_to_check = [' '.join(model), ''.join(model), '-'.join(model)]
        for model_name in models_mapping[used_car.make]:
            for model in models_to_check:
                if model in models_mapping[used_car.make][model_name]:
                    used_car.model = model_name.strip()
                    break
    if not used_car.model:
        return None

    logging.debug("model of used car: %s", used_car.model)

    # get odometer
    m = re.match('.*odometer: (\d+)[^\d]*.*', attr_text)
    used_car.odometer = float(m.group(1).strip()) if m else None

    # get cylinders
    m = re.match('.*cylinders: (\d+)[^\d]*.*', attr_text)
    used_car.cylinders = int(m.group(1).strip()) if m else None

    # get drive
    m = re.match('.*drive: ([\w:]+) .*', attr_text)
    used_car.drive = m.group(1).strip() if is_valid(m, ['title']) else None

    # get fuel
    m = re.match('.*fuel: ([\w:]+) .*', attr_text)
    used_car.fuel = m.group(1) if is_valid(m, ['title']) else None

    # get color
    m = re.match('.*paint color: ([\w:]+) .*', attr_text)
    used_car.color = m.group(1).strip() if is_valid(m, ['title']) else None

    # get type
    m = re.match('.*type: ([-\w:]+) .*', attr_text)
    used_car.type = m.group(1).strip() if is_valid(m, ['title']) else None

    # get size
    m = re.match('.*size: ([-\w:]+) .*', attr_text)
    used_car.size = m.group(1).strip() if is_valid(m, ['title']) else None

    # get condition
    m = re.match('.*condition: (like new|[\w:]+) .*', attr_text)
    used_car.condition = m.group(1).strip() if is_valid(m, ['title']) else None

    # get transmission
    m = re.match('.*transmission: ([\w:]+) .*', attr_text)
    used_car.transmission = m.group(1).strip() if is_valid(m, ['title']) else None

    # get others
    used_car.dealer = item['dealer']

    used_car.latitude = item['latitude']
    if used_car.latitude:
        used_car.latitude = float(used_car.latitude.strip())

    used_car.longitude = item['longitude']
    if used_car.longitude:
        used_car.longitude = float(used_car.longitude.strip())

    # used_car.address = item['address']
    used_car.posted_at = item['posted_at']
    used_car.post_url = item['url']

    return used_car
