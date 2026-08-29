from init import exit
def argparse(options, args):
	options = {key: (item if item != [True] else []) for key, item in options.copy().items()}
	exitwith = lambda message: [print(message), exit(1)]
	curarg = None
	files_to_open = []
	for arg in args:
		if not curarg and not arg.startswith('--'):
			files_to_open.append(arg)
			continue
		if curarg and options[curarg] in (False, None) and not arg.startswith('--'):
			files_to_open.append(arg)
			continue
		if arg.startswith('--'):
			if curarg and options[curarg] not in (False, None):
				exitwith(f'unexpected "{arg}" after option "--{curarg}"')
			arg = arg[2:]
		if curarg and options[curarg] in (False, None):
			curarg = None
		if not curarg:
			if '=' in arg:
				opn, opv = arg.split('=', 1)
				if opn not in options:
					exitwith(f'error: unknown option "--{opn}"')
				if options[opn] == True:
					options[opn] = opv
				elif type(options[opn]) == list:
					options[opn].append(opv)
				elif options[opn] in (False, None):
					exitwith(f'error: option "--{opn}" does not take any argument')
				else:
					exitwith(f'error: repeated argument "--{arg}"')
			else:
				if arg not in options:
					exitwith(f'error: unknown option "--{arg}"')
				if options[arg] == True or type(options[arg]) == list:
					curarg = arg
				elif options[arg] == False:
					curarg = arg
					options[arg] = None
				else:
					exitwith(f'error: repeated argument "--{arg}"')
		elif curarg:
			if type(options[curarg]) == list:
				options[curarg].append(arg)
			else:
				options[curarg] = arg
			curarg = None
	if curarg and options[curarg] not in (False, None):
		exitwith(f'error: unspecified option "{curarg}"')
	for option in options:
		if options[option] is None:
			options[option] = True
		elif options[option] == True:
			options[option] = None
	return options, files_to_open
