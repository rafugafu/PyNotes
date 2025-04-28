import sys, os
def encryptdecrypt(file):
	try:
		filebytes = list(open(file, 'rb').read())
	except:
		sys.exit(0)
	passwdbyte = list(' 9nhvroi eht38tr455``""<>><,,..??/\\|ty857tc gh98h5489 5gc54tg/;ger"hgruigr``~}}[[}}|k_l-646'.encode('utf-8'))
	def xorlists(list1, list2):
		result = []
		for i in range(len(list2)):
			result.append(list1[i % len(list1)] ^ list2[i])
		return result
	resultbyte = bytes(xorlists(passwdbyte, filebytes))
	os.remove(file)
	open(file, 'wb+').write(resultbyte)