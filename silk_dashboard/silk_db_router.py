from django.conf import settings

class SilkDBRouter:
    """
    Routes Silk models to the correct database.
    """

    def db_for_read(self, model, **hints):
        """Send Silk read queries to the correct database"""
        if model._meta.app_label == 'silk':
            return 'silk_live' if settings.IS_LIVE else 'silk_dev'
        return None

    def db_for_write(self, model, **hints):
        """Send Silk write queries to the correct database"""
        if model._meta.app_label == 'silk':
            return 'silk_live' if settings.IS_LIVE else 'silk_dev'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        """Allow relations between Silk objects"""
        if obj1._meta.app_label == 'silk' or obj2._meta.app_label == 'silk':
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """Ensure Silk tables are created only in the correct database"""
        if app_label == 'silk':
            return db == ('silk_live' if settings.IS_LIVE else 'silk_dev')
        return None
