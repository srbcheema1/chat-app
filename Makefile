all:
	echo "all"

compile:
	echo "compiling proto file"
	# -I is equivalent to -proto_path
	# python -m grpc_tools.protoc -I=proto/ --python_out=proto/ --grpc_python_out=proto/ proto/validator.proto
	python -m grpc_tools.protoc -I=proto/ --python_out=. --grpc_python_out=. proto/validator.proto

clean:
	rm *pb2*
