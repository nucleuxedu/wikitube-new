import socket
from django.core.mail.backends.smtp import EmailBackend as DjangoEmailBackend
import ssl

class CustomEmailBackend(DjangoEmailBackend):
    def __init__(self, host=None, port=None, username=None, password=None,
                 use_tls=None, fail_silently=False, use_ssl=None,
                 ssl_keyfile=None, ssl_certfile=None, timeout=None, **kwargs):
        super().__init__(host=host, port=port, username=username, password=password,
                         use_tls=use_tls, fail_silently=fail_silently,
                         use_ssl=use_ssl, ssl_keyfile=ssl_keyfile,
                         ssl_certfile=ssl_certfile, timeout=timeout, **kwargs)

    def open(self):
        """
        Ensures we have a connection to the email server. Returns whether or not a
        new connection was required (True or False).
        """
        if self.connection:
            return False

        connection_params = {
            "local_hostname": socket.getfqdn(),
            "timeout": self.timeout if self.timeout is not None else None,
        }
        if self.use_ssl:
            connection_params["context"] = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
            if self.ssl_certfile:
                connection_params["context"].load_cert_chain(
                    certfile=self.ssl_certfile, keyfile=self.ssl_keyfile
                )

        try:
            self.connection = self.connection_class(self.host, self.port, **connection_params)
            if not self.use_ssl and self.use_tls:
                self.connection.starttls(context=connection_params.get("context", None))
            if self.username and self.password:
                self.connection.login(self.username, self.password)
            return True
        except OSError:
            if not self.fail_silently:
                raise
