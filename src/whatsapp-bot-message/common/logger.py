import logging
import logging.config

logging.config.fileConfig(
    fname='./whatsapp-bot-message/common/file.conf',
    disable_existing_loggers=True
)
# Get the logger specified in the file
logger = logging.getLogger(__name__)
