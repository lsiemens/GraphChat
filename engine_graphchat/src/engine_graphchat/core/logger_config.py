import logging


class IndentedFormatter(logging.Formatter):
    def format(self, record):
        message = super().format(record)

        lines = message.splitlines()
        if record.exc_info:
            lines[1:] = ["  |" + line for line in lines[1:]]
        else:
            lines[1:] = ["  " + line for line in lines[1:]]
        message = "\n".join(lines)
        return message


def configure(name, fname):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        handler = logging.FileHandler(fname)
        handler.setLevel(logging.INFO)

        formatter = IndentedFormatter("%(levelname)s:%(name)s: %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
