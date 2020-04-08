class CurrentUserDefault:
    """Return current logged-in user"""
    def set_context(self, serializer_field):
        user = serializer_field.context['request'].user
        self.user = user

    def __call__(self):
        return self.user

    def __repr__(self):
        return '%s()' % self.__class__.__name__
