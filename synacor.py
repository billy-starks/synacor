from pprint import pprint
import sys
import pickle
import types

memory = {address:0 for address in range(0, 2**15)}
registry = [0 for _ in range(8)]
stack = []

ip = 0
input_buffer = ""
trace_active = False
debugging = False
debugging_disabled = False

def load_program(file):
	global ip
	with open(file, 'rb') as fp:
		address = 0
		while True:
			byte_data = fp.read(2)
			if byte_data is None or address >= 2**15:
				break
			word = int.from_bytes(byte_data, byteorder='little')
			memory[address] = word
			address += 1
	ip = 0

def load_program_mod(file):
	global ip
	with open(file, 'rb') as fp:
		address = 0
		while True:
			byte_data = fp.read(2)
			if byte_data is None or address >= 2**15:
				break
			word = int.from_bytes(byte_data, byteorder='little')
			memory[address] = word
			address += 1
	ip = 0

def run_program(debug=False):
	global ip, debugging, debugging_disabled

	while True:
		if ip == 5489:
			memory[5489] = 21
			memory[5490] = 21
			print(memory[5489])
			registry[0] = 6
			registry[7] = 25734
			print("Debugging Activated")
			debugging = True
		# if ip == 5588:
		# 	registry[0] = 32765
		# 	print("Debugging Activated")
		# 	debugging = True
		# if ip == 6027 and not debugging_disabled:
		# 	debugging = True
		# 	print("Debugging Activated")
		# 	print(memory[5489])
		# 	registry[7] = 0
		# if debugging:
		# 	print(ip, registry)
		# 	inp = input()
		# 	if inp in ["c", "cont", "continue"]:
		# 		debugging = False
		# 	if inp in ["s", "stop"]:
		# 		debugging_disabled = True

		word = get_word()
		func = opcode_to_func.get(word)
		if isinstance(func, types.FunctionType):
			func()
		elif func is not None:
			if func == "halt":
				break
			if func == "noop":
				continue

def read_program(pointer, length=20):
	global ip
	before_read_ip = ip
	ip = pointer
	i = 0
	program =""
	while i < length and ip in memory:
		start_ip = ip
		word = get_word()
		func = opcode_to_name.get(word, word)
		num_args = opcode_to_args.get(word)
		num_args = 0 if num_args is None else num_args
		args = [get_word() for _ in range(num_args)]
		program += f"{start_ip}: {func} {args}\n"
		i += 1
	ip = before_read_ip
	with open("program", "w") as file:
		file.write(program)




def get_word():
	"""
	Return the word that ip points to, and increments ip
	This returns the raw word that ip points to, and doesn't attempt to dereference registry addresses
	"""
	global ip

	word = memory[ip]
	ip += 1
	return word

def process_argument(value):
	if value > (2**15 + 8):
		raise Exception(f"Invalid value: {value}")
	if value >= 2**15:
		registry_num = value - 2**15
		return registry[registry_num]
	return value

def get_arg():
	"""
	Gets the argument that ip points to
	If ip points to a registry value (32768 - 32775), this returns the value stored in that registry address
	"""
	value = get_word()
	return process_argument(value)

def get_mem():
	"""
	Gets the value at the memory address that ip points to, and increments ip
	"""
	value = get_word()
	address = process_argument(value)
	return memory[address]

def do_print(text):
	print(text, end='', file=sys.stdout)

def set_to(location, value):
	if location >= 2**15:
		registry_num = location - 2**15
		if registry_num > 7:
			raise Exception(f"Trying to set to invalid location {location}")
		registry[registry_num] = value
	else:
		memory[location] = value

def do_out():
	arg = get_arg()
	do_print(chr(arg))

def do_jmp():
	global ip

	arg = get_arg()
	ip = arg

def do_jt():
	global ip

	a = get_arg()
	b = get_arg()
	if a != 0:
		ip = b

def do_jf():
	global ip

	a = get_arg()
	b = get_arg()
	if a == 0:
		ip = b

def do_set():
	a = get_word()
	b = get_arg()
	if not (2**15 <= a < 2**15 + 8):
		raise Exception(f"Can't set data to non-registry input {a}")
	registry_num = a - 2**15
	registry[registry_num] = b

