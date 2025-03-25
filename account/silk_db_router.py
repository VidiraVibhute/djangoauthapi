class SilkDBRouter:
    """
    A database router to send all Silk model operations to the 'silk' database.
    """

    def db_for_read(self, model, **hints):
        if model._meta.app_label == 'silk':
            return 'silk'
        return None

    def db_for_write(self, model, **hints):
        if model._meta.app_label == 'silk':
            return 'silk'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        if obj1._meta.app_label == 'silk' or obj2._meta.app_label == 'silk':
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label == 'silk':
            return db == 'silk'
        return db == 'default'
