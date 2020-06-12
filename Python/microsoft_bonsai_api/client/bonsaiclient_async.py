from microsoft_bonsai_api.simulator.aio import SimulatorAPI
from .config import BonsaiClientConfig

# The API object that handles the REST connection to the bonsai platform.
class BonsaiClientAsync(SimulatorAPI):
    def __init__(self, config: BonsaiClientConfig, **kwargs):
        self._headers = {
            "Content-Type": "application/json",
            "Authorization": config.access_key,
        }

        self.workspace = config.workspace
        super(BonsaiClientAsync, self).__init__(
            base_url=config.server,
            headers=self._headers,
            logging_enable=config.enable_logging,
            kwargs=kwargs,
        )