def do_add():
	store_location = get_word()
	a = get_arg()
	b = get_arg()
	sum = (a + b) % 2**15
	set_to(store_location, sum)

def do_eq():
	store_location = get_word()
	a = get_arg()
	b = get_arg()
	if a == b:
		set_to(store_location, 1)
	else:
		set_to(store_location, 0)

def do_push():
	arg = get_arg()
	stack.append(arg)

def do_pop():
	location = get_word()
	if not stack:
		raise Exception("Trying to pop from empty stack")
	value = stack.pop()
	set_to(location, value)

def do_gt():
	store_location = get_word()
	a = get_arg()
	b = get_arg()
	if a > b:
		set_to(store_location, 1)
	else:
		set_to(store_location, 0)

def do_and():
	store_location = get_word()
	a = get_arg()
	b = get_arg()
	value = a & b
	set_to(store_location, value)

def do_or():
	store_location = get_word()
	a = get_arg()
	b = get_arg()
	value = a | b
	set_to(store_location, value)

def do_not():
	store_location = get_word()
	a = get_arg()
	bitstring = bin(a)[2:].zfill(15)
	inverted_bitstring = "".join(("1" if x == "0" else "0") for x in bitstring)
	set_to(store_location, int(inverted_bitstring, 2))

def do_call():
	global ip

	dest = get_arg()
	next_address = ip
	stack.append(next_address)
	ip = dest

def do_mult():
	store_location = get_word()
	a = get_arg()
	b = get_arg()
	product = (a * b) % 2**15
	set_to(store_location, product)

def do_mod():
	store_location = get_word()
	a = get_arg()
	b = get_arg()
	modulus = (a % b)
	set_to(store_location, modulus)

def do_ret():
	global ip

	if not stack:
		exit(0)
	ip = stack.pop()

def do_rmem():
	store_location = get_word()
	a = get_mem()
	set_to(store_location, a)

def do_wmem():
	store_location = get_arg()
	a = get_arg()
	set_to(store_location, a)

def do_in():
	global input_buffer, trace_active

	store_location = get_word()
	while not input_buffer:
		input_buffer = input('>: ') + '\n'
	character = ord(input_buffer[0])
	input_buffer = input_buffer[1:]
	if character == ord("!"):
		save_state()
	if character == ord("?"):
		load_state()
	if character == ord("}"):
		trace_active = True
	set_to(store_location, character)

def save_state():
	with open('savestate', 'wb') as handle:
		data = memory, registry, stack, ip
		pickle.dump(data, handle)

def load_state():
	global memory, registry, stack, ip
	with open('savestate', 'rb') as handle:
		memory, registry, stack, ip = pickle.load(handle)
		print(registry)
		registry[7] = 32767

opcode_to_func = {
	19: do_out,
	6: do_jmp,
	7: do_jt,
	8: do_jf,
	1: do_set,
	9: do_add,
	4: do_eq,
	2: do_push,
	3: do_pop,
	5: do_gt,
	12: do_and,
	13: do_or,
	14: do_not,
	17: do_call,
	10: do_mult,
	11: do_mod,
	18: do_ret,
	15: do_rmem,
	16: do_wmem,
	20: do_in,
	0: "halt",
	21: "noop"
}

opcode_to_name = {
	19: "out",
	6: "jmp",
	7: "jt",
	8: "jf",
	1: "set",
	9: "add",
	4: "eq",
	2: "push",
	3: "pop",
	5: "gt",
	12: "and",
	13: "or",
	14: "not",
	17: "call",
	10: "mult",
	11: "mod",
	18: "ret",
	15: "rmem",
	16: "wmem",
	20: "in",
	0: "halt",
	21: "noop"
}

opcode_to_args = {
	19: 1,
	6: 1,
	7: 2,
	8: 2,
	1: 2,
	9: 3,
	4: 3,
	2: 1,
	3: 1,
	5: 3,
	12: 3,
	13: 3,
	14: 2,
	17: 1,
	10: 3,
	11: 3,
	18: 0,
	15: 2,
	16: 2,
	20: 1,
	0: 0,
	21: 0
}

load_program_mod("challenge.bin")
# read_program(0, length=9999999999999)
run_program(debug=True)
