class AuditRouter(object):
    """
    A router to control all database operations on models in the
    audit application.
    """
    def db_for_write(self, model, **hints):
        """
        Attempts to read/write audit models go to the db set in AUDIT_DB.
        """

        if model._meta.app_label == 'audit':
            return 'audit_db'
        return None

    db_for_read = db_for_write

    def allow_relation(self, obj1, obj2, **hints):
        """
        Allow relations if a model in the audit app is involved.
        """
        if obj1._meta.app_label == 'audit' or \
           obj2._meta.app_label == 'audit':
           return True
        return None

    def allow_syncdb(self, db, model):
        """
        Make sure the audit app only appears in the AUDIT_DB database.
        """
        if db == 'audit_db':
            return model._meta.app_label == 'audit'
        elif model._meta.app_label == 'audit':
            return False
        return None
