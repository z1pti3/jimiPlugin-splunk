from core import plugin, model

class _splunk(plugin._plugin):
    version = 0.1

    def install(self):
        # Register models
        model.registerModel("splunkSearch","_splunkSearch","_trigger","plugins.splunk.models.trigger")
        return True

    def uninstall(self):
        # deregister models
        model.deregisterModel("splunkSearch","_splunkSearch","_trigger","plugins.splunk.models.trigger")
        return True

    def upgrade(self,LatestPluginVersion):
        pass