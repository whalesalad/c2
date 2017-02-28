from c2.api.presenter import BasePresenter


class UserPresenter(BasePresenter):
    @property
    def serialized(self):
        return self.serialize(self.objects, fields=[
            'full_name',
            'first_name',
            'last_name',
            'email',
            'is_staff',
            ('created', lambda u: self.epoch(u.created)),
            ('team', lambda u: u.team.identifier)
        ])


class TeamPresenter(BasePresenter):
    @property
    def serialized(self):
        return self.serialize(self.objects, fields=['identifier', 'name'])


class MembershipPresenter(BasePresenter):
    @property
    def fields(self):
        return [
            'id',
            'role',
            ('created', lambda m: self.epoch(m.created)),
        ]


class APIKeyPresenter(BasePresenter):
    @property
    def fields(self):
        return [
            ('name', lambda k: k.name or 'Default Key'),
            'access_key',
            'secret_key',
            'is_active',
            ('created', lambda k: self.epoch(k.created)),
        ]