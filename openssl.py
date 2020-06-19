# pylint: disable=C0111
from base64 import b64encode

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.x509 import load_pem_x509_certificate


class OpenSSL:
    def __init__(self, certificate):
        self.key = OpenSSL.__load_cert_from_file(certificate)
        self.__cache = dict()

    @staticmethod
    def __load_cert_from_file(filename):
        with open(filename, "br") as x509_file:
            crl = load_pem_x509_certificate(x509_file.read(), default_backend())
            rsa = crl.public_key()
            return rsa

    def encrypt(self, text):
        if isinstance(text, str):
            text = text.encode("utf-8")
        if not self.__cache.get(text):
            raw_result = self.key.encrypt(text, padding.PKCS1v15())
            result = b64encode(raw_result).decode("utf-8")
            self.__cache[text] = result
        return self.__cache[text]


if __name__ == "__main__":

    def main():
        openssl = OpenSSL("SanitelCF.cer")
        print(openssl.encrypt(b"prova"))

    main()
