from Crypto.Cipher import AES
import os
import pickle
import constants
# AES Encryption MODE_EAX
#
# def encrypt(plaintext,key):
# 	# Encrypting and serializing plaintext
# 	cipher = AES.new(key,AES.MODE_EAX)
# 	nonce = cipher.nonce
# 	ciphertext,tag=cipher.encrypt_and_digest(plaintext)
# 	return serial((nonce,ciphertext,tag))
#
# def decrypt(msg,key):
# 	# Decrypting and unserialize Ciphertext
# 	nonce,ciphertext,tag=unserial(msg)
# 	cipher = AES.new(key, AES.MODE_EAX, nonce=nonce)
# 	plaintext = cipher.decrypt(ciphertext)
# 	try:
# 		cipher.verify(tag)
# 		return (constants.SUCCESS,plaintext)
# 	except ValueError:
# 		print("Key incorrect or message corrupted...")
# 		return (constants.CORRUPTED_KEY,None)
# Fake Encryption For Testing


def encrypt(plaintext,key):
	return plaintext


def decrypt(ciphertext,key):
	return ciphertext


def get_key():
	return os.urandom(constants.N_BITS)


def serial(x):
	return pickle.dumps(x)


def unserial(x):
	return pickle.loads(x)


# #Test
if __name__ =="__main__":
	dict={"user":"A"}
	mykey=get_key()
	enc=encrypt(serial(dict),mykey)
	_,dec=decrypt(enc,mykey)
	print(unserial(dec))