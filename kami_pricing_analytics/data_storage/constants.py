from kami_pricing_analytics.data_storage.modes.sql_storage.postgresql import (
    PostgreSQLConnection,
)
from kami_pricing_analytics.data_storage.settings import (
    MySQLSettings,
    PLSQLSettings,
    PostgreSQLSettings,
    SQLiteSettings,
    SQLServerSettings,
)

database_settingss_classes = {
    'sqlite': SQLiteSettings,
    'postgresql': PostgreSQLSettings,
    'mysql': MySQLSettings,
    'sqlserver': SQLServerSettings,
    'plsql': PLSQLSettings,
}

nosql_settingss_classes = {}

settings_classes = database_settingss_classes | nosql_settingss_classes

storage_classes = {'postgresql': PostgreSQLConnection}
