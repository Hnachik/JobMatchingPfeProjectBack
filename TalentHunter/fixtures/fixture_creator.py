from collections import defaultdict


class FixtureCreator:
    CATEGORY = 'jobMatchingApi.JobCategory'
    USER = 'accounts.User'
    RECRUITER = 'accounts.Recruiter'
    JOB_POST = 'jobMatchingApi.JobPost'

    def __init__(self, data, recruiter_name=None):
        """Initialize fixtures.

        Fixtures for each model are stored in self._fixtures dict,
        where the key is the name of the model.
        """
        self._data = data
        self._fixtures = defaultdict(list)
        self._auto_ids = defaultdict(int)
        self._recruiter = recruiter_name if recruiter_name is not None else 'Recruiter'

        self._init_categories()
        self._init_recruiter()
        self._init_job_posts()

    def get_fixtures(self):
        """Return valid Django fixtures list."""
        result = []

        fixtures_order = [
            self.CATEGORY,
            self.USER,
            self.RECRUITER,
            self.JOB_POST,
        ]

        for key in fixtures_order:
            print(key)
            result += self._fixtures[key]

        return result

    def _auto_id(self, model_name):
        """Get id for new record (counted in ascending order from 1)."""
        self._auto_ids[model_name] += 1
        return self._auto_ids[model_name]

    def _get_id(self, model_name, fields):
        """Get id of a specific record.

        Returns the first matching record in 'model_name' model.
        """
        if not isinstance(fields, dict):
            raise AttributeError('Argument fields must be a dict')

        for model in self._fixtures[model_name]:
            if model_name == 'jobpost.Recruiter':
                if model['fields']['company_name'] == fields['company_name']:
                    return model['pk']
            else:
                if all(model['fields'][field] == fields[field]
                   for field in fields):
                    return model['pk']

    def _exists(self, model_name, fields):
        """Check if a specific record exists."""
        return self._get_id(model_name, fields) is not None

    def _add_record(self, model_name, fields, pk=None):
        """Add a record to fixtures list."""
        self._fixtures[model_name].append({
            'model': model_name,
            'pk': self._auto_id(model_name) if pk is None else pk,
            'fields': fields
        })

    def _add_if_not_exists(self, model_name, fields):
        if not self._exists(model_name, fields):
            self._add_record(model_name, fields)

    def _get_category_set(self, category_list):
        category_map = {category['fields']['category_name']: category['pk']
                        for category in self._fixtures[self.CATEGORY]}

        return [category_map[category] for category in category_list]

    def _init_categories(self):
        for item in self._data:
            for category in item['fields']:
                self._add_if_not_exists(self.CATEGORY, {
                    'category_name': category
                })

    def _init_recruiter(self):
        i = 0
        j = 0
        for item in self._data:
            i += 1
            user_name = 'User' + str(i)
            user_email = '{s}@gmail.com'.format(s=user_name)
            self._add_if_not_exists(self.USER, {
                'username': user_name,
                'password': 'pbkdf2_sha256$120000$Wdnp6gUfa0kb$Z7DK+ljXkluKSYwSGYuNrevvC+mhcHAeOdNgtcEGrFA=',
                'email': user_email
            })

        for item in self._data:
            j += 1
            self._add_if_not_exists(self.RECRUITER, {
                'user': j,
                'company_name': item['company_name'],
                'company_description': item['company_description'],
                'company_logo': item['company_logo'],
                'address': item['location']
            })

    def _init_job_posts(self):

        for item in self._data:

            recruiter_id = self._get_id(self.RECRUITER, {'company_name': item['company_name']})
            if recruiter_id:

                self._add_if_not_exists(self.JOB_POST, {
                    'recruiter': recruiter_id,
                    'post_url': item['post_url'],
                    'job_title': item['job_title'],
                    'job_description': item['job_description'],
                    'job_requirements': item['job_requirements'],
                    'job_type': item['job_type'],
                    'location': item['location'],
                    'publication_date': item['publication_date'],
                    'expiration_date': item['expiration_date'],
                    'category_set': self._get_category_set(item['fields'])
                })
