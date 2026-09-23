import sys, os


def encryptdecrypt(file):
    """XOR-encrypt or decrypt a file in place against a fixed key.

    XOR is its own inverse, so this single function both encrypts and
    decrypts depending on the file's current state.
    """
    try:
        filebytes = list(open(file, "rb").read())
    except:
        # File missing or unreadable; nothing to encrypt/decrypt.
        sys.exit(0)
    passwdbyte = list(
        ' 9nhvroi eht38tr455``""<>><,,..??/\\|ty857tc gh98h5489 5gc54tg/;ger"hgruigr``~}}[[}}|k_l-646'.encode(
            "utf-8"
        )
    )

    def xorlists(list1, list2):
        """XOR each byte of list2 with list1, repeating list1 as needed."""
        result = []
        for i in range(len(list2)):
            result.append(list1[i % len(list1)] ^ list2[i])
        return result

    resultbyte = bytes(xorlists(passwdbyte, filebytes))
    os.remove(file)
    open(file, "wb+").write(resultbyte)